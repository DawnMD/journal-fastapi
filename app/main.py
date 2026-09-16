from fastapi import FastAPI

from app.auth import CurrentUser
from app.routers import main_journal

app = FastAPI()

app.include_router(main_journal.router)


@app.get("/me")
def get_me(user_id: CurrentUser):
    return {
        "user_id": user_id,
    }
