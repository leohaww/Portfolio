"""
========================================================
  ENTERPRISE PORTFOLIO WEB APP
  File: app.py
  Desc: Main application entry point — Flask routes,
        middleware, auth, and blueprint registration.
========================================================
"""

import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, jsonify, send_from_directory,
    abort
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from db import (
    init_db, get_db,
    # User
    create_user, get_user_by_email, get_user_by_id, get_all_users, update_user, delete_user,
    # Projects
    create_project, get_all_projects, get_project_by_id, update_project, delete_project,
    # Skills
    create_skill, get_all_skills, update_skill, delete_skill,
    # Experience
    create_experience, get_all_experiences, update_experience, delete_experience,
    # Education
    create_education, get_all_educations, update_education, delete_education,
    # Certificates
    create_certificate, get_all_certificates, update_certificate, delete_certificate,
    # Contact
    create_contact_message, get_all_messages, get_unread_count, mark_message_read,
    # Audit
    log_activity, get_audit_logs,
    # Settings
    get_settings, update_setting,
    # Analytics
    log_visitor, get_visitor_stats,
)

# ─────────────────────────────────────────────
#  App Factory
# ─────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif", "webp", "pdf", "svg"}

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


def save_upload(file, subfolder="general"):
    if file and allowed_file(file.filename):
        folder = os.path.join(app.config["UPLOAD_FOLDER"], subfolder)
        os.makedirs(folder, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ts}_{secure_filename(file.filename)}"
        path = os.path.join(folder, filename)
        file.save(path)
        return f"uploads/{subfolder}/{filename}"
    return None


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("auth_login"))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("auth_login"))
            if session.get("role") not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator


def log_action(action, detail=""):
    if "user_id" in session:
        log_activity(session["user_id"], action, detail, request.remote_addr, request.user_agent.string)


@app.context_processor
def inject_globals():
    settings = get_settings()
    unread = get_unread_count() if "user_id" in session else 0
    return dict(
        site_settings=settings,
        unread_messages=unread,
        current_user=get_user_by_id(session["user_id"]) if "user_id" in session else None,
        now=datetime.now(),
    )


# ─────────────────────────────────────────────
#  Visitor Analytics Middleware
# ─────────────────────────────────────────────
@app.before_request
def track_visitor():
    if not request.path.startswith("/static") and not request.path.startswith("/admin"):
        log_visitor(
            ip=request.remote_addr,
            path=request.path,
            user_agent=request.user_agent.string,
            referrer=request.referrer or ""
        )


# ─────────────────────────────────────────────
#  PUBLIC ROUTES — Portfolio
# ─────────────────────────────────────────────
@app.route("/")
def index():
    projects = get_all_projects(featured_only=True, limit=6)
    skills = get_all_skills()
    experiences = get_all_experiences()
    educations = get_all_educations()
    certificates = get_all_certificates()
    stats = get_visitor_stats()
    settings = get_settings()
    return render_template(
        "index.html",
        projects=projects,
        skills=skills,
        experiences=experiences,
        educations=educations,
        certificates=certificates,
        stats=stats,
        settings=settings,
    )


@app.route("/projects")
def projects():
    category = request.args.get("category", "")
    search = request.args.get("q", "")
    all_projects = get_all_projects(category=category, search=search)
    return render_template("projects.html", projects=all_projects, category=category, search=search)


@app.route("/projects/<int:project_id>")
def project_detail(project_id):
    project = get_project_by_id(project_id)
    if not project:
        abort(404)
    return render_template("project_detail.html", project=project)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()
        if not all([name, email, subject, message]):
            flash("Semua field wajib diisi.", "danger")
        else:
            create_contact_message(name, email, subject, message, request.remote_addr)
            flash("Pesan Anda berhasil dikirim! Kami akan segera menghubungi Anda.", "success")
            return redirect(url_for("contact"))
    return render_template("contact.html")


