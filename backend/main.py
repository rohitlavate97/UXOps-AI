from fastapi import FastAPI

app = FastAPI(
    title="UXOps AI API",
    description="Enterprise AI UI/UX Quality Engineering Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.get("/")
def read_root():
    return {"message": "Welcome to UXOps AI API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
