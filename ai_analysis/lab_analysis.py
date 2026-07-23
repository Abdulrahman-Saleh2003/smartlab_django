import re
import json
import statistics
from pathlib import Path
from django.conf import settings
from rapidfuzz import process, fuzz

# ====================== إعدادات عامة ======================
NUM = r"[-+]?\d[\d,]*\.?\d*"

NOISE_WORDS = {
    "SERUM", "BLOOD", "PLASMA", "URINE", "TOTAL", "LEVEL", "LEVELS", "COUNT", 
    "TEST", "PANEL", "VALUE", "RATIO", "CONCENTRATION", "RESULT", "FINDING", "REFERENCE"
}

COMMON_LAB_ACRONYMS = {
    "RBC": "RED CELL", "WBC": "WHITE CELL", "HGB": "HEMOGLOBIN", "HB": "HEMOGLOBIN",
    "HCT": "HEMATOCRIT", "PLT": "PLATELET", "RDW": "RED CELL DISTRIBUTION WIDTH",
    "ESR": "ERYTHROCYTE SEDIMENTATION RATE", "ALT": "ALANINE AMINOTRANSFERASE",
    "AST": "ASPARTATE AMINOTRANSFERASE", "ALP": "ALKALINE PHOSPHATASE",
    "BUN": "UREA NITROGEN", "CR": "CREATININE", "NA": "SODIUM", "K": "POTASSIUM",
    "CL": "CHLORIDE", "CA": "CALCIUM", "TSH": "THYROID STIMULATING HORMONE",
    "T3": "TRIIODOTHYRONINE", "T4": "THYROXINE", "FT3": "FREE T3", "FT4": "FREE T4",
    "HDL": "HIGH DENSITY LIPOPROTEIN", "LDL": "LOW DENSITY LIPOPROTEIN", "TG": "TRIGLYCERIDES",
    "HBA1C": "HEMOGLOBIN A1C", "A1C": "HEMOGLOBIN A1C", "PT": "PROTHROMBIN TIME",
    "PTT": "PARTIAL THROMBOPLASTIN TIME", "INR": "INTERNATIONAL NORMALIZED RATIO",
    "CRP": "C REACTIVE PROTEIN", "PSA": "PROSTATE SPECIFIC ANTIGEN", "BILI": "BILIRUBIN",
    "TBIL": "TOTAL BILIRUBIN", "DBIL": "DIRECT BILIRUBIN", "ALB": "ALBUMIN",
    "TP": "TOTAL PROTEIN", "GGT": "GAMMA GLUTAMYL TRANSFERASE", "LDH": "LACTATE DEHYDROGENASE",
    "CK": "CREATINE KINASE", "CKMB": "CREATINE KINASE MB", "TROP": "TROPONIN",
    "FER": "FERRITIN", "FOL": "FOLATE", "B12": "VITAMIN B12", "VITD": "VITAMIN D",
    "UA": "URIC ACID", "GLU": "GLUCOSE", "FBG": "FASTING BLOOD GLUCOSE",
    "PPBG": "POSTPRANDIAL BLOOD GLUCOSE", "MPV": "MEAN PLATELET VOLUME",
    "PDW": "PLATELET DISTRIBUTION WIDTH", "NEUT": "NEUTROPHILS", "LYMPH": "LYMPHOCYTES",
    "MONO": "MONOCYTES", "EOS": "EOSINOPHILS", "BASO": "BASOPHILS", "RETIC": "RETICULOCYTE",
}

def normalize_name(name):
    name = str(name).upper().strip()
    name = re.sub(r"[^A-Z0-9%<> ]", " ", name)
    tokens = [t for t in name.split() if t not in NOISE_WORDS]
    tokens = [COMMON_LAB_ACRONYMS.get(t, t) for t in tokens]
    name = " ".join(tokens)
    return re.sub(r"\s+", " ", name).strip()


def normalize_category(cat):
    c = str(cat).lower()
    if any(x in c for x in ["female", "women"]):
        return "female"
    if any(x in c for x in ["male", "men"]):
        return "male"
    return "general"


def parse_range_string(range_str):
    if not range_str or not isinstance(range_str, str):
        return []
    
    range_str = range_str.strip()
    parsed = []
    
    # أنماط متعددة
    patterns = [
        r"(\d[\d.,]*)\s*[-–—]\s*(\d[\d.,]*)",
        r"(\d[\d.,]*)\s*to\s*(\d[\d.,]*)",
        r"(\d[\d.,]*)\s*-\s*(\d[\d.,]*)",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, range_str)
        for low_str, high_str in matches:
            try:
                low = float(low_str.replace(",", ""))
                high = float(high_str.replace(",", ""))
                parsed.append({"type": "range", "low": low, "high": high})
            except:
                continue
    
    # أقل من / أكبر من
    m_lt = re.search(r"<\\s*(\\d[\\d.,]*)", range_str)
    m_gt = re.search(r">\\s*(\\d[\\d.,]*)", range_str)
    if m_lt:
        parsed.append({"type": "lt", "high": float(m_lt.group(1).replace(",", ""))})
    if m_gt:
        parsed.append({"type": "gt", "low": float(m_gt.group(1).replace(",", ""))})
    
    # استخراج أول رقمين إذا لم ينجح السابق
    if not parsed:
        numbers = re.findall(r"\d[\d.,]*", range_str)
        if len(numbers) >= 2:
            try:
                low = float(numbers[0].replace(",", ""))
                high = float(numbers[1].replace(",", ""))
                parsed.append({"type": "range", "low": low, "high": high})
            except:
                pass
    
    return parsed


