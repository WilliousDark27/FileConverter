import io
from fastapi import FastAPI, File, UploadFile
from converter import file_to_str, get_file_group

app = FastAPI()

ALLOWED_MIMETYPES = {
    "text/plain": "txt",
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "application/vnd.oasis.opendocument.text": "odt",
    "image/jpeg": "jpeg",
    "image/png": "png",
    "image/webp": "webp",
    "image/avif": "avif",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": "pptx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/vnd.oasis.opendocument.spreadsheet": "ods",
}

@app.post("/convert")
async def convert(file: UploadFile =  File(...)):
    file_type = ALLOWED_MIMETYPES.get(file.content_type)
    if not file_type:
        return {"error": "Invalid file type!"}
    file_group = get_file_group(file_type)
    return {
        "file_type": file.content_type,
        "file_group": file_group,
        "result": file_to_str(io.BytesIO(await file.read()), file_group, file_type)
    }

# uvicorn main:app --reload