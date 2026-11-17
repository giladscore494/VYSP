// Admin page: login, uploads (with WebP variants made here in the browser), captions,
// delete, drag-to-reorder and site texts. No framework, no build step.

const MAX_PHOTOS = 50;
const MAX_BYTES = 30 * 1024 * 1024;
const ACCEPTED = { "image/jpeg": "jpg", "image/png": "png", "image/webp": "webp" };
const SIZES = [2000, 800];

const $ = (sel) => document.querySelector(sel);
const views = {
  loading: $("#view-loading"),
  unconfigured: $("#view-unconfigured"),
  login: $("#view-login"),
  admin: $("#view-admin"),
};

let site = null;           // last known site.json
let busyUploads = 0;

/* --------------------------------------------------------------- Utils */

function show(name) {
  for (const [key, el] of Object.entries(views)) el.hidden = key !== name;
  $("#logout").hidden = name !== "admin";
}

function announce(text) {
  const el = $("#announce");
  el.textContent = "";
  requestAnimationFrame(() => { el.textContent = text; });
}

function randomId() {
  const bytes = crypto.getRandomValues(new Uint8Array(20));
  const alphabet = "abcdefghijklmnopqrstuvwxyz0123456789";
  return Array.from(bytes, (b) => alphabet[b % 36]).join("");
}

const mbFormat = new Intl.NumberFormat("he-IL", { maximumFractionDigits: 1 });
function formatMB(bytes) {
  return `${mbFormat.format(bytes / (1024 * 1024))}\u00a0MB`;
}

class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status; }
}

async function api(path, { method = "GET", body } = {}) {
  let res;
  try {
    res = await fetch("/api" + path, {
      method,
      headers: body !== undefined ? { "content-type": "application/json" } : undefined,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      credentials: "same-origin",
      cache: "no-store",
    });
  } catch {
    throw new ApiError("אין חיבור לאינטרנט, או שהשרת לא זמין. בדקו את החיבור ונסו שוב.", 0);
  }
  let data = null;
  try { data = await res.json(); } catch { data = null; }
  if (!res.ok) {
    if (res.status === 401 && path !== "/login") sessionExpired();
    throw new ApiError((data && data.error) || `אירעה שגיאה (${res.status}). נסו שוב.`, res.status);
  }
  return data;
}

function sessionExpired() {
  show("login");
  const err = $("#login-error");
  err.textContent = "פג תוקף ההתחברות. היכנסו שוב.";
  err.hidden = false;
}

/* ---------------------------------------------------------------- Boot */

async function boot() {
  show("loading");
  let state;
  try {
    state = await api("/session");
  } catch (e) {
    views.loading.innerHTML = "";
    const p = document.createElement("p");
    p.className = "error";
    p.textContent = e.message;
    views.loading.append(p);
    return;
  }
  if (!state.configured) { show("unconfigured"); return; }
  if (!state.authenticated) {
    show("login");
    // Focus the field only with a mouse; on phones it would throw the keyboard up unasked.
    if (matchMedia("(pointer: fine)").matches) $("#token").focus();
    return;
  }
  await enterAdmin();
}

async function enterAdmin() {
  show("admin");
  try {
    site = await api("/site");
  } catch (e) {
    toastError(e.message);
    return;
  }
  renderAll();
}

$("#recheck").addEventListener("click", boot);

/* --------------------------------------------------------------- Login */

$("#login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = $("#token");
  const err = $("#login-error");
  const btn = $("#login-submit");
  const token = input.value.trim();
  err.hidden = true;
  input.removeAttribute("aria-invalid");
  if (!token) {
    err.textContent = "כתבו את קוד הגישה.";
    err.hidden = false;
    input.setAttribute("aria-invalid", "true");
    input.focus();
    return;
  }
  btn.disabled = true;
  btn.textContent = "בודק…";
  try {
    await api("/login", { method: "POST", body: { token } });
    input.value = "";
    await enterAdmin();
  } catch (ex) {
    err.textContent = ex.message;
    err.hidden = false;
    input.setAttribute("aria-invalid", "true");
    input.select();
  } finally {
    btn.disabled = false;
    btn.textContent = "כניסה";
  }
});

