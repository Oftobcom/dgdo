import requests
from ..domain.driver import Driver

MATCHING_URL = "http://matching:8001/assign"

class MatchingService:
    def assign_driver(self, trip):
        # Prepare payload for matching
        payload = {
            "origin": {"lat": trip.origin_lat, "lon": trip.origin_lon},
            "drivers": [
                # In MVP, we have no DB; in real life, we'd query available drivers
            ]
        }
        # Try to call matching service; if not available, return None
        try:
            r = requests.post(MATCHING_URL, json=payload, timeout=2)
            if r.status_code == 200:
                data = r.json()
                return data.get("driver_id")
        except Exception as e:
            print("matching service call failed:", e)
        return None