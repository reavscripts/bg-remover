import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from rembg import remove

app = FastAPI()

def _norm_origin(s: str) -> str:
    s = (s or "").strip()
    return s[:-1] if s.endswith("/") else s

# ENV
FRONTEND_URL = _norm_origin(os.getenv("FRONTEND_URL", "*"))
MAX_BYTES = int(os.getenv("MAX_BYTES", str(10 * 1024 * 1024)))  # default 10MB
API_KEY = os.getenv("API_KEY", "")  # optional

if FRONTEND_URL == "*":
    origins = ["*"]
else:
    # allow comma-separated list in FRONTEND_URL
    raw = [_norm_origin(x) for x in FRONTEND_URL.split(",")]
    raw = [x for x in raw if x]
    # include both with and without trailing slash (some tools differ)
    origins = sorted(set(raw + [x + "/" for x in raw]))

# Regex fallback (helps if an origin differs slightly or you use preview domains)
# - allows https://removebg.reav.space and any https://*.reav.space
# - allows Vercel preview domains https://*.vercel.app
ORIGIN_REGEX = r"^https://([a-z0-9-]+\.)?reav\.space/?$|^https://[a-z0-9-]+\.vercel\.app/?$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=ORIGIN_REGEX if origins != ["*"] else None,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/")
def root():
    return {"service": "bg-remover", "status": "ok"}

@app.post("/remove-bg")
async def remove_bg(
    file: UploadFile = File(...),
    x_api_key: str | None = Header(default=None),  # reads 'x-api-key' header
):
    # Optional API key protection
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="File is not an image")

    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"Image too large (max {MAX_BYTES} bytes)")

    try:
        out = remove(data)  # returns PNG bytes with alpha
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

    return Response(content=out, media_type="image/png")