$("#logout").addEventListener("click", async () => {
  try { await api("/logout", { method: "POST" }); } catch { /* ignore */ }
  site = null;
  $("#photos").innerHTML = "";
  show("login");
});

/* ------------------------------------------------------------ Rendering */

function renderAll() {
  renderTexts();
  renderPhotos();
}

function renderTexts() {
  const t = site.texts;
  $("#top-name").textContent = t.name ? `ניהול: ${t.name}` : "ניהול האתר";
  const form = $("#texts-form");
  form.name.value = t.name || "";
  form.subtitle.value = t.subtitle || "";
  form.phone.value = t.phone || "";
  form.whatsapp.value = t.whatsapp || "";
}

function photoUrl(p, size) { return `/img/${p.id}/${size}.${p.v}`; }

function renderPhotos() {
  const list = $("#photos");
  const focused = document.activeElement && document.activeElement.closest(".photo");
  const focusId = focused && focused.dataset.id;
  const focusClass = focused && document.activeElement.className;
  list.innerHTML = "";
  site.photos.forEach((p, i) => list.append(photoRow(p, i)));
  updateCounts();
  if (focusId) {
    const row = list.querySelector(`[data-id="${focusId}"]`);
    const target = row && (focusClass.includes("grip") ? row.querySelector(".grip") : focusClass.includes("cap") ? row.querySelector(".cap") : null);
    if (target) target.focus();
  }
}

function updateCounts() {
  const n = site.photos.length;
  $("#photo-count").textContent = `${n} מתוך ${MAX_PHOTOS}`;
  $("#empty").hidden = n > 0;
  $("#order-hint").hidden = n < 2;
  const full = n >= MAX_PHOTOS;
  const pick = $("#pick");
  pick.setAttribute("aria-disabled", full ? "true" : "false");
  $("#file").disabled = full;
  pick.textContent = full ? "הגעתם למקסימום של 50 תמונות" : "הוספת תמונות";
  [...$("#photos").children].forEach((row, i) => {
    row.querySelector(".pos").textContent = String(i + 1);
    row.querySelector(".grip").setAttribute("aria-label", `שינוי מיקום לתמונה ${i + 1}. גוררים, או משתמשים בחיצים למעלה ולמטה`);
    row.querySelector(".cap-label").textContent = `כיתוב לתמונה ${i + 1}`;
    const [up, down] = row.querySelectorAll(".mv");
    up.disabled = i === 0;
    down.disabled = i === n - 1;
    up.setAttribute("aria-label", `הזזת תמונה ${i + 1} מקום אחד למעלה`);
    down.setAttribute("aria-label", `הזזת תמונה ${i + 1} מקום אחד למטה`);
  });
}

function photoRow(p, i) {
  const li = document.createElement("li");
  li.className = "photo";
  li.dataset.id = p.id;
  li.innerHTML = `
    <button type="button" class="grip"></button>
    <div class="thumb-wrap"><img class="thumb" alt="" width="96" height="96" loading="lazy" decoding="async"><span class="pos"></span></div>
    <div class="photo-main">
      <label class="vh cap-label" for="cap-${p.id}"></label>
      <input class="field cap" id="cap-${p.id}" name="caption" maxlength="200" placeholder="כיתוב, לא חובה…" autocomplete="off" enterkeyhint="done">
      <span class="photo-status" aria-live="polite"></span>
    </div>
    <div class="row-actions">
      <button type="button" class="mv" data-move="-1">למעלה</button>
      <button type="button" class="mv" data-move="1">למטה</button>
      <button type="button" class="del">מחיקה</button>
    </div>`;
  li.querySelector(".thumb").src = photoUrl(p, "w800");
  const cap = li.querySelector(".cap");
  cap.value = p.caption || "";
  cap.dataset.saved = p.caption || "";
  li.querySelector(".pos").textContent = String(i + 1);
  return li;
}

