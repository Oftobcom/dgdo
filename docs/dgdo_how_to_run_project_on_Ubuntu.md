# DG Do MVP

## How to run and test this project on Ubuntu

Here is the **exact, step-by-step process** to run and test the DG Do MVP project.

---

# ✅ 1. Prerequisites

Install:

### ✔ Docker

### ✔ Docker Compose

### ✔ Git

Check versions:

```bash
docker --version
docker compose version
git --version
```

If these work — you're ready.

---

# ✅ 2. Clone the project

```bash
git clone https://github.com/your-username/dgdo.git
cd dgdo
```

Replace the URL with your repo.

---

# ✅ 3. Run the full stack

Inside the project folder:

```bash
docker compose up --build
```

This launches:

| Component           | Port |
| ------------------- | ---- |
| FastAPI API         | 8000 |
| C++ Matching Engine | 8001 |
| Admin Panel         | 8002 |
| Postgres            | 5432 |

You should see logs for:

* `api` (FastAPI)
* `matching` (C++)
* `admin` (FastAPI)
* `postgres`

When all containers say: **"Started successfully"**, the stack is running.

---

# ⭐ 4. Test the MVP components

Below are the actual test steps you can perform right now.

---

## 🔹 TEST 1 — Open FastAPI docs

Open:

👉 [http://localhost:8000/docs](http://localhost:8000/docs)

You should see Swagger UI with API endpoints.

---

## 🔹 TEST 2 — Create a passenger

POST request:

```
POST http://localhost:8000/passengers/register
Content-Type: application/json
```

Body:

```json
{
  "name": "John Doe",
  "phone": "+1234567890"
}
```

Expected result:

```json
{
  "id": "<uuid>",
  "name": "John Doe",
  "phone": "+1234567890"
}
```

---

## 🔹 TEST 3 — Create a trip request

```
POST http://localhost:8000/trips/request
```

Body:

```json
{
  "passenger_id": "<uuid from previous}",
  "origin_lat": 40.12,
  "origin_lon": 69.34,
  "dest_lat": 40.15,
  "dest_lon": 69.35
}
```

You should get:

```json
{
  "trip_id": "<uuid>",
  "status": "requested"
}
```

At this moment, FastAPI should call the **C++ Matching Engine** via HTTP.

---

## 🔹 TEST 4 — Driver updates position using WebSocket

Connect (in browser console or VSCode extension):

`ws://localhost:8000/ws/drivers/<driver_id>`

Send:

```json
{
  "lat": 40.120,
  "lon": 69.330,
  "status": "available"
}
```

Expected: API updates the driver location in DB.

---

## 🔹 TEST 5 — Admin panel

Open:

👉 [http://localhost:8002/](http://localhost:8002/)

Expected: minimal UI where you can see:

* active drivers
* active trips
* trip statuses

Even if it's very basic (HTML + JSON), this is enough for MVP testing.

---

# ⭐ 5. Integration Test (Main MVP Scenario)

Follow this flow:

---

### Step 1 — Create a passenger

(via API)

### Step 2 — Driver goes online

(via WebSocket)

### Step 3 — Passenger requests a trip

API → Matching engine assigns nearest driver.

### Step 4 — Trip status changes

* `requested`
* `assigned`
* `en_route`
* `completed`

### Step 5 — Admin UI shows everything

Drivers + Trips.
