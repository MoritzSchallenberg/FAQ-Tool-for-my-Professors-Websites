from pathlib import Path
from time import time
from typing import Dict, List, Optional
import hashlib
import hmac
import secrets

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .auth import create_token, require_admin
from .config import get_settings
from .database import execute, fetch_all, fetch_one, init_pool

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

settings = get_settings()

app = FastAPI(
    title="FAQ-Tool Elektrotechnik",
    description="Ein kleines FAQ-System für Fragen von Studierenden mit Adminbereich.",
    version="1.1.0",
)

allowed_origins = [origin.strip() for origin in settings.allowed_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# Very small in-memory rate limiter for question submission.
# For multi-server production, replace with Redis or database-backed rate limiting.
_rate_limit: Dict[str, List[float]] = {}


class AdminLogin(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


class QuestionCreate(BaseModel):
    question_text: str = Field(min_length=5, max_length=settings.max_question_length)
    category_id: Optional[int] = None
    category_name: Optional[str] = Field(default=None, max_length=120)
    course_slug: Optional[str] = Field(default=None, max_length=120)
    # Optional contact field; frontend currently does not show it by default.
    contact_email: Optional[str] = Field(default=None, max_length=255)
    # Honeypot field against simple spambots. It must stay empty.
    website: Optional[str] = Field(default=None, max_length=200)


class AnswerPayload(BaseModel):
    answer_text: str = Field(min_length=1, max_length=8000)
    publish: bool = False


class StatusPayload(BaseModel):
    status: str = Field(pattern="^(open|answered|published|hidden|deleted)$")


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class AdminQuestionUpdate(BaseModel):
    question_text: str = Field(min_length=5, max_length=settings.max_question_length)
    answer_text: Optional[str] = Field(default=None, max_length=8000)
    category_id: Optional[int] = None
    category_name: Optional[str] = Field(default=None, max_length=120)
    status: str = Field(pattern="^(open|answered|published|hidden|deleted)$")


@app.on_event("startup")
def startup() -> None:
    init_pool()


@app.get("/", include_in_schema=False)
def page_index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/ask", include_in_schema=False)
def page_ask():
    return FileResponse(FRONTEND_DIR / "ask.html")


@app.get("/admin-login", include_in_schema=False)
def page_admin_login():
    return FileResponse(FRONTEND_DIR / "admin-login.html")


@app.get("/admin", include_in_schema=False)
def page_admin():
    return FileResponse(FRONTEND_DIR / "admin.html")


@app.get("/embed", include_in_schema=False)
def page_embed():
    embed_file = FRONTEND_DIR / "embed.html"
    if embed_file.exists():
        return FileResponse(embed_file)
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/meta")
def meta():
    return {
        "course_slug": settings.course_slug,
        "course_name": settings.course_name,
        "max_question_length": settings.max_question_length,
    }


@app.post("/api/admin/login")
def admin_login(payload: AdminLogin):
    if not secrets.compare_digest(payload.username, settings.admin_username):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login fehlgeschlagen.")
    if not secrets.compare_digest(payload.password, settings.admin_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login fehlgeschlagen.")
    return {"token": create_token(payload.username), "username": payload.username}


@app.get("/api/categories")
def get_categories():
    return fetch_all(
        """
        SELECT id, name
        FROM categories
        WHERE is_active = 1
        ORDER BY sort_order ASC, name ASC
        """
    )


@app.post("/api/admin/categories", status_code=201)
def create_category(payload: CategoryCreate, _: str = Depends(require_admin)):
    name = " ".join(payload.name.strip().split())
    if not name:
        raise HTTPException(status_code=400, detail="Kategorie darf nicht leer sein.")

    existing = fetch_one("SELECT id, is_active FROM categories WHERE name = %s", (name,))
    if existing:
        if int(existing["is_active"]):
            raise HTTPException(status_code=400, detail="Diese Kategorie existiert bereits.")
        execute("UPDATE categories SET is_active = 1 WHERE id = %s", (existing["id"],))
        return {"message": "Kategorie wurde wieder aktiviert.", "category_id": existing["id"]}

    next_order = fetch_one("SELECT COALESCE(MAX(sort_order), 0) + 10 AS next_order FROM categories")
    category_id = execute(
        "INSERT INTO categories (name, sort_order, is_active) VALUES (%s, %s, 1)",
        (name, int(next_order["next_order"]) if next_order else 100),
    )
    return {"message": "Kategorie wurde hinzugefügt.", "category_id": category_id}


@app.delete("/api/admin/categories/{category_id}")
def remove_category(category_id: int, _: str = Depends(require_admin)):
    category = fetch_one("SELECT id, name FROM categories WHERE id = %s AND is_active = 1", (category_id,))
    if not category:
        raise HTTPException(status_code=404, detail="Kategorie wurde nicht gefunden.")

    # Fragen behalten, aber die entfernte Kategorie lösen. So gehen keine Fragen verloren.
    execute("UPDATE questions SET category_id = NULL WHERE category_id = %s", (category_id,))
    execute("UPDATE categories SET is_active = 0 WHERE id = %s", (category_id,))
    return {"message": f"Kategorie '{category['name']}' wurde entfernt. Zugeordnete Fragen bleiben erhalten."}


@app.get("/api/faqs")
def get_public_faqs(query: str = "", category_id: Optional[int] = None):
    params: List[object] = []
    where = ["q.is_public = 1", "q.status = 'published'"]

    if query.strip():
        where.append("(q.question_text LIKE %s OR a.answer_text LIKE %s OR c.name LIKE %s)")
        term = f"%{query.strip()}%"
        params.extend([term, term, term])

    if category_id is not None:
        where.append("q.category_id = %s")
        params.append(category_id)

    sql = f"""
        SELECT
            q.id,
            q.question_text,
            q.created_at,
            c.name AS category_name,
            a.answer_text,
            a.updated_at AS answer_updated_at
        FROM questions q
        LEFT JOIN categories c ON q.category_id = c.id
        LEFT JOIN answers a ON a.question_id = q.id
        WHERE {' AND '.join(where)}
        ORDER BY q.answered_at DESC, q.created_at DESC
        LIMIT 200
    """
    return fetch_all(sql, tuple(params))


def _client_key(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    ip = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else "unknown")
    return ip


def _check_rate_limit(request: Request) -> None:
    now = time()
    key = _client_key(request)
    recent = [ts for ts in _rate_limit.get(key, []) if now - ts < 3600]
    if len(recent) >= settings.max_questions_per_hour:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Zu viele Fragen in kurzer Zeit. Bitte später erneut versuchen.",
        )
    recent.append(now)
    _rate_limit[key] = recent


def _ip_hash(request: Request) -> str:
    key = _client_key(request)
    return hmac.new(
        settings.ip_hash_salt.encode("utf-8"),
        key.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _get_course_id(slug: Optional[str]) -> int:
    course_slug = slug or settings.course_slug
    course = fetch_one("SELECT id FROM courses WHERE slug = %s", (course_slug,))
    if course:
        return int(course["id"])
    return execute("INSERT INTO courses (name, slug) VALUES (%s, %s)", (settings.course_name, course_slug))


def _get_category_id(category_id: Optional[int], category_name: Optional[str]) -> Optional[int]:
    if category_id is not None:
        existing = fetch_one("SELECT id FROM categories WHERE id = %s AND is_active = 1", (category_id,))
        if existing:
            return int(existing["id"])
        raise HTTPException(status_code=400, detail="Kategorie wurde nicht gefunden.")

    if category_name and category_name.strip():
        name = category_name.strip()[:120]
        existing = fetch_one("SELECT id FROM categories WHERE name = %s", (name,))
        if existing:
            return int(existing["id"])
        return execute("INSERT INTO categories (name) VALUES (%s)", (name,))

    return None


@app.post("/api/questions", status_code=201)
def create_question(payload: QuestionCreate, request: Request):
    if payload.website:
        # Fake success so simple bots don't learn from the response.
        return {"message": "Frage wurde gespeichert."}

    _check_rate_limit(request)

    course_id = _get_course_id(payload.course_slug)
    category_id = _get_category_id(payload.category_id, payload.category_name)

    question_id = execute(
        """
        INSERT INTO questions
            (course_id, category_id, question_text, contact_email, source_ip_hash, status, is_public)
        VALUES
            (%s, %s, %s, %s, %s, 'open', 0)
        """,
        (
            course_id,
            category_id,
            payload.question_text.strip(),
            payload.contact_email.strip() if payload.contact_email else None,
            _ip_hash(request),
        ),
    )

    return {
        "message": "Frage wurde gespeichert und wartet auf Freigabe.",
        "question_id": question_id,
    }


@app.get("/api/admin/questions")
def admin_questions(status_filter: str = "open", _: str = Depends(require_admin)):
    params: List[object] = []
    where: List[str] = []

    if status_filter != "all":
        if status_filter not in {"open", "answered", "published", "hidden", "deleted"}:
            raise HTTPException(status_code=400, detail="Ungültiger Statusfilter.")
        where.append("q.status = %s")
        params.append(status_filter)
    else:
        where.append("q.status <> 'deleted'")

    sql = f"""
        SELECT
            q.id,
            q.question_text,
            q.status,
            q.is_public,
            q.created_at,
            q.answered_at,
            q.contact_email,
            q.category_id,
            c.name AS category_name,
            a.answer_text,
            a.updated_at AS answer_updated_at
        FROM questions q
        LEFT JOIN categories c ON q.category_id = c.id
        LEFT JOIN answers a ON a.question_id = q.id
        WHERE {' AND '.join(where)}
        ORDER BY q.created_at DESC
        LIMIT 500
    """
    return fetch_all(sql, tuple(params))


@app.post("/api/admin/questions/{question_id}/answer")
def answer_question(question_id: int, payload: AnswerPayload, _: str = Depends(require_admin)):
    question = fetch_one("SELECT id FROM questions WHERE id = %s AND status <> 'deleted'", (question_id,))
    if not question:
        raise HTTPException(status_code=404, detail="Frage wurde nicht gefunden.")

    existing = fetch_one("SELECT id FROM answers WHERE question_id = %s", (question_id,))
    if existing:
        execute(
            "UPDATE answers SET answer_text = %s, updated_at = CURRENT_TIMESTAMP WHERE question_id = %s",
            (payload.answer_text.strip(), question_id),
        )
    else:
        execute(
            "INSERT INTO answers (question_id, answer_text) VALUES (%s, %s)",
            (question_id, payload.answer_text.strip()),
        )

    if payload.publish:
        execute(
            "UPDATE questions SET status = 'published', is_public = 1, answered_at = CURRENT_TIMESTAMP WHERE id = %s",
            (question_id,),
        )
        return {"message": "Antwort wurde gespeichert und veröffentlicht."}

    execute(
        "UPDATE questions SET status = 'answered', is_public = 0, answered_at = CURRENT_TIMESTAMP WHERE id = %s",
        (question_id,),
    )
    return {"message": "Antwort wurde gespeichert."}


@app.patch("/api/admin/questions/{question_id}")
def update_admin_question(question_id: int, payload: AdminQuestionUpdate, _: str = Depends(require_admin)):
    question = fetch_one("SELECT id FROM questions WHERE id = %s AND status <> 'deleted'", (question_id,))
    if not question:
        raise HTTPException(status_code=404, detail="Frage wurde nicht gefunden.")

    answer_text = payload.answer_text.strip() if payload.answer_text else ""
    if payload.status in {"answered", "published"} and not answer_text:
        raise HTTPException(
            status_code=400,
            detail="Für den Status 'beantwortet' oder 'veröffentlicht' muss eine Antwort eingetragen sein.",
        )

    category_id = _get_category_id(payload.category_id, payload.category_name)
    is_public = 1 if payload.status == "published" else 0

    if payload.status in {"answered", "published"}:
        execute(
            """
            UPDATE questions
            SET question_text = %s,
                category_id = %s,
                status = %s,
                is_public = %s,
                answered_at = COALESCE(answered_at, CURRENT_TIMESTAMP)
            WHERE id = %s
            """,
            (payload.question_text.strip(), category_id, payload.status, is_public, question_id),
        )
    else:
        execute(
            """
            UPDATE questions
            SET question_text = %s,
                category_id = %s,
                status = %s,
                is_public = %s
            WHERE id = %s
            """,
            (payload.question_text.strip(), category_id, payload.status, is_public, question_id),
        )

    existing_answer = fetch_one("SELECT id FROM answers WHERE question_id = %s", (question_id,))
    if answer_text:
        if existing_answer:
            execute(
                "UPDATE answers SET answer_text = %s, updated_at = CURRENT_TIMESTAMP WHERE question_id = %s",
                (answer_text, question_id),
            )
        else:
            execute(
                "INSERT INTO answers (question_id, answer_text) VALUES (%s, %s)",
                (question_id, answer_text),
            )
    elif existing_answer:
        execute("DELETE FROM answers WHERE question_id = %s", (question_id,))

    return {"message": "Frage wurde aktualisiert."}


@app.patch("/api/admin/questions/{question_id}/status")
def update_question_status(question_id: int, payload: StatusPayload, _: str = Depends(require_admin)):
    question = fetch_one("SELECT id FROM questions WHERE id = %s", (question_id,))
    if not question:
        raise HTTPException(status_code=404, detail="Frage wurde nicht gefunden.")

    is_public = 1 if payload.status == "published" else 0
    execute(
        "UPDATE questions SET status = %s, is_public = %s WHERE id = %s",
        (payload.status, is_public, question_id),
    )
    return {"message": "Status wurde aktualisiert."}


@app.delete("/api/admin/questions/{question_id}")
def delete_question(question_id: int, _: str = Depends(require_admin)):
    execute("UPDATE questions SET status = 'deleted', is_public = 0 WHERE id = %s", (question_id,))
    return {"message": "Frage wurde gelöscht/ausgeblendet."}
