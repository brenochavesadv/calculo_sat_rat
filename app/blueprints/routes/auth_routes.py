from flask import Blueprint, request, render_template, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, set_access_cookies, set_refresh_cookies
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from app.models.user import User

bp = Blueprint("auth", __name__)

@bp.get("/login")
def page_login():
    return render_template("login.html")


@bp.get("/login/createadmin")
def page_create_admin():
    return render_template("create_admin.html")

@bp.post("/auth/init_admin")
def init_admin():
    #data = request.get_json(force=True)
    #username = data.get("username", "admin")
    #password = data.get("password", "admin")
    username = "admin"; password = "admin"
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user); db.session.commit()
    return {"ok": True, "username": username}

@bp.post("/auth/login")
def login():
    data = request.get_json(force=True)
    username = data.get("username"); password = data.get("password")
    if not username or not password:
        return {"error": "credenciais inválidas"}, 400
    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return {"error": "usuário/senha incorretos"}, 401
    # Use the plain username (string) as identity so the JWT subject is a string
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    resp = jsonify({"access_token": access_token, "refresh_token": refresh_token})
    # Set tokens as cookies so browser will send them on subsequent navigations
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)
    return resp


@bp.post("/auth/refresh")
@jwt_required(refresh=True)
def refresh():
    ident = get_jwt_identity()
    # ident will be the username string
    access_token = create_access_token(identity=ident)
    resp = jsonify({"access_token": access_token})
    set_access_cookies(resp, access_token)
    return resp
