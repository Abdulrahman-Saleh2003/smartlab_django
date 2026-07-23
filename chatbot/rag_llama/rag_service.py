

import os
from dotenv import load_dotenv
from llama_index.core import (
    VectorStoreIndex, SimpleDirectoryReader,
    StorageContext, load_index_from_storage,
    Settings, PromptTemplate
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openrouter import OpenRouter
from llama_index.embeddings.openai import OpenAIEmbedding
import json

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, "data")
STORAGE_DIR = os.path.join(BASE_DIR, "storage")


class LlamaRAGService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def initialize(self):
        if self._initialized:
            return

        self.llm = OpenRouter(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            model="deepseek/deepseek-chat",
            temperature=0.2,
            max_tokens=1024
        )
        self.embed_model = OpenAIEmbedding(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            api_base="https://openrouter.ai/api/v1",
            model="text-embedding-3-small"
        )
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)

        if os.path.exists(STORAGE_DIR) and os.listdir(STORAGE_DIR):
            storage_context = StorageContext.from_defaults(persist_dir=STORAGE_DIR)
            self.index = load_index_from_storage(storage_context)
        else:
            documents = SimpleDirectoryReader(DATA_DIR).load_data()
            self.index = VectorStoreIndex.from_documents(documents)
            self.index.storage_context.persist(persist_dir=STORAGE_DIR)

        self._initialized = True

#     def ask(self, question: str, lab_json: dict = None) -> str:
#         self.initialize()

#         if lab_json:
#             enriched_question = f"""
# سؤال المريض: {question}

# نتائج تحليله المخبري:
# {json.dumps(lab_json, ensure_ascii=False, indent=2)}
# """
#         else:
#             enriched_question = question

#         custom_prompt = PromptTemplate(
#             "أنت مساعد طبي ذكي...\n\n"
#             "سياق:\n{context_str}\n\n"
#             "السؤال: {query_str}"
#         )

#         query_engine = self.index.as_query_engine(
#             similarity_top_k=3,
#             text_qa_template=custom_prompt
#         )
#         response = query_engine.query(enriched_question)
#         return str(response)

    def ask(self, question: str, lab_json: dict = None) -> str:
        self.initialize()

        if lab_json:
            enriched_question = f"""
    سؤال المريض: {question}

    نتائج التحليل الحالي:
    {json.dumps(lab_json, ensure_ascii=False, indent=2)}
    """
        else:
            enriched_question = question

        # Prompt محسن للتنسيق الجميل
        # custom_prompt = PromptTemplate(
        #     "أنت طبيب ذكي ومحترف جداً.\n"
        #     "أجب بأسلوب **طبي احترافي ومنظم** باستخدام Markdown.\n"
        #     "استخدم جداول، عناوين، نقاط، وأيقونات عند الحاجة.\n\n"
        #     "السياق الطبي:\n{context_str}\n\n"
        #     "السؤال: {query_str}\n\n"
        #     "الإجابة يجب أن تكون مرتبة، واضحة، وسهلة القراءة."
        # )
        custom_prompt = PromptTemplate(
    "أنت طبيب ذكي ومحترف جداً.\n"
    "أجب بأسلوب طبي احترافي ومنظم باستخدام Markdown.\n\n"
    "السياق الطبي:\n{context_str}\n\n"
    "السؤال: {query_str}\n\n"
    "**قواعد تنسيق صارمة يجب اتباعها دائماً:**\n"
    "1. لا تكرر النجمتين ** داخل العناوين (#، ##، ###) — العنوان أصلاً يظهر بخط عريض تلقائياً.\n"
    "2. عند عرض تصنيفات أو نطاقات قيم (طبيعي/مرتفع/منخفض)، استخدم دائماً جدول Markdown "
    "(| عمود | عمود |) بدلاً من قوائم نقطية متداخلة.\n"
    "3. لا تستخدم نقاط فرعية متداخلة (لا نقطة تحت نقطة). إذا احتجت تفصيل تحت عنوان، "
    "استخدم عنوان فرعي (###) أو جدول، وليس قائمة نقطية بمستويين.\n"
    "4. لا تضع مسافات زائدة في نهاية الأسطر.\n"
    "5. اجعل كل قسم مفصولاً بعنوان واضح (##) بدون رموز تعبيرية زائدة داخل الجداول."
)

        query_engine = self.index.as_query_engine(
            similarity_top_k=5,
            text_qa_template=custom_prompt
        )
        response = query_engine.query(enriched_question)
        return str(response)




# ====================== دالة المقارنة (خارج الكلاس) ======================
def compare_two_reports(current_json: dict, previous_json: dict) -> str:
    """مقارنة بين تقريرين"""
    try:
        current_tests = {}
        for panel in current_json.get("panels", []):
            for test in panel.get("tests", []):
                name = test.get("test_name", "").strip().upper()
                if name:
                    current_tests[name] = {
                        "value": test.get("value"),
                        "status": test.get("status", "Normal"),
                        "status_ar": test.get("status_ar", "طبيعي")
                    }

        lines = ["📊 **تقرير المقارنة بين التحاليل:**\n"]
        found_any = False

        for panel in previous_json.get("panels", []):
            for prev in panel.get("tests", []):
                name = prev.get("test_name", "").strip().upper()
                if not name or name not in current_tests:
                    continue

                found_any = True
                curr = current_tests[name]

                prev_value = prev.get("value")
                curr_value = curr["value"]
                prev_status = prev.get("status")
                curr_status = curr["status"]

                if prev_value == curr_value:
                    change = "✅ مستقر"
                elif curr_status == "Normal" and prev_status != "Normal":
                    change = "🟢 **تحسن كبير**"
                elif curr_status in ["High", "Critical_High"]:
                    change = "🔴 **تدهور** (مرتفع)"
                elif curr_status in ["Low", "Critical_Low"]:
                    change = "🔴 **تدهور** (منخفض)"
                else:
                    change = "⚪ تغير"

                lines.append(f"• **{name}**: {prev_value} → **{curr_value}** | {change}")

        if not found_any:
            return "لم يتم العثور على تحاليل مشتركة."

        return "\n".join(lines)

    except Exception as e:
        return f"خطأ في المقارنة: {str(e)}"


# Instance
llama_rag_service = LlamaRAGService()