# ─────────────────────────────────────────────
#  AUTH ROUTES
# ─────────────────────────────────────────────
@app.route("/auth/login", methods=["GET", "POST"])
def auth_login():
    if "user_id" in session:
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        otp_code = request.form.get("otp_code", "").strip()

        user = get_user_by_email(email)
        if user and check_password_hash(user["password_hash"], password):
            # MFA check (simplified — in production: TOTP via pyotp)
            if user["mfa_enabled"]:
                stored_otp = session.get("pending_otp")
                if not stored_otp or otp_code != stored_otp:
                    # Generate and "send" OTP (console simulation)
                    otp = str(secrets.randbelow(900000) + 100000)
                    session["pending_otp"] = otp
                    session["pending_user_id"] = user["id"]
                    print(f"[MFA OTP for {email}]: {otp}")
                    flash(f"Kode OTP telah dikirim ke email Anda. (Dev mode: cek console)", "info")
                    return render_template("auth/login.html", require_otp=True, email=email)
                session.pop("pending_otp", None)
                session.pop("pending_user_id", None)

            session.permanent = True
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["email"] = user["email"]
            session["name"] = user["full_name"]
            log_activity(user["id"], "LOGIN", f"Login sukses dari {request.remote_addr}", request.remote_addr, request.user_agent.string)
            flash(f"Selamat datang, {user['full_name']}!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Email atau password salah.", "danger")

    return render_template("auth/login.html", require_otp=False)


@app.route("/auth/logout")
@login_required
def auth_logout():
    log_action("LOGOUT", "User logout")
    session.clear()
    flash("Anda telah berhasil logout.", "info")
    return redirect(url_for("auth_login"))


# ─────────────────────────────────────────────
#  ADMIN ROUTES
# ─────────────────────────────────────────────
@app.route("/admin")
@login_required
def admin_dashboard():
    stats = {
        "total_projects": len(get_all_projects()),
        "total_skills": len(get_all_skills()),
        "total_messages": len(get_all_messages()),
        "unread_messages": get_unread_count(),
        "total_users": len(get_all_users()),
        "visitor_stats": get_visitor_stats(),
    }
    recent_logs = get_audit_logs(limit=10)
    recent_messages = get_all_messages(limit=5)
    return render_template("admin/dashboard.html", stats=stats, recent_logs=recent_logs, recent_messages=recent_messages)


# ── Projects CRUD ──────────────────────────
@app.route("/admin/projects")
@login_required
def admin_projects():
    projects = get_all_projects()
    return render_template("admin/projects.html", projects=projects)


@app.route("/admin/projects/create", methods=["GET", "POST"])
@login_required
@role_required("admin", "manager")
def admin_create_project():
    if request.method == "POST":
        image_url = ""
        if "image" in request.files:
            image_url = save_upload(request.files["image"], "projects") or ""
        data = {
            "title": request.form.get("title", ""),
            "description": request.form.get("description", ""),
            "short_desc": request.form.get("short_desc", ""),
            "tech_stack": request.form.get("tech_stack", ""),
            "category": request.form.get("category", ""),
            "demo_url": request.form.get("demo_url", ""),
            "github_url": request.form.get("github_url", ""),
            "image_url": image_url,
            "is_featured": 1 if request.form.get("is_featured") else 0,
            "status": request.form.get("status", "active"),
        }
        create_project(**data)
        log_action("CREATE_PROJECT", f"Proyek '{data['title']}' dibuat")
        flash("Proyek berhasil ditambahkan!", "success")
        return redirect(url_for("admin_projects"))
    return render_template("admin/project_form.html", project=None, action="create")


@app.route("/admin/projects/<int:pid>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin", "manager")
def admin_edit_project(pid):
    project = get_project_by_id(pid)
    if not project:
        abort(404)
    if request.method == "POST":
        image_url = project["image_url"]
        if "image" in request.files and request.files["image"].filename:
            image_url = save_upload(request.files["image"], "projects") or image_url
        data = {
            "title": request.form.get("title", ""),
            "description": request.form.get("description", ""),
            "short_desc": request.form.get("short_desc", ""),
            "tech_stack": request.form.get("tech_stack", ""),
            "category": request.form.get("category", ""),
            "demo_url": request.form.get("demo_url", ""),
            "github_url": request.form.get("github_url", ""),
            "image_url": image_url,
            "is_featured": 1 if request.form.get("is_featured") else 0,
            "status": request.form.get("status", "active"),
        }
        update_project(pid, **data)
        log_action("EDIT_PROJECT", f"Proyek ID {pid} diedit")
        flash("Proyek berhasil diperbarui!", "success")
        return redirect(url_for("admin_projects"))
    return render_template("admin/project_form.html", project=project, action="edit")


