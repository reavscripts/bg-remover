import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from rembg import remove

app = FastAPI()

# ENV 
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")
MAX_BYTES = int(os.getenv("MAX_BYTES", str(10 * 1024 * 1024)))  # default 10MB
API_KEY = os.getenv("API_KEY", "")  # opzionale

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

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...), x_api_key: str | None = None):
    # opzionale: protezione con chiave
    if API_KEY:
        if x_api_key != API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="File non è un'immagine")

    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"Immagine troppo grande (max {MAX_BYTES} bytes)")

    try:
        out = remove(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore processing: {str(e)}")

    return Response(content=out, media_type="image/png")
