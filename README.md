# dgdo

# DG Do — Open Source Ride-Hailing Platform

DG Do is an open-source mobility-on-demand platform focused on simplicity, modularity, and learnability.

The project's goal is to demonstrate a working framework for a ride-hailing platform, including:
- Driver and passenger registration
- Trip creation
- Driver acceptance
- Status tracking
- Map integration (OpenStreetMap)

## Technologies
- **Backend:** C++, Python, FastAPI
- **Database:** PostgreSQL + PostGIS
- **Frontend:** React + Leaflet

## Purpose
The project is developed primarily for educational and research purposes. At the same time, we welcome and encourage any practical applications or real-world implementations that may emerge from its use.

## License
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

---

## 🏃‍♂️ Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/dgdo.git
cd dgdo
````

### 2. Launch all services with Docker Compose

```bash
docker compose up --build
```

After a few moments, all services should be running locally.

---

## 🔧 Local Services & Access Links

| Service             | URL / Port                                          |
| ------------------- | --------------------------------------------------- |
| FastAPI API Gateway | [http://localhost:8000](http://localhost:8000)      |
| C++ Matching Engine | [http://localhost:8001](http://localhost:8001)      |
| Admin Panel         | [http://localhost:8002](http://localhost:8002)      |
| Postgres Database   | localhost:5432                                      |

> **Tip:** Use your browser to access the web services (API docs available at `/docs` on FastAPI).

---

## 🧩 Project Structure

```
dgdo/
├── api/                # FastAPI API Gateway
├── matching/           # C++ Matching Engine
├── admin/              # Admin Panel (FastAPI placeholder)
├── db-postgresql/      # Database init scripts
└── docker-compose.yml  # Orchestration of all services
```

---

## ⚡ Quick Notes

* **API Gateway:** Handles REST + WebSocket requests from passengers, drivers, and admin.
* **Matching Engine:** C++ service for high-load driver assignment logic.
* **Admin Panel:** Minimal interface for testing/monitoring.
* **Database:** PostgreSQL stores passengers, drivers, and trips.

---

## 📌 Contact / Contributing

* Contributions are welcome! Please open issues or pull requests.
* Follow standard GitHub fork → feature branch → pull request workflow.