@app.route("/admin/projects/<int:pid>/delete", methods=["POST"])
@login_required
@role_required("admin")
def admin_delete_project(pid):
    delete_project(pid)
    log_action("DELETE_PROJECT", f"Proyek ID {pid} dihapus")
    flash("Proyek berhasil dihapus.", "success")
    return redirect(url_for("admin_projects"))


# ── Skills CRUD ──────────────────────────────
@app.route("/admin/skills")
@login_required
def admin_skills():
    skills = get_all_skills()
    return render_template("admin/skills.html", skills=skills)


@app.route("/admin/skills/create", methods=["POST"])
@login_required
def admin_create_skill():
    create_skill(
        name=request.form.get("name", ""),
        category=request.form.get("category", ""),
        level=int(request.form.get("level", 50)),
        icon=request.form.get("icon", ""),
    )
    log_action("CREATE_SKILL", f"Skill '{request.form.get('name')}' ditambahkan")
    flash("Skill berhasil ditambahkan!", "success")
    return redirect(url_for("admin_skills"))


@app.route("/admin/skills/<int:sid>/delete", methods=["POST"])
@login_required
@role_required("admin")
def admin_delete_skill(sid):
    delete_skill(sid)
    flash("Skill berhasil dihapus.", "success")
    return redirect(url_for("admin_skills"))


# ── Experience CRUD ──────────────────────────
@app.route("/admin/experience")
@login_required
def admin_experience():
    exps = get_all_experiences()
    return render_template("admin/experience.html", experiences=exps)


@app.route("/admin/experience/create", methods=["POST"])
@login_required
def admin_create_experience():
    create_experience(
        company=request.form.get("company", ""),
        role=request.form.get("role", ""),
        start_date=request.form.get("start_date", ""),
        end_date=request.form.get("end_date", ""),
        description=request.form.get("description", ""),
        is_current=1 if request.form.get("is_current") else 0,
        location=request.form.get("location", ""),
    )
    flash("Pengalaman berhasil ditambahkan!", "success")
    return redirect(url_for("admin_experience"))


@app.route("/admin/experience/<int:eid>/delete", methods=["POST"])
@login_required
@role_required("admin")
def admin_delete_experience(eid):
    delete_experience(eid)
    flash("Pengalaman berhasil dihapus.", "success")
    return redirect(url_for("admin_experience"))


# ── Education CRUD ───────────────────────────
@app.route("/admin/education")
@login_required
def admin_education():
    edus = get_all_educations()
    return render_template("admin/education.html", educations=edus)


@app.route("/admin/education/create", methods=["POST"])
@login_required
def admin_create_education():
    create_education(
        institution=request.form.get("institution", ""),
        degree=request.form.get("degree", ""),
        field=request.form.get("field", ""),
        start_year=request.form.get("start_year", ""),
        end_year=request.form.get("end_year", ""),
        gpa=request.form.get("gpa", ""),
        description=request.form.get("description", ""),
    )
    flash("Pendidikan berhasil ditambahkan!", "success")
    return redirect(url_for("admin_education"))


@app.route("/admin/education/<int:eid>/delete", methods=["POST"])
@login_required
@role_required("admin")
def admin_delete_education(eid):
    delete_education(eid)
    flash("Pendidikan berhasil dihapus.", "success")
    return redirect(url_for("admin_education"))


# ── Certificates CRUD ────────────────────────
@app.route("/admin/certificates")
@login_required
def admin_certificates():
    certs = get_all_certificates()
    return render_template("admin/certificates.html", certificates=certs)


@app.route("/admin/certificates/create", methods=["POST"])
@login_required
def admin_create_certificate():
    image_url = ""
    if "image" in request.files:
        image_url = save_upload(request.files["image"], "certificates") or ""
    create_certificate(
        name=request.form.get("name", ""),
        issuer=request.form.get("issuer", ""),
        issue_date=request.form.get("issue_date", ""),
        credential_id=request.form.get("credential_id", ""),
        credential_url=request.form.get("credential_url", ""),
        image_url=image_url,
    )
    flash("Sertifikat berhasil ditambahkan!", "success")
    return redirect(url_for("admin_certificates"))


