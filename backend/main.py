from auth.router import router as auth_router
from auth.router import workspace_router
from fastapi import FastAPI

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


@app.get("/")
def read_root():
    return {"message": "Welcome to UXOps AI API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
