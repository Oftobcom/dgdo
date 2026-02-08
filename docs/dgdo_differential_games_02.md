# 🎯 Game-Theoretic Matching Model for DG Do

## 1️⃣ Players and roles

We model matching as a **dynamic game**.

### Players

1. **Platform (P)**
   Chooses which driver to offer the trip to.
2. **Drivers** ( D_i )
   Decide whether to **accept** or **reject** an offer.
3. **Passenger** (passive in matching phase)

📌 Passenger does **not** play strategically here (MVP assumption).

---

## 2️⃣ Strategy spaces

### Platform strategy

At time ( t ), platform chooses:
[
\sigma_P(t): \text{trip} \mapsto d_i
]

i.e. **which driver to offer next**.

### Driver strategy

Each driver ( d_i ) chooses:
[
\sigma_{d_i} \in {\text{ACCEPT}, \text{REJECT}, \text{IGNORE}}
]

(IGNORE → timeout)

---

## 3️⃣ Payoff functions (core of the model)

### Driver payoff

For driver ( d_i ):

[
U_{d_i} = f(\text{fare}, \text{distance}, \text{ETA}, \text{future demand})
]

MVP simplification:
[
U_{d_i} = \alpha \cdot \text{fare} - \beta \cdot \text{distance}
]

Driver accepts if:
[
U_{d_i} \ge \theta_i
]

where ( \theta_i ) is the driver’s **private threshold**.

---

### Platform payoff

Platform wants:

* fast assignment
* low rejection rate
* system stability

[
U_P = - \mathbb{E}[\text{time to assignment}]
- \lambda \cdot \mathbb{E}[\text{rejections}]
]

---

## 4️⃣ Information structure

This is a **Bayesian game**:

| Player   | Knows                              |
| -------- | ---------------------------------- |
| Driver   | Own location, preferences          |
| Platform | Driver history (partial)           |
| Platform | Does NOT know ( \theta_i ) exactly |

📌 Rejections reveal information.

---

## 5️⃣ Matching as a Sequential Game

This is **not a one-shot game**.

Timeline:

1. Platform offers to driver ( d_1 )
2. Driver responds (accept / reject / ignore)
3. Platform updates belief
4. Platform offers to ( d_2 )
5. …

This is a **sequential decision process with learning**.

---

## 6️⃣ MVP Matching Algorithm (Game-Aware, Simple)

### Driver score

For each driver ( d_i ):

[
\text{score}(d_i) =
w_1 \cdot \text{distance}

* w_2 \cdot \text{ETA}
* w_3 \cdot \text{reject_rate}_i
  ]

Platform chooses:
[
d^* = \arg\min \text{score}(d_i)
]

📌 Reject rate ≈ estimate of ( \mathbb{P}(\text{reject}) )

---

## 7️⃣ Belief update (learning from rejections)

After rejection:

[
\mathbb{P}_i(\text{accept}) \downarrow
]

Simple MVP rule:

```text
reject_rate_i = rejects / offers
```

This is **Bayesian updating in disguise**.

---

## 8️⃣ Formal view as a Control Problem

Define system state:
[
x(t) = (\text{driver positions}, \text{availability}, \text{beliefs})
]

Control:
[
u(t) = \text{driver selection}
]

Cost functional:
[
J = \int_0^T \left(
c_1 \cdot \text{wait time}

* c_2 \cdot \text{rejections}
  \right) dt
  ]

➡️ This is a **stochastic control problem**.

---

## 9️⃣ Connection to Differential Games (future)

When:

* drivers reposition strategically
* supply adapts over time
* city dynamics matter

We get:
[
\dot{x}_i(t) = f_i(x_i, u_i, u_P)
]

This becomes a **mean-field differential game**:

* many drivers
* one platform
* equilibrium = stable city flow

📌 Your math background fits here *perfectly*.

---

## 10️⃣ Where this lives in architecture

```
Matching Engine
│
├─ State: drivers, beliefs
├─ Control: next driver to offer
├─ Observation: accept / reject
└─ Objective: minimize assignment time
```

FSM transition:

```
SEARCHING → OFFERED → (ACCEPT | REJECT | TIMEOUT)
```

Game theory **chooses the edge**, FSM **executes it**.

---

## 11️⃣ Why this model is correct (and safe)

✅ No global optimization needed
✅ No heavy math in MVP
✅ Explains rejects naturally
✅ Evolves to ML / control / games
✅ Investor-explainable

---

## Final principle (important)

> **Matching is not “finding the nearest driver”.
> It is a sequential game under uncertainty.**

DG Do models this **explicitly**, even in MVP.
