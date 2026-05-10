"""
========================================================
  ENTERPRISE PORTFOLIO WEB APP
  File: db.py
  Desc: Database abstraction layer — SQLite-backed,
        designed for drop-in swap to PostgreSQL/MySQL.
        Covers: Users, Projects, Skills, Experience,
        Education, Certificates, Messages, Audit Logs,
        Site Settings, Visitor Analytics.
========================================================
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "portfolio.db")

# ─────────────────────────────────────────────
#  Connection
# ─────────────────────────────────────────────
def get_db():
    """Return a SQLite connection with Row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ─────────────────────────────────────────────
#  Schema Bootstrap
# ─────────────────────────────────────────────
def init_db():
    """Create all tables and seed default data if first run."""
    with get_db() as conn:
        conn.executescript("""
        -- ── Users ─────────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name     TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            role          TEXT    NOT NULL DEFAULT 'staff',   -- admin | manager | staff
            mfa_enabled   INTEGER NOT NULL DEFAULT 0,
            avatar_url    TEXT    DEFAULT '',
            is_active     INTEGER NOT NULL DEFAULT 1,
            last_login    TEXT,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        -- ── Projects ──────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS projects (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            title         TEXT    NOT NULL,
            short_desc    TEXT    DEFAULT '',
            description   TEXT    DEFAULT '',
            tech_stack    TEXT    DEFAULT '',
            category      TEXT    DEFAULT '',
            image_url     TEXT    DEFAULT '',
            demo_url      TEXT    DEFAULT '',
            github_url    TEXT    DEFAULT '',
            is_featured   INTEGER NOT NULL DEFAULT 0,
            status        TEXT    NOT NULL DEFAULT 'active',  -- active | archived | draft
            sort_order    INTEGER DEFAULT 0,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
            updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        -- ── Skills ────────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS skills (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            category      TEXT    DEFAULT '',   -- Frontend | Backend | DevOps | etc.
            level         INTEGER DEFAULT 80,   -- 0–100
            icon          TEXT    DEFAULT '',
            sort_order    INTEGER DEFAULT 0,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        -- ── Experience ────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS experiences (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            company       TEXT    NOT NULL,
            role          TEXT    NOT NULL,
            location      TEXT    DEFAULT '',
            start_date    TEXT    DEFAULT '',
            end_date      TEXT    DEFAULT '',
            is_current    INTEGER DEFAULT 0,
            description   TEXT    DEFAULT '',
            sort_order    INTEGER DEFAULT 0,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        -- ── Education ─────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS educations (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            institution   TEXT    NOT NULL,
            degree        TEXT    DEFAULT '',
            field         TEXT    DEFAULT '',
            start_year    TEXT    DEFAULT '',
            end_year      TEXT    DEFAULT '',
            gpa           TEXT    DEFAULT '',
            description   TEXT    DEFAULT '',
            sort_order    INTEGER DEFAULT 0,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        -- ── Certificates ──────────────────────────────────────
        CREATE TABLE IF NOT EXISTS certificates (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            issuer        TEXT    DEFAULT '',
            issue_date    TEXT    DEFAULT '',
            credential_id TEXT    DEFAULT '',
            credential_url TEXT   DEFAULT '',
            image_url     TEXT    DEFAULT '',
            sort_order    INTEGER DEFAULT 0,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        -- ── Contact Messages ──────────────────────────────────
        CREATE TABLE IF NOT EXISTS contact_messages (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    NOT NULL,
            subject       TEXT    DEFAULT '',
            message       TEXT    NOT NULL,
            ip_address    TEXT    DEFAULT '',
            is_read       INTEGER NOT NULL DEFAULT 0,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        );

        -- ── Audit Logs ────────────────────────────────────────
        CREATE TABLE IF NOT EXISTS audit_logs (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER,
            action        TEXT    NOT NULL,
            detail        TEXT    DEFAULT '',
            ip_address    TEXT    DEFAULT '',
            user_agent    TEXT    DEFAULT '',
            created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        );

        -- ── Site Settings ─────────────────────────────────────
        CREATE TABLE IF NOT EXISTS settings (
            key           TEXT PRIMARY KEY,
            value         TEXT    DEFAULT ''
        );

        -- ── Visitor Analytics ─────────────────────────────────
        CREATE TABLE IF NOT EXISTS visitors (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address    TEXT    DEFAULT '',
            path          TEXT    DEFAULT '',
            user_agent    TEXT    DEFAULT '',
            referrer      TEXT    DEFAULT '',
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        );
        """)

        # ── Seed default admin user ────────────────────────────
        from werkzeug.security import generate_password_hash
        existing = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
        if not existing:
            conn.execute("""
                INSERT INTO users (full_name, email, password_hash, role, mfa_enabled)
                VALUES (?, ?, ?, ?, ?)
            """, (
                "Leo Nardi",
                "admin@portfolio.com",
                generate_password_hash("Admin@1234"),
                "admin",
                0,
            ))

        # ── Seed default settings ──────────────────────────────
        defaults = {
            "site_name":        "Leo Nardi",
            "site_tagline":     "Enterprise Professional Portfolio",
            "owner_name":       "Leo Nardi",
            "owner_title":      "Senior Full-Stack Engineer",
            "owner_email":      "leo@example.com",
            "owner_phone":      "+62 813-9188-653",
            "owner_location":   "Surabaya, East Java, Indonesia",
            "github_url":       "https://github.com/leohaww",
            "linkedin_url":     "https://www.linkedin.com/in/leo-nardi-b4213b402/",
            "instagram_url":    "https://www.instagram.com/leoo.ais/",
            "tiktok_url":       "https://www.tiktok.com/@nardi_91",
            "upwork_url":       "https://www.upwork.com/freelancers/~010abdd35dc04e6722?mp_source=share",
            "lynk_url":         "https://lynk.id/leo_nard",
            "twitter_url":      "",
            "meta_description": "Portfolio profesional Leo Nardi — Full-Stack Engineer berbasis di Surabaya.",
            "primary_color":    "#0a0a0f",
            "accent_color":     "#6c63ff",
            "owner_avatar":     "",
        }
        for k, v in defaults.items():
            conn.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

        # ── Seed sample skills ─────────────────────────────────
        skill_count = conn.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
        if skill_count == 0:
            sample_skills = [
                ("Python", "Backend", 92, "devicon-python-plain"),
                ("Flask / FastAPI", "Backend", 88, "devicon-flask-original"),
                ("PostgreSQL", "Database", 85, "devicon-postgresql-plain"),
                ("React.js", "Frontend", 80, "devicon-react-original"),
                ("Docker", "DevOps", 78, "devicon-docker-plain"),
                ("JavaScript", "Frontend", 85, "devicon-javascript-plain"),
                ("Redis", "Database", 72, "devicon-redis-plain"),
                ("AWS", "Cloud", 70, "devicon-amazonwebservices-original"),
                ("Git / GitHub", "DevOps", 90, "devicon-git-plain"),
                ("Tailwind CSS", "Frontend", 82, "devicon-tailwindcss-plain"),
            ]
            conn.executemany(
                "INSERT INTO skills (name, category, level, icon) VALUES (?,?,?,?)",
                sample_skills
            )

        conn.commit()
    print(f"[DB] Database initialized → {DB_PATH}")


