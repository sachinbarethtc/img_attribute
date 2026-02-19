# from enum import Enum
# from typing import List, Optional
# from pydantic import BaseModel, Field, ConfigDict

# # Enums based on Allowed Values
# class Category(str, Enum):
#     T_SHIRT = "t-shirt"
#     SHIRT = "shirt"
#     KURTA = "kurta"
#     DRESS = "dress"
#     SAREE = "saree"
#     TOP = "top"
#     BLOUSE = "blouse"
#     JACKET = "jacket"
#     COAT = "coat"
#     HOODIE = "hoodie"
#     SWEATER = "sweater"
#     JEANS = "jeans"
#     TROUSERS = "trousers"
#     SHORTS = "shorts"
#     SKIRT = "skirt"
#     ETHNIC_SET = "ethnic_set"
#     JUMPSUIT = "jumpsuit"
#     OTHER = "other"

# class Color(str, Enum):
#     BLACK = "black"
#     WHITE = "white"
#     RED = "red"
#     BLUE = "blue"
#     GREEN = "green"
#     YELLOW = "yellow"
#     PINK = "pink"
#     PURPLE = "purple"
#     ORANGE = "orange"
#     BROWN = "brown"
#     GREY = "grey"
#     BEIGE = "beige"
#     MAROON = "maroon"
#     NAVY = "navy"
#     MULTI = "multi"

# class Pattern(str, Enum):
#     SOLID = "solid"
#     STRIPED = "striped"
#     CHECKED = "checked"
#     FLORAL = "floral"
#     PRINTED = "printed"
#     EMBROIDERED = "embroidered"
#     SELF_DESIGN = "self_design"
#     GRAPHIC = "graphic"
#     ABSTRACT = "abstract"
#     OTHER = "other"

# class SleeveLength(str, Enum):
#     SLEEVELESS = "sleeveless"
#     SHORT = "short"
#     THREE_QUARTER = "three_quarter"
#     FULL = "full"
#     NULL = "null"

# class Neckline(str, Enum):
#     ROUND = "round"
#     V_NECK = "v_neck"
#     SQUARE = "square"
#     SWEETHEART = "sweetheart"
#     HALTER = "halter"
#     BOAT = "boat"
#     COLLAR = "collar"
#     MANDARIN = "mandarin"
#     HIGH_NECK = "high_neck"
#     OFF_SHOULDER = "off_shoulder"
#     NULL = "null"

# class Fit(str, Enum):
#     SLIM = "slim"
#     REGULAR = "regular"
#     RELAXED = "relaxed"
#     OVERSIZED = "oversized"
#     BODYCON = "bodycon"
#     STRAIGHT = "straight"
#     NULL = "null"

# class Gender(str, Enum):
#     MALE = "male"
#     FEMALE = "female"
#     UNISEX = "unisex"
#     NULL = "null"

# class GarmentLength(str, Enum):
#     CROPPED = "cropped"
#     WAIST_LENGTH = "waist_length"
#     HIP_LENGTH = "hip_length"
#     KNEE_LENGTH = "knee_length"
#     MIDI = "midi"
#     ANKLE_LENGTH = "ankle_length"
#     FLOOR_LENGTH = "floor_length"
#     NULL = "null"

# class MaterialType(str, Enum):
#     COTTON = "cotton"
#     POLYESTER = "polyester"
#     SILK = "silk"
#     CHIFFON = "chiffon"
#     GEORGETTE = "georgette"
#     WOOL = "wool"
#     DENIM = "denim"
#     LINEN = "linen"
#     RAYON = "rayon"
#     LEATHER = "leather"
#     KNIT = "knit"
#     OTHER = "other"
#     NULL = "null"

# class Texture(str, Enum):
#     SMOOTH = "smooth"
#     RIBBED = "ribbed"
#     KNITTED = "knitted"
#     SHEER = "sheer"
#     TEXTURED = "textured"
#     DISTRESSED = "distressed"
#     NULL = "null"

