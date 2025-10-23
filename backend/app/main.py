from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from io import BytesIO
import pandas as pd

app = FastAPI(title="Excel Cleaner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Excel Cleaner API running successfully"}

@app.post("/clean")
async def clean(file: UploadFile = File(...)):
    try:
        data = await file.read()
        df = pd.read_csv(BytesIO(data)) if file.filename.lower().endswith(".csv") else pd.read_excel(BytesIO(data))

        # cleaning logic
        df = df.drop_duplicates()

        out = BytesIO()
        if file.filename.lower().endswith(".csv"):
            df.to_csv(out, index=False)
            mtype = "text/csv"
            fname = "cleaned.csv"
        else:
            with pd.ExcelWriter(out, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            mtype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            fname = "cleaned.xlsx"
        out.seek(0)

        headers = {
            "Content-Disposition": f'attachment; filename="{fname}"',
            "X-Filename": fname,
            "X-Clean-Summary": f"rows={len(df)},cols={len(df.columns)}",
        }
        return StreamingResponse(out, media_type=mtype, headers=headers)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed: {e}")
