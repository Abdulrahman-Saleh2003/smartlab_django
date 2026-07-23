# # lab_reports/views.py
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# from rest_framework import status
# from django.conf import settings
# from django.core.cache import cache
# from PIL import Image
# import requests
# import threading
# import uuid


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def analyze_report(request):

#     image_file = request.FILES.get('image')
#     if not image_file:
#         return Response({"error": "يجب رفع صورة التحليل"}, status=400)

#     image_bytes = image_file.read()
#     image_name  = image_file.name
#     image_type  = image_file.content_type

#     job_id = str(uuid.uuid4())
#     cache.set(f"ocr_{job_id}", {"status": "processing"}, timeout=600)

#     # def run_ocr():
#         try:
#             response = requests.post(
#                 f"{settings.COLAB_API_URL}/analyze",
#                 files={"image": (image_name, image_bytes, image_type)},
#                 timeout=300
#             )
#             data = response.json()
#             cache.set(f"ocr_{job_id}", {
#                 "status": "done",
#                 "ocr_result": data.get("ocr_result")
#             }, timeout=600)
#         except Exception as e:
#             cache.set(f"ocr_{job_id}", {
#                 "status": "error",
#                 "error": str(e)
#             }, timeout=600)
#     def run_ocr():
#         for attempt in range(3):
#             try:
#                 response = requests.post(
#                     f"{settings.COLAB_API_URL}/analyze",
#                     files={"image": (image_name, image_bytes, image_type)},
#                     timeout=(10, 300)  # (connect_timeout, read_timeout)
#                 )
#                 data = response.json()
#                 cache.set(f"ocr_{job_id}", {
#                     "status": "done",
#                     "ocr_result": data.get("ocr_result")
#                 }, timeout=600)
#                 return
#             except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
#                 if attempt == 2:
#                     cache.set(f"ocr_{job_id}", {
#                         "status": "error",
#                         "error": f"فشل الاتصال بعد {attempt+1} محاولات: {str(e)}"
#                     }, timeout=600)
#                 else:
#                     time.sleep(3)  # انتظر شوي قبل إعادة المحاولة
#             except Exception as e:
#                 cache.set(f"ocr_{job_id}", {
#                     "status": "error",
#                     "error": str(e)
#                 }, timeout=600)
#                 return
#         threading.Thread(target=run_ocr).start()

#         return Response({
#             "success": True,
#             "job_id": job_id,
#             "message": "جاري التحليل، استخدم job_id للاستعلام عن النتيجة"
#         }, status=status.HTTP_202_ACCEPTED)


# @api_view(['GET'])
# @permission_classes([AllowAny])
# def check_result(request, job_id):
#     result = cache.get(f"ocr_{job_id}")
#     if not result:
#         return Response({"error": "job_id غير موجود أو انتهت صلاحيته"}, status=404)
#     return Response(result)




# lab_reports/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.core.cache import cache
import requests
import threading
import time
import uuid
from PIL import Image
import io
# استورد الخدمتين هون (عدّل المسار حسب مكانهم الفعلي بمشروعك)
# from .services import llama_rag_service, voiceflow_rag_service


@api_view(['POST'])
@permission_classes([AllowAny])
def analyze_report(request):

    image_file = request.FILES.get('image')
    
    

    if not image_file:
        return Response({"error": "يجب رفع صورة التحليل"}, status=400)
    img = Image.open(image_file)
    img = img.convert("RGB")
    image_bytes = image_file.read()
    image_name  = image_file.name
    image_type  = image_file.content_type
    max_size = 1536
    if max(img.size) > max_size:
        scale = max_size / max(img.size)
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    image_bytes = buffer.getvalue()
    image_name = "compressed_" + image_file.name
    image_type = "image/jpeg"

    job_id = str(uuid.uuid4())
    cache.set(f"ocr_{job_id}", {"status": "processing"}, timeout=600)

    def run_ocr():
        for attempt in range(3):
            try:
                response = requests.post(
                    f"{settings.COLAB_API_URL}/analyze",
                    files={"image": (image_name, image_bytes, image_type)},
                    timeout=(10, 300)  # (connect_timeout, read_timeout)
                )
                data = response.json()
                cache.set(f"ocr_{job_id}", {
                    "status": "done",
                    "ocr_result": data.get("ocr_result")
                }, timeout=600)
                return
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                if attempt == 2:
                    cache.set(f"ocr_{job_id}", {
                        "status": "error",
                        "error": f"فشل الاتصال بعد {attempt + 1} محاولات: {str(e)}"
                    }, timeout=600)
                else:
                    time.sleep(3)
            except Exception as e:
                cache.set(f"ocr_{job_id}", {
                    "status": "error",
                    "error": str(e)
                }, timeout=600)
                return

    # ⚠️ هاد لازم يكون خارج run_ocr، على مستوى analyze_report
    threading.Thread(target=run_ocr).start()

    return Response({
        "success": True,
        "job_id": job_id,
        "message": "جاري التحليل، استخدم job_id للاستعلام عن النتيجة"
    }, status=status.HTTP_202_ACCEPTED)


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
        return Response(
            {"error": "يجب إرسال سؤال"},
            status=400
        )

    try:
        # 1- تحليل بيانات المريض
        llama_answer = llama_rag_service.ask(question, lab_json)

        # 2- جلب المعرفة الطبية من الملفات
        voiceflow_answer = voiceflow_rag_service.ask(question, lab_json)

        # 3- دمج النتيجتين
        final_answer = f"""
تحليل بيانات المريض:

{llama_answer}


المراجع الطبية:

{voiceflow_answer}


الخلاصة:
اعتماداً على بيانات المريض والمراجع الطبية،
يرجى اعتبار هذا التحليل معلومات مساعدة وليس تشخيصاً نهائياً.
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
        return Response({
            "error": str(e)
        }, status=500)










#     question = request.data.get('question', '').strip()
#     lab_json = request.data.get('lab_json', None)

#     if not question:
#         return Response(
#             {"error": "يجب إرسال سؤال"},
#             status=400
#         )


#     try:

#         # 1- تحليل بيانات المريض
#         llama_answer = llama_rag_service.ask(
#             question,
#             lab_json
#         )


#         # 2- جلب المعرفة الطبية من الملفات
#         voiceflow_answer = voiceflow_rag_service.ask(
#             question,
#             lab_json
#         )


#         # 3- دمج النتيجتين
#         final_answer = f"""
# تحليل بيانات المريض:

# {llama_answer}


# المراجع الطبية:

# {voiceflow_answer}


# الخلاصة:
# اعتماداً على بيانات المريض والمراجع الطبية،
# يرجى اعتبار هذا التحليل معلومات مساعدة وليس تشخيصاً نهائياً.
# """


#         return Response({
#             "success": True,
#             "answer": final_answer,
#             "sources": {
#                 "llama": llama_answer,
#                 "voiceflow": voiceflow_answer
#             }
#         })


#     except Exception as e:

#         return Response({
#             "error": str(e)
#         }, status=500)