# class ClosureType(str, Enum):
#     BUTTONS = "buttons"
#     ZIPPER = "zipper"
#     HOOK = "hook"
#     DRAWSTRING = "drawstring"
#     ELASTIC = "elastic"
#     NONE = "none"
#     NULL = "null"

# class CollarType(str, Enum):
#     SPREAD = "spread"
#     MANDARIN = "mandarin"
#     PETER_PAN = "peter_pan"
#     SHAWL = "shawl"
#     HOODED = "hooded"
#     NONE = "none"
#     NULL = "null"

# class PocketType(str, Enum):
#     SIDE_POCKETS = "side_pockets"
#     PATCH_POCKETS = "patch_pockets"
#     WELT_POCKETS = "welt_pockets"
#     CARGO_POCKETS = "cargo_pockets"
#     NONE = "none"
#     NULL = "null"

# class Style(str, Enum):
#     CASUAL = "casual"
#     FORMAL = "formal"
#     ETHNIC = "ethnic"
#     WESTERN = "western"
#     FESTIVE = "festive"
#     SPORTY = "sporty"
#     PARTY = "party"
#     STREETWEAR = "streetwear"

# class Occasion(str, Enum):
#     CASUAL = "casual"
#     OFFICE = "office"
#     FESTIVE = "festive"
#     WEDDING = "wedding"
#     PARTY = "party"
#     VACATION = "vacation"
#     SPORTS = "sports"

# class Season(str, Enum):
#     SUMMER = "summer"
#     WINTER = "winter"
#     MONSOON = "monsoon"
#     SPRING = "spring"
#     AUTUMN = "autumn"
#     ALL_SEASON = "all_season"

# class FashionAttributeResponse(BaseModel):
#     category: Optional[str] = None
#     color: Optional[str] = None
#     pattern: Optional[str] = None
#     sleeve_length: Optional[str] = None
#     neckline: Optional[str] = None
#     fit: Optional[str] = None
#     gender: Optional[str] = None
#     garment_length: Optional[str] = None
#     material_type: Optional[str] = None
#     texture: Optional[str] = None
#     closure_type: Optional[str] = None
#     collar_type: Optional[str] = None
#     pocket_type: Optional[str] = None
#     style: List[str] = []
#     occasion: List[str] = []
#     season: List[str] = []
#     item_count: Optional[int] = Field(default=1, description="Number of distinct fashion items detected in the image")
#     is_garment_visible: Optional[bool] = Field(default=True, description="True if the garment is clearly visible and not folded/obscured")
#     quality_issue: Optional[str] = Field(default=None, description="Description of the quality issue if not visible")
#     message: Optional[str] = Field(default=None, description="Status message or error description")

#     model_config = ConfigDict(extra="ignore")

# class ErrorResponse(BaseModel):
#     error: str
#     detail: Optional[str] = None




from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator

class DivisionDetection(BaseModel):
    division: str
    item_count: int = 1
    is_garment_visible: bool = True

class DepartmentDetection(BaseModel):
    department: Optional[str] = None

class FashionAttributeResponse(BaseModel):
    division: Optional[str] = ""
    department: Optional[str] = ""
    item_count: Optional[int] = 0
    is_garment_visible: Optional[bool] = True
    quality_issue: Optional[str] = None
    color: Optional[str] = ""
    pattern: Optional[str] = ""
    sleeve_length: Optional[str] = ""
    neckline: Optional[str] = ""
    fit: Optional[str] = ""
    gender: Optional[str] = ""
    garment_length: Optional[str] = ""
    material_type: Optional[str] = ""
    texture: Optional[str] = ""
    closure_type: Optional[str] = ""
    collar_type: Optional[str] = ""
    pocket_type: Optional[str] = ""
    style: Optional[List[str]] = []
    occasion: Optional[List[str]] = []
    season: Optional[List[str]] = []
    message: Optional[str] = None

    model_config = ConfigDict(extra="ignore")

    @field_validator("style", "occasion", "season", mode="before")
    @classmethod
    def ensure_list(cls, v: Any) -> List[str]:
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        if isinstance(v, list):
            return [str(item) for item in v]
        return []

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None