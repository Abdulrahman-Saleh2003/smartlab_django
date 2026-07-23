import json
import uuid
import threading
import time
from PIL import Image
import io
from django.core.cache import cache
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

# استيراد الخدمات
from ai_models.ocr_service import ocr_service


@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_report(request):
    image_file = request.FILES.get('image')
    gender = request.data.get('gender')                    # "male" أو "female"
    previous_json_str = request.data.get('previous_json')  # JSON string اختياري

    if not image_file:
        return Response({"error": "يجب رفع صورة التحليل"}, status=400)

    try:
        # فتح وتحضير الصورة
        img = Image.open(image_file).convert("RGB")

        # تحويل previous_json من string إلى dict
        previous_json = None
        if previous_json_str:
            try:
                previous_json = json.loads(previous_json_str)
            except json.JSONDecodeError:
                previous_json = None

        job_id = str(uuid.uuid4())
        cache.set(f"ocr_{job_id}", {"status": "processing"}, timeout=600)

        def run_ocr():
            try:
                # ←←← هنا يتم الـ OCR + التحليل الذكي معاً
                result = ocr_service.analyze_image(
                    image=img,
                    gender=gender,
                    previous_json=previous_json
                )

                cache.set(f"ocr_{job_id}", {
                    "status": "done",
                    "result": result
                }, timeout=600)

            except Exception as e:
                cache.set(f"ocr_{job_id}", {
                    "status": "error",
                    "error": str(e)
                }, timeout=600)

        # تشغيل في Thread منفصل
        threading.Thread(target=run_ocr, daemon=True).start()

        return Response({
            "success": True,
            "job_id": job_id,
            "message": "جاري تحليل التقرير الطبي..."
        }, status=status.HTTP_202_ACCEPTED)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_result(request, job_id):
    result = cache.get(f"ocr_{job_id}")
    if not result:
        return Response({"error": "job_id غير موجود أو انتهت صلاحيته"}, status=404)
    
    return Response(result)


@api_view(['POST'])
@permission_classes([AllowAny])
def ask_question(request):
    question = request.data.get('question', '').strip()
    lab_json = request.data.get('lab_json', None)

    if not question:
        return Response({"error": "يجب إرسال سؤال"}, status=400)

    try:
        llama_answer = llama_rag_service.ask(question, lab_json)
        voiceflow_answer = voiceflow_rag_service.ask(question, lab_json)

        final_answer = f"""
تحليل بيانات المريض:
{llama_answer}

المراجع الطبية:
{voiceflow_answer}

الخلاصة:
اعتماداً على بيانات المريض والمراجع الطبية، يرجى اعتبار هذا التحليل معلومات مساعدة وليس تشخيصاً نهائياً.
"""

        return Response({
            "success": True,
            "answer": final_answer,
            "sources": {
                "llama": llama_answer,
                "voiceflow": voiceflow_answer
            }
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)