# ─────────────────────────────────────────────
#  Users
# ─────────────────────────────────────────────
def create_user(full_name, email, password_hash, role="staff", mfa_enabled=0):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO users (full_name, email, password_hash, role, mfa_enabled) VALUES (?,?,?,?,?)",
            (full_name, email, password_hash, role, mfa_enabled)
        )
        conn.commit()


def get_user_by_email(email):
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE email=? AND is_active=1", (email,)).fetchone()


def get_user_by_id(uid):
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()


def get_all_users():
    with get_db() as conn:
        return conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()


def update_user(uid, **kwargs):
    allowed = ["full_name", "email", "role", "mfa_enabled", "is_active", "avatar_url"]
    sets = ", ".join(f"{k}=?" for k in kwargs if k in allowed)
    vals = [v for k, v in kwargs.items() if k in allowed]
    if sets:
        with get_db() as conn:
            conn.execute(f"UPDATE users SET {sets} WHERE id=?", (*vals, uid))
            conn.commit()


def delete_user(uid):
    with get_db() as conn:
        conn.execute("DELETE FROM users WHERE id=?", (uid,))
        conn.commit()


# ─────────────────────────────────────────────
#  Projects
# ─────────────────────────────────────────────
def create_project(title, short_desc="", description="", tech_stack="", category="",
                   image_url="", demo_url="", github_url="", is_featured=0, status="active"):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO projects (title, short_desc, description, tech_stack, category,
                                  image_url, demo_url, github_url, is_featured, status)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (title, short_desc, description, tech_stack, category,
              image_url, demo_url, github_url, is_featured, status))
        conn.commit()


