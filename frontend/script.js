const FAQ_API_BASE = window.FAQ_API_BASE || "";

function $(selector) {
    return document.querySelector(selector);
}

function createElement(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined && text !== null) element.textContent = text;
    return element;
}

function showMessage(targetSelector, text, type = "success") {
    const target = $(targetSelector);
    if (!target) return;
    target.textContent = text;
    target.className = `message ${type}`;
    target.hidden = false;
}

async function apiFetch(path, options = {}) {
    const response = await fetch(`${FAQ_API_BASE}${path}`, {
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        ...options,
    });

    let data = null;
    try {
        data = await response.json();
    } catch (error) {
        data = { detail: "Unerwartete Serverantwort." };
    }

    if (!response.ok) {
        const message = data.detail || data.message || "Anfrage fehlgeschlagen.";
        throw new Error(message);
    }
    return data;
}

async function loadMeta() {
    try {
        const meta = await apiFetch("/api/meta");
        document.querySelectorAll("[data-course-name]").forEach((el) => {
            el.textContent = meta.course_name;
        });
    } catch (error) {
        // Seite bleibt trotzdem nutzbar.
    }
}

async function loadCategories(selectId, includeAllOption = false) {
    const select = document.getElementById(selectId);
    if (!select) return [];

    const categories = await apiFetch("/api/categories");
    select.innerHTML = "";

    if (includeAllOption) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "Alle Kategorien";
        select.appendChild(option);
    }

    categories.forEach((category) => {
        const option = document.createElement("option");
        option.value = category.id;
        option.textContent = category.name;
        select.appendChild(option);
    });

    return categories;
}

function renderFAQTable(faqs) {
    const container = $("#faq-list");
    if (!container) return;
    container.innerHTML = "";

    if (!faqs.length) {
        container.appendChild(createElement("p", "", "Es wurden noch keine veröffentlichten Fragen gefunden."));
        return;
    }

    const table = createElement("table", "faq-table");
    const thead = document.createElement("thead");
    thead.innerHTML = "<tr><th>Frage</th><th>Kategorie</th><th>Antwort</th></tr>";
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    faqs.forEach((faq) => {
        const tr = document.createElement("tr");

        const questionTd = document.createElement("td");
        questionTd.appendChild(createElement("div", "faq-question", faq.question_text));

        const categoryTd = document.createElement("td");
        categoryTd.textContent = faq.category_name || "Allgemein";

        const answerTd = document.createElement("td");
        answerTd.appendChild(createElement("div", "faq-answer", faq.answer_text || "Noch keine Antwort veröffentlicht."));

        tr.appendChild(questionTd);
        tr.appendChild(categoryTd);
        tr.appendChild(answerTd);
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    container.appendChild(table);
}

async function loadPublicFAQs() {
    const query = $("#search-input")?.value || "";
    const categoryId = $("#category-filter")?.value || "";
    const params = new URLSearchParams();
    if (query.trim()) params.set("query", query.trim());
    if (categoryId) params.set("category_id", categoryId);

    const faqs = await apiFetch(`/api/faqs?${params.toString()}`);
    renderFAQTable(faqs);
}

async function initFAQPage() {
    if (!$("#faq-list")) return;
    await loadCategories("category-filter", true);
    await loadPublicFAQs();

    $("#search-form")?.addEventListener("submit", async (event) => {
        event.preventDefault();
        await loadPublicFAQs();
    });

    $("#category-filter")?.addEventListener("change", loadPublicFAQs);
}

async function initAskPage() {
    const form = $("#ask-form");
    if (!form) return;

    await loadCategories("question-category", false);

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = {
            question_text: $("#question-text").value,
            category_id: $("#question-category").value ? Number($("#question-category").value) : null,
            website: $("#website")?.value || "",
        };

        try {
            const result = await apiFetch("/api/questions", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            showMessage("#ask-message", result.message || "Frage wurde gespeichert.", "success");
            form.reset();
        } catch (error) {
            showMessage("#ask-message", error.message, "error");
        }
    });
}

function getToken() {
    return localStorage.getItem("faq_admin_token");
}

function setToken(token) {
    localStorage.setItem("faq_admin_token", token);
}

function clearToken() {
    localStorage.removeItem("faq_admin_token");
}

async function initLoginPage() {
    const form = $("#admin-login-form");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const payload = {
            username: $("#admin-username").value,
            password: $("#admin-password").value,
        };

        try {
            const result = await apiFetch("/api/admin/login", {
                method: "POST",
                body: JSON.stringify(payload),
            });
            setToken(result.token);
            window.location.href = "/admin";
        } catch (error) {
            showMessage("#login-message", error.message, "error");
        }
    });
}

