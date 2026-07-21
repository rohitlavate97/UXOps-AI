from fastapi import FastAPI

from analysis.accessibility_router import router as accessibility_router
from analysis.design_system_router import router as design_system_router
from analysis.recommendation_router import router as recommendation_router
from analysis.ui_analysis_router import router as ui_analysis_router
from analysis.ux_analysis_router import router as ux_analysis_router
from auth.router import router as auth_router
from auth.router import workspace_router
from ocr.router import router as ocr_router
from storage.router import router as storage_router
from vision.component_router import router as component_router

app = FastAPI(
    title="UXOps AI API",
    description="Enterprise AI UI/UX Quality Engineering Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register routers under api/v1
app.include_router(auth_router, prefix="/api/v1")
app.include_router(workspace_router, prefix="/api/v1")
app.include_router(storage_router, prefix="/api/v1")
app.include_router(ocr_router, prefix="/api/v1")
app.include_router(component_router, prefix="/api/v1")
app.include_router(accessibility_router, prefix="/api/v1")
app.include_router(ui_analysis_router, prefix="/api/v1")
app.include_router(ux_analysis_router, prefix="/api/v1")
app.include_router(design_system_router, prefix="/api/v1")
app.include_router(recommendation_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Welcome to UXOps AI API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