@app.route("/admin/certificates/<int:cid>/delete", methods=["POST"])
@login_required
@role_required("admin")
def admin_delete_certificate(cid):
    delete_certificate(cid)
    flash("Sertifikat berhasil dihapus.", "success")
    return redirect(url_for("admin_certificates"))


# ── Messages ────────────────────────────────
@app.route("/admin/messages")
@login_required
def admin_messages():
    messages = get_all_messages()
    return render_template("admin/messages.html", messages=messages)


@app.route("/admin/messages/<int:mid>/read", methods=["POST"])
@login_required
def admin_read_message(mid):
    mark_message_read(mid)
    return redirect(url_for("admin_messages"))


# ── Users (Admin only) ───────────────────────
@app.route("/admin/users")
@login_required
@role_required("admin")
def admin_users():
    users = get_all_users()
    return render_template("admin/users.html", users=users)


@app.route("/admin/users/create", methods=["POST"])
@login_required
@role_required("admin")
def admin_create_user():
    password = request.form.get("password", secrets.token_urlsafe(12))
    create_user(
        full_name=request.form.get("full_name", ""),
        email=request.form.get("email", "").lower(),
        password_hash=generate_password_hash(password),
        role=request.form.get("role", "staff"),
        mfa_enabled=1 if request.form.get("mfa_enabled") else 0,
    )
    log_action("CREATE_USER", f"User baru '{request.form.get('email')}' dibuat")
    flash(f"User berhasil dibuat! Password sementara: {password}", "success")
    return redirect(url_for("admin_users"))


@app.route("/admin/users/<int:uid>/delete", methods=["POST"])
@login_required
@role_required("admin")
def admin_delete_user(uid):
    if uid == session["user_id"]:
        flash("Anda tidak bisa menghapus akun sendiri.", "danger")
    else:
        delete_user(uid)
        log_action("DELETE_USER", f"User ID {uid} dihapus")
        flash("User berhasil dihapus.", "success")
    return redirect(url_for("admin_users"))


# ── Audit Logs ───────────────────────────────
@app.route("/admin/audit-logs")
@login_required
@role_required("admin", "manager")
def admin_audit_logs():
    logs = get_audit_logs(limit=200)
    return render_template("admin/audit_logs.html", logs=logs)


# ── Settings ────────────────────────────────
@app.route("/admin/settings", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_settings():
    if request.method == "POST":
        for key in ["site_name", "site_tagline", "owner_name", "owner_title",
                    "owner_email", "owner_phone", "owner_location",
                    "github_url", "linkedin_url", "twitter_url", "instagram_url",
                    "tiktok_url", "upwork_url", "lynk_url",
                    "meta_description", "primary_color", "accent_color"]:
            val = request.form.get(key, "")
            update_setting(key, val)

        if "avatar" in request.files and request.files["avatar"].filename:
            avatar_path = save_upload(request.files["avatar"], "avatars")
            if avatar_path:
                update_setting("owner_avatar", avatar_path)

        log_action("UPDATE_SETTINGS", "Pengaturan situs diperbarui")
        flash("Pengaturan berhasil disimpan!", "success")
        return redirect(url_for("admin_settings"))
    return render_template("admin/settings.html")


# ── Analytics API ────────────────────────────
@app.route("/admin/analytics/data")
@login_required
def admin_analytics_data():
    stats = get_visitor_stats()
    return jsonify(stats)


# ─────────────────────────────────────────────
#  API ENDPOINTS (JSON)
# ─────────────────────────────────────────────
@app.route("/api/projects")
def api_projects():
    projects = get_all_projects()
    return jsonify([dict(p) for p in projects])


@app.route("/api/skills")
def api_skills():
    skills = get_all_skills()
    return jsonify([dict(s) for s in skills])


@app.route("/api/health")
def api_health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


# ─────────────────────────────────────────────
#  Error Handlers
# ─────────────────────────────────────────────
@app.errorhandler(403)
def forbidden(e):
    return render_template("errors/403.html"), 403


@app.errorhandler(404)
def not_found(e):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("errors/500.html"), 500


# ─────────────────────────────────────────────
#  Bootstrap
# ─────────────────────────────────────────────
if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
