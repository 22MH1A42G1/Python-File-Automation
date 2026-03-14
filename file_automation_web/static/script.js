/* =========================================================
   script.js  –  File Automation Web App
   ========================================================= */

"use strict";

// ── STATE ─────────────────────────────────────────────────
let selectedFiles = [];   // FileList-style array for the upload tab

// ── DOM REFS ──────────────────────────────────────────────
const $ = id => document.getElementById(id);

// ── TABS ──────────────────────────────────────────────────
document.querySelectorAll(".nav-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    // Deactivate all
    document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
    // Activate clicked
    btn.classList.add("active");
    document.getElementById(btn.dataset.tab).classList.add("active");
    // Auto-refresh file list when the browse tab is opened
    if (btn.dataset.tab === "tab-files") loadFiles();
  });
});

// ── TOAST ─────────────────────────────────────────────────
let toastTimer;
function showToast(msg, type = "info") {
  const t = $("toast");
  t.textContent = msg;
  t.className   = `toast ${type}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.add("hidden"), 3500);
}

// ── RESULT BOX ────────────────────────────────────────────
function showResult(boxId, { success, message, files, errors }) {
  const box = $(boxId);
  box.classList.remove("hidden");

  const icon   = success ? "✅" : "❌";
  const cls    = success ? "success" : "error";

  let html = `<div class="result-header ${cls}">${icon} ${escHtml(message)}</div>`;
  html += `<div class="result-body">`;

  if (files && files.length) {
    html += buildTable(files);
  }
  if (errors && errors.length) {
    html += `<p style="color:var(--warn);margin-top:.5rem;font-size:.83rem;">
               ⚠️ ${errors.length} error(s): ${errors.map(e => escHtml(e.file)).join(", ")}
             </p>`;
  }
  html += `</div>`;
  box.innerHTML = html;
}

function buildTable(files) {
  if (!files.length) return "";
  const keys = Object.keys(files[0]);
  let t = `<table class="result-table"><thead><tr>`;
  keys.forEach(k => t += `<th>${escHtml(k)}</th>`);
  t += `</tr></thead><tbody>`;
  files.forEach(row => {
    t += "<tr>";
    keys.forEach(k => t += `<td>${escHtml(String(row[k] ?? ""))}</td>`);
    t += "</tr>";
  });
  return t + "</tbody></table>";
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ── UPLOAD TAB ────────────────────────────────────────────
const fileInput  = $("fileInput");
const dropZone   = $("dropZone");
const filePreview = $("filePreview");

// Drag-and-drop
dropZone.addEventListener("dragover", e => {
  e.preventDefault();
  dropZone.classList.add("drag-over");
});
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("drag-over"));
dropZone.addEventListener("drop", e => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  addFiles([...e.dataTransfer.files]);
});
dropZone.addEventListener("click", e => {
  if (e.target.tagName !== "LABEL") fileInput.click();
});
fileInput.addEventListener("change", () => addFiles([...fileInput.files]));

function addFiles(newFiles) {
  newFiles.forEach(f => {
    if (!selectedFiles.find(x => x.name === f.name && x.size === f.size))
      selectedFiles.push(f);
  });
  renderPreview();
}

function renderPreview() {
  if (!selectedFiles.length) {
    filePreview.classList.add("hidden");
    return;
  }
  filePreview.classList.remove("hidden");
  filePreview.innerHTML = selectedFiles.map((f, i) =>
    `<span class="file-tag">
       ${escHtml(f.name)}
       <span class="remove-tag" data-i="${i}" title="Remove">✕</span>
     </span>`
  ).join("");
  filePreview.querySelectorAll(".remove-tag").forEach(el => {
    el.addEventListener("click", () => {
      selectedFiles.splice(Number(el.dataset.i), 1);
      renderPreview();
    });
  });
}

$("btnClearInput").addEventListener("click", () => {
  selectedFiles = [];
  fileInput.value = "";
  renderPreview();
});

$("btnUpload").addEventListener("click", async () => {
  if (!selectedFiles.length) { showToast("Please select files first.", "error"); return; }

  const btn = $("btnUpload");
  btn.innerHTML = '<span class="spinner"></span> Uploading…';
  btn.disabled = true;

  const form = new FormData();
  selectedFiles.forEach(f => form.append("files", f));

  try {
    const res  = await fetch("/upload", { method: "POST", body: form });
    const data = await res.json();
    showResult("uploadResult", data);
    showToast(data.message, data.success ? "success" : "error");
    if (data.success) { selectedFiles = []; fileInput.value = ""; renderPreview(); }
  } catch (err) {
    showToast("Upload failed. Check the server.", "error");
  } finally {
    btn.innerHTML = "Upload Now";
    btn.disabled = false;
  }
});

// ── RENAME TAB ────────────────────────────────────────────
$("btnRename").addEventListener("click", async () => {
  const prefix = $("renamePrefix").value.trim() || "file";
  const btn    = $("btnRename");
  btn.innerHTML = '<span class="spinner"></span> Renaming…';
  btn.disabled  = true;

  try {
    const res  = await fetch("/rename", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prefix }),
    });
    const data = await res.json();
    showResult("renameResult", data);
    showToast(data.message, data.success ? "success" : "error");
  } catch {
    showToast("Rename failed. Check the server.", "error");
  } finally {
    btn.innerHTML = "Rename Files";
    btn.disabled  = false;
  }
});

// ── CSV → JSON TAB ────────────────────────────────────────
$("btnCsvToJson").addEventListener("click", async () => {
  const btn = $("btnCsvToJson");
  btn.innerHTML = '<span class="spinner"></span> Converting…';
  btn.disabled  = true;

  try {
    const res  = await fetch("/csv-to-json", { method: "POST" });
    const data = await res.json();
    showResult("csvResult", data);
    showToast(data.message, data.success ? "success" : "error");
  } catch {
    showToast("Conversion failed. Check the server.", "error");
  } finally {
    btn.innerHTML = "Convert CSV → JSON";
    btn.disabled  = false;
  }
});

// ── ORGANISE TAB ──────────────────────────────────────────
$("btnOrganise").addEventListener("click", async () => {
  const btn = $("btnOrganise");
  btn.innerHTML = '<span class="spinner"></span> Organising…';
  btn.disabled  = true;

  try {
    const res  = await fetch("/organize", { method: "POST" });
    const data = await res.json();
    showResult("organiseResult", data);
    showToast(data.message, data.success ? "success" : "error");
  } catch {
    showToast("Organise failed. Check the server.", "error");
  } finally {
    btn.innerHTML = "Organise Files";
    btn.disabled  = false;
  }
});

// ── FILES TAB ─────────────────────────────────────────────
async function loadFiles() {
  try {
    const res  = await fetch("/files");
    const data = await res.json();
    renderFileList("uploadList",    data.uploads,    false);
    renderFileList("processedList", data.processed,  true);
  } catch {
    showToast("Could not load file list.", "error");
  }
}

function renderFileList(listId, files, showDownload) {
  const ul = $(listId);
  if (!files || !files.length) {
    ul.innerHTML = `<li class="empty-msg">No files here yet.</li>`;
    return;
  }
  ul.innerHTML = files.map(f => {
    const dlBtn = showDownload
      ? `<a class="btn btn-primary btn-sm dl-btn" href="/download/${encodeURIComponent(f)}" download>⬇ Download</a>`
      : "";
    return `<li><span class="fname">${escHtml(f)}</span>${dlBtn}</li>`;
  }).join("");
}

$("btnRefresh").addEventListener("click", loadFiles);

$("btnClearUploads").addEventListener("click", async () => {
  if (!confirm("Clear all files from uploads/?")) return;
  await fetch("/clear-uploads", { method: "POST" });
  showToast("Uploads cleared.", "success");
  loadFiles();
});

$("btnClearProcessed").addEventListener("click", async () => {
  if (!confirm("Clear all files from processed/?")) return;
  await fetch("/clear-processed", { method: "POST" });
  showToast("Processed files cleared.", "success");
  loadFiles();
});

// ── INIT ──────────────────────────────────────────────────
loadFiles();
