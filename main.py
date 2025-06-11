from fastapi import FastAPI
from app.routes import router
from app.database import create_tables
from setup_db import seed_database

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
def startup():
    create_tables()
    seed_database()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
