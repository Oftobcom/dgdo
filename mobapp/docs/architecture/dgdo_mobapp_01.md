**Component Diagram for the DG Do Mobile App** in a simple block-schematic

UML style that shows the internal components and their interactions:

---

```text
            +--------------------------------+
            |         DG Do Mobile App        |
            +--------------------------------+
                           |
    -------------------------------------------------
    |                 |                 |         |
+---------+      +---------+      +---------+    +---------+
| HomeScreen|    | TripScreen|    |ProfileScreen| | OtherScreens|
+---------+      +---------+      +---------+    +---------+
      |                |                |
      v                v                v
+---------------------------------------------+
|               UI Components                 |
|  - MapView                                   |
|  - Marker                                    |
|  - Buttons                                   |
+---------------------------------------------+
      |                |                |
      v                v                v
+---------------------------------------------+
|                 Services                     |
|  - API Service (REST)                        |
|  - WebSocket Service (Live Driver Tracking) |
|  - Location Service (GPS/Permissions)       |
+---------------------------------------------+
      |
      v
+---------------------------------------------+
|                Redux Store                  |
|  - tripSlice (from/to, driver info)        |
|  - userSlice (auth token, user info)       |
+---------------------------------------------+
```

**Explanation of interactions:**

1. **Screens** → render UI and interact with **Services** for data and events.
2. **UI Components** → reusable elements inside screens, receive data from **Services** or **Redux Store**.
3. **Services** → handle communication:

   * API Service → backend REST calls (e.g., `/trip/request`)
   * WebSocket Service → live driver position updates
   * Location Service → GPS coordinates of user
4. **Redux Store** → central state management for the app; Screens and Services read/write state here.

---

---
config:
  layout: elk
---
graph TB
    App["DG Do Mobile App"]
    HomeScreen["HomeScreen"]
    TripScreen["TripScreen"]
    ProfileScreen["ProfileScreen"]
    MapView["MapView"]
    Marker["Marker"]
    Buttons["Buttons"]
    APIService["API Service<br/>(REST Calls)"]
    WSService["WebSocket Service<br/>(Live Driver Tracking)"]
    LocationService["Location Service<br/>(GPS / Permissions)"]
    ReduxStore["Redux Store<br/>(tripSlice, userSlice)"]
    HomeScreen --> MapView
    HomeScreen --> Marker
    HomeScreen --> Buttons

    TripScreen --> MapView
    TripScreen --> Marker
    TripScreen --> Buttons

    ProfileScreen --> Buttons
    HomeScreen --> APIService
    HomeScreen --> WSService
    HomeScreen --> LocationService

    TripScreen --> APIService
    TripScreen --> WSService
    TripScreen --> LocationService
    APIService --> ReduxStore
    WSService --> ReduxStore
    LocationService --> ReduxStore
    HomeScreen --> ReduxStore
    TripScreen --> ReduxStore
    ProfileScreen --> ReduxStore