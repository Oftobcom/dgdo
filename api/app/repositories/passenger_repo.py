from ..domain.passenger import Passenger

class PassengerRepo:
    def __init__(self):
        self._store = {}
    def create(self, p: Passenger):
        self._store[str(p.id)] = p
        return p
    def get(self, pid: str):
        return self._store.get(pid)