/* -------------------------------------------------------------- Captions */

const photosEl = $("#photos");

photosEl.addEventListener("keydown", (e) => {
  if (e.target.classList.contains("cap") && e.key === "Enter") {
    e.preventDefault();
    e.target.blur();
  }
});

photosEl.addEventListener("focusout", (e) => {
  if (e.target.classList.contains("cap")) saveCaption(e.target);
});

async function saveCaption(input) {
  const value = input.value.trim();
  if (value === input.dataset.saved) return;
  const row = input.closest(".photo");
  const status = row.querySelector(".photo-status");
  status.classList.remove("is-error");
  status.textContent = "שומר…";
  try {
    const res = await api(`/photos/${row.dataset.id}`, { method: "PATCH", body: { caption: value } });
    site = res.site;
    input.dataset.saved = value;
    status.textContent = "הכיתוב נשמר";
    setTimeout(() => { if (status.textContent === "הכיתוב נשמר") status.textContent = ""; }, 2500);
  } catch (e) {
    status.classList.add("is-error");
    status.textContent = e.message;
  }
}

/* ------------------------------------------------- Move buttons (tap) */

photosEl.addEventListener("click", (e) => {
  const btn = e.target.closest(".mv");
  if (!btn || btn.disabled) return;
  const row = btn.closest(".photo");
  const up = btn.dataset.move === "-1";
  if (up && row.previousElementSibling) photosEl.insertBefore(row, row.previousElementSibling);
  else if (!up && row.nextElementSibling) photosEl.insertBefore(row.nextElementSibling, row);
  else return;
  updateCounts();
  // Keep focus on the same control; if it just became disabled, use its partner.
  const same = row.querySelector(`.mv[data-move="${btn.dataset.move}"]`);
  (same.disabled ? row.querySelector(`.mv:not([data-move="${btn.dataset.move}"])`) : same).focus();
  announce(`התמונה הועברה למקום ${[...photosEl.children].indexOf(row) + 1}`);
  scheduleOrderSave();
});

/* ---------------------------------------------------------------- Delete */

photosEl.addEventListener("click", async (e) => {
  const btn = e.target.closest(".del");
  if (!btn) return;
  const row = btn.closest(".photo");
  if (!btn.classList.contains("is-armed")) {
    // First tap arms the button; a second tap within a few seconds deletes.
    disarmAll();
    btn.classList.add("is-armed");
    btn.textContent = "למחוק?";
    btn.setAttribute("aria-label", "לחצו שוב כדי למחוק את התמונה לצמיתות");
    btn._timer = setTimeout(() => disarm(btn), 4000);
    return;
  }
  clearTimeout(btn._timer);
  btn.disabled = true;
  btn.textContent = "מוחק…";
  const status = row.querySelector(".photo-status");
  try {
    const res = await api(`/photos/${row.dataset.id}`, { method: "DELETE" });
    site = res.site;
    const index = [...photosEl.children].indexOf(row);
    row.remove();
    updateCounts();
    announce("התמונה נמחקה");
    const next = photosEl.children[index] || photosEl.children[index - 1];
    if (next) next.querySelector(".grip").focus();
    else $("#pick").focus();
  } catch (ex) {
    btn.disabled = false;
    disarm(btn);
    status.classList.add("is-error");
    status.textContent = ex.message;
  }
});

function disarm(btn) {
  btn.classList.remove("is-armed");
  btn.textContent = "מחיקה";
  btn.removeAttribute("aria-label");
}
function disarmAll() {
  photosEl.querySelectorAll(".del.is-armed").forEach((b) => { clearTimeout(b._timer); disarm(b); });
}

