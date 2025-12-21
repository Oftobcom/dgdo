# Here’s a **step-by-step guide** to run and test your `TripRequestService` Python gRPC server:

---

## **1️⃣ Build the Docker image**

### Base image

docker build -t dgdo-python-base -f docker/python_base.Dockerfile .


# Python services
docker build -t dgdo-telemetry -f docker/telemetry_service.Dockerfile .
docker build -t dgdo-ml-feedback -f docker/ml_feedback_service.Dockerfile .

Assuming your `trip_request_service.Dockerfile` is ready:

```bash
docker build -t dgdo-trip-request -f docker/trip_request_service.Dockerfile .
```

---

## **2️⃣ Run the container**

Expose port `50052` for gRPC:

```bash
docker run -d -p 50052:50052 --name dgdo-trip-request dgdo-trip-request
```

Check it’s running:

```bash
docker ps
```

You should see `dgdo-trip-request` running on port 50052.

---

## **3️⃣ Test with Python client**

Find `test_trip_request.py`.

---

## **4️⃣ Run the test script**

If your generated proto files are in `PYTHONPATH` (from `python_base.Dockerfile`):

```bash
python3 test_trip_request.py
```

Expected output:

```
Created TripRequest: id: "b2f4f4f8-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
passenger_id: "passenger_1"
status: OPEN
...
Fetched TripRequest: ...
Cancelled TripRequest: status: CANCELLED
...
```

---

# Here’s a **step-by-step guide** to run and test your `TripService` Python gRPC server:

---

## **1️⃣ Build the Docker image**

Assuming your `trip_service.Dockerfile` is ready:

```bash
docker build -t dgdo-trip-service -f docker/trip_service.Dockerfile .
```

---

## **2️⃣ Run the container**

Expose port `50053` for gRPC:

```bash
docker run -d -p 50053:50053 --name dgdo-trip-service dgdo-trip-service
```

Check it’s running:

```bash
docker ps
```

You should see `dgdo-trip-service` running on port 50053.

---

## **3️⃣ Test with Python client**

Find `test_trip_service.py`.

---

## **4️⃣ Run the test script**

```bash
python3 test_trip_service.py
```

Expected output is similar to:

```
=== Created Trip ===
ID: bb4fd4ab-d2a9-4308-add2-3829e05aecf4
TripRequest ID: req_001
Passenger: passenger_1, Driver: driver_1
Origin: (39.6, 67.8)
Destination: (39.65, 67.85)
Status: ACCEPTED
Version: 1
Created: 2025-12-21 11:16:12.515680
Updated: 2025-12-21 11:16:12.515736
...
```

---
