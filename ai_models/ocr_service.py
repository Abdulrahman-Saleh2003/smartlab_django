

import requests
import json
import time
from PIL import Image
import io
from django.conf import settings
from ai_analysis.lab_analysis import lab_analyzer

class MedicalOCRService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def analyze_image(self, image: Image.Image, gender: str = None, previous_json: dict = None) -> dict:
        """يرسل الصورة إلى Colab + ngrok ثم يعمل التحليل الطبي"""
        
        # 1. تحضير الصورة
        img = image.convert("RGB")
        w, h = img.size
        if max(w, h) > 1536:
            scale = 1536 / max(w, h)
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        image_bytes = buffer.getvalue()

        # 2. استدعاء Colab عبر ngrok
        COLAB_URL = "https://stifling-probe-tarantula.ngrok-free.dev/analyze"   # غيرها إذا تغيرت

        try:
            response = requests.post(
                COLAB_URL,
                files={"image": ("image.jpg", image_bytes, "image/jpeg")},
                timeout=160
            )
            
            if response.status_code != 200:
                raise Exception(f"Colab returned {response.status_code}")

            data = response.json()
            ocr_result = data.get("ocr_result")

            if not ocr_result:
                raise Exception("لم يرجع Colab نتيجة OCR")

        except Exception as e:
            print(f"❌ خطأ في الاتصال بـ Colab: {e}")
            return {"error": f"فشل الاتصال بالـ OCR: {str(e)}"}

        # 3. التحليل الطبي المحلي (reference ranges + classification)
        final_result = lab_analyzer.process_ocr_result(
            ocr_data=ocr_result,
            gender=gender,
            previous_json=previous_json
        )

        return final_result


# Instance واحدة
ocr_service = MedicalOCRService()
print("✅ MedicalOCRService جاهز (يتصل بـ Colab + ngrok)")