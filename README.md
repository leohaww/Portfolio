# Enterprise Portfolio Web App

Aplikasi web portfolio enterprise berbasis **Python + Flask** dengan sistem admin
lengkap, RBAC, Audit Trail, MFA, dan Analytics.

---

## 🚀 Cara Menjalankan di PyCharm

### 1. Clone / Extract project ini
```
portfolio_app/
├── app.py           ← Entry point utama
├── db.py            ← Database layer (SQLite)
├── requirements.txt
├── static/
│   ├── css/main.css
│   ├── js/main.js
│   └── uploads/
└── templates/
    ├── base.html
    ├── index.html
    ├── projects.html
    ├── project_detail.html
    ├── contact.html
    ├── auth/login.html
    ├── admin/
    │   ├── dashboard.html
    │   ├── projects.html
    │   ├── project_form.html
    │   ├── skills.html
    │   ├── experience.html
    │   ├── education.html
    │   ├── certificates.html
    │   ├── messages.html
    │   ├── users.html
    │   ├── audit_logs.html
    │   └── settings.html
    ├── partials/
    │   ├── admin_sidebar.html
    │   └── admin_topbar.html
    └── errors/
        ├── 403.html
        ├── 404.html
        └── 500.html
```

### 2. Buat Virtual Environment di PyCharm
```
File → Settings → Project → Python Interpreter → Add Interpreter → Virtualenv
```
Atau lewat terminal:
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac / Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Run di PyCharm
```
Run → Edit Configurations → Python
Script path  : path/ke/portfolio_app/app.py
Working dir  : path/ke/portfolio_app/
```

### 5. Jalankan
```bash
python app.py
```
Buka browser: **http://localhost:5000**

---

## 🔐 Default Admin Login
| Field    | Value                  |
|----------|------------------------|
| Email    | `admin@portfolio.com`  |
| Password | `Admin@1234`           |
| Role     | Admin                  |

Login admin: **http://localhost:5000/auth/login**
Dashboard  : **http://localhost:5000/admin**

---

## 📋 Fitur Enterprise yang Diimplementasikan

### Security & IAM
- ✅ **MFA (Multi-Factor Authentication)** — OTP 6-digit via console (dev mode)
- ✅ **RBAC** — 3 role: Admin, Manager, Staff dengan hak akses berbeda
- ✅ **Audit Trail** — Setiap aksi user tercatat (login, CRUD, delete)
- ✅ **Session Management** — Session persistent 8 jam
- ✅ **Password Hashing** — Werkzeug PBKDF2

### Workflow & Data
- ✅ **CRUD Lengkap** — Projects, Skills, Experience, Education, Certificates
- ✅ **File Upload** — Gambar project, avatar, sertifikat (max 16MB)
- ✅ **Search & Filter** — Pencarian real-time di semua tabel
- ✅ **Smart Routing** — Redirect otomatis berdasarkan role

### Analytics & Reporting
- ✅ **Visitor Analytics** — Total, harian, weekly, top pages
- ✅ **Interactive Chart** — Grafik traffic 7 hari (Chart.js)
- ✅ **KPI Dashboard** — 4 metric card utama
- ✅ **Contact Inbox** — Pesan masuk dengan status read/unread

### UI / UX
- ✅ **Responsive** — Mobile, tablet, desktop
- ✅ **Dark Enterprise Theme** — Deep navy + electric violet
- ✅ **Smooth Animations** — Reveal on scroll, counter, skill bars
- ✅ **Toast Notifications** — Flash messages dengan auto-dismiss
- ✅ **Devicon Integration** — 1000+ ikon teknologi

---

## 🛠 Tech Stack

| Layer      | Teknologi                          |
|------------|------------------------------------|
| Backend    | Python 3.10+, Flask 3.0            |
| Database   | SQLite (dev) → swap ke PostgreSQL  |
| Frontend   | Jinja2, Vanilla JS, CSS Variables  |
| Charts     | Chart.js 4.4                       |
| Icons      | Font Awesome 6 + Devicon           |
| Fonts      | Syne, Space Grotesk, JetBrains Mono|

---

## 🔄 Upgrade ke Production

```bash
# Ganti SQLite → PostgreSQL di db.py:
# DB_PATH → DATABASE_URL env variable
# sqlite3 → psycopg2

# Gunakan Gunicorn:
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Set environment variable:
SECRET_KEY=your-super-secret-key-here
```

---

## 📁 Database
Database otomatis dibuat saat pertama run: `portfolio.db`
Data seed default: admin user + 10 sample skills.

---

*Built with ❤️ — Enterprise Portfolio v1.0*
