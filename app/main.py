from fastapi import FastAPI

from fastapi_pagination import add_pagination

from app.api.router_v1 import router_v1
from app.api.router_v2 import router_v2


app = FastAPI()

app.include_router(router_v1)
app.include_router(router_v2)

add_pagination(app)

@app.get("/health")
def health() -> dict[str, bool]: return {"ok": True}