/* --------------------------------------------------------------- Reorder */

let orderSaveTimer = null;

function currentOrder() { return [...photosEl.children].map((li) => li.dataset.id); }

function scheduleOrderSave() {
  clearTimeout(orderSaveTimer);
  orderSaveTimer = setTimeout(saveOrder, 350);
}

async function saveOrder() {
  const ids = currentOrder();
  if (site && ids.join() === site.photos.map((p) => p.id).join()) return;
  try {
    const res = await api("/order", { method: "PUT", body: { ids } });
    site = res.site;
    flashCount("הסדר נשמר");
  } catch (e) {
    toastError(e.message);
    if (e.status === 409) {
      try { site = await api("/site"); renderPhotos(); } catch { /* keep */ }
    }
  }
}

function flashCount(text) {
  const el = $("#photo-count");
  el.textContent = text;
  announce(text);
  clearTimeout(flashCount._t);
  flashCount._t = setTimeout(updateCounts, 1800);
}

// Keyboard: arrows on the grip move the photo.
photosEl.addEventListener("keydown", (e) => {
  if (!e.target.classList.contains("grip")) return;
  const row = e.target.closest(".photo");
  let moved = false;
  if (e.key === "ArrowUp" && row.previousElementSibling) {
    photosEl.insertBefore(row, row.previousElementSibling);
    moved = true;
  } else if (e.key === "ArrowDown" && row.nextElementSibling) {
    photosEl.insertBefore(row.nextElementSibling, row);
    moved = true;
  } else if (e.key === "Home" && row.previousElementSibling) {
    photosEl.prepend(row);
    moved = true;
  } else if (e.key === "End" && row.nextElementSibling) {
    photosEl.append(row);
    moved = true;
  }
  if (moved) {
    e.preventDefault();
    e.target.focus();
    updateCounts();
    announce(`התמונה הועברה למקום ${[...photosEl.children].indexOf(row) + 1}`);
    scheduleOrderSave();
  }
});

// Pointer drag (touch, pen and mouse) from the grip.
let drag = null;

photosEl.addEventListener("pointerdown", (e) => {
  const grip = e.target.closest(".grip");
  if (!grip || e.button !== 0 || drag) return;
  const row = grip.closest(".photo");
  const rows = [...photosEl.children];
  e.preventDefault();
  grip.setPointerCapture(e.pointerId);
  disarmAll();
  const rects = rows.map((r) => {
    const b = r.getBoundingClientRect();
    return { top: b.top + window.scrollY, height: b.height };
  });
  drag = {
    row,
    grip,
    pointerId: e.pointerId,
    rows,
    rects,
    from: rows.indexOf(row),
    to: rows.indexOf(row),
    startY: e.clientY + window.scrollY,
    lastClientY: e.clientY,
    raf: 0,
    started: false,
  };
});

photosEl.addEventListener("pointermove", (e) => {
  if (!drag || e.pointerId !== drag.pointerId) return;
  drag.lastClientY = e.clientY;
  if (!drag.started) {
    if (Math.abs(e.clientY + window.scrollY - drag.startY) < 4) return;
    drag.started = true;
    drag.row.classList.add("is-dragging");
    photosEl.classList.add("is-sorting");
    if (navigator.vibrate) navigator.vibrate(8);
  }
  layoutDrag();
  if (!drag.raf) drag.raf = requestAnimationFrame(autoScroll);
});

function layoutDrag() {
  const { row, rows, rects, from } = drag;
  const dy = drag.lastClientY + window.scrollY - drag.startY;
  row.style.transform = `translateY(${dy}px)`;
  const center = rects[from].top + dy + rects[from].height / 2;
  let to = from;
  for (let i = 0; i < rows.length; i++) {
    const mid = rects[i].top + rects[i].height / 2;
    if (i < from && center < mid) { to = i; break; }
    if (i > from && center > mid) to = i;
  }
  drag.to = to;
  const shift = rects[from].height;
  rows.forEach((r, i) => {
    if (r === row) return;
    let offset = 0;
    if (from < to && i > from && i <= to) offset = -shift;
    if (from > to && i >= to && i < from) offset = shift;
    r.style.transform = offset ? `translateY(${offset}px)` : "";
  });
}