function authHeaders() {
    const token = getToken();
    if (!token) {
        window.location.href = "/admin-login";
        return {};
    }
    return { Authorization: `Bearer ${token}` };
}

function statusLabel(status) {
    const labels = {
        open: "offen",
        answered: "beantwortet",
        published: "veröffentlicht",
        hidden: "ausgeblendet",
        deleted: "gelöscht",
    };
    return labels[status] || status;
}

function statusLongLabel(status) {
    const labels = {
        open: "Offen",
        answered: "Beantwortet, aber nicht veröffentlicht",
        published: "Veröffentlicht",
        hidden: "Ausgeblendet",
        deleted: "Gelöscht",
    };
    return labels[status] || status;
}

function formatDate(value) {
    if (!value) return "";
    try {
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return value;
        return date.toLocaleString("de-DE", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    } catch (error) {
        return value;
    }
}

let adminQuestionsCache = [];
let adminCategoriesCache = [];
let adminFiltersActivated = false;

function updateAdminStats(questions) {
    const counts = { open: 0, answered: 0, published: 0, hidden: 0 };
    questions.forEach((question) => {
        if (counts[question.status] !== undefined) counts[question.status] += 1;
    });

    const setText = (id, value) => {
        const target = document.getElementById(id);
        if (target) target.textContent = String(value);
    };

    setText("stat-open", counts.open);
    setText("stat-answered", counts.answered);
    setText("stat-published", counts.published);
    setText("stat-hidden", counts.hidden);
}

async function loadAdminCategoryControls() {
    adminCategoriesCache = await loadCategories("admin-category-filter", true);

    const removeSelect = document.getElementById("remove-category-select");
    if (removeSelect) {
        removeSelect.innerHTML = "";
        if (!adminCategoriesCache.length) {
            const option = document.createElement("option");
            option.value = "";
            option.textContent = "Keine Kategorie vorhanden";
            removeSelect.appendChild(option);
        } else {
            adminCategoriesCache.forEach((category) => {
                const option = document.createElement("option");
                option.value = category.id;
                option.textContent = category.name;
                removeSelect.appendChild(option);
            });
        }
    }
}

async function addCategory() {
    const input = $("#add-category-name");
    const name = input?.value.trim() || "";

    if (!name) {
        showMessage("#admin-message", "Bitte einen Kategorienamen eingeben.", "error");
        return;
    }

    try {
        const result = await apiFetch("/api/admin/categories", {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify({ name }),
        });
        showMessage("#admin-message", result.message || "Kategorie wurde hinzugefügt.", "success");
        if (input) input.value = "";
        await loadAdminCategoryControls();
        applyAdminFilters();
    } catch (error) {
        showMessage("#admin-message", error.message, "error");
    }
}

async function removeCategory() {
    const select = $("#remove-category-select");
    const categoryId = select?.value || "";
    const categoryName = select?.selectedOptions?.[0]?.textContent || "diese Kategorie";

    if (!categoryId) {
        showMessage("#admin-message", "Bitte zuerst eine Kategorie auswählen.", "error");
        return;
    }

    if (!confirm(`Kategorie '${categoryName}' wirklich entfernen? Fragen bleiben erhalten, verlieren aber diese Kategorie.`)) {
        return;
    }

    try {
        const result = await apiFetch(`/api/admin/categories/${categoryId}`, {
            method: "DELETE",
            headers: authHeaders(),
        });
        showMessage("#admin-message", result.message || "Kategorie wurde entfernt.", "success");
        await loadAdminCategoryControls();
        await loadAdminQuestions();
    } catch (error) {
        showMessage("#admin-message", error.message, "error");
    }
}

function filterAdminQuestions() {
    const statusFilter = $("#admin-status-filter")?.value || "open";
    const categoryFilter = $("#admin-category-filter")?.value || "";
    const search = ($("#admin-search-input")?.value || "").trim().toLowerCase();

    return adminQuestionsCache.filter((question) => {
        const statusMatches = statusFilter === "all" || question.status === statusFilter;
        if (!statusMatches) return false;

        const categoryMatches = !categoryFilter || String(question.category_id || "") === String(categoryFilter);
        if (!categoryMatches) return false;

        if (!search) return true;
        const haystack = [
            question.question_text,
            question.answer_text,
            question.category_name,
            question.created_at,
            question.answered_at,
            String(question.id),
        ]
            .filter(Boolean)
            .join(" ")
            .toLowerCase();

        return haystack.includes(search);
    });
}

function buildCategorySelect(question) {
    const select = document.createElement("select");
    select.className = "admin-row-category";
    select.id = `category-${question.id}`;

    const emptyOption = document.createElement("option");
    emptyOption.value = "";
    emptyOption.textContent = "Allgemein / ohne Kategorie";
    select.appendChild(emptyOption);

    adminCategoriesCache.forEach((category) => {
        const option = document.createElement("option");
        option.value = category.id;
        option.textContent = category.name;
        if (String(question.category_id || "") === String(category.id)) option.selected = true;
        select.appendChild(option);
    });

    return select;
}

function buildStatusSelect(question) {
    const select = document.createElement("select");
    select.className = "admin-row-status";
    select.id = `status-${question.id}`;

    ["open", "answered", "published", "hidden"].forEach((status) => {
        const option = document.createElement("option");
        option.value = status;
        option.textContent = statusLongLabel(status);
        if (question.status === status) option.selected = true;
        select.appendChild(option);
    });

    return select;
}

function renderAdminQuestionsTable(questions) {
    const tbody = $("#admin-question-list");
    const wrapper = $("#admin-table-wrapper");
    const hint = $("#admin-filter-hint");
    const summary = $("#admin-result-summary");
    if (!tbody || !wrapper) return;

    tbody.innerHTML = "";

    if (!adminFiltersActivated) {
        wrapper.hidden = true;
        if (hint) hint.hidden = false;
        if (summary) summary.hidden = true;
        return;
    }

    if (hint) hint.hidden = true;
    if (summary) {
        const statusText = statusLongLabel($("#admin-status-filter")?.value || "open");
        const categorySelect = $("#admin-category-filter");
        const categoryText = categorySelect?.selectedOptions?.[0]?.textContent || "Alle Kategorien";
        const search = ($("#admin-search-input")?.value || "").trim();
        summary.textContent = `${questions.length} Frage(n) gefunden · Status: ${statusText} · Kategorie: ${categoryText}${search ? ` · Suche: ${search}` : ""}`;
        summary.hidden = false;
    }

    if (!questions.length) {
        wrapper.hidden = true;
        const empty = $("#admin-filter-hint");
        if (empty) {
            empty.innerHTML = "<strong>Keine passenden Fragen gefunden.</strong><p>Ändern Sie Status, Kategorie oder Suche.</p>";
            empty.hidden = false;
        }
        return;
    }

    wrapper.hidden = false;

    questions.forEach((question) => {
        const tr = document.createElement("tr");
        tr.dataset.questionId = question.id;

        const idTd = document.createElement("td");
        idTd.className = "admin-id-cell";
        idTd.appendChild(createElement("strong", "", `#${question.id}`));
        idTd.appendChild(createElement("div", "admin-small-note", formatDate(question.created_at) || ""));
        if (question.contact_email) {
            idTd.appendChild(createElement("div", "admin-contact-note", "Kontakt angegeben"));
        }

        const statusTd = document.createElement("td");
        statusTd.appendChild(buildStatusSelect(question));
        statusTd.appendChild(createElement("div", `status-badge status-${question.status}`, statusLabel(question.status)));

        const categoryTd = document.createElement("td");
        categoryTd.appendChild(buildCategorySelect(question));

        const questionTd = document.createElement("td");
        const questionTextarea = document.createElement("textarea");
        questionTextarea.id = `question-${question.id}`;
        questionTextarea.className = "admin-row-question";
        questionTextarea.value = question.question_text || "";
        questionTextarea.placeholder = "Frage bearbeiten";
        questionTd.appendChild(questionTextarea);

        const answerTd = document.createElement("td");
        const answerTextarea = document.createElement("textarea");
        answerTextarea.id = `answer-${question.id}`;
        answerTextarea.className = "admin-row-answer";
        answerTextarea.value = question.answer_text || "";
        answerTextarea.placeholder = "Antwort bearbeiten oder neu eintragen";
        answerTd.appendChild(answerTextarea);

        const actionTd = document.createElement("td");
        actionTd.className = "admin-actions-cell";
        const saveBtn = createElement("button", "primary-button", "Speichern");
        saveBtn.type = "button";
        saveBtn.addEventListener("click", () => saveAdminQuestionRow(question.id));

        const deleteBtn = createElement("button", "danger-button", "Löschen");
        deleteBtn.type = "button";
        deleteBtn.addEventListener("click", () => deleteQuestion(question.id));

        actionTd.append(saveBtn, deleteBtn);

        tr.append(idTd, statusTd, categoryTd, questionTd, answerTd, actionTd);
        tbody.appendChild(tr);
    });
}

function applyAdminFilters() {
    renderAdminQuestionsTable(filterAdminQuestions());
}

async function loadAdminQuestions() {
    try {
        adminQuestionsCache = await apiFetch("/api/admin/questions?status_filter=all", {
            headers: authHeaders(),
        });
        updateAdminStats(adminQuestionsCache);
        applyAdminFilters();

        const updated = $("#admin-last-updated");
        if (updated) updated.textContent = `Zuletzt aktualisiert: ${new Date().toLocaleString("de-DE")}`;
    } catch (error) {
        if (error.message.includes("Admin") || error.message.includes("Token") || error.message.includes("einloggen")) {
            clearToken();
            window.location.href = "/admin-login";
        } else {
            showMessage("#admin-message", error.message, "error");
        }
    }
}

async function saveAnswer(questionId, publish) {
    const textarea = $(`#answer-${questionId}`);
    const answerText = textarea?.value || "";
    if (!answerText.trim()) {
        showMessage("#admin-message", "Bitte zuerst eine Antwort eingeben.", "error");
        return;
    }

    try {
        const result = await apiFetch(`/api/admin/questions/${questionId}/answer`, {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify({ answer_text: answerText, publish }),
        });
        showMessage("#admin-message", result.message, "success");
        await loadAdminQuestions();
    } catch (error) {
        showMessage("#admin-message", error.message, "error");
    }
}

async function saveAdminQuestionRow(questionId) {
    const questionText = $(`#question-${questionId}`)?.value || "";
    const answerText = $(`#answer-${questionId}`)?.value || "";
    const categoryValue = $(`#category-${questionId}`)?.value || "";
    const statusValue = $(`#status-${questionId}`)?.value || "open";

    if (!questionText.trim()) {
        showMessage("#admin-message", "Die Frage darf nicht leer sein.", "error");
        return;
    }

    if (["answered", "published"].includes(statusValue) && !answerText.trim()) {
        showMessage("#admin-message", "Für 'beantwortet' oder 'veröffentlicht' muss eine Antwort eingetragen sein.", "error");
        return;
    }

    try {
        const result = await apiFetch(`/api/admin/questions/${questionId}`, {
            method: "PATCH",
            headers: authHeaders(),
            body: JSON.stringify({
                question_text: questionText,
                answer_text: answerText,
                category_id: categoryValue ? Number(categoryValue) : null,
                status: statusValue,
            }),
        });
        showMessage("#admin-message", result.message, "success");
        await loadAdminQuestions();
    } catch (error) {
        showMessage("#admin-message", error.message, "error");
    }
}

async function setQuestionStatus(questionId, status) {
    try {
        const result = await apiFetch(`/api/admin/questions/${questionId}/status`, {
            method: "PATCH",
            headers: authHeaders(),
            body: JSON.stringify({ status }),
        });
        showMessage("#admin-message", result.message, "success");
        await loadAdminQuestions();
    } catch (error) {
        showMessage("#admin-message", error.message, "error");
    }
}

async function deleteQuestion(questionId) {
    if (!confirm("Diese Frage wirklich löschen/ausblenden? Sie erscheint danach nicht mehr in der normalen Adminliste.")) return;
    try {
        const result = await apiFetch(`/api/admin/questions/${questionId}`, {
            method: "DELETE",
            headers: authHeaders(),
        });
        showMessage("#admin-message", result.message, "success");
        await loadAdminQuestions();
    } catch (error) {
        showMessage("#admin-message", error.message, "error");
    }
}

async function initAdminPage() {
    if (!$("#admin-question-list")) return;
    if (!getToken()) {
        window.location.href = "/admin-login";
        return;
    }

    try {
        await loadAdminCategoryControls();
    } catch (error) {
        showMessage("#admin-message", `Kategorien konnten nicht geladen werden: ${error.message}`, "error");
    }

    $("#add-category-button")?.addEventListener("click", addCategory);
    $("#add-category-name")?.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            addCategory();
        }
    });
    $("#remove-category-button")?.addEventListener("click", removeCategory);

    $("#show-admin-questions-button")?.addEventListener("click", () => {
        adminFiltersActivated = true;
        applyAdminFilters();
    });

    $("#admin-status-filter")?.addEventListener("change", () => {
        if (adminFiltersActivated) applyAdminFilters();
    });
    $("#admin-category-filter")?.addEventListener("change", () => {
        if (adminFiltersActivated) applyAdminFilters();
    });
    $("#admin-search-input")?.addEventListener("input", () => {
        if (adminFiltersActivated) applyAdminFilters();
    });
    $("#refresh-admin-button")?.addEventListener("click", loadAdminQuestions);
    $("#logout-button")?.addEventListener("click", () => {
        clearToken();
        window.location.href = "/admin-login";
    });

    await loadAdminQuestions();
}

document.addEventListener("DOMContentLoaded", async () => {
    await loadMeta();
    await initFAQPage();
    await initAskPage();
    await initLoginPage();
    await initAdminPage();
});