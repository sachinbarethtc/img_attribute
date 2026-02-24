# import json
# import logging
# from typing import Dict, Any, Optional
# from groq import Groq
# from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception
# from app.config import settings
# from app.utils import encode_image
# from app.schemas import FashionAttributeResponse

# logger = logging.getLogger(__name__)

# SYSTEM_PROMPT = """You are a professional fashion product attribute extraction engine.

# Return ONLY valid JSON.
# No explanation.
# No markdown.
# No extra text.
# If attribute not visible return null.
# Use only allowed values."""

# USER_PROMPT_TEMPLATE = """Analyze the garment in the image and extract:

# Core Attributes:
# - item_count (integer: count of distinct fashion items visible)
# - is_garment_visible (boolean: true if fully visible/unfolded, false if folded/obscured/blurry)
# - quality_issue (string: describe issue if not visible, else null)
# - category
# - color
# - pattern
# - sleeve_length
# - neckline
# - fit
# - gender

# Additional Attributes:
# - garment_length
# - material_type
# - texture
# - closure_type
# - collar_type
# - pocket_type
# - style
# - occasion
# - season

# Allowed Values:

# category:
# [t-shirt, shirt, kurta, dress, saree, top, blouse, jacket, coat, hoodie, sweater, jeans, trousers, shorts, skirt, ethnic_set, jumpsuit, other]

# color:
# [black, white, red, blue, green, yellow, pink, purple, orange, brown, grey, beige, maroon, navy, multi]

# pattern:
# [solid, striped, checked, floral, printed, embroidered, self_design, graphic, abstract, other]

# sleeve_length:
# [sleeveless, short, three_quarter, full, null]

# neckline:
# [round, v_neck, square, sweetheart, halter, boat, collar, mandarin, high_neck, off_shoulder, null]

# fit:
# [slim, regular, relaxed, oversized, bodycon, straight, null]

# gender:
# [male, female, unisex, null]

# garment_length:
# [cropped, waist_length, hip_length, knee_length, midi, ankle_length, floor_length, null]

# material_type:
# [cotton, polyester, silk, chiffon, georgette, wool, denim, linen, rayon, leather, knit, other, null]

# texture:
# [smooth, ribbed, knitted, sheer, textured, distressed, null]

# closure_type:
# [buttons, zipper, hook, drawstring, elastic, none, null]

# collar_type:
# [spread, mandarin, peter_pan, shawl, hooded, none, null]

# pocket_type:
# [side_pockets, patch_pockets, welt_pockets, cargo_pockets, none, null]

# style:
# [casual, formal, ethnic, western, festive, sporty, party, streetwear]

# occasion:
# [casual, office, festive, wedding, party, vacation, sports]

# season:
# [summer, winter, monsoon, spring, autumn, all_season]

# Return output in this strict JSON structure:

# {
#   "item_count": 0,
#   "is_garment_visible": true,
#   "quality_issue": null,
#   "category": "",
#   "color": "",
#   "pattern": "",
#   "sleeve_length": "",
#   "neckline": "",
#   "fit": "",
#   "gender": "",
#   "garment_length": "",
#   "material_type": "",
#   "texture": "",
#   "closure_type": "",
#   "collar_type": "",
#   "pocket_type": "",
#   "style": [],
#   "occasion": [],
#   "season": []
# }"""

# class GroqService:
#     def __init__(self):
#         print(f"DEBUG: Initializing GroqService with key length: {len(settings.GROQ_API_KEY) if settings.GROQ_API_KEY else 0}")
#         print(f"DEBUG: Using model: {settings.GROQ_MODEL}")
#         try:
#             self.client = Groq(api_key=settings.GROQ_API_KEY)
#             self.model = settings.GROQ_MODEL
#             print("DEBUG: Groq client initialized successfully")
#         except Exception as e:
#             print(f"DEBUG: Failed to initialize Groq client: {e}")
#             raise e

#     @retry(
#         stop=stop_after_attempt(settings.MAX_RETRIES),
#         wait=wait_fixed(2),
#         retry=retry_if_exception(lambda e: not isinstance(e, ValueError))
#     )
#     def analyze_image(self, image_bytes: bytes) -> Dict[str, Any]:
#         """
#         Analyzes an image using Groq Vision API and extracts fashion attributes.
#         """
#         try:
#             base64_image = encode_image(image_bytes)
            
