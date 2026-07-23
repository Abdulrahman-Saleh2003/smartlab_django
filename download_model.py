# from transformers import Qwen2VLForConditionalGeneration, AutoProcessor

# print("جاري التحميل... (~2.5 GB)")
# model = Qwen2VLForConditionalGeneration.from_pretrained("Qwen/Qwen2-VL-2B-Instruct")
# processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-2B-Instruct")
# print("تم التحميل!")
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from huggingface_hub import snapshot_download
import os

model_id = "Qwen/Qwen2-VL-2B-Instruct"

# تحديد مسار التحميل المحلي
local_dir = "./model_cache"

print(f"جاري التحميل إلى: {local_dir}")

# هذا السطر سيقوم بإظهار شريط تقدم (Progress Bar) تلقائياً أثناء التحميل
snapshot_download(repo_id=model_id, local_dir=local_dir)

print("تم التحميل بنجاح! جاري تهيئة النموذج...")

# تحميل النموذج من المسار المحلي
model = Qwen2VLForConditionalGeneration.from_pretrained(local_dir)
processor = AutoProcessor.from_pretrained(local_dir)

print("تمت التهيئة وجاهز للاستخدام.")