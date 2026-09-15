from fastapi import FastAPI

from app.auth import CurrentUser

app = FastAPI()


@app.get("/me")
def get_me(user_id: CurrentUser):
    return {
        "user_id": user_id,
    }