function autoScroll() {
  if (!drag) return;
  drag.raf = 0;
  if (!drag.started) return;
  const edge = 90;
  const y = drag.lastClientY;
  let speed = 0;
  if (y < edge) speed = -Math.ceil((edge - y) / 6);
  else if (y > window.innerHeight - edge) speed = Math.ceil((y - (window.innerHeight - edge)) / 6);
  if (speed) {
    window.scrollBy(0, speed);
    layoutDrag();
    drag.raf = requestAnimationFrame(autoScroll);
  }
}

function endDrag(e) {
  if (!drag || (e && e.pointerId !== drag.pointerId)) return;
  const { row, rows, from, to, started, raf } = drag;
  cancelAnimationFrame(raf);
  rows.forEach((r) => { r.style.transform = ""; });
  row.classList.remove("is-dragging");
  photosEl.classList.remove("is-sorting");
  drag = null;
  if (!started || from === to) return;
  const ref = rows[to];
  if (from < to) ref.after(row);
  else ref.before(row);
  updateCounts();
  announce(`התמונה הועברה למקום ${to + 1}`);
  scheduleOrderSave();
}

photosEl.addEventListener("pointerup", endDrag);
photosEl.addEventListener("pointercancel", endDrag);
photosEl.addEventListener("lostpointercapture", endDrag);

/* ----------------------------------------------------------------- Texts */

$("#texts-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const err = $("#texts-error");
  const status = $("#texts-status");
  const btn = $("#texts-submit");
  err.hidden = true;
  status.textContent = "";
  form.querySelectorAll("[aria-invalid]").forEach((el) => el.removeAttribute("aria-invalid"));
  const body = {
    name: form.name.value.trim(),
    subtitle: form.subtitle.value.trim(),
    phone: form.phone.value.trim(),
    whatsapp: form.whatsapp.value.trim(),
  };
  if (!body.name) {
    err.textContent = "יש למלא את שם הצימר.";
    err.hidden = false;
    form.name.setAttribute("aria-invalid", "true");
    form.name.focus();
    return;
  }
  btn.disabled = true;
  status.textContent = "שומר…";
  try {
    const res = await api("/texts", { method: "PUT", body });
    site = res.site;
    renderTexts();
    status.textContent = "הפרטים נשמרו ויופיעו באתר מיד.";
  } catch (ex) {
    status.textContent = "";
    err.textContent = ex.message;
    err.hidden = false;
    if (ex.status === 400) {
      const field = /וואטסאפ/.test(ex.message) ? form.whatsapp : /טלפון/.test(ex.message) ? form.phone : null;
      if (field) { field.setAttribute("aria-invalid", "true"); field.focus(); }
    }
  } finally {
    btn.disabled = false;
  }
});

/* --------------------------------------------------------------- Uploads */

const fileInput = $("#file");
const drop = $("#drop");
const queueEl = $("#queue");
const pending = [];
let running = false;

fileInput.addEventListener("change", () => {
  addFiles([...fileInput.files]);
  fileInput.value = "";
});

["dragenter", "dragover"].forEach((type) => {
  document.addEventListener(type, (e) => {
    if (!views.admin.hidden && e.dataTransfer && [...e.dataTransfer.types].includes("Files")) {
      e.preventDefault();
      drop.classList.add("is-over");
    }
  });
});
document.addEventListener("dragleave", (e) => {
  if (e.relatedTarget === null) drop.classList.remove("is-over");
});
document.addEventListener("drop", (e) => {
  if (!e.dataTransfer || ![...e.dataTransfer.types].includes("Files")) return;
  e.preventDefault();
  drop.classList.remove("is-over");
  if (views.admin.hidden) return;
  addFiles([...e.dataTransfer.files]);
});

