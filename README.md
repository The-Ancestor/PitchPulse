# PitchPulse | High-Performance Athletic Analytics & Scouting Portal

PitchPulse is a production-ready, full-stack data architecture engine designed to track football player development, match engine conditioning, and athletic performance metric states (such as high-intensity sand training and recovery metrics). Built using a secure server-driven architecture, the system operates as an administrative scout dashboard with dynamic access layers.

## 🚀 Live Deployment
* **Live Application:** https://pitchpulse-rsj3.onrender.com/register
* **Database Infrastructure**

---

## 🛠️ System Architecture & Mental Model

PitchPulse is built as a robust monolith utilizing a structured multi-layered design pattern. This ensures data integrity remains bulletproof under operational stress while protecting downstream routes from unauthorized traffic or malicious payloads.

### 1. Database Layer (The Engine)
* **Engine:** PostgreSQL / SQLite
* **Object-Relational Mapping (ORM):** SQLAlchemy
* **Design Philosophy:** Data structures are highly normalized to eliminate redundancy. Relationships are strictly enforced at the database disk level using foreign key constraints, cascading deletions, and distinct unique flags (e.g., separating authentication data from individual player physical profiles).

### 2. Application Layer (The Guard & Controller)
* **Framework:** Flask (Python)
* **Session Management:** Flask-Login (Stateful Encrypted Session Cookies)
* **Security Matrix:** Implementation of Role-Based Access Control (RBAC). 
  * **Scout Role:** Full administrative read/write authorization (`GET`/`POST`) to onboard talent and log data matrixes.
  * **Player Role:** Restricted read-only token state preventing system manipulation.
  * **Password Defense:** Hashed using salted `PBKDF2` key-derivation transformations via `werkzeug.security` before entering persistence storage.

### 3. Presentation Layer (The Shield)
* **Engine:** Jinja2 Template Framework
* **Styling Matrix:** Tailwind CSS (Dark-mode high-performance configuration)
* **Rationale:** Decoupled layout structures enable future front-end evolution (e.g., swapping templates out for a dynamic React client interface) without modifying backend database schemas or business route logic.

---

## 💾 Core Tech Stack

* **Backend Engine:** Python 3.11+, Flask
* **Database Integration:** SQLAlchemy, Alembic (Migrations)
* **Security & Auth:** Flask-Login, Werkzeug Security
* **Environment Tooling:** Kali Linux development workspace, Git, Virtual Environments (`venv`)


⚙️ Local Development Installation

To run this system matrix inside a local Kali Linux environment or isolated workspace:

    Clone the repository:
    Bash

git clone [https://github.com/The-Ancestor/PitchPulse.git](https://github.com/The-Ancestor/PitchPulse.git)
cd PitchPulse

Initialize and trigger the virtual environment:
Bash

python3 -m venv venv
source venv/bin/activate

Compile package dependencies:
Bash

pip install -r requirements.txt

Map environment parameters & connect database:
Configure your database URI strings inside your environment or config.py files.

Initialize schemas & fire up the local server:
Bash

flask shell
>>> from app import db
>>> db.create_all()
>>> exit()
flask run





