import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from rembg import remove

app = FastAPI()

# ENV
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")
MAX_BYTES = int(os.getenv("MAX_BYTES", str(10 * 1024 * 1024)))  # default 10MB
API_KEY = os.getenv("API_KEY", "")  # optional

origins = ["*"] if FRONTEND_URL == "*" else [FRONTEND_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