function addFiles(files) {
  if (!files.length) return;
  const room = MAX_PHOTOS - site.photos.length - pending.length - busyUploads;
  files.forEach((file, i) => {
    const job = { file, el: uploadRow(file) };
    queueEl.append(job.el);
    if (i >= room) {
      fail(job, `אפשר לשמור עד ${MAX_PHOTOS} תמונות. מחקו תמונה כדי להוסיף חדשה.`, false);
      return;
    }
    pending.push(job);
    setState(job, "ממתין…", 0);
  });
  runQueue();
}

function uploadRow(file) {
  const li = document.createElement("li");
  li.className = "up";
  li.innerHTML = `
    <p class="up-name"></p>
    <p class="up-state"></p>
    <div class="up-bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span></span></div>`;
  li.querySelector(".up-name").textContent = file.name || "תמונה";
  li.querySelector(".up-bar").setAttribute("aria-label", `התקדמות ההעלאה של ${file.name || "התמונה"}`);
  return li;
}

function setState(job, text, fraction) {
  job.el.querySelector(".up-state").textContent = text;
  if (fraction !== undefined) {
    const pct = Math.round(fraction * 100);
    const bar = job.el.querySelector(".up-bar");
    bar.setAttribute("aria-valuenow", String(pct));
    bar.querySelector("span").style.setProperty("--p", String(fraction));
  }
}

function fail(job, message, canRetry = true) {
  job.el.classList.add("is-error");
  setState(job, "נכשל");
  job.el.querySelector(".up-msg")?.remove();
  job.el.querySelector(".up-actions")?.remove();
  const msg = document.createElement("p");
  msg.className = "error up-msg";
  msg.textContent = message;
  const actions = document.createElement("div");
  actions.className = "up-actions";
  if (canRetry) {
    const retry = document.createElement("button");
    retry.type = "button";
    retry.className = "btn";
    retry.textContent = "ניסיון חוזר";
    retry.addEventListener("click", () => {
      job.el.classList.remove("is-error");
      msg.remove();
      actions.remove();
      setState(job, "ממתין…", 0);
      pending.push(job);
      runQueue();
    });
    actions.append(retry);
  }
  const dismiss = document.createElement("button");
  dismiss.type = "button";
  dismiss.className = "btn";
  dismiss.textContent = "הסרה מהרשימה";
  dismiss.addEventListener("click", () => job.el.remove());
  actions.append(dismiss);
  job.el.append(msg, actions);
}

async function runQueue() {
  if (running) return;
  running = true;
  // One photo at a time keeps memory low on phones and keeps the chosen order.
  while (pending.length) {
    const job = pending.shift();
    busyUploads++;
    try {
      await uploadOne(job);
    } catch (e) {
      fail(job, e.message || "ההעלאה נכשלה. נסו שוב.", e.retry !== false);
    } finally {
      busyUploads--;
    }
  }
  running = false;
}

class UploadError extends Error {
  constructor(message, retry = true) { super(message); this.retry = retry; }
}

async function detectType(file) {
  const head = new Uint8Array(await file.slice(0, 16).arrayBuffer());
  if (head[0] === 0xff && head[1] === 0xd8 && head[2] === 0xff) return "image/jpeg";
  if (head[0] === 0x89 && head[1] === 0x50 && head[2] === 0x4e && head[3] === 0x47) return "image/png";
  if (head[0] === 0x52 && head[1] === 0x49 && head[2] === 0x46 && head[3] === 0x46 &&
      head[8] === 0x57 && head[9] === 0x45 && head[10] === 0x42 && head[11] === 0x50) return "image/webp";
  const box = String.fromCharCode(...head.slice(4, 12));
  if (/^ftyp(heic|heix|hevc|mif1|msf1|heim|heis)/.test(box)) return "image/heic";
  return null;
}

