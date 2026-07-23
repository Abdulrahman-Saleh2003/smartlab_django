# # ai_models/ocr_service.py
# import torch
# import json
# import gc
# from PIL import Image
# from pathlib import Path
# from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
# from peft import PeftModel
# from json_repair import repair_json
# from django.conf import settings
# from ai_analysis.lab_analysis import LabReportAnalyzer

# PROMPT = """You are a highly accurate medical OCR system.
# Extract medical lab results from the image into JSON format.

# **CRITICAL RULES**:
# 1. Copy values, units, and reference ranges EXACTLY as seen in the image.
# 2. Pay close attention to decimal points (e.g., 4.52 vs 45.2).
# 3. If a field is empty or not visible, use null or an empty string "".
# 4. NEVER invent or guess numbers.

# **Output format**:
# {
#   "report_type": "...",
#   "panels": [
#     {
#       "panel_name": "...",
#       "tests": [
#         {"test_name": "...", "value": "...", "unit": "...", "reference_range": "...", "flag": "..."}
#       ]
#     }
#   ]
# }
# Return ONLY valid JSON."""


# class MedicalOCRService:
#     _instance = None  # Singleton

#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#             cls._instance._initialized = False
#         return cls._instance

#     def initialize(self):
#         if self._initialized:
#             return

#         print("⏳ جاري تحميل الموديل...")
        
#         # تحميل الـ base model بشكل أخف
#         base_model = Qwen2VLForConditionalGeneration.from_pretrained(
#             str(settings.BASE_MODEL_PATH),
#             torch_dtype  = torch.float32,
#             device_map   = "cpu",
#             low_cpu_mem_usage = True,  # ← مهم!
#         )

#         self.model = PeftModel.from_pretrained(
#             base_model,
#             str(settings.LORA_WEIGHTS_PATH),
#             is_trainable = False,
#         )
#         self.model.eval()

#         self.processor = AutoProcessor.from_pretrained(
#             str(settings.LORA_WEIGHTS_PATH)
#         )

#         self.device = "cpu"
#         self._initialized = True
#         print("✅ الموديل جاهز على cpu")
#     # def initialize(self):
#         if self._initialized:
#             return

#         print("⏳ جاري تحميل الموديل...")
#         device = "cuda" if torch.cuda.is_available() else "cpu"

#         # تحميل الـ base model
#         base_model = Qwen2VLForConditionalGeneration.from_pretrained(
#             str(settings.BASE_MODEL_PATH),
#             torch_dtype=torch.float16 if device == "cuda" else torch.float32,
#             device_map=device,
#         )

#         # إضافة الـ LoRA weights
#         self.model = PeftModel.from_pretrained(
#             base_model,
#             str(settings.LORA_WEIGHTS_PATH),
#             is_trainable=False,
#         )
#         self.model.eval()

#         self.processor = AutoProcessor.from_pretrained(
#             str(settings.LORA_WEIGHTS_PATH)
#         )

#         self.device = device
#         self._initialized = True
#         print(f"✅ الموديل جاهز على {device}")

#     def analyze_image(self, image: Image.Image) -> dict:
#         """تحليل صورة وإرجاع JSON"""
#         self.initialize()

#         # تصغير الصورة إذا كانت كبيرة
#         w, h = image.size
#         if max(w, h) > 1536:
#             scale = 1536 / max(w, h)
#             image = image.resize(
#                 (int(w * scale), int(h * scale)), Image.LANCZOS
#             )

#         messages = [{
#             "role": "user",
#             "content": [
#                 {"type": "image", "image": image},
#                 {"type": "text", "text": PROMPT},
#             ],
#         }]

#         text = self.processor.apply_chat_template(
#             messages, tokenize=False, add_generation_prompt=True
#         )

#         inputs = self.processor(
#             text=text,
#             images=[image],
#             return_tensors="pt",
#             padding=True,
#         )
#         inputs = {
#             k: v.to(self.device)
#             for k, v in inputs.items()
#             if isinstance(v, torch.Tensor)
#         }

#         with torch.no_grad():
#             output_ids = self.model.generate(
#                 **inputs,
#                 max_new_tokens=2048,
#                 do_sample=False,
#                 temperature=0.0,
#                 repetition_penalty=1.05,
#                 pad_token_id=self.processor.tokenizer.eos_token_id,
#             )

#         input_len = inputs["input_ids"].shape[1]
#         result = self.processor.tokenizer.decode(
#             output_ids[0][input_len:], skip_special_tokens=True
#         ).strip()

#         del inputs, output_ids
#         if self.device == "cuda":
#             torch.cuda.empty_cache()
#         gc.collect()

#         try:
#             return json.loads(result)
#         except Exception:
#             return repair_json(result, return_objects=True)
#     def analyze_image(self, image: Image.Image) -> dict:
#         # الـ OCR الحالي
#         ocr_result = ...  # الكود الحالي

#         # ←←← التحليل الجديد
#         analyzer = LabReportAnalyzer()
#         final_result = analyzer.process_ocr_result(ocr_result, gender=None, previous_json=None)

#         return final_result

# # instance واحد للمشروع كله
# ocr_service = MedicalOCRService()

