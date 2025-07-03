from fastapi import FastAPI
from backend.api.routes import router 

app = FastAPI(title="Application Dependency Insights")
app.include_router(router)
