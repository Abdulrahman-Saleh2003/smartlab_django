import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


class VoiceflowRAGService:
  def ask(self, question: str, lab_json: dict = None) -> str:
    api_key = os.getenv("VOICEFLOW_API_KEY")
    
    if not api_key:
        return "❌ مفتاح VOICEFLOW_API_KEY غير موجود"

    if lab_json:
        enriched_question = f"سؤال: {question}\n\nنتائج التحليل:\n{json.dumps(lab_json, ensure_ascii=False, indent=2)}"
    else:
        enriched_question = question

    url = "https://general-runtime.voiceflow.com/knowledge-base/query"
    headers = {
        "Authorization": api_key,
        "accept": "application/json",
        "content-type": "application/json"
    }
    payload = {"question": enriched_question, "chunkLimit": 5}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # استخراج الإجابة النظيفة
            output = data.get("output")
            if output:
                return output
            
            # إذا لم يكن output، نحاول استخراج من الـ chunks
            chunks = data.get("chunks", [])
            if chunks:
                texts = [chunk.get("content", "") for chunk in chunks if chunk.get("content")]
                return "\n\n".join(texts[:3])  # أول 3 chunks
            
            return "لم يتم العثور على إجابة مناسبة."

        else:
            return f"خطأ Voiceflow: {response.status_code}"

    except Exception as e:
        return f"خطأ في الاتصال: {str(e)}"
#     def ask(self, question: str, lab_json: dict = None) -> str:
#         api_key = os.getenv("VOICEFLOW_API_KEY")

#         # دمج الـ JSON مع السؤال إذا موجود
#         if lab_json:
#             enriched_question = f"""
# سؤال المريض: {question}

# نتائج تحليله المخبري:
# {json.dumps(lab_json, ensure_ascii=False, indent=2)}
# """
#         else:
#             enriched_question = question

#         url = "https://general-runtime.voiceflow.com/knowledge-base/query"
        
#         headers = {
#             "Authorization": api_key,
#             "accept": "application/json",
#             "content-type": "application/json"
#         }
#         payload = {"question": enriched_question, "chunkLimit": 3}

#         try:
#             response = requests.post(url, json=payload, headers=headers, timeout=30)
#             if response.status_code == 200:
#                 data = response.json()
#                 return data.get("output", "لم يتم العثور على إجابة في المستندات.")
#             else:
#                 return f"خطأ من السيرفر: {response.status_code}"
#         except Exception as e:
#             return f"حدث خطأ: {str(e)}"
    

voiceflow_rag_service = VoiceflowRAGService()