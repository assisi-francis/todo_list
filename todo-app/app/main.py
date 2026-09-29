import pathlib
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from .database import engine, Base
from .routes import router

app = FastAPI(title="Todo App")

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Include routes
app.include_router(router)

# Static files setup
# We use absolute paths based on this file's location
BASE_DIR = pathlib.Path(__file__).parent.parent
static_dir = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def read_index():
    return FileResponse(static_dir / "index.html")
