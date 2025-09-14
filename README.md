
# AI Query Interface App - Made by Erin James
## FastAPI + React Native (Expo) Project

This project combines a **FastAPI backend** with a **React Native frontend (Expo)** to provide a natural language interface for querying structured data.

---

## Prerequisites

- Python 3.8+
- Node.js and npm
- Expo CLI (install via: `npm install -g expo-cli`)
- Android emulator or physical device with USB debugging enabled

---

## Setup Instructions

### 1. Clone the Repository
Download or clone the project files to your local machine.

---

### 2. Configure API Endpoint
Update the IP address in `api.ts` to match your local machine’s IP.

---

### 3. Set Up the Backend (FastAPI)

- **Create and activate a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate
````

> **IMPORTANT (Windows users):**
>
> ```bash
> venv\Scripts\activate
> ```

* **Install dependencies:**

```bash
pip install -r requirements.txt
```

* **Start the FastAPI server:**

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

### 4. Set Up the Frontend (React Native)

* **Start the Expo development server in a separate terminal:**

```bash
npx expo start
```

* **When prompted:**

  * Press **`a`** to launch on Android
  * Press **`w`** to open in your browser

Ensure an Android emulator is running or a physical device is connected.

---

### 5. Test the Application

Enter natural language queries such as:

* `Who is the top customer?`
* `What is the top item?`
* `Show items under $5`

---

## Notes

* The backend must be running and accessible from the device or emulator.
* Ensure your local IP is reachable from the emulator or physical device.

---




https://github.com/user-attachments/assets/22dd5e82-d455-46b4-b10b-9336a265ec2a



Architecture and Approach can be found here: https://docs.google.com/document/d/1W60SNneXM8Dkd_KnyjIiCqf24luVggmKzlDjqrolKYk/edit?usp=sharing
