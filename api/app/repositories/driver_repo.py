from ..domain.driver import Driver

class DriverRepo:
    def __init__(self):
        self._store = {}
    def create(self, d: Driver):
        self._store[str(d.id)] = d
        return d
    def list_available(self):
        return [d for d in self._store.values() if d.status == "available"]
    def update_location(self, driver_id: str, lat: float, lon: float):
        d = self._store.get(driver_id)
        if d:
            d.lat = lat
            d.lon = lon
        return d