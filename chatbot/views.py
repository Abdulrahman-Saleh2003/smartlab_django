from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .rag_llama.rag_service import llama_rag_service
from .rag_voiceflow.voiceflow_service import voiceflow_rag_service



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .rag_llama.rag_service import llama_rag_service,compare_two_reports
from .rag_voiceflow.voiceflow_service import voiceflow_rag_service
import markdown  # ← ضيف هاد الاستيراد فوق

from .markdown_utils import markdown_to_html   # ← ضيف هاد فوق الملف كله



@api_view(['POST'])
@permission_classes([AllowAny])
def full_medical_analysis(request):
    question = request.data.get('question', '').strip()
    lab_json = request.data.get('lab_json')           # التقرير الحالي
    previous_json = request.data.get('previous_json') # التقرير السابق (اختياري)

    if not question:
        return Response({"error": "يجب إرسال سؤال"}, status=400)

    try:
        # فقط Llama (بدون Voiceflow)
        llama_answer = llama_rag_service.ask(question, lab_json)

        # مقارنة إذا وجد تقرير سابق
        comparison = ""
        if lab_json and previous_json:
            comparison = compare_two_reports(lab_json, previous_json)
            comparison = f"\n\n{comparison}\n\n"

        final_answer = f"""
**تحليل بيانات المريض (بواسطة Llama):**
{llama_answer}

{comparison}

**الخلاصة:**
هذا تحليل مساعد مبني على البيانات المخبرية.  
**يُفضل استشارة الطبيب فوراً** للتقييم السريري والتشخيص النهائي.
"""

        return Response({
            "success": True,
            "answer": final_answer,
            "comparison": comparison.strip(),
            "sources": {
                "llama": llama_answer
            }
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def chat_llama(request):
#     """RAG اليدوي باستخدام llama_index"""
#     question = request.data.get('question', '').strip()
#     lab_json = request.data.get('lab_json', None)  # اختياري

#     if not question:
#         return Response({"error": "يجب إرسال سؤال"}, status=400)

#     try:
#         # answer = llama_rag_service.ask(question, lab_json)
#         # return Response({"success": True, "answer": answer})
#         answer = llama_rag_service.ask(question, lab_json)

#         # تحويل الماركداون لـ HTML جاهز للعرض
#         answer_html = markdown.markdown(
#             answer,
#             extensions=['tables', 'fenced_code', 'nl2br']
#         )

#         return Response({
#             "success": True,
#             "answer": answer,          # النص الخام (لو حبيت تستخدمه لشي تاني)
#             "answer_html": answer_html  # ← هاد يلي تعرضه بالواجهة
#         })
    
    
    
    
#     except Exception as e:
#         return Response({"error": str(e)}, status=500)





    
@api_view(['POST'])
@permission_classes([AllowAny])
def chat_llama(request):
    """RAG اليدوي باستخدام llama_index"""
    question = request.data.get('question', '').strip()
    lab_json = request.data.get('lab_json', None)  # اختياري

    if not question:
        return Response({"error": "يجب إرسال سؤال"}, status=400)

    try:
        answer = llama_rag_service.ask(question, lab_json)
        return Response({
            "success": True,
            "answer": answer,
            "answer_html": markdown_to_html(answer)   # ← الإضافة الوحيدة هون
        })
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def chat_voiceflow(request):
    question = request.data.get('question', '').strip()
    lab_json = request.data.get('lab_json', None)

    if not question:
        return Response({"error": "يجب إرسال سؤال"}, status=400)

    try:
        answer = voiceflow_rag_service.ask(question, lab_json)
        
        # إذا رجع None، نعطي رسالة واضحة
        if not answer:
            answer = "لم يتم الحصول على رد من Voiceflow. تأكد من إعدادات الخدمة."

        return Response({
            "success": True,
            "answer": answer
        })

    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=500)