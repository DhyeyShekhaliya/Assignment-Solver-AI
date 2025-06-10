from .utils.mongo_logger import log_event
from .utils.gemini import ask_gemini
from .utils.supabase_client import upload_to_supabase
from .utils.doc_generator import generate_answer_doc
import uuid
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from docx import Document
import tempfile
import os

class UploadDocView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        # Save uploaded DOCX to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp:
            for chunk in uploaded_file.chunks():
                temp.write(chunk)
            temp_path = temp.name

        try:
            # Parse text from uploaded DOC
            doc = Document(temp_path)
            question_text = "\n".join([para.text for para in doc.paragraphs])

            # Call Gemini for AI-generated answer
            answer = ask_gemini(f"Answer the following college assignment question:\n{question_text}")
            log_event("gemini_response", {"answer_preview": answer[:200]})

            # Generate answered DOCX (renamed to original filename)
            original_name = os.path.splitext(uploaded_file.name)[0]
            final_filename = f"{original_name}-answered.docx"
            output_path = f"/tmp/{final_filename}"
            generate_answer_doc(question_text, answer, output_path)

            # Upload to Supabase
            try:
                download_url = upload_to_supabase(output_path, final_filename)
            except Exception as e:
                return Response({"error": str(e)}, status=500)

            # Log completion
            log_event("upload_complete", {
                "original_filename": uploaded_file.name,
                "doc_preview": question_text[:300],
                "gemini_preview": answer[:300],
                "download_url": download_url
            })

            # Cleanup
            os.remove(temp_path)
            os.remove(output_path)

            return Response({
                "message": "File processed and answer generated.",
                "filename": final_filename,
                "download_url": download_url
            }, status=200)

        except Exception as e:
            log_event("processing_error", {"error": str(e)})
            print(f"[DEBUG] Processing Exception: {str(e)}")  
            return Response({"error": "Processing failed."}, status=500)