async function uploadOne(job) {
  const { file } = job;
  if (site.photos.length >= MAX_PHOTOS) throw new UploadError(`אפשר לשמור עד ${MAX_PHOTOS} תמונות. מחקו תמונה כדי להוסיף חדשה.`, false);
  if (file.size > MAX_BYTES) throw new UploadError(`הקובץ גדול מדי (${formatMB(file.size)}). הגודל המרבי הוא 30MB לתמונה.`, false);
  if (file.size === 0) throw new UploadError("הקובץ ריק.", false);

  const type = await detectType(file);
  if (type === "image/heic") {
    throw new UploadError("זה קובץ HEIC של אייפון, שאינו נתמך. בחרו את התמונה דרך כפתור הוספת התמונות בטלפון עצמו (האייפון ימיר אותה ל-JPEG), או שנו פעם אחת באייפון: הגדרות ← מצלמה ← פורמטים ← ״התאימות הגבוהה ביותר״.", false);
  }
  if (!type || !ACCEPTED[type]) throw new UploadError("סוג הקובץ אינו נתמך. אפשר להעלות JPEG,‏ PNG או WebP בלבד.", false);

  setState(job, "מכין גרסאות לאתר…", 0.02);
  const variants = await makeVariants(file);

  const id = randomId();
  const parts = [
    { name: "w800", blob: variants.small, type: variants.type },
    { name: "w2000", blob: variants.large, type: variants.type },
    { name: "original", blob: file, type },
  ];
  const total = parts.reduce((n, p) => n + p.blob.size, 0);
  let done = 0;
  for (const part of parts) {
    await putFile(`/api/photos/${id}/${part.name}`, part.blob, part.type, (loaded) => {
      const frac = (done + loaded) / total;
      setState(job, `מעלה… ${Math.round(frac * 100)}%`, 0.05 + frac * 0.9);
    });
    done += part.blob.size;
  }

  setState(job, "שומר…", 0.97);
  let res;
  try {
    res = await api("/photos", {
      method: "POST",
      body: { id, width: variants.width, height: variants.height, originalType: type, variantType: variants.type },
    });
  } catch (e) {
    throw new UploadError(e.message, e.status !== 409 || /לא הגיעו/.test(e.message));
  }
  site = res.site;
  setState(job, "הועלתה", 1);
  photosEl.append(photoRow(res.photo, site.photos.length - 1));
  updateCounts();
  setTimeout(() => job.el.remove(), 2500);
}

function putFile(url, blob, type, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("PUT", url);
    xhr.setRequestHeader("content-type", type);
    xhr.upload.onprogress = (e) => { if (e.lengthComputable) onProgress(e.loaded); };
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) { onProgress(blob.size); resolve(); return; }
      let msg = `ההעלאה נכשלה (${xhr.status}). נסו שוב.`;
      try { const d = JSON.parse(xhr.responseText); if (d && d.error) msg = d.error; } catch { /* keep */ }
      if (xhr.status === 401) sessionExpired();
      reject(new UploadError(msg, xhr.status !== 415 && xhr.status !== 413));
    };
    xhr.onerror = () => reject(new UploadError("החיבור נקטע באמצע ההעלאה. בדקו את האינטרנט ונסו שוב."));
    xhr.ontimeout = () => reject(new UploadError("ההעלאה ארכה זמן רב מדי. נסו שוב בחיבור יציב יותר."));
    xhr.send(blob);
  });
}

/* --------------------------------------------------- Variants (browser) */

let webpNative = null;
function canEncodeWebpNatively() {
  if (webpNative === null) {
    const c = document.createElement("canvas");
    c.width = c.height = 2;
    webpNative = c.toDataURL("image/webp").startsWith("data:image/webp");
  }
  return webpNative;
}

