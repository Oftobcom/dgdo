from fastapi import APIRouter

router = APIRouter(prefix="/passenger")

@router.post("/")
def register_passenger():
    return {"todo": "register passenger"}
