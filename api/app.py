from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from rembg import remove

app = FastAPI()

# In produzione metti qui il dominio Vercel, es: https://tuo-sito.vercel.app
ALLOWED_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_BYTES = 10 * 1024 * 1024  # 10MB

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="File non è un'immagine")

    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Immagine troppo grande (max 10MB)")

    try:
        out = remove(data)  # restituisce PNG bytes con alpha
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore processing: {str(e)}")

    return Response(content=out, media_type="image/png")
