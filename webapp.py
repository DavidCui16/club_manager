from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import database as db
import os

app = Flask(__name__)
app.secret_key = "club_manager_secret_key_2026"

ADMIN_PASSWORD = "admin123"


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        error = "密码错误"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    total_income, total_expense, balance = db.get_finance_summary()
    member_count = len(db.get_all_members())
    event_count = len(db.get_all_events())
    return render_template(
        "index.html",
        member_count=member_count,
        event_count=event_count,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
    )


# ---------- Members ----------
@app.route("/members")
@login_required
def members():
    return render_template("members.html")


@app.route("/api/members")
@login_required
def api_members():
    keyword = request.args.get("search", "")
    rows = db.search_members(keyword) if keyword else db.get_all_members()
    return jsonify([dict(r) for r in rows])


@app.route("/api/members", methods=["POST"])
@login_required
def api_add_member():
    data = request.get_json()
    db.add_member(
        data["name"], data.get("student_id", ""), data.get("phone", ""),
        data.get("email", ""), data.get("department", ""), data.get("notes", ""),
    )
    return jsonify({"ok": True})


@app.route("/api/members/<int:member_id>", methods=["PUT"])
@login_required
def api_update_member(member_id):
    data = request.get_json()
    db.update_member(
        member_id, data["name"], data.get("student_id", ""), data.get("phone", ""),
        data.get("email", ""), data.get("department", ""),
        data.get("status", "active"), data.get("notes", ""),
    )
    return jsonify({"ok": True})


@app.route("/api/members/<int:member_id>", methods=["DELETE"])
@login_required
def api_delete_member(member_id):
    db.delete_member(member_id)
    return jsonify({"ok": True})


@app.route("/api/members/import", methods=["POST"])
@login_required
def api_import_members():
    if "file" not in request.files:
        return jsonify({"ok": False, "msg": "未选择文件"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"ok": False, "msg": "未选择文件"}), 400
    if not file.filename.lower().endswith((".xlsx", ".xls")):
        return jsonify({"ok": False, "msg": "仅支持 .xlsx / .xls 格式的 Excel 文件"}), 400

    import tempfile
    fd, tmp_path = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    file.save(tmp_path)

    try:
        count, skipped = db.import_members_from_excel(tmp_path)
        msg = f"成功导入 {count} 人"
        if skipped:
            msg += f"，跳过 {skipped} 人（学号重复）"
        return jsonify({"ok": True, "count": count, "skipped": skipped, "msg": msg})
    except Exception as e:
        return jsonify({"ok": False, "msg": str(e)}), 400
    finally:
        os.remove(tmp_path)


# ---------- Events ----------
@app.route("/events")
@login_required
def events():
    return render_template("events.html")


@app.route("/api/events")
@login_required
def api_events():
    keyword = request.args.get("search", "")
    rows = db.search_events(keyword) if keyword else db.get_all_events()
    return jsonify([dict(r) for r in rows])


@app.route("/api/events", methods=["POST"])
@login_required
def api_add_event():
    data = request.get_json()
    db.add_event(
        data["name"], data.get("event_date", ""), data.get("location", ""),
        data.get("description", ""),
        int(data.get("max_participants", 0)), float(data.get("fee", 0)),
    )
    return jsonify({"ok": True})


@app.route("/api/events/<int:event_id>", methods=["PUT"])
@login_required
def api_update_event(event_id):
    data = request.get_json()
    db.update_event(
        event_id, data["name"], data.get("event_date", ""), data.get("location", ""),
        data.get("description", ""),
        int(data.get("max_participants", 0)), float(data.get("fee", 0)),
        data.get("status", "upcoming"),
    )
    return jsonify({"ok": True})


@app.route("/api/events/<int:event_id>", methods=["DELETE"])
@login_required
def api_delete_event(event_id):
    db.delete_event(event_id)
    return jsonify({"ok": True})


@app.route("/api/events/<int:event_id>/participants")
@login_required
def api_event_participants(event_id):
    rows = db.get_event_participants(event_id)
    return jsonify([dict(r) for r in rows])


@app.route("/api/events/<int:event_id>/participants", methods=["POST"])
@login_required
def api_add_participant(event_id):
    data = request.get_json()
    ok = db.add_participant(event_id, data["member_id"])
    return jsonify({"ok": ok, "msg": "" if ok else "该成员已报名"})


@app.route("/api/events/<int:event_id>/participants/<int:member_id>", methods=["DELETE"])
@login_required
def api_remove_participant(event_id, member_id):
    db.remove_participant(event_id, member_id)
    return jsonify({"ok": True})


# ---------- Finances ----------
@app.route("/finances")
@login_required
def finances():
    return render_template("finances.html")


@app.route("/api/finances")
@login_required
def api_finances():
    rows = db.get_all_finances()
    return jsonify([dict(r) for r in rows])


@app.route("/api/finances", methods=["POST"])
@login_required
def api_add_finance():
    data = request.get_json()
    member_id = data.get("member_id") or None
    event_id = data.get("event_id") or None
    db.add_finance(
        data["type"], float(data["amount"]), data.get("category", ""),
        data.get("description", ""), member_id, event_id,
    )
    return jsonify({"ok": True})


@app.route("/api/finances/<int:fin_id>", methods=["PUT"])
@login_required
def api_update_finance(fin_id):
    data = request.get_json()
    db.update_finance(fin_id, data["type"], float(data["amount"]),
                      data.get("category", ""), data.get("description", ""))
    return jsonify({"ok": True})


@app.route("/api/finances/<int:fin_id>", methods=["DELETE"])
@login_required
def api_delete_finance(fin_id):
    db.delete_finance(fin_id)
    return jsonify({"ok": True})


@app.route("/api/summary")
@login_required
def api_summary():
    income, expense, balance = db.get_finance_summary()
    members = [dict(r) for r in db.get_all_members() if r["status"] == "active"]
    return jsonify({
        "income": income, "expense": expense, "balance": balance,
        "members": members,
    })


db.init_db()
application = app

if __name__ == "__main__":
    print("社团管理系统 Web 版已启动")
    print("在同一局域网的其他电脑上访问: http://本机IP:5000")
    print("本机访问: http://127.0.0.1:5000")
    application.run(host="0.0.0.0", port=5000, debug=False)
