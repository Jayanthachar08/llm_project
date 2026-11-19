import os
import io
import logging
from typing import Tuple, Optional
from PIL import Image
import pymupdf as fitz
from fastapi import UploadFile, HTTPException
from backend.app.core.config import settings

logger = logging.getLogger("campusflow.document_service")

# Setup Tesseract path if configured
if settings.TESSERACT_CMD:
    try:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
    except Exception as e:
        logger.warning("Could not set custom tesseract path: %s", e)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB

class DocumentService:
    @staticmethod
    def validate_file(file: UploadFile) -> Tuple[str, str]:
        """Validate file extension and content type."""
        filename = file.filename or "unknown"
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format '{ext}'. Supported formats: PDF, PNG, JPG, JPEG."
            )
        return filename, ext

    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        """Extract text from text-based PDF using PyMuPDF with OCR fallback for scanned pages."""
        extracted_text = ""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                if page_text and page_text.strip():
                    extracted_text += f"\n--- Page {page_num + 1} ---\n" + page_text
                else:
                    # Attempt OCR on scanned page image
                    try:
                        pix = page.get_pixmap(dpi=200)
                        img_data = pix.tobytes("png")
                        ocr_text = DocumentService.extract_text_from_image(img_data)
                        if ocr_text.strip():
                            extracted_text += f"\n--- Page {page_num + 1} (OCR) ---\n" + ocr_text
                    except Exception as ocr_err:
                        logger.warning("OCR fallback failed on PDF page %d: %s", page_num + 1, ocr_err)
            doc.close()
        except Exception as e:
            logger.error("PyMuPDF extraction failed: %s", e)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to process PDF document: {str(e)}"
            )

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract readable text from the uploaded PDF. The document may be blank, password-protected, or unreadable."
            )
        return extracted_text.strip()

    @staticmethod
    def extract_text_from_image(image_bytes: bytes) -> str:
        """Extract text from image using Pillow and Tesseract OCR."""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            # Convert to grayscale for better OCR contrast
            gray_image = image.convert("L")
            
            import pytesseract
            text = pytesseract.image_to_string(gray_image)
            return text.strip()
        except ImportError:
            logger.warning("pytesseract is not installed or available.")
            raise HTTPException(
                status_code=500,
                detail="OCR engine is not configured on the server. Please paste the announcement text directly."
            )
        except Exception as e:
            logger.error("Image OCR failed: %s", e)
            error_msg = str(e)
            if "tesseract is not installed or it's not in your PATH" in error_msg.lower():
                raise HTTPException(
                    status_code=400,
                    detail="Tesseract OCR executable is not available in system PATH. Please paste the announcement text or upload a digital PDF."
                )
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract text from image: {error_msg}"
            )

    @staticmethod
    async def process_upload(file: UploadFile) -> Tuple[str, str, str]:
        """
        Process uploaded file (PDF or Image) and extract text.
        Returns: (filename, source_type, extracted_text)
        """
        filename, ext = DocumentService.validate_file(file)
        content = await file.read()
        
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB."
            )
        
        if ext == ".pdf":
            source_type = "pdf"
            extracted_text = DocumentService.extract_text_from_pdf(content)
        else:
            source_type = "image"
            extracted_text = DocumentService.extract_text_from_image(content)
            if not extracted_text.strip():
                raise HTTPException(
                    status_code=400,
                    detail="No readable text found in the image. Please verify image quality or paste the text directly."
                )

        return filename, source_type, extracted_text

    @staticmethod
    def process_pasted_text(text: str) -> str:
        """Clean and normalize pasted academic announcement text."""
        cleaned = text.strip()
        if not cleaned or len(cleaned) < 5:
            raise HTTPException(
                status_code=400,
                detail="Announcement text is too short or empty. Please provide meaningful academic text."
            )
        return cleaned

document_service = DocumentService()
