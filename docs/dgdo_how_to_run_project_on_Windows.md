# DG Do MVP

## How to run and test this project on Windows, WSL

Here is the **exact, step-by-step process** to run and test this MVP project.

---

# ✅ 1. REQUIRED: Make sure Docker Desktop is installed

On **Windows 10**, Docker can only run through **Docker Desktop**.

Install it (if not already):
[https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

During installation, ensure:

✔ **Enable WSL 2 integration**
✔ **Integrate with your Ubuntu distribution**

After install:

1. Open Docker Desktop
2. Go to **Settings → Resources → WSL Integration**
3. Enable your Ubuntu (should look like):

```
[✓] Enable integration with Ubuntu
```

---

# ✅ 2. Check that Docker works inside WSL Ubuntu

Open **Ubuntu (WSL)** and run:

```bash
docker version
docker compose version
```

Both must work.

If you get “Cannot connect to the Docker daemon”:

Run:

```bash
sudo service docker stop
```

Then restart Docker Desktop on Windows.

---

# 🧩 3. Clone your project inside WSL

In **Ubuntu WSL terminal**:

```bash
cd ~
git clone https://github.com/your-username/dgdo.git
cd dgdo
```

Do **NOT** clone into Windows filesystem (`/mnt/c/...`).
Docker becomes extremely slow there.

Good:

```
/home/rahmatjon/dgdo
```

Bad:

```
/mnt/c/Users/...
```

---

# 🚀 4. Run the whole MVP

Inside WSL Ubuntu:

```bash
docker compose up --build
```

This starts:

| Component           | URL                                            |
| ------------------- | ---------------------------------------------- |
| FastAPI API Gateway | [http://localhost:8000](http://localhost:8000) |
| C++ Matching Engine | [http://localhost:8001](http://localhost:8001) |
| Admin Panel         | [http://localhost:8002](http://localhost:8002) |
| PostgreSQL          | localhost:5432                                 |

You will see logs from:

* api
* matching
* admin
* postgres

---

# 🌐 5. Access services from your Windows browser

Even if everything runs in **WSL**,
you can open it in **Chrome/Firefox on Windows**:

### ✔ FastAPI

[http://localhost:8000/docs](http://localhost:8000/docs)

### ✔ C++ Matching Engine

[http://localhost:8001](http://localhost:8001)

### ✔ Admin Panel

[http://localhost:8002](http://localhost:8002)

### ✔ Postgres

host: `localhost`
port: `5432`

This works because Docker Desktop exposes ports globally.

---

# 🛠 6. Test the MVP (Step-by-step)

## 1) Passenger Registration

POST in Swagger:

```
POST /passengers/register
```

Body:

```json
{
  "name": "John",
  "phone": "+123456"
}
```

## 2) Create Trip Request

```
POST /trips/request
```

## 3) Driver WebSocket

You can test using **websocat** or a browser WebSocket client:

```
ws://localhost:8000/ws/drivers/<driver_id>
```

Send:

```json
{
  "lat": 40.12,
  "lon": 69.33,
  "status": "available"
}
```

## 4) Admin Panel

Open:

[http://localhost:8002](http://localhost:8002)

You should see drivers & trips.

---

# ⚠ Common Windows 10 + WSL Issues (and Fixes)

### 🔸 Error: "Cannot connect to docker daemon"

Fix:

* Start Docker Desktop
* Enable WSL integration
* Restart Ubuntu

### 🔸 Ports not available

Close other apps using 8000–8002, 5432.

### 🔸 Poor performance

Move your project **OUT** of `/mnt/c/`.

---

# ⚠ How to open the Ubuntu terminal in Windows WSL

Here are **all the ways** to open your Ubuntu terminal on Windows (WSL). Use whichever is easiest for you.

---

## ✅ **1. Open Ubuntu from Start Menu**

The simplest:

1. Press **Windows key**
2. Type **“Ubuntu”**
3. Click **Ubuntu** (for example: *Ubuntu 22.04 LTS*)

This opens the WSL terminal.

---

## ✅ **2. Open with Windows Terminal**

If you have Windows Terminal installed:

1. Open **Windows Terminal**
2. Click the down arrow (▼)
3. Choose **Ubuntu**

---

## ✅ **3. Run from Command Prompt**

Open **cmd** and type:

```
wsl
```

or directly:

```
ubuntu
```

---

## ✅ **4. Run from PowerShell**

Open **PowerShell** and type:

```
wsl
```

or:

```
ubuntu
```

If you have multiple distros:

```
wsl -l -v
wsl -d Ubuntu
```

---

## ✅ **5. Run a specific command in Ubuntu**

Without opening a full terminal:

```
wsl ls -la
```

---

## ⚠️ If Ubuntu doesn't open

Try:

```
wsl --set-default-version 2
wsl --set-default Ubuntu
```

Or restart WSL:

```
wsl --shutdown
```

---

# ⚠ How to check whether Ubuntu is installed correctly on WSL

To check whether **Ubuntu is installed correctly on WSL**, run these commands in **PowerShell** or **Command Prompt**.

---

## ✅ **STEP 1 — Check if WSL detects your Ubuntu**

Open **PowerShell** and run:

```powershell
wsl -l -v
```

You should see something like:

```
  NAME            STATE           VERSION
* Ubuntu          Running         2
```

### ✔ If “Ubuntu” appears → it is installed

### ❌ If nothing appears → Ubuntu is not installed or WSL is broken

---

## ✅ **STEP 2 — Try launching Ubuntu**

In PowerShell:

```powershell
ubuntu
```

or:

```powershell
wsl -d Ubuntu
```

✔ If it opens → Ubuntu works
❌ If you get an error → tell me the exact message

---

## ✅ **STEP 3 — Check WSL version (important)**

Still in PowerShell:

```powershell
wsl --status
```

Expected output:

* Default version: **2**
* Kernel: non-zero
* WSL2 enabled

---

## ✅ **STEP 4 — Check the Ubuntu file system exists**

Run:

```powershell
explorer.exe \\wsl$
```

This should open Windows Explorer showing:

```
Ubuntu/
   home/
   usr/
   bin/
```

---

## 👍 If everything works

Then your Ubuntu is installed correctly.

## ⚠️ If something fails

Please copy the output of:

```
wsl -l -v
```

and look for a solution online. Sorry.
