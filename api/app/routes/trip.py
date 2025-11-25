from fastapi import APIRouter

router = APIRouter(prefix="/trip")

@router.post("/")
def create_trip():
    return {"todo": "create trip"}

@router.post("/{id}/status")
def update_status(id: str):
    return {"todo": f"update status for trip {id}"}