def get_all_projects(featured_only=False, category="", search="", limit=None):
    sql = "SELECT * FROM projects WHERE 1=1"
    params = []
    if featured_only:
        sql += " AND is_featured=1"
    if category:
        sql += " AND category=?"
        params.append(category)
    if search:
        sql += " AND (title LIKE ? OR description LIKE ? OR tech_stack LIKE ?)"
        params.extend([f"%{search}%"] * 3)
    sql += " ORDER BY is_featured DESC, sort_order ASC, created_at DESC"
    if limit:
        sql += f" LIMIT {int(limit)}"
    with get_db() as conn:
        return conn.execute(sql, params).fetchall()


def get_project_by_id(pid):
    with get_db() as conn:
        return conn.execute("SELECT * FROM projects WHERE id=?", (pid,)).fetchone()


def update_project(pid, **kwargs):
    allowed = ["title", "short_desc", "description", "tech_stack", "category",
               "image_url", "demo_url", "github_url", "is_featured", "status", "sort_order"]
    sets = ", ".join(f"{k}=?" for k in kwargs if k in allowed)
    vals = [v for k, v in kwargs.items() if k in allowed]
    if sets:
        with get_db() as conn:
            conn.execute(
                f"UPDATE projects SET {sets}, updated_at=datetime('now') WHERE id=?",
                (*vals, pid)
            )
            conn.commit()


def delete_project(pid):
    with get_db() as conn:
        conn.execute("DELETE FROM projects WHERE id=?", (pid,))
        conn.commit()


# ─────────────────────────────────────────────
#  Skills
# ─────────────────────────────────────────────
def create_skill(name, category="", level=80, icon=""):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO skills (name, category, level, icon) VALUES (?,?,?,?)",
            (name, category, level, icon)
        )
        conn.commit()


def get_all_skills():
    with get_db() as conn:
        return conn.execute("SELECT * FROM skills ORDER BY category, level DESC").fetchall()


def update_skill(sid, **kwargs):
    allowed = ["name", "category", "level", "icon", "sort_order"]
    sets = ", ".join(f"{k}=?" for k in kwargs if k in allowed)
    vals = [v for k, v in kwargs.items() if k in allowed]
    if sets:
        with get_db() as conn:
            conn.execute(f"UPDATE skills SET {sets} WHERE id=?", (*vals, sid))
            conn.commit()


def delete_skill(sid):
    with get_db() as conn:
        conn.execute("DELETE FROM skills WHERE id=?", (sid,))
        conn.commit()


# ─────────────────────────────────────────────
#  Experience
# ─────────────────────────────────────────────
def create_experience(company, role, start_date="", end_date="", description="",
                      is_current=0, location=""):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO experiences (company, role, start_date, end_date, description, is_current, location)
            VALUES (?,?,?,?,?,?,?)
        """, (company, role, start_date, end_date, description, is_current, location))
        conn.commit()


def get_all_experiences():
    with get_db() as conn:
        return conn.execute("SELECT * FROM experiences ORDER BY is_current DESC, start_date DESC").fetchall()


def update_experience(eid, **kwargs):
    allowed = ["company", "role", "start_date", "end_date", "description", "is_current", "location", "sort_order"]
    sets = ", ".join(f"{k}=?" for k in kwargs if k in allowed)
    vals = [v for k, v in kwargs.items() if k in allowed]
    if sets:
        with get_db() as conn:
            conn.execute(f"UPDATE experiences SET {sets} WHERE id=?", (*vals, eid))
            conn.commit()


def delete_experience(eid):
    with get_db() as conn:
        conn.execute("DELETE FROM experiences WHERE id=?", (eid,))
        conn.commit()


# ─────────────────────────────────────────────
#  Education
# ─────────────────────────────────────────────
def create_education(institution, degree="", field="", start_year="", end_year="",
                     gpa="", description=""):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO educations (institution, degree, field, start_year, end_year, gpa, description)
            VALUES (?,?,?,?,?,?,?)
        """, (institution, degree, field, start_year, end_year, gpa, description))
        conn.commit()


def get_all_educations():
    with get_db() as conn:
        return conn.execute("SELECT * FROM educations ORDER BY start_year DESC").fetchall()


def update_education(eid, **kwargs):
    allowed = ["institution", "degree", "field", "start_year", "end_year", "gpa", "description"]
    sets = ", ".join(f"{k}=?" for k in kwargs if k in allowed)
    vals = [v for k, v in kwargs.items() if k in allowed]
    if sets:
        with get_db() as conn:
            conn.execute(f"UPDATE educations SET {sets} WHERE id=?", (*vals, eid))
            conn.commit()


def delete_education(eid):
    with get_db() as conn:
        conn.execute("DELETE FROM educations WHERE id=?", (eid,))
        conn.commit()


