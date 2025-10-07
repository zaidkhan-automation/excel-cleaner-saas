from fastapi import FastAPI, UploadFile, File
from  fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from io import BytesIO

app = FastAPI(title="Excel Cleaner API")

# ✅ Allow frontend (Streamlit, local dev, or Render frontend) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later you can restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Home route (to fix 404)
@app.get("/")
def home():
    return {"message": "✅ Excel Cleaner API is running successfully!"}

# ✅ Health check route
@app.get("/health")
def health():
    return {"status": "ok"}

# ✅ Excel cleaning endpoint
@app.post("/clean")
async def clean_excel(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))

        # --- Cleaning steps ---
        df.drop_duplicates(inplace=True)
        df.columns = [c.strip().title() for c in df.columns]
        df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # Handle missing values (fill empty cells with blank)
        df.fillna("", inplace=True)

        # Return cleaned Excel as bytes
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)

        return {
            "status": "success",
            "rows": len(df),
            "columns": list(df.columns)
        }

    except Exception as e:
        return {"error": str(e)}
