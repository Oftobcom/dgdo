# dgdo_ride_type_pricing_rules.md

# DG Do — Ride Type Pricing Rules

## 1. Overview

This document defines pricing rules for all supported ride types in the DG Do platform.

Each ride type defines:

* Base fare
* Per kilometer rate
* Per minute rate
* Minimum fare
* Cancellation fee
* Surge eligibility
* Commission rate
* Driver incentive multiplier (optional)

All prices are expressed in **TJS (Tajik Somoni)**.

---

## 2. Common Pricing Formula

### 2.1 Base Fare Formula

```
base_fare = base_fee
           + (estimated_distance_km × per_km_rate)
           + (estimated_time_min × per_min_rate)
```

### 2.2 Final Fare Formula

```
final_fare = max(base_fare × surge_multiplier, minimum_fare)
```

---

## 3. Ride Types

---

## 3.1 ECONOMY

**Purpose:** Standard affordable rides.

### Parameters

| Parameter            | Value   |
| -------------------- | ------- |
| base_fee             | 5 TJS   |
| per_km_rate          | 2.5 TJS |
| per_min_rate         | 0.5 TJS |
| minimum_fare         | 10 TJS  |
| cancellation_fee     | 5 TJS   |
| surge_allowed        | YES     |
| max_surge_multiplier | 2.5x    |
| platform_commission  | 15%     |

### Rules

* Default ride type
* Eligible for surge pricing
* Surge capped at 2.5x
* Used for most passengers

---

## 3.2 COMFORT

**Purpose:** Higher quality vehicles.

### Parameters

| Parameter            | Value   |
| -------------------- | ------- |
| base_fee             | 8 TJS   |
| per_km_rate          | 3.5 TJS |
| per_min_rate         | 0.7 TJS |
| minimum_fare         | 15 TJS  |
| cancellation_fee     | 7 TJS   |
| surge_allowed        | YES     |
| max_surge_multiplier | 2.0x    |
| platform_commission  | 18%     |

### Rules

* Requires higher vehicle rating
* Limited surge cap (2.0x)
* Drivers must meet quality threshold

---

## 3.3 XL / VAN

**Purpose:** Group rides (4–6 passengers).

### Parameters

| Parameter            | Value   |
| -------------------- | ------- |
| base_fee             | 10 TJS  |
| per_km_rate          | 4.0 TJS |
| per_min_rate         | 0.8 TJS |
| minimum_fare         | 20 TJS  |
| cancellation_fee     | 10 TJS  |
| surge_allowed        | YES     |
| max_surge_multiplier | 3.0x    |
| platform_commission  | 20%     |

### Rules

* Larger vehicle required
* Higher surge cap due to scarcity
* Supply-sensitive pricing

---

## 3.4 DELIVERY

**Purpose:** Parcel delivery.

### Parameters

| Parameter            | Value   |
| -------------------- | ------- |
| base_fee             | 6 TJS   |
| per_km_rate          | 2.0 TJS |
| per_min_rate         | 0.4 TJS |
| minimum_fare         | 8 TJS   |
| cancellation_fee     | 4 TJS   |
| surge_allowed        | LIMITED |
| max_surge_multiplier | 1.8x    |
| platform_commission  | 12%     |

### Rules

* Surge limited to 1.8x
* No passenger waiting fee
* No ride duration adjustment after drop-off

---

## 4. Surge Pricing Rules

Surge is applied if:

```
demand / available_drivers > surge_threshold
```

### Default Threshold

```
surge_threshold = 1.2
```

### Surge Multiplier Formula

```
surge_multiplier = min(
    1 + ((demand_supply_ratio - 1) × surge_coefficient),
    max_surge_multiplier
)
```

Where:

```
surge_coefficient = 0.8
```

---

## 5. Cancellation Policy

### 5.1 Passenger Cancellation

| Condition           | Fee                            |
| ------------------- | ------------------------------ |
| Cancel within 2 min | 0                              |
| Driver en route     | cancellation_fee               |
| Driver arrived      | cancellation_fee + waiting_fee |

---

### 5.2 Driver Cancellation

* No charge to passenger
* Driver rating penalty
* Possible temporary restriction if frequent

---

## 6. Waiting Time Policy

After driver arrival:

```
free_wait_time = 3 minutes
waiting_fee_per_min = 0.5 TJS
```

Applied only to passenger rides (not delivery).

---

## 7. Commission Calculation

```
platform_commission = final_fare × commission_rate
driver_earnings = final_fare - platform_commission
```

---

## 8. Rounding Rules

* All fares rounded up to nearest 0.5 TJS
* Surge multiplier rounded to 2 decimal places

---

## 9. Fraud Protection Rules

* Surge capped per ride type
* Hard maximum fare limit per km
* Detect abnormal route inflation
* Reject pricing if distance > 3× direct route

---

# End of Document