# ─────────────────────────────────────────────
#  Certificates
# ─────────────────────────────────────────────
def create_certificate(name, issuer="", issue_date="", credential_id="",
                       credential_url="", image_url=""):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO certificates (name, issuer, issue_date, credential_id, credential_url, image_url)
            VALUES (?,?,?,?,?,?)
        """, (name, issuer, issue_date, credential_id, credential_url, image_url))
        conn.commit()


def get_all_certificates():
    with get_db() as conn:
        return conn.execute("SELECT * FROM certificates ORDER BY issue_date DESC").fetchall()


def update_certificate(cid, **kwargs):
    allowed = ["name", "issuer", "issue_date", "credential_id", "credential_url", "image_url"]
    sets = ", ".join(f"{k}=?" for k in kwargs if k in allowed)
    vals = [v for k, v in kwargs.items() if k in allowed]
    if sets:
        with get_db() as conn:
            conn.execute(f"UPDATE certificates SET {sets} WHERE id=?", (*vals, cid))
            conn.commit()


def delete_certificate(cid):
    with get_db() as conn:
        conn.execute("DELETE FROM certificates WHERE id=?", (cid,))
        conn.commit()


# ─────────────────────────────────────────────
#  Contact Messages
# ─────────────────────────────────────────────
def create_contact_message(name, email, subject, message, ip_address=""):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO contact_messages (name, email, subject, message, ip_address)
            VALUES (?,?,?,?,?)
        """, (name, email, subject, message, ip_address))
        conn.commit()


def get_all_messages(limit=None):
    sql = "SELECT * FROM contact_messages ORDER BY created_at DESC"
    if limit:
        sql += f" LIMIT {int(limit)}"
    with get_db() as conn:
        return conn.execute(sql).fetchall()


def get_unread_count():
    with get_db() as conn:
        row = conn.execute("SELECT COUNT(*) as c FROM contact_messages WHERE is_read=0").fetchone()
        return row["c"] if row else 0


def mark_message_read(mid):
    with get_db() as conn:
        conn.execute("UPDATE contact_messages SET is_read=1 WHERE id=?", (mid,))
        conn.commit()


# ─────────────────────────────────────────────
#  Audit Logs
# ─────────────────────────────────────────────
def log_activity(user_id, action, detail="", ip_address="", user_agent=""):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO audit_logs (user_id, action, detail, ip_address, user_agent)
            VALUES (?,?,?,?,?)
        """, (user_id, action, detail, ip_address, user_agent))
        conn.commit()


def get_audit_logs(limit=100):
    with get_db() as conn:
        return conn.execute("""
            SELECT al.*, u.full_name, u.email
            FROM audit_logs al
            LEFT JOIN users u ON al.user_id = u.id
            ORDER BY al.created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()


# ─────────────────────────────────────────────
#  Site Settings
# ─────────────────────────────────────────────
def get_settings():
    with get_db() as conn:
        rows = conn.execute("SELECT key, value FROM settings").fetchall()
        return {r["key"]: r["value"] for r in rows}


def update_setting(key, value):
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, value))
        conn.commit()


# ─────────────────────────────────────────────
#  Visitor Analytics
# ─────────────────────────────────────────────
def log_visitor(ip, path, user_agent="", referrer=""):
    try:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO visitors (ip_address, path, user_agent, referrer) VALUES (?,?,?,?)",
                (ip, path, user_agent, referrer)
            )
            conn.commit()
    except Exception:
        pass  # Never crash on analytics failure


def get_visitor_stats():
    with get_db() as conn:
        total = conn.execute("SELECT COUNT(*) as c FROM visitors").fetchone()["c"]
        today = conn.execute(
            "SELECT COUNT(*) as c FROM visitors WHERE date(created_at)=date('now')"
        ).fetchone()["c"]
        this_week = conn.execute(
            "SELECT COUNT(*) as c FROM visitors WHERE created_at >= datetime('now','-7 days')"
        ).fetchone()["c"]
        top_pages = conn.execute("""
            SELECT path, COUNT(*) as visits
            FROM visitors
            GROUP BY path
            ORDER BY visits DESC
            LIMIT 10
        """).fetchall()
        daily_7d = conn.execute("""
            SELECT date(created_at) as day, COUNT(*) as visits
            FROM visitors
            WHERE created_at >= datetime('now','-7 days')
            GROUP BY day
            ORDER BY day ASC
        """).fetchall()
        return {
            "total": total,
            "today": today,
            "this_week": this_week,
            "top_pages": [dict(r) for r in top_pages],
            "daily_7d": [dict(r) for r in daily_7d],
        }
