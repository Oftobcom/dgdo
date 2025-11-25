from ..domain.trip import Trip

class TripRepo:
    def __init__(self):
        self._store = {}
    def create(self, t: Trip):
        self._store[str(t.id)] = t
        return t
    def get(self, tid: str):
        return self._store.get(tid)
    def update_status(self, tid: str, status: str):
        t = self._store.get(tid)
        if t:
            t.status = status
        return t