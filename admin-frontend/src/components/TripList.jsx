import React, { useEffect, useState } from 'react';
import { fetchTrips, updateTripStatus } from '../services/api';

export default function TripList() {
  const [trips, setTrips] = useState([]);

  useEffect(() => {
    fetchTrips().then(setTrips);
  }, []);

  const markComplete = async (tripId) => {
    await updateTripStatus(tripId, 'completed');
    setTrips(trips.map(t => t.id === tripId ? { ...t, status: 'completed' } : t));
  };

  return (
    <div>
      <h2>Trips</h2>
      <ul>
        {trips.map(trip => (
          <li key={trip.id} style={{ marginBottom: '10px' }}>
            <strong>{trip.passenger_id}</strong> → {trip.driver_id || 'unassigned'}
            (<em>{trip.status}</em>)
            {trip.status !== 'completed' && (
              <button onClick={() => markComplete(trip.id)} style={{ marginLeft: '10px' }}>Complete</button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}