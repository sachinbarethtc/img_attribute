from typing import List, Optional, Union, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator

class DivisionDetection(BaseModel):
    division: str
    item_count: int = 1
    is_garment_visible: bool = True
    is_coordinated_set: bool = False   # True when upper+lower worn together as a set

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



# -------------------------------
# Vendor Output Schema
# -------------------------------

class VendorAttribute(BaseModel):
    no_of_pcs: Optional[str] = None
    brand: Optional[str] = None
    style_pattern: Optional[str] = None
    assortment: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    vendor_design: Optional[str] = None
    fabric: Optional[str] = None
    neck_waist: Optional[str] = None
    fit: Optional[str] = None
    sleeve_or_intensity: Optional[str] = None
    sleeve_style: Optional[str] = None
    product_type: Optional[str] = None
    trend_design: Optional[str] = None
    pattern_coverage_or_occasion: Optional[str] = None
    garment_length: Optional[str] = None
    pocket_type: Optional[str] = None
    gender_wash: Optional[str] = None


class VendorResult(BaseModel):
    division: str
    department: str
    attributes: List[VendorAttribute]


class VendorResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    result: Optional[VendorResult] = None