def distance_to_normal(value, parsed_ranges):
    if not parsed_ranges:
        return None
    best = None
    for r in parsed_ranges:
        if r["type"] == "range":
            d = value - r["low"] if value < r["low"] else (value - r["high"] if value > r["high"] else 0)
        elif r["type"] == "lt":
            d = value - r["high"] if value > r["high"] else 0
        elif r["type"] == "gt":
            d = value - r["low"] if value < r["low"] else 0
        else:
            continue
        if best is None or abs(d) < abs(best):
            best = d
    return best


def classify_severity(value_str, parsed_ranges, critical_low=None, critical_high=None):
    try:
        value = float(str(value_str).strip().replace(",", ""))
    except (ValueError, TypeError):
        return None, "غير قابل للتصنيف", None
    
    if not parsed_ranges:
        return None, "لا يوجد رينج", None
    
    dist = distance_to_normal(value, parsed_ranges)
    if dist is None:
        return None, "غير قابل للتصنيف", None
    
    if abs(dist) < 0.001:
        return "Normal", "طبيعي", 0
    if dist > 0:
        if critical_high is not None and value >= critical_high:
            return "Critical_High", "خطر / حرج (مرتفع)", dist
        return "High", "غير طبيعي (مرتفع)", dist
    else:
        if critical_low is not None and value <= critical_low:
            return "Critical_Low", "خطر / حرج (منخفض)", dist
        return "Low", "غير طبيعي (منخفض)", dist


def find_test_nodes(data):
    found = []
    NAME_KEYS = ["test_name", "name", "test", "analyte", "parameter", "item"]
    VALUE_KEYS = ["value", "result", "measured_value", "reading", "test_value"]
    
    def walk(node):
        if isinstance(node, dict):
            keys_lower = {str(k).lower().strip(): k for k in node.keys()}
            name_key = next((keys_lower.get(c) for c in NAME_KEYS if c in keys_lower), None)
            value_key = next((keys_lower.get(c) for c in VALUE_KEYS if c in keys_lower), None)
            if name_key and value_key:
                found.append({
                    "node": node,
                    "name_key": name_key,
                    "value_key": value_key,
                    "range_key": next((keys_lower.get(c) for c in ["reference_range", "normal_range", "range", "ref_range"] if c in keys_lower), None)
                })
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)
    walk(data)
    return found


def build_fuzzy_index(reference_db):
    entries = []
    for main_key, info in reference_db.items():
        entries.append((normalize_name(main_key), main_key))
        for alias in info.get("aliases", []):
            entries.append((normalize_name(alias), main_key))
    return entries


def fuzzy_find(test_name, reference_db, fuzzy_index, score_cutoff=82):
    norm = normalize_name(test_name)
    if not norm or len(norm) < 2:
        return None, None, 0
    choices = [e[0] for e in fuzzy_index]
    match = process.extractOne(norm, choices, scorer=fuzz.WRatio, score_cutoff=score_cutoff)
    if not match:
        return None, None, 0
    _, score, idx = match
    return reference_db[fuzzy_index[idx][1]], fuzzy_index[idx][1], score


def process_report(data, reference_db, fuzzy_index, gender=None):
    test_nodes = find_test_nodes(data)
    for t in test_nodes:
        node = t["node"]
        test_name = str(node[t["name_key"]])
        value = node.get(t["value_key"])
        ocr_range = str(node.get(t.get("range_key"), "")).strip() if t.get("range_key") else ""

        entry, matched_key, score = fuzzy_find(test_name, reference_db, fuzzy_index)

        range_str = ocr_range
        if entry and not range_str:
            ranges = entry.get("ranges", {})
            range_str = (ranges.get(gender) or ranges.get("general") or next(iter(ranges.values()), ""))

        parsed = parse_range_string(range_str)
        status, status_ar, dist = classify_severity(value, parsed)

        node.update({
            "reference_range": range_str,
            "reference_range_source": "OCR" if ocr_range else "reference_db",
            "matched_reference_test": matched_key,
            "match_confidence": round(score, 1) if entry else None,
            "status": status,
            "status_ar": status_ar,
            "distance_from_normal": dist
        })
    return test_nodes


class LabReportAnalyzer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.reference_db = self._load_reference_db()
            self.fuzzy_index = build_fuzzy_index(self.reference_db)
            self._initialized = True

    def _load_reference_db(self):
        path = Path(settings.BASE_DIR) / "ai_analysis/data/reference_ranges_master.json"
        if not path.exists():
            raise FileNotFoundError(f"الملف غير موجود: {path}")
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def process_ocr_result(self, ocr_data: dict, gender=None, previous_json=None):
        current_nodes = process_report(ocr_data, self.reference_db, self.fuzzy_index, gender)
        result = {"current_report": ocr_data}
        if previous_json:
            result["previous_report"] = previous_json
        return result


lab_analyzer = LabReportAnalyzer()
print("✅ Lab Analysis Service Loaded Successfully")