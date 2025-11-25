# DG Do Admin Panel — React.js MVP

This document provides a ready-to-run React.js admin panel for DG Do Matching Engine, integrated with FastAPI API Gateway.

## 1️⃣ Folder structure
```
dgdo/
├── admin-frontend/
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.jsx
│       ├── index.jsx
│       ├── components/
│       │   └── TripList.jsx
│       └── services/
│           └── api.js
```

## 2️⃣ package.json
```json
{
  "name": "dgdo-admin",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
```

## 3️⃣ public/index.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DG Do Admin Panel</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>
```

## 4️⃣ src/index.jsx
```jsx
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);
```

## 5️⃣ src/App.jsx
```jsx
import React from 'react';
import TripList from './components/TripList';

export default function App() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>DG Do Admin Panel</h1>
      <TripList />
    </div>
  );
}
```

## 6️⃣ src/components/TripList.jsx
```jsx
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
```

## 7️⃣ src/services/api.js
```js
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
```

## 8️⃣ Dockerfile for React Admin Panel
```dockerfile
# Build stage
FROM node:20 as build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 9️⃣ Update docker-compose.yml
```yaml
  admin-frontend:
    build: ./admin-frontend
    ports:
      - "8002:80"
    depends_on:
      - api
```

## 🔹 Notes
- React admin panel runs on `localhost:8002`
- Fetches data from FastAPI API (`localhost:8000`)
- Ensure **CORS middleware** is enabled in FastAPI:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8002"],
    allow_methods=["*"],
    allow_headers=["*"]
)
```
- Run everything with:
```bash
docker compose up --build
```

