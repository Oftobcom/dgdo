A **Saga** is a **pattern for managing long-running business transactions** that span multiple services. Instead of a single database transaction (which can’t span services), a saga breaks the workflow into **steps**, each with its own action and **compensation** in case of failure.

A **workflow coordinator** is the component that:

1. **Orchestrates the steps** in the saga. For your trip creation workflow, this would mean:

   * Call TripRequestService to create a request
   * Call MatchingService to get candidate drivers
   * Call PricingService to calculate the fare
   * Call DriverStatusService to assign a driver
   * Call TripService to create the trip record
2. **Tracks state**: knows which step succeeded and which failed.
3. **Executes compensations** on failures to roll back previous steps. For example:

   * If pricing fails, cancel the trip request
   * If driver assignment fails, unassign any partially assigned driver
4. **Ensures idempotency and replayability**: re-running the same workflow with the same inputs should produce the same result.
5. **Integrates telemetry and logging** for auditing and metrics.

In short: the **Saga / workflow coordinator** is like the conductor of an orchestra, making sure all the microservices play their part in the right order, and if something goes wrong, it gracefully rolls back the music.

For your DG Do platform, this is exactly what `trip_workflow.py` will implement.

+-----------------+
| Passenger sends  |
| trip request     |
+-----------------+
          |
          v
+-----------------+        Failure?       +----------------------+
| TripRequestSvc  |---------------------> | N/A (already fail)   |
|  CreateTripReq  |                       +----------------------+
+-----------------+
          |
          v
+-----------------+        Failure?       +----------------------+
| MatchingSvc     |---------------------> | Compensate: Cancel   |
|  GetCandidates  |                       | TripRequest          |
+-----------------+                       +----------------------+
          |
          v
+-----------------+        Failure?       +----------------------+
| PricingSvc      |---------------------> | Compensate: Cancel   |
|  CalculateFare  |                       | TripRequest          |
+-----------------+                       +----------------------+
          |
          v
+-----------------+        Failure?       +----------------------+
| DriverStatusSvc |---------------------> | Compensate: Cancel   |
|  AssignDriver   |                       | TripRequest          |
+-----------------+                       | Compensate
