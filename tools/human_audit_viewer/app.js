(() => {
  "use strict";

  const REPO = "tailolicon/hachimi-tl-vi";
  const GITHUB_RAW = `https://raw.githubusercontent.com/${REPO}/main/`;
  const STORAGE_PREFIX = "hachimi-human-audit:";
  const SETTINGS_KEY = `${STORAGE_PREFIX}settings:v1`;

  const state = {
    dataRoot: "",
    activePlan: null,
    plan: null,
    batchMeta: [],
    batchCache: new Map(),
    currentBatchIndex: 0,
    allEntries: null,
    allLoadAbort: false,
    annotations: {},
    annotationPlanId: null,
  };

  const $ = (id) => document.getElementById(id);
  const els = {
    planId: $("planId"), candidateCount: $("candidateCount"), batchCount: $("batchCount"),
    annotationProgress: $("annotationProgress"), planWarning: $("planWarning"), reloadPlanBtn: $("reloadPlanBtn"),
    settingsBtn: $("settingsBtn"), searchInput: $("searchInput"), categoryFilter: $("categoryFilter"),
    verdictFilter: $("verdictFilter"), riskFilter: $("riskFilter"), prevBatchBtn: $("prevBatchBtn"),
    nextBatchBtn: $("nextBatchBtn"), batchNumberInput: $("batchNumberInput"), goBatchBtn: $("goBatchBtn"),
    loadedInfo: $("loadedInfo"), loadAllBtn: $("loadAllBtn"), cancelLoadBtn: $("cancelLoadBtn"),
    globalLoadProgressWrap: $("globalLoadProgressWrap"), globalLoadProgress: $("globalLoadProgress"),
    globalLoadLabel: $("globalLoadLabel"), visibleCount: $("visibleCount"), scopeLabel: $("scopeLabel"),
    exportJsonBtn: $("exportJsonBtn"), exportCsvBtn: $("exportCsvBtn"), exportIssuesBtn: $("exportIssuesBtn"),
    importInput: $("importInput"), entryList: $("entryList"), emptyState: $("emptyState"),
    entryTemplate: $("entryTemplate"), settingsDialog: $("settingsDialog"), dataRootInput: $("dataRootInput"),
    useLocalBtn: $("useLocalBtn"), useGithubBtn: $("useGithubBtn"), saveSettingsBtn: $("saveSettingsBtn"),
  };

  function defaultRoot() {
    return new Set(["localhost", "127.0.0.1", "::1"]).has(location.hostname) ? "../../" : GITHUB_RAW;
  }

  function normalizeRoot(value) {
    let root = String(value || "").trim() || defaultRoot();
    if (!root.endsWith("/")) root += "/";
    return root;
  }

  function loadSettings() {
    try {
      const parsed = JSON.parse(localStorage.getItem(SETTINGS_KEY) || "{}");
      state.dataRoot = normalizeRoot(parsed.dataRoot || defaultRoot());
    } catch {
      state.dataRoot = normalizeRoot(defaultRoot());
    }
    els.dataRootInput.value = state.dataRoot;
  }

  function saveSettings() {
    state.dataRoot = normalizeRoot(els.dataRootInput.value);
    localStorage.setItem(SETTINGS_KEY, JSON.stringify({ dataRoot: state.dataRoot }));
  }

  function urlFor(path) {
    const clean = String(path).replace(/^\/+/, "");
    return `${state.dataRoot}${clean}?_=${Date.now()}`;
  }

  async function fetchJson(path) {
    const response = await fetch(urlFor(path), { cache: "no-store" });
    if (!response.ok) throw new Error(`${response.status} ${response.statusText} — ${path}`);
    return response.json();
  }

  function annotationStorageKey(planId) { return `${STORAGE_PREFIX}annotations:${planId}`; }

  function loadAnnotations(planId) {
    state.annotationPlanId = planId;
    try { state.annotations = JSON.parse(localStorage.getItem(annotationStorageKey(planId)) || "{}"); }
    catch { state.annotations = {}; }
  }

  function persistAnnotations() {
    if (!state.annotationPlanId) return;
    localStorage.setItem(annotationStorageKey(state.annotationPlanId), JSON.stringify(state.annotations));
    updateAnnotationProgress();
  }

  function annotationFor(uid) {
    return state.annotations[uid] || { verdict: "unreviewed", tags: [], note: "", proposed_text: "", updated_at: null };
  }

  function updateAnnotation(uid, patch) {
    const next = { ...annotationFor(uid), ...patch, updated_at: new Date().toISOString() };
    if (next.verdict === "unreviewed" && !next.note && !next.proposed_text && (!next.tags || !next.tags.length)) delete state.annotations[uid];
    else state.annotations[uid] = next;
    persistAnnotations();
  }

  function updateAnnotationProgress() {
    const total = Number(state.activePlan?.candidate_count || 0);
    const reviewed = Object.values(state.annotations).filter((a) => a.verdict && a.verdict !== "unreviewed").length;
    els.annotationProgress.textContent = `${reviewed.toLocaleString("vi-VN")} / ${total.toLocaleString("vi-VN")}`;
  }

  function allTermRecords(item) {
    return [
      ...(item.locked_terms || []), ...(item.community_terms || []), ...(item.source_bridge_terms || []),
      ...(item.source_bridge_risks || []), ...(item.skill_name_canonical ? [item.skill_name_canonical] : []),
    ].filter(Boolean);
  }

  function termIds(item) {
    return allTermRecords(item).map((t) => String(t.id || t.category || "")).filter(Boolean).join(" ").toLowerCase();
  }

  function categoryFor(item) {
    const path = String(item.source_path || "").replace(/\\/g, "/").toLowerCase();
    const ids = termIds(item);
    const key = String(item.key || "").toLowerCase();
    const kind = String(item.kind || "").toLowerCase();
    if (ids.includes("condition")) return "Condition";
    if (path.match(/(^|\/)text_data\/?16(\.json)?$/) || path.includes("text_data/16.json")) return "Song title";
    if (path.match(/(^|\/)text_data\/?17(\.json)?$/) || path.includes("text_data/17.json")) return "Song credit";
    if (path.includes("text_data/131")) return "Mission / Race objective";
    if (path.includes("text_data/147")) return "Title / Factor";
    if (path.includes("text_data/170")) return "Character";
    if (path.includes("text_data/171")) return "Interaction / System";
    if (path.includes("text_data/172") || ids.includes("spark") || ids.includes("legacy")) return "Spark / Inheritance";
    if (item.skill_name_canonical || ids.includes("skill")) return "Skill";
    if (ids.includes("race") || path.includes("race_") || path.includes("/race")) return "Race";
    if (ids.includes("support_card")) return "Support Card";
    if (kind === "localize" || path.endsWith("localize_dict.json") || key) return "UI / System";
    return kind || "Other";
  }

  function locatorFor(item) {
    const path = String(item.source_path || "");
    const jp = Array.isArray(item.json_path) ? item.json_path.map(String).join("/") : "";
    if (item.key) return String(item.key);
    return jp ? `${path} :: ${jp}` : path || String(item.uid || "");
  }

  function searchableText(item) {
    const a = annotationFor(item.uid);
    return [item.uid, item.kind, item.source_path, locatorFor(item), item.source_text, item.current_text, categoryFor(item),
      ...(item.risk_flags || []), JSON.stringify(allTermRecords(item)), a.note, a.proposed_text, ...(a.tags || [])].join("\n").toLowerCase();
  }

  function riskMatches(item, filter) {
    const score = Number(item.risk_score || 0);
    const flags = (item.risk_flags || []).map(String);
    const hay = flags.join(" ").toLowerCase();
    if (!filter) return true;
    if (filter === "has-risk") return score > 0 || flags.length > 0;
    if (filter === "high-risk") return score >= 10;
    if (filter === "term-risk") return /term|canonical|skill_name|calque/.test(hay) || allTermRecords(item).length > 0;
    if (filter === "bridge-risk") return /bridge/.test(hay) || (item.source_bridge_terms || []).length > 0 || (item.source_bridge_risks || []).length > 0;
    if (filter === "structure-risk") return /numeric|structure|placeholder|token|newline/.test(hay);
    return true;
  }

  function filteredEntries(entries) {
    const q = els.searchInput.value.trim().toLowerCase();
    const category = els.categoryFilter.value;
    const verdict = els.verdictFilter.value;
    const risk = els.riskFilter.value;
    return entries.filter((item) => {
      if (q && !searchableText(item).includes(q)) return false;
      if (category && categoryFor(item) !== category) return false;
      if (verdict && (annotationFor(item.uid).verdict || "unreviewed") !== verdict) return false;
      return riskMatches(item, risk);
    });
  }

  function escapeHtml(value) {
    return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;").replaceAll("'", "&#039;");
  }

  function contextBlock(title, body) {
    const block = document.createElement("section"); block.className = "context-block";
    const h = document.createElement("h4"); h.textContent = title; block.appendChild(h);
    if (typeof body === "string") { const pre = document.createElement("pre"); pre.textContent = body; block.appendChild(pre); }
    else block.appendChild(body);
    return block;
  }

  function renderTermList(records) {
    const wrap = document.createElement("div"); wrap.className = "term-list";
    if (!records.length) { const span = document.createElement("span"); span.className = "muted"; span.textContent = "Không có."; wrap.appendChild(span); return wrap; }
    for (const term of records) {
      const div = document.createElement("div"); div.className = "term-item";
      const id = term.id || "(no id)";
      const preferred = term.preferred || term.target_vi || term.target || "";
      const accepted = Array.isArray(term.accepted) ? term.accepted : [];
      const forbidden = Array.isArray(term.forbidden) ? term.forbidden : [];
      const aliases = Array.isArray(term.matched_aliases) ? term.matched_aliases : (Array.isArray(term.zh_cn) ? term.zh_cn : (Array.isArray(term.ja) ? term.ja : []));
      const note = term.basis || term.note || "";
      div.innerHTML = `<strong>${escapeHtml(id)}</strong>${preferred ? `<div><span class="term-key">preferred:</span> ${escapeHtml(preferred)}</div>` : ""}${accepted.length ? `<div><span class="term-key">accepted:</span> ${escapeHtml(accepted.join(" · "))}</div>` : ""}${forbidden.length ? `<div><span class="term-key">forbidden:</span> ${escapeHtml(forbidden.join(" · "))}</div>` : ""}${aliases.length ? `<div><span class="term-key">matched:</span> ${escapeHtml(aliases.join(" · "))}</div>` : ""}${note ? `<div><span class="term-key">basis:</span> ${escapeHtml(note)}</div>` : ""}`;
      wrap.appendChild(div);
    }
    return wrap;
  }

  const verdictLabel = (v) => ({ ok: "OK", issue: "Có lỗi", check: "Cần kiểm tra", unreviewed: "Chưa audit" }[v] || "Chưa audit");
  const riskClass = (score) => score >= 10 ? "risk-high" : score > 0 ? "risk-mid" : "risk-low";

  function flashSaved(card) {
    const el = card.querySelector(".saved-indicator"); el.classList.add("flash"); el.textContent = "Đã lưu";
    clearTimeout(el._timer); el._timer = setTimeout(() => { el.classList.remove("flash"); el.textContent = "Tự lưu trong browser"; }, 900);
  }

  function debounce(fn, delay) { let timer; return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); }; }

  async function copyText(text) {
    try { await navigator.clipboard.writeText(String(text)); }
    catch { const area = document.createElement("textarea"); area.value = String(text); document.body.appendChild(area); area.select(); document.execCommand("copy"); area.remove(); }
  }

  function renderEntry(item, displayIndex) {
    const node = els.entryTemplate.content.firstElementChild.cloneNode(true);
    const annotation = annotationFor(item.uid); const category = categoryFor(item); const score = Number(item.risk_score || 0);
    node.dataset.uid = item.uid;
    node.querySelector(".entry-number").textContent = `#${displayIndex}`;
    node.querySelector(".category-badge").textContent = category;
    const riskBadge = node.querySelector(".risk-badge"); riskBadge.textContent = `risk ${score}`; riskBadge.classList.add(riskClass(score));
    const verdictBadge = node.querySelector(".verdict-badge"); verdictBadge.textContent = verdictLabel(annotation.verdict); verdictBadge.classList.add(annotation.verdict || "unreviewed");
    node.querySelector(".entry-meta").textContent = `${locatorFor(item)}  •  ${item.uid}  •  source batch ${item.source_batch ?? "?"} / entry ${item.entry_index ?? "?"}`;
    node.querySelector(".source-text").textContent = item.source_text ?? "";
    node.querySelector(".current-text").textContent = item.current_text ?? "";
    node.querySelector(".raw-json").textContent = JSON.stringify(item, null, 2);
    node.querySelector(".copy-source").addEventListener("click", () => copyText(item.source_text ?? ""));
    node.querySelector(".copy-current").addEventListener("click", () => copyText(item.current_text ?? ""));

    const grid = document.createElement("div"); grid.className = "context-grid";
    grid.appendChild(contextBlock("Risk flags", `score: ${score}\n${(item.risk_flags || []).join("\n") || "Không có risk flag."}`));
    grid.appendChild(contextBlock("Locked terms", renderTermList(item.locked_terms || [])));
    grid.appendChild(contextBlock("Community terms", renderTermList(item.community_terms || [])));
    grid.appendChild(contextBlock("Source bridge", renderTermList([...(item.source_bridge_terms || []), ...(item.source_bridge_risks || [])])));
    if (item.skill_name_canonical) grid.appendChild(contextBlock("Canonical Skill", renderTermList([item.skill_name_canonical])));
    grid.appendChild(contextBlock("Identity", `kind: ${item.kind ?? ""}\nsource_path: ${item.source_path ?? ""}\njson_path: ${JSON.stringify(item.json_path ?? [])}`));
    node.querySelector(".context-body").appendChild(grid);

    const verdictButtons = [...node.querySelectorAll("[data-verdict]")];
    const setVerdictUI = (verdict) => {
      verdictButtons.forEach((b) => b.classList.toggle("active", b.dataset.verdict === verdict));
      verdictBadge.className = `badge verdict-badge ${verdict}`; verdictBadge.textContent = verdictLabel(verdict);
    };
    setVerdictUI(annotation.verdict || "unreviewed");
    verdictButtons.forEach((button) => button.addEventListener("click", () => {
      const verdict = button.dataset.verdict; updateAnnotation(item.uid, { verdict }); setVerdictUI(verdict); flashSaved(node);
      if (els.verdictFilter.value) render();
    }));

    const tagInputs = [...node.querySelectorAll(".issue-tags input")];
    for (const input of tagInputs) {
      input.checked = (annotation.tags || []).includes(input.value);
      input.addEventListener("change", () => {
        const tags = tagInputs.filter((x) => x.checked).map((x) => x.value); const patch = { tags };
        if (tags.length && annotationFor(item.uid).verdict === "unreviewed") patch.verdict = "issue";
        updateAnnotation(item.uid, patch); setVerdictUI(annotationFor(item.uid).verdict); flashSaved(node);
      });
    }

    const note = node.querySelector(".audit-note"); note.value = annotation.note || "";
    note.addEventListener("input", debounce(() => { updateAnnotation(item.uid, { note: note.value }); flashSaved(node); }, 250));
    const proposal = node.querySelector(".audit-proposal"); proposal.value = annotation.proposed_text || "";
    proposal.addEventListener("input", debounce(() => { updateAnnotation(item.uid, { proposed_text: proposal.value }); flashSaved(node); }, 250));
    return node;
  }

  function populateCategories(entries) {
    const existing = els.categoryFilter.value;
    const categories = [...new Set(entries.map(categoryFor))].sort((a, b) => a.localeCompare(b));
    els.categoryFilter.innerHTML = `<option value="">Tất cả</option>` + categories.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("");
    if (categories.includes(existing)) els.categoryFilter.value = existing;
  }

  function currentScopeEntries() {
    if (state.allEntries) { els.scopeLabel.textContent = "scope: toàn bộ corpus đã tải"; return state.allEntries; }
    const meta = state.batchMeta[state.currentBatchIndex]; const batch = meta ? state.batchCache.get(meta.batch_id) : null;
    els.scopeLabel.textContent = meta ? `scope: ${meta.batch_id}` : "scope: batch hiện tại";
    return batch?.items || [];
  }

  function render() {
    const sourceEntries = currentScopeEntries(); populateCategories(sourceEntries); const entries = filteredEntries(sourceEntries);
    els.visibleCount.textContent = entries.length.toLocaleString("vi-VN"); els.entryList.innerHTML = "";
    els.emptyState.classList.toggle("hidden", entries.length > 0);
    const fragment = document.createDocumentFragment(); entries.forEach((item, i) => fragment.appendChild(renderEntry(item, i + 1))); els.entryList.appendChild(fragment);
    updateLoadedInfo(); updateBatchControls();
  }

  function updateLoadedInfo() { els.loadedInfo.textContent = `${state.batchCache.size.toLocaleString("vi-VN")} / ${state.batchMeta.length.toLocaleString("vi-VN")} batch đã tải`; }
  function updateBatchControls() {
    const n = state.batchMeta.length; els.batchNumberInput.max = Math.max(1, n); els.batchNumberInput.value = n ? state.currentBatchIndex + 1 : 1;
    els.prevBatchBtn.disabled = state.currentBatchIndex <= 0; els.nextBatchBtn.disabled = state.currentBatchIndex >= n - 1;
  }

  async function loadBatch(index, { renderAfter = true } = {}) {
    if (!state.batchMeta.length) return null;
    const safeIndex = Math.max(0, Math.min(index, state.batchMeta.length - 1)); const meta = state.batchMeta[safeIndex];
    let batch = state.batchCache.get(meta.batch_id); if (!batch) { batch = await fetchJson(meta.batch_path); state.batchCache.set(meta.batch_id, batch); }
    state.currentBatchIndex = safeIndex; state.allEntries = null; if (renderAfter) render(); return batch;
  }

  async function loadPlan() {
    setBusy(true);
    try {
      const previousPlanId = state.activePlan?.plan_id || null;
      const active = await fetchJson("work/translation_review/active_plan.json");
      if (active.status !== "active" || !active.plan_path) throw new Error(`active_plan status=${active.status}; không có active review plan.`);
      const plan = await fetchJson(active.plan_path);
      state.activePlan = active; state.plan = plan; state.batchMeta = Array.isArray(plan.batches) ? [...plan.batches] : [];
      state.batchCache.clear(); state.currentBatchIndex = 0; state.allEntries = null; state.allLoadAbort = false;
      loadAnnotations(active.plan_id);
      els.planId.textContent = active.plan_id; els.planId.title = active.plan_id;
      els.candidateCount.textContent = Number(active.candidate_count || 0).toLocaleString("vi-VN");
      els.batchCount.textContent = Number(active.batch_count || state.batchMeta.length).toLocaleString("vi-VN"); updateAnnotationProgress();
      if (previousPlanId && previousPlanId !== active.plan_id) {
        els.planWarning.textContent = `Plan đã đổi: ${previousPlanId} → ${active.plan_id}. Audit local được tách riêng theo plan để không trộn annotation cũ.`; els.planWarning.classList.remove("hidden");
      } else els.planWarning.classList.add("hidden");
      if (state.batchMeta.length) await loadBatch(0, { renderAfter: false }); render();
    } catch (error) { showFatal(error); } finally { setBusy(false); }
  }

  function setBusy(busy) { els.reloadPlanBtn.disabled = busy; els.reloadPlanBtn.textContent = busy ? "Đang tải…" : "↻ Tải plan mới nhất"; }
  function showFatal(error) {
    els.entryList.innerHTML = ""; els.emptyState.classList.remove("hidden"); els.emptyState.querySelector("h2").textContent = "Không tải được dữ liệu";
    els.emptyState.querySelector("p").textContent = `${error.message}. Kiểm tra Data source. Khi dùng local, hãy chạy static server từ root repo thay vì mở index.html bằng file://.`; console.error(error);
  }

  async function loadAllCorpus() {
    if (!state.batchMeta.length || state.allEntries) return;
    state.allLoadAbort = false; els.loadAllBtn.disabled = true; els.cancelLoadBtn.classList.remove("hidden"); els.globalLoadProgressWrap.classList.remove("hidden");
    let completed = 0; const total = state.batchMeta.length; const concurrency = 8; let cursor = 0;
    const updateProgress = () => { const pct = total ? Math.round((completed / total) * 100) : 0; els.globalLoadProgress.style.width = `${pct}%`; els.globalLoadLabel.textContent = `${completed}/${total} (${pct}%)`; updateLoadedInfo(); };
    const worker = async () => {
      while (!state.allLoadAbort) {
        const index = cursor++; if (index >= total) return; const meta = state.batchMeta[index];
        if (!state.batchCache.has(meta.batch_id)) {
          try { state.batchCache.set(meta.batch_id, await fetchJson(meta.batch_path)); } catch (error) { console.error("Failed batch", meta.batch_id, error); }
        }
        completed++; updateProgress();
      }
    };
    await Promise.all(Array.from({ length: concurrency }, worker)); els.cancelLoadBtn.classList.add("hidden"); els.loadAllBtn.disabled = false;
    if (!state.allLoadAbort) { state.allEntries = state.batchMeta.flatMap((meta) => state.batchCache.get(meta.batch_id)?.items || []); els.globalLoadLabel.textContent = `Đã tải ${state.allEntries.length.toLocaleString("vi-VN")} entry`; render(); }
    else els.globalLoadLabel.textContent = `Đã dừng ở ${completed}/${total} batch`;
  }

  function summarizeAnnotations() {
    const counts = { total: 0, ok: 0, issue: 0, check: 0, unreviewed: 0 };
    for (const a of Object.values(state.annotations)) { counts.total++; const key = a.verdict || "unreviewed"; if (counts[key] !== undefined) counts[key]++; }
    return counts;
  }

  function annotationsExportPayload() {
    return { schema_version: 1, tool: "hachimi-human-audit-viewer", repository: REPO, plan_id: state.activePlan?.plan_id || null,
      context_snapshot_sha256: state.activePlan?.context_snapshot_sha256 || null, source_bridge_policy_sha256: state.activePlan?.source_bridge_policy_sha256 || null,
      exported_at: new Date().toISOString(), data_root: state.dataRoot, counts: summarizeAnnotations(), annotations: state.annotations };
  }

  function downloadText(filename, text, type = "text/plain;charset=utf-8") {
    const blob = new Blob([text], { type }); const url = URL.createObjectURL(blob); const a = document.createElement("a"); a.href = url; a.download = filename;
    document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function exportJson() { downloadText(`human-audit-${state.activePlan?.plan_id || "unknown"}.json`, JSON.stringify(annotationsExportPayload(), null, 2) + "\n", "application/json;charset=utf-8"); }
  function csvEscape(value) { return `"${String(value ?? "").replaceAll('"', '""')}"`; }
  function itemMapForExport() { const map = new Map(); for (const batch of state.batchCache.values()) for (const item of batch.items || []) map.set(item.uid, item); return map; }

  function exportCsv() {
    const items = itemMapForExport(); const rows = [["uid", "verdict", "tags", "category", "locator", "source_text", "current_text", "proposed_text", "note", "updated_at"]];
    for (const [uid, a] of Object.entries(state.annotations)) { const item = items.get(uid); rows.push([uid, a.verdict || "", (a.tags || []).join("|"), item ? categoryFor(item) : "", item ? locatorFor(item) : "", item?.source_text || "", item?.current_text || "", a.proposed_text || "", a.note || "", a.updated_at || ""]); }
    downloadText(`human-audit-${state.activePlan?.plan_id || "unknown"}.csv`, rows.map((row) => row.map(csvEscape).join(",")).join("\n") + "\n", "text/csv;charset=utf-8");
  }

  function exportIssuesMarkdown() {
    const items = itemMapForExport(); const lines = ["# Human audit issues", "", `Plan: \`${state.activePlan?.plan_id || "unknown"}\``, `Exported: ${new Date().toISOString()}`, ""];
    const issues = Object.entries(state.annotations).filter(([, a]) => ["issue", "check"].includes(a.verdict));
    for (const [uid, a] of issues) {
      const item = items.get(uid); lines.push(`## ${a.verdict === "issue" ? "Lỗi" : "Cần kiểm tra"} — ${uid}`);
      if (item) { lines.push(`- Category: ${categoryFor(item)}`, `- Locator: \`${locatorFor(item).replaceAll("`", "\\`")}\``, `- Tags: ${(a.tags || []).join(", ") || "—"}`, "", "**Source**", "", "```text", String(item.source_text || ""), "```", "", "**Bản Việt hiện tại**", "", "```text", String(item.current_text || ""), "```"); }
      if (a.note) lines.push("", `**Ghi chú:** ${a.note}`); if (a.proposed_text) lines.push("", "**Đề xuất:**", "", "```text", a.proposed_text, "```"); lines.push("");
    }
    if (!issues.length) lines.push("_Chưa có annotation lỗi/cần kiểm tra._", "");
    downloadText(`human-audit-issues-${state.activePlan?.plan_id || "unknown"}.md`, lines.join("\n"));
  }

  async function importAudit(file) {
    const payload = JSON.parse(await file.text()); const incomingPlan = payload.plan_id || null;
    if (incomingPlan && state.activePlan?.plan_id && incomingPlan !== state.activePlan.plan_id && !confirm(`File thuộc plan khác:\n${incomingPlan}\n\nPlan hiện tại:\n${state.activePlan.plan_id}\n\nVẫn import vào plan hiện tại?`)) return;
    const incoming = payload.annotations || payload; if (!incoming || typeof incoming !== "object" || Array.isArray(incoming)) throw new Error("File import không có object annotations hợp lệ.");
    state.annotations = { ...state.annotations, ...incoming }; persistAnnotations(); render();
  }

  function attachEvents() {
    els.reloadPlanBtn.addEventListener("click", loadPlan);
    els.settingsBtn.addEventListener("click", () => { els.dataRootInput.value = state.dataRoot; els.settingsDialog.showModal(); });
    els.useLocalBtn.addEventListener("click", () => { els.dataRootInput.value = "../../"; });
    els.useGithubBtn.addEventListener("click", () => { els.dataRootInput.value = GITHUB_RAW; });
    els.saveSettingsBtn.addEventListener("click", () => { saveSettings(); setTimeout(loadPlan, 0); });
    const rerender = debounce(render, 120); els.searchInput.addEventListener("input", rerender); els.categoryFilter.addEventListener("change", render); els.verdictFilter.addEventListener("change", render); els.riskFilter.addEventListener("change", render);
    els.prevBatchBtn.addEventListener("click", () => loadBatch(state.currentBatchIndex - 1)); els.nextBatchBtn.addEventListener("click", () => loadBatch(state.currentBatchIndex + 1));
    els.goBatchBtn.addEventListener("click", () => { const target = Number(els.batchNumberInput.value) - 1; if (Number.isFinite(target)) loadBatch(target); });
    els.batchNumberInput.addEventListener("keydown", (event) => { if (event.key === "Enter") els.goBatchBtn.click(); });
    els.loadAllBtn.addEventListener("click", loadAllCorpus); els.cancelLoadBtn.addEventListener("click", () => { state.allLoadAbort = true; });
    els.exportJsonBtn.addEventListener("click", exportJson); els.exportCsvBtn.addEventListener("click", exportCsv); els.exportIssuesBtn.addEventListener("click", exportIssuesMarkdown);
    els.importInput.addEventListener("change", async () => { const file = els.importInput.files?.[0]; if (!file) return; try { await importAudit(file); } catch (error) { alert(`Import thất bại: ${error.message}`); } finally { els.importInput.value = ""; } });
    document.addEventListener("keydown", (event) => { if (event.target.matches("input, textarea, select")) return; if (event.key === "[") els.prevBatchBtn.click(); if (event.key === "]") els.nextBatchBtn.click(); if (event.key === "/") { event.preventDefault(); els.searchInput.focus(); } });
  }

  async function init() { loadSettings(); attachEvents(); await loadPlan(); }
  init();
})();
