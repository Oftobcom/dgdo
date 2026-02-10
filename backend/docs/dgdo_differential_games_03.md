# 🎯 Game-Theoretic Driver Behavior Model

## 1️⃣ Driver as a rational agent

Each driver ( i ) is modeled as a **utility-maximizing agent** who repeatedly faces offers from the platform.

At each offer time ( t ), the driver chooses an action:

[
a_i(t) \in { \text{ACCEPT}, \text{REJECT}, \text{IGNORE} }
]

This is a **repeated decision problem under uncertainty**.

---

## 2️⃣ Driver state variables

Each driver has an internal (partially observable) state:

[
s_i(t) =
\big(
x_i(t),;
v_i(t),;
e_i(t),;
\theta_i
\big)
]

Where:

* ( x_i(t) ) — location
* ( v_i(t) ) — velocity / mobility
* ( e_i(t) ) — expected future demand (belief)
* ( \theta_i ) — private acceptance threshold

📌 ( \theta_i ) is **not known** to the platform.

---

## 3️⃣ Driver payoff function

For a given trip offer ( k ), driver payoff is:

[
U_i^{(k)} =
\underbrace{F_k}_{\text{fare}}

* \alpha \cdot \underbrace{D_{ik}}_{\text{pickup distance}}
* \beta \cdot \underbrace{T_{ik}}_{\text{time cost}}

- \gamma \cdot \underbrace{E_i}_{\text{future opportunity}}
  ]

Interpretation:

* Long pickup → reject
* Low fare → reject
* High expected future demand → reject (strategic waiting)

---

## 4️⃣ Driver decision rule (best response)

Driver follows a **threshold strategy**:

[
\text{ACCEPT} \iff U_i^{(k)} \ge \theta_i
]

Otherwise:

* REJECT if active decision
* IGNORE if cognitively / operationally overloaded

📌 This is a **dominant strategy** given fixed beliefs.

---

## 5️⃣ Platform–Driver interaction as a Stackelberg game

This is a **leader–follower game**:

* **Leader**: Platform
  chooses which driver to offer and at what conditions.
* **Follower**: Driver
  responds optimally (accept/reject).

Formally:

[
\max_{\sigma_P}
;\mathbb{E}[U_P(\sigma_P, \sigma_i^*)]
\quad
\text{s.t.}
\quad
\sigma_i^* = \arg\max_{\sigma_i} U_i
]

This is **Stackelberg equilibrium**.

---

## 6️⃣ Learning driver behavior (belief update)

Platform does not know ( \theta_i ), but observes actions.

After rejection:
[
\mathbb{P}(\theta_i > U_i^{(k)}) \uparrow
]

MVP belief update:

```text
accept_rate_i = accepted / offered
```

Advanced (Bayesian):
[
\theta_i \sim \text{Beta}(\alpha_i, \beta_i)
]

Each accept/reject updates the posterior.

---

## 7️⃣ Strategic driver behaviors (important!)

Even in MVP, drivers behave strategically:

### 🧠 Behavior A — Cherry-picking

Driver rejects short / cheap trips.

### 🧠 Behavior B — Waiting for surge

Driver rejects now to get better future offers.

### 🧠 Behavior C — Fatigue

Driver ignores offers late in shift.

📌 All three are captured by ( \theta_i(t) ) being **time-dependent**.

---

## 8️⃣ MVP implementation (no heavy math)

### Practical proxy for ( \theta_i )

```text
effective_accept_score =
fare
- w1 * pickup_distance
- w2 * ETA
- w3 * recent_rejects
```

Decision:

```text
ACCEPT if score >= 0
```

The platform **does not compute this** —
it **infers it statistically**.

---

## 9️⃣ Coupling with matching engine

Matching engine chooses driver ( i ) that maximizes:

[
\mathbb{P}_i(\text{ACCEPT}) \cdot
\frac{1}{\text{ETA}_i}
]

This is **expected utility maximization**.

---

## 🔟 Dynamic / differential extension (future)

Let driver motion obey:

[
\dot{x}_i(t) = u_i(t)
]

Driver control ( u_i(t) ) chosen to maximize:

[
J_i = \int_0^T
\big(
\text{income} - \text{effort}
\big),dt
]

Platform control:
[
u_P(t) = \text{pricing + matching}
]

➡️ This becomes a **differential game**:

* many drivers
* one platform
* equilibrium = spatial supply balance

This is exactly where **mean-field games** enter.

---

## 11️⃣ Why this model is powerful

✅ Explains rejects naturally
✅ Predicts waiting behavior
✅ Compatible with FSM
✅ MVP-safe
✅ Mathematically deep
✅ Extendable to pricing & control

---

## Final insight (key takeaway)

> **Drivers are not workers reacting to commands.
> They are strategic agents playing a repeated game against the platform.**

DG Do wins by **modeling this explicitly**, not fighting it.

---

If you want next, we can:

* derive **platform optimal policy**
* integrate **pricing + matching**
* formalize **mean-field equilibrium**
* turn this into **RL / control code**

Say the next level.
