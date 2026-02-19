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
        """Stage 1: Detect Division, Item Count, and Visibility"""
        system_prompt = (
            f"You are a fashion expert. Return ONLY valid JSON with 'division', 'item_count', and 'is_garment_visible' keys. "
            f"Allowed division values: {', '.join(allowed_divisions)}. "
            f"'item_count' is an integer. 'is_garment_visible' is a boolean."
        )
        user_content = [
            {"type": "text", "text": "Detect the division, count distinct garments, and check if the garments are clearly visible (not blurred, folded, or obscured)."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(image_bytes)}"}}
        ]
        
        raw_response = self._call_groq(system_prompt, user_content)
        data = json.loads(raw_response)
        div = str(data.get("division", "")).strip()
        item_count = int(data.get("item_count", 1))
        is_visible = bool(data.get("is_garment_visible", True))
        
        # Case-insensitive matching
        matched_div = None
        for allowed in allowed_divisions:
            if div.lower() == allowed.lower():
                matched_div = allowed
                break
        
        if not matched_div:
            raise ValueError(f"Invalid division detected: '{div}'. Allowed: {allowed_divisions}")
            
        return DivisionDetection(division=matched_div, item_count=item_count, is_garment_visible=is_visible)

    def detect_department(self, image_bytes: bytes, division: str, allowed_departments: List[str]) -> Optional[str]:
        """Stage 2: Detect Department based on Division"""
        if not allowed_departments:
            return None
            
        system_prompt = (
            f"You are a fashion expert. Detect the department for this '{division}' garment. "
            f"Return ONLY JSON with 'department' key. You must pick from the provided list."
        )
        user_content = [
            {"type": "text", "text": f"Select the most appropriate department from this list for the {division} garment: {', '.join(allowed_departments)}"},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(image_bytes)}"}}
        ]
        
        raw_response = self._call_groq(system_prompt, user_content)
        data = json.loads(raw_response)
        dept = str(data.get("department", "")).strip()
        
        # Exact case match for department as per requirements
        if dept in allowed_departments:
            return dept
        
        # Fallback to case-insensitive if exact match fails
        for allowed in allowed_departments:
            if dept.lower() == allowed.lower():
                return allowed
                
        return None

    def extract_attributes(self, image_bytes: bytes, division: str, department: Optional[str]) -> Dict[str, Any]:
        """Stage 3: Extract remaining attributes with full context"""
        system_prompt = (
            "You are a professional fashion attribute extractor. Return ONLY valid JSON. "
            "If an attribute is not visible, set it to null. Use the specified allowed values strictly."
        )
        
        user_prompt = f"""
Division: {division}
Department: {department or 'N/A'}

Extract these attributes carefully:
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
        
        # Check for multiple garments in final stage
        if data.get("item_count", 1) > 1:
            return FashionAttributeResponse(
                division=division,
                department=department,
                item_count=data.get("item_count"),
                is_garment_visible=bool(data.get("is_garment_visible", True)),
                message="There is multiple garments so upload single garment image."
            ).model_dump()
            
        # Validate and return
        return FashionAttributeResponse(**data).model_dump()