function loadImage(file) {
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.decoding = "async";
    img.onload = () => resolve({ img, url });
    img.onerror = () => { URL.revokeObjectURL(url); reject(new UploadError("לא ניתן לפתוח את התמונה. ייתכן שהקובץ פגום. נסו לבחור אותה שוב או לשלוח אותה לעצמכם מחדש.", false)); };
    img.src = url;
  });
}

function canvasToBlob(canvas, type, quality) {
  return new Promise((resolve) => canvas.toBlob(resolve, type, quality));
}

async function encode(canvas, quality, wantWebp) {
  if (wantWebp && canEncodeWebpNatively()) {
    const blob = await canvasToBlob(canvas, "image/webp", quality);
    if (blob && blob.type === "image/webp") return blob;
  }
  if (wantWebp) {
    try {
      const { encodeWebp } = await import("./vendor/webp/encode.js");
      const ctx = canvas.getContext("2d");
      const data = ctx.getImageData(0, 0, canvas.width, canvas.height);
      return await encodeWebp(data, Math.round(quality * 100));
    } catch (e) {
      console.warn("WebP encoder unavailable, falling back to JPEG", e);
    }
  }
  return null;
}

async function makeVariants(file) {
  const { img, url } = await loadImage(file);
  try {
    // naturalWidth/Height already account for the photo's EXIF rotation.
    const width = img.naturalWidth;
    const height = img.naturalHeight;
    if (!width || !height) throw new UploadError("לא ניתן לקרוא את מידות התמונה. נסו קובץ אחר.", false);

    const canvases = [];
    let source = img;
    let sw = width;
    let sh = height;
    for (const target of SIZES) {
      const w = Math.min(target, sw);
      const h = Math.round((w / width) * height);
      const c = document.createElement("canvas");
      c.width = w;
      c.height = h;
      const ctx = c.getContext("2d", { alpha: false });
      ctx.fillStyle = "#fff";
      ctx.fillRect(0, 0, w, h);
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = "high";
      ctx.drawImage(source, 0, 0, w, h);
      canvases.push(c);
      // Downscale the next size from this one: sharper and lighter on memory.
      source = c;
      sw = w;
      sh = h;
    }
    void sh;

    const [largeCanvas, smallCanvas] = canvases;
    let type = "image/webp";
    let large = await encode(largeCanvas, 0.86, true);
    let small = large ? await encode(smallCanvas, 0.82, true) : null;
    if (!large || !small) {
      type = "image/jpeg";
      large = await canvasToBlob(largeCanvas, "image/jpeg", 0.88);
      small = await canvasToBlob(smallCanvas, "image/jpeg", 0.84);
    }
    canvases.forEach((c) => { c.width = 0; c.height = 0; });
    if (!large || !small) throw new UploadError("הדפדפן לא הצליח להכין את גרסאות התמונה. נסו דפדפן אחר.", false);
    return { width, height, large, small, type };
  } finally {
    URL.revokeObjectURL(url);
  }
}

/* ----------------------------------------------------------------- Toast */

function toastError(message) {
  const el = $("#photos-error");
  el.textContent = message;
  el.hidden = false;
  clearTimeout(toastError._t);
  toastError._t = setTimeout(() => { el.hidden = true; }, 8000);
}

function textsDirty() {
  if (!site || views.admin.hidden) return false;
  const f = $("#texts-form");
  const t = site.texts;
  return ["name", "subtitle", "phone", "whatsapp"].some((k) => f[k].value.trim() !== (t[k] || ""));
}

function captionsDirty() {
  return [...document.querySelectorAll(".cap")].some((c) => c.value.trim() !== c.dataset.saved);
}

window.addEventListener("beforeunload", (e) => {
  if (running || pending.length || textsDirty() || captionsDirty()) { e.preventDefault(); e.returnValue = ""; }
});

boot();
