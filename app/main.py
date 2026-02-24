# # from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
# # from fastapi.middleware.cors import CORSMiddleware
# # from app.schemas import FashionAttributeResponse, ErrorResponse
# # from app.services.groq_service import GroqService
# # import logging

# # # Configure logging
# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)

# # app = FastAPI(
# #     title="Fashion Attribute Extraction API",
# #     description="Extracts fashion attributes from images using Groq Vision API.",
# #     version="1.0.0"
# # )

# # # CORS Middleware
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],  # Production: specify domains
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # # Dependency
# # def get_groq_service():
# #     return GroqService()

# # @app.get("/health", tags=["Health"])
# # async def health_check():
# #     """Health check endpoint."""
# #     return {"status": "ok"}

# # @app.post("/analyze", response_model=FashionAttributeResponse, responses={500: {"model": ErrorResponse}}, tags=["Analysis"])
# # async def analyze_fashion_attributes(
# #     file: UploadFile = File(...),
# #     service: GroqService = Depends(get_groq_service)
# # ):
# #     """
# #     Upload an image to extract fashion attributes.
# #     """
# #     if not file.content_type.startswith("image/"):
# #         raise HTTPException(status_code=400, detail="File must be an image.")

# #     try:
# #         contents = await file.read()
# #         if not contents:
# #              raise HTTPException(status_code=400, detail="Empty file.")
             
# #         result = service.analyze_image(contents)
# #         return result

# #     except Exception as e:
# #         logger.error(f"Analysis failed: {str(e)}")
# #         raise HTTPException(status_code=500, detail=str(e))

# # if __name__ == "__main__":
# #     import uvicorn
# #     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)




# from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
# from fastapi.middleware.cors import CORSMiddleware
# from contextlib import asynccontextmanager
# from app.schemas import FashionAttributeResponse, ErrorResponse
# from app.services.groq_service import GroqService
# from app.utils import load_divisions_and_departments
# import logging
# import os

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # In-memory storage for divisions and departments
# DIV_DEPT_MAPPING = {}

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Load Excel on startup
#     global DIV_DEPT_MAPPING
#     excel_path = "division.xlsx"
#     try:
#         DIV_DEPT_MAPPING = load_divisions_and_departments(excel_path)
#         logger.info(f"Successfully loaded {len(DIV_DEPT_MAPPING)} divisions from {excel_path}")
#     except Exception as e:
#         logger.error(f"Failed to load division.xlsx: {e}")
#         # In production, you might want to stop startup if this is critical
#     yield

# app = FastAPI(
#     title="Fashion Attribute Extraction API",
#     description="Multi-stage attribute extraction pipeline using Groq Vision.",
#     version="2.0.0",
#     lifespan=lifespan
# )

# # CORS Middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Dependency
# def get_groq_service():
#     return GroqService()

# @app.get("/health", tags=["Health"])
# async def health_check():
#     return {"status": "ok", "divisions_loaded": list(DIV_DEPT_MAPPING.keys())}

# @app.post("/analyze", response_model=FashionAttributeResponse, responses={500: {"model": ErrorResponse}}, tags=["Analysis"])
# async def analyze_fashion_attributes(
#     file: UploadFile = File(...),
#     service: GroqService = Depends(get_groq_service)
# ):
#     """
#     3-Stage Pipeline:
#     1. Detect Division
#     2. Detect Department (filtered by Division)
#     3. Extract remaining attributes
#     """
#     # Safe content type check
#     is_image = False
#     if file.content_type and file.content_type.startswith("image/"):
#         is_image = True
#     elif file.filename and file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
#         is_image = True
        
#     if not is_image:
#         raise HTTPException(status_code=400, detail="File must be an image.")

#     try:
#         contents = await file.read()
#         if not contents:
#              raise HTTPException(status_code=400, detail="Empty file.")
        
#         # Stage 1: Detect Division
#         allowed_divisions = list(DIV_DEPT_MAPPING.keys())
#         if not allowed_divisions:
#              raise HTTPException(status_code=500, detail="Division map not loaded.")
             
#         try:
#             division_data = service.detect_division(contents, allowed_divisions)
#             division = division_data.division

