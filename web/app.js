const fileEl = document.getElementById("file");
const btn = document.getElementById("btn");
const statusEl = document.getElementById("status");
const prev = document.getElementById("prev");
const out = document.getElementById("out");
const download = document.getElementById("download");

let file = null;

fileEl.addEventListener("change", () => {
  file = fileEl.files?.[0] || null;
  if (!file) return;

  prev.src = URL.createObjectURL(file);
  out.removeAttribute("src");
  download.classList.add("hidden");
  btn.disabled = false;
  statusEl.textContent = "";
});

btn.addEventListener("click", async () => {
  if (!file) return;

  btn.disabled = true;
  statusEl.textContent = "Elaborazione...";

  try {
    const fd = new FormData();
    fd.append("file", file);

    const res = await fetch(window.API_URL, {
      method: "POST",
      body: fd,
      headers: window.API_KEY ? { "x-api-key": window.API_KEY } : {},
    });

    if (!res.ok) {
      const msg = await res.text();
      throw new Error(msg || `HTTP ${res.status}`);
    }

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    out.src = url;
    download.href = url;
    download.classList.remove("hidden");
    statusEl.textContent = "Fatto.";
  } catch (e) {
    statusEl.textContent = "Errore: " + (e?.message || String(e));
  } finally {
    btn.disabled = false;
  }
});

