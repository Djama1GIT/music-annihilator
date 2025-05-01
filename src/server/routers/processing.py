from fastapi import APIRouter

router = APIRouter(
    prefix="/processing",
    tags=["Processing"],
)


@router.get("/")
def process():
    return {"Hello": "World"}