#             # Block ONLY when multiple unrelated garments are present.
#             # A Coordinated Set (upper garment + lower garment worn together, e.g. shirt+pant,
#             # top+jeans, kurta+pyjama) is intentional and should pass through the full pipeline.
#             if division_data.item_count > 1 and not division_data.is_coordinated_set:
#                 return FashionAttributeResponse(
#                     division=division,
#                     item_count=division_data.item_count,
#                     is_garment_visible=division_data.is_garment_visible,
#                     message="There is multiple garments so upload single garment image."
#                 )
#         except Exception as e:
#             logger.error(f"Stage 1 (Division) failed: {e}")
#             raise HTTPException(status_code=422, detail=f"Division detection failed or invalid: {str(e)}")

#         # Stage 2: Detect Department
#         allowed_departments = DIV_DEPT_MAPPING.get(division, [])
#         department = service.detect_department(contents, division, allowed_departments)

#         # Stage 3: Remaining Attributes
#         # Forward is_coordinated_set so Stage 3 skips the multiple-garment guard
#         # and informs the LLM it is analysing a coordinated outfit.
#         final_result = service.extract_attributes(
#             contents, division, department,
#             is_coordinated_set=division_data.is_coordinated_set
#         )

#         return final_result

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail="Internal server error during processing.")

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)




from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.schemas import VendorResponse, ErrorResponse
from app.services.groq_service import GroqService
from app.utils import load_divisions_and_departments
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for divisions and departments
DIV_DEPT_MAPPING = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load Excel on startup
    global DIV_DEPT_MAPPING
    excel_path = "division.xlsx"
    try:
        DIV_DEPT_MAPPING = load_divisions_and_departments(excel_path)
        logger.info(f"Successfully loaded {len(DIV_DEPT_MAPPING)} divisions from {excel_path}")
    except Exception as e:
        logger.error(f"Failed to load division.xlsx: {e}")
    yield


app = FastAPI(
    title="Fashion Attribute Extraction API",
    description="Multi-stage attribute extraction pipeline using Groq Vision.",
    version="3.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_groq_service():
    return GroqService()


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "divisions_loaded": list(DIV_DEPT_MAPPING.keys())
    }


@app.post(
    "/analyze",
    response_model=VendorResponse,
    responses={500: {"model": ErrorResponse}},
    tags=["Analysis"]
)
async def analyze_fashion_attributes(
    file: UploadFile = File(...),
    service: GroqService = Depends(get_groq_service)
):
    """
    3-Stage Pipeline:
    1. Detect Division
    2. Detect Department (filtered by Division)
    3. Extract remaining attributes
    4. Convert to Vendor Format
    """

    # Validate image
    is_image = False
    if file.content_type and file.content_type.startswith("image/"):
        is_image = True
    elif file.filename and file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        is_image = True

    if not is_image:
        raise HTTPException(status_code=400, detail="File must be an image.")

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file.")

        # -------------------------
        # Stage 1: Detect Division
        # -------------------------
        allowed_divisions = list(DIV_DEPT_MAPPING.keys())
        if not allowed_divisions:
            raise HTTPException(status_code=500, detail="Division map not loaded.")

        try:
            division_data = service.detect_division(contents, allowed_divisions)
            division = division_data.division

            # Block only unrelated multiple garments
            if division_data.item_count > 1 and not division_data.is_coordinated_set:
                return {
                    "success": False,
                    "message": "There is multiple garments so upload single garment image.",
                    "result": None
                }

        except Exception as e:
            logger.error(f"Stage 1 (Division) failed: {e}")
            raise HTTPException(status_code=422, detail=f"Division detection failed: {str(e)}")

        # -------------------------
        # Stage 2: Detect Department
        # -------------------------
        allowed_departments = DIV_DEPT_MAPPING.get(division, [])
        department = service.detect_department(contents, division, allowed_departments)

        # -------------------------
        # Stage 3: Extract Attributes
        # -------------------------
        internal_result = service.extract_attributes(
            contents,
            division,
            department,
            is_coordinated_set=division_data.is_coordinated_set
        )

        # -------------------------
        # Stage 4: Convert to Vendor Format
        # -------------------------
        vendor_output = service.map_internal_to_vendor(internal_result)

        return vendor_output

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during processing."
        )

@app.get("/")
async def root():
    return {"message": "API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)