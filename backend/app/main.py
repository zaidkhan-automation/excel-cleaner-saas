from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/clean")
async def clean_excel(file: UploadFile = File(...)):
    raw = await file.read()
    df = pd.read_excel(io.BytesIO(raw))

    # ——— your cleaning logic ———
    df.dropna(how="all", inplace=True)
    df.columns = [c.strip() for c in df.columns]
    # add more of your pro-v1 logic here

    # write to in-memory Excel
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    buf.seek(0)

    headers = {
        "Content-Disposition": 'attachment; filename="cleaned.xlsx"'
    }
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )
