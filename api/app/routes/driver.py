from fastapi import APIRouter

router = APIRouter(prefix="/driver")

@router.post("/location")
def update_location():
    return {"todo": "update location"}