#             completion = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {
#                         "role": "system",
#                         "content": SYSTEM_PROMPT
#                     },
#                     {
#                         "role": "user",
#                         "content": [
#                             {
#                                 "type": "text",
#                                 "text": USER_PROMPT_TEMPLATE
#                             },
#                             {
#                                 "type": "image_url",
#                                 "image_url": {
#                                     "url": f"data:image/jpeg;base64,{base64_image}"
#                                 }
#                             }
#                         ]
#                     }
#                 ],
#                 temperature=0.1,
#                 max_tokens=1024,
#                 top_p=1,
#                 stream=False,
#                 stop=None,
#             )

#             content = completion.choices[0].message.content.strip()
            
#             # Basic cleanup: remove markdown code blocks if present
#             if content.startswith("```json"):
#                 content = content[7:]
#             if content.startswith("```"):
#                 content = content[3:]
#             if content.endswith("```"):
#                 content = content[:-3]
            
#             content = content.strip()
#             print(f"DEBUG: RAW CONTENT: {content}")

#             # Parse JSON - this will raise JSONDecodeError if invalid, triggering retry
#             data = json.loads(content)
            
#             # Validate against schema
#             validated_data = FashionAttributeResponse(**data)
            
#             # Check for multiple garments
#             if validated_data.item_count and validated_data.item_count > 1:
#                 return {
#                     "item_count": validated_data.item_count,
#                     "message": f"Multiple fashion items ({validated_data.item_count}) detected. Please upload an image with a single garment.",
#                     "category": None,
#                     "color": None
#                 }
            
#             # Check for image quality
#             if not validated_data.is_garment_visible:
#                  return {
#                     "item_count": validated_data.item_count,
#                     "is_garment_visible": False,
#                     "quality_issue": validated_data.quality_issue,
#                     "message": f"Image quality issue: {validated_data.quality_issue or 'Garment not clearly visible'}. Please upload a clear, unfolded image of the garment.",
#                     "category": None,
#                     "color": None
#                 }

#             return validated_data.model_dump()

#         except Exception as e:
#             logger.error(f"Error processing image with Groq: {str(e)}", exc_info=True)
#             if hasattr(e, 'response'):
#                  logger.error(f"Groq API Response: {e.response.text}")
#             raise e



import json
import logging
import re
from typing import Dict, Any, Optional, List
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception
from app.config import settings
from app.utils import encode_image
from app.schemas import FashionAttributeResponse, DivisionDetection, DepartmentDetection

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Department Code Context
# Naming convention:
#   - T at the START of a compound code (e.g. T-B) means Teenage
#   - T at the END of a compound code (e.g. BT, GT) means Toddler
#   - Standalone "T" means Toddler (1–3 yrs)
# ---------------------------------------------------------------------------
DEPARTMENT_CODE_CONTEXT: Dict[str, str] = {
    "B":   "Boys — Young boy wearing kids outfit",
    "BJ":  "Boys Junior — Older boy (8–14 yrs) clothing",
    "BT":  "Boys Toddler — Toddler boy clothing (1–3 yrs)",
    "BS":  "Boys Senior — Teenage boy clothing (14+ yrs)",
    "G":   "Girls — Young girl clothing",
    "GJ":  "Girls Junior — Older girl (8–14 yrs) clothing",
    "GT":  "Girls Toddler — Toddler girl clothing (1–3 yrs)",
    "GS":  "Girls Senior — Teenage girl clothing (14+ yrs)",
    "M":   "Men — Adult male clothing",
    "W":   "Women — Adult female clothing",
    "L":   "Ladies — Women traditional / formal clothing",
    "I":   "Infant — Baby clothing (0–12 months)",
    "IB":  "Infant Boys — Baby boy clothing (0–12 months)",
    "IG":  "Infant Girls — Baby girl clothing (0–12 months)",
    "T":   "Toddler — 1–3 year child clothing",
    "T-B": "Teenage Boys — Teenage boy clothing (13–17 yrs)",
    "WW":  "Women Western — Women's western-style clothing",
}


