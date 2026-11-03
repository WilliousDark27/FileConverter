from io import BytesIO
import numpy as np
import docx
import pymupdf
import zipfile
import xml.etree.ElementTree as ET
import easyocr
from PIL import Image
import pillow_avif
import pptx
import pandas

reader = easyocr.Reader(['ru', 'en'])

def get_file_group(file_type: str):
    if file_type in ("jpeg", "png", "webp", "avif"):
        return "image"
    if file_type in ("xlsx", "ods"):
        return "sheet"
    return file_type

def file_to_str(file_bytes: BytesIO, file_group: str, file_type: str):
    result = ""

    if file_group == "txt":
        result = file_bytes.getvalue().decode("utf-8")

    elif file_group == "docx":
        doc = docx.Document(file_bytes)
        for paragraph in doc.paragraphs:
            result += paragraph.text + "\n"

    elif file_group == "pdf":
        doc = pymupdf.open(stream=file_bytes)
        for page in doc:
            result += page.get_text()

    elif file_group == "odt":
        with zipfile.ZipFile(file_bytes) as zf:
                xml_content = zf.read('content.xml')
        root = ET.fromstring(xml_content)
        for elem in root.iter():
            if elem.tag.endswith('p') and elem.text:
                result += elem.text

    elif file_group == "image":
        image = Image.open(file_bytes)

        if image.mode != "RGB":
            image = image.convert("RGB")

        image_np = np.array(image) 
        ocr_results = reader.readtext(image_np)
        result = "\n".join([text for (_, text, _) in ocr_results])

    elif file_group == "pptx":
        prs = pptx.Presentation(file_bytes)
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    for paragraph in shape.text_frame.paragraphs:
                        for run in paragraph.runs:
                            if run.text.strip():
                                result += run.text + "\n"

    elif file_group == "sheet":
        all_sheets = pandas.read_excel(file_bytes, sheet_name=None, engine= "openpyxl" if file_type == "xlsx" else "odf")
        for sheet_name, df in all_sheets.items():     
            sheet_text = df.to_csv(index=False) 
            result += sheet_text  + "\n"

    return result