from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
import subprocess
import json
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all frontend origins (change this for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

UPLOAD_FOLDER = "uploads"
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    file_path = f"{UPLOAD_FOLDER}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Extract C2PA metadata using c2patool
    c2pa_metadata = extract_c2pa_metadata(file_path)
    
    # Extract general EXIF metadata using exiftool
    exif_metadata = extract_exif_metadata(file_path)
    
    return {"filename": file.filename, "c2pa_metadata": c2pa_metadata, "exif_metadata": exif_metadata}


def extract_c2pa_metadata(image_path: str):
    try:
        result = subprocess.run(["c2patool", image_path, "--detailed"], capture_output=True, text=True)
        return json.loads(result.stdout) if result.stdout else {"error": "No C2PA metadata found"}
    except Exception as e:
        return {"error": str(e)}


def extract_exif_metadata(image_path: str):
    try:
        result = subprocess.run(["exiftool", "-j", image_path], capture_output=True, text=True)
        return json.loads(result.stdout)[0] if result.stdout else {"error": "No EXIF metadata found"}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