def build_department_context_string(departments: List[str]) -> str:
    """
    For a list of department names (e.g. ['T-Shirt [BJ]', 'T-Shirt [BS]', 'T-Shirt [M]']),
    extract the audience codes from brackets and return an enriched reference table
    that explains what each code means.
    """
    lines = ["Department options with audience context:"]
    seen_codes: set = set()

    for dept in departments:
        # Extract all codes inside brackets, e.g. 'T-Shirt FS[BJ]' -> ['BJ']
        codes = re.findall(r'\[([A-Z][A-Z0-9-]*)\]', dept)
        code_meanings = []
        for code in codes:
            meaning = DEPARTMENT_CODE_CONTEXT.get(code)
            if meaning and code not in seen_codes:
                code_meanings.append(f"{code} = {meaning}")
                seen_codes.add(code)
        if code_meanings:
            lines.append(f"  • {dept}  →  {', '.join(code_meanings)}")
        else:
            lines.append(f"  • {dept}")

    return "\n".join(lines)

def clean_json_response(content: str) -> str:
    """Removes markdown and extra text from LLM response."""
    # Remove markdown code blocks
    content = re.sub(r'```json\s*', '', content)
    content = re.sub(r'```\s*', '', content)
    return content.strip()

class GroqService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    @retry(stop=stop_after_attempt(settings.MAX_RETRIES), wait=wait_fixed(2))
    def _call_groq(self, system_prompt: str, user_content: List[Dict[str, Any]]) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.1,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        return clean_json_response(completion.choices[0].message.content)

    def detect_division(self, image_bytes: bytes, allowed_divisions: List[str]) -> DivisionDetection:
        """Stage 1: Detect Division, Item Count, Visibility, and Coordinated Set status."""
        divisions_formatted = "\n".join(f"  - {d}" for d in allowed_divisions)
        system_prompt = (
            f"You are a fashion expert. Return ONLY valid JSON with these EXACT keys: "
            f"'division', 'item_count', 'is_garment_visible', 'is_coordinated_set'. "
            f"For 'division', you MUST copy one value VERBATIM (character-for-character) from this list:\n"
            f"{divisions_formatted}\n"
            f"Do NOT shorten, abbreviate, or paraphrase the division name. "
            f"For example, if the list has 'Women Ethnic' and 'Women Western', never return just 'Women'. "
            f"'item_count' is an integer counting ALL distinct garment pieces visible. "
            f"'is_garment_visible' is a boolean (true if clearly visible, not blurred/folded/obscured). "
            f"'is_coordinated_set' is a boolean with STRICT rules — "
            f"set to TRUE ONLY when ALL these conditions are met: "
            f"(1) there is EXACTLY ONE upper garment (shirt/top/kurta/jacket etc.), "
            f"(2) there is EXACTLY ONE lower garment (pant/jeans/skirt/shorts etc.), "
            f"(3) they form a SINGLE coordinated outfit (worn together or intentionally paired). "
            f"Set 'is_coordinated_set' to FALSE in ALL other cases, including: "
            f"multiple outfits displayed together (e.g. 2 sets side by side on hangers), "
            f"two separate tops, two separate bottoms, or any other combination beyond one upper + one lower. "
            f"IMPORTANT: Two coordinated sets displayed together = is_coordinated_set FALSE."
        )
        user_content = [
            {
                "type": "text",
                "text": (
                    "Analyse this image carefully:\n"
                    "1. Identify the garment division.\n"
                    "2. Count ALL distinct garment pieces visible (item_count).\n"
                    "3. Check if the garment(s) are clearly visible (is_garment_visible).\n"
                    "4. is_coordinated_set = true ONLY if there is exactly ONE top + ONE bottom forming "
                    "a single coordinated outfit. If you see 2 or more outfits/sets/pairs "
                    "displayed (even if each pair is upper+lower), set is_coordinated_set = false."
                )
            },
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(image_bytes)}"}}
        ]

        raw_response = self._call_groq(system_prompt, user_content)
        data = json.loads(raw_response)
        div = str(data.get("division", "")).strip()
        item_count = int(data.get("item_count", 1))
        is_visible = bool(data.get("is_garment_visible", True))
        is_coordinated_set = bool(data.get("is_coordinated_set", False))

        # Tier 1: exact case-insensitive match
        matched_div = None
        for allowed in allowed_divisions:
            if div.lower() == allowed.lower():
                matched_div = allowed
                break

        # Tier 2: prefix / starts-with match (handles 'Women' → 'Women Western' / 'Women Ethnic')
        if not matched_div:
            prefix_matches = [a for a in allowed_divisions if a.lower().startswith(div.lower())]
            if len(prefix_matches) == 1:
                # Unambiguous single prefix match — safe to use
                matched_div = prefix_matches[0]
                logger.warning(
                    f"Division '{div}' resolved via prefix match to '{matched_div}'. "
                    f"Prompt may need tuning."
                )
            elif len(prefix_matches) > 1:
                # Ambiguous — can't safely pick one, raise error
                raise ValueError(
                    f"Ambiguous division '{div}' matches multiple: {prefix_matches}. "
                    f"LLM must return the full exact name."
                )

        if not matched_div:
            raise ValueError(f"Invalid division detected: '{div}'. Allowed: {allowed_divisions}")

        return DivisionDetection(
            division=matched_div,
            item_count=item_count,
            is_garment_visible=is_visible,
            is_coordinated_set=is_coordinated_set
        )

    def detect_department(self, image_bytes: bytes, division: str, allowed_departments: List[str]) -> Optional[str]:
        """Stage 2: Detect Department based on Division and audience code context."""
        if not allowed_departments:
            return None

        # Build enriched context table so the LLM knows what each code suffix means
        context_table = build_department_context_string(allowed_departments)

        system_prompt = (
            f"You are a fashion expert specialising in garment classification. "
            f"Your task is to identify the most appropriate department for a '{division}' garment. "
            f"Department names contain audience codes inside brackets (e.g. [BJ], [M], [W]). "
            f"Each code indicates who the garment is designed for — a specific age group and gender. "
            f"\n\n{context_table}"
            f"\n\nINSTRUCTIONS:"
            f"\n1. Carefully look at the garment AND the person wearing it (if visible)."
            f"\n2. Estimate the wearer's apparent age group and gender from the image."
            f"\n3. Match the garment type + age group + gender to the best department from the list."
            f"\n4. Return ONLY valid JSON with a single key: 'department'."
            f"\n5. The value MUST be copied exactly (character-for-character) from the allowed list."
        )

        dept_list_str = "\n".join(f"  {i+1}. {d}" for i, d in enumerate(allowed_departments))
        user_text = (
            f"Division: {division}\n"
            f"\nAllowed departments (pick EXACTLY one, copy the text as-is):\n{dept_list_str}\n"
            f"\nAnalyse the image carefully — note the garment style and the apparent age/gender "
            f"of the person wearing it — then return the best matching department as JSON."
        )

        user_content = [
            {"type": "text", "text": user_text},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(image_bytes)}"}}
        ]

        raw_response = self._call_groq(system_prompt, user_content)
        data = json.loads(raw_response)
        dept = str(data.get("department", "")).strip()

        # Exact match first
        if dept in allowed_departments:
            return dept

        # Fallback: case-insensitive match
        for allowed in allowed_departments:
            if dept.lower() == allowed.lower():
                return allowed

        return None

    def extract_attributes(
        self,
        image_bytes: bytes,
        division: str,
        department: Optional[str],
        is_coordinated_set: bool = False
    ) -> Dict[str, Any]:
        """Stage 3: Extract remaining attributes with full context."""
        coordinated_note = (
            "NOTE: This image shows a COORDINATED SET — the person is wearing an upper garment "
            "(e.g. shirt/top/kurta) AND a lower garment (e.g. pant/jeans/skirt) together as one outfit. "
            "Extract attributes for the overall outfit, treating it as a single coordinated item.\n\n"
            if is_coordinated_set else ""
        )

        system_prompt = (
            "You are a professional fashion attribute extractor. Return ONLY valid JSON. "
            "If an attribute is not visible, set it to null. Use the specified allowed values strictly."
        )

        user_prompt = f"""Division: {division}
Department: {department or 'N/A'}

{coordinated_note}Extract these attributes carefully:
- item_count (integer)
- is_garment_visible (boolean)
- quality_issue (null if visible)
- color: [black, white, red, blue, green, yellow, pink, purple, orange, brown, grey, beige, maroon, navy, multi]
- pattern: [solid, striped, checked, floral, printed, embroidered, self_design, graphic, abstract, other]
- sleeve_length: [sleeveless, short, three_quarter, full, null]
- neckline: [round, v_neck, square, sweetheart, halter, boat, collar, mandarin, high_neck, off_shoulder, null]
- fit: [slim, regular, relaxed, oversized, bodycon, straight, null]
- gender: [male, female, unisex, null]
- garment_length: [cropped, waist_length, hip_length, knee_length, midi, ankle_length, floor_length, null]
- material_type: [cotton, polyester, silk, chiffon, georgette, wool, denim, linen, rayon, leather, knit, other, null]
- texture: [smooth, ribbed, knitted, sheer, textured, distressed, null]
- closure_type: [buttons, zipper, hook, drawstring, elastic, none, null]
- collar_type: [spread, mandarin, peter_pan, shawl, hooded, none, null]
- pocket_type: [side_pockets, patch_pockets, welt_pockets, cargo_pockets, none, null]
- style: [casual, formal, ethnic, western, festive, sporty, party, streetwear]
- occasion: [casual, office, festive, wedding, party, vacation, sports]
- season: [summer, winter, monsoon, spring, autumn, all_season]

Return the output in the requested JSON structure.
"""
        
        user_content = [
            {"type": "text", "text": user_prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(image_bytes)}"}}
        ]
        
        raw_response = self._call_groq(system_prompt, user_content)
        data = json.loads(raw_response)

        # Enforce consistency
        data["division"] = division
        data["department"] = department

        # Guard: block truly multiple unrelated garments.
        # Skip this check for coordinated sets — they intentionally have item_count > 1.
        if data.get("item_count", 1) > 1 and not is_coordinated_set:
            return FashionAttributeResponse(
                division=division,
                department=department,
                item_count=data.get("item_count"),
                is_garment_visible=bool(data.get("is_garment_visible", True)),
                message="There is multiple garments so upload single garment image."
            ).model_dump()

        # Validate and return
        return FashionAttributeResponse(**data).model_dump()
    

    # --------------------------------------------------
    # Mapping Internal Schema → Vendor Format
    # --------------------------------------------------

    def map_internal_to_vendor(self, internal_data: Dict[str, Any]) -> Dict[str, Any]:

        # Handle error cases (multiple garments etc.)
        if internal_data.get("message") and internal_data.get("item_count", 1) > 1:
            return {
                "success": False,
                "message": internal_data.get("message"),
                "result": None
            }

        attribute = {
            "no_of_pcs": str(internal_data.get("item_count", 1)),
            "brand": None,  # Not predicted yet
            "style_pattern": internal_data.get("pattern"),
            "assortment": "SINGLE",
            "size": None,  # Not predicted yet
            "color": internal_data.get("color"),
            "vendor_design": internal_data.get("style")[0] if internal_data.get("style") else None,
            "fabric": internal_data.get("material_type"),
            "neck_waist": internal_data.get("neckline"),
            "fit": internal_data.get("fit"),
            "sleeve_or_intensity": internal_data.get("sleeve_length"),
            "sleeve_style": None,
            "product_type": internal_data.get("department"),
            "trend_design": internal_data.get("pattern"),
            "pattern_coverage_or_occasion": (
                internal_data.get("occasion")[0] if internal_data.get("occasion") else None
            ),
            "garment_length": internal_data.get("garment_length"),
            "pocket_type": internal_data.get("pocket_type"),
            "gender_wash": internal_data.get("gender"),
        }

        return {
            "success": True,
            "message": internal_data.get("message"),
            "result": {
                "division": internal_data.get("division"),
                "department": internal_data.get("department"),
                "attributes": [attribute]
            }
        }
