const API_BASE = 'http://localhost:8000';

export async function fetchTrips() {
  const res = await fetch(`${API_BASE}/trips`);
  return res.json();
}

export async function updateTripStatus(tripId, status) {
  const res = await fetch(`${API_BASE}/trips/${tripId}/status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status })
  });
  return res.json();
}