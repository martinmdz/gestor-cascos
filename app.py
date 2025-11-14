from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
import json, os

app = Flask(__name__)
# 👇 acá definís la clave secreta
app.secret_key = os.urandom(24)  
# también podrías usar un string fijo, ej: "mi_clave_super_secreta"

DATA_FILE = "data/inventario.json"

# Inicializar archivo si no existe
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"cascos": [], "usuarios": []}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/")
def presentacion():
    return render_template("presentacion.html")

@app.route("/inicio")
def inicio():
    if not session.get('admin'):
        return redirect(url_for("login"))
    return render_template("index.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("presentacion"))

@app.route("/registro")
def registro():
    return render_template("registro.html")

@app.route("/registrar_admin", methods=["POST"])
def registrar_admin():
    data = load_data()
    admin = {
        "id": len(data["administradores"]) + 1,
        "nombre": request.form["nombre"],
        "dni": request.form["dni"],
        "correo": request.form["correo"],
        "password": generate_password_hash(request.form["password"])
    }
    data["administradores"].append(admin)
    save_data(data)
    return redirect(url_for("login"))

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login_admin", methods=["POST"])
def login_admin():
    data = load_data()
    dni_correo = request.form["dni_correo"]
    password = request.form["password"]
    for admin in data["administradores"]:
        if (admin["dni"] == dni_correo or admin["correo"] == dni_correo) and check_password_hash(admin["password"], password):
            # Aquí podrías guardar sesión con flask.session
            session['admin'] = admin['id']
            return redirect(url_for("inicio"))
    return "Credenciales inválidas"

@app.route("/inventario")
def inventario():
    data = load_data()
    return render_template("inventario.html", cascos=data["cascos"])

@app.route("/editar_casco", methods=["POST"])
def editar_casco():
    data = load_data()
    casco_id = int(request.form["casco_id"])
    nuevo_nombre = request.form["nuevo_nombre"]
    for casco in data["cascos"]:
        if casco["id"] == casco_id:
            casco["nombre"] = nuevo_nombre
    save_data(data)
    return redirect(url_for("inventario"))

@app.route("/eliminar_casco", methods=["POST"])
def eliminar_casco():
    data = load_data()
    casco_id = int(request.form["casco_id"])
    data["cascos"] = [c for c in data["cascos"] if c["id"] != casco_id]
    save_data(data)
    return redirect(url_for("inventario"))


@app.route("/usuarios")
def usuarios():
    data = load_data()
    return render_template("usuarios.html", usuarios=data["usuarios"])

@app.route("/prestamos")
def prestamos():
    data = load_data()
    return render_template("prestamos.html", cascos=data["cascos"], usuarios=data["usuarios"])

@app.route("/estadisticas")
def estadisticas():
    data = load_data()
    total_cascos = len(data["cascos"])
    prestados = sum(1 for c in data["cascos"] if c.get("prestado"))
    disponibles = total_cascos - prestados
    return render_template("estadisticas.html", total=total_cascos, prestados=prestados, disponibles=disponibles)

@app.route("/add_casco", methods=["POST"])
def add_casco():
    data = load_data()
    casco = {
        "id": len(data["cascos"]) + 1,
        "nombre": request.form["nombre"],
        "geles": int(request.form["geles"]),
        "prestado": False,
        "usuario": None
    }
    data["cascos"].append(casco)
    save_data(data)
    return redirect(url_for("inventario"))

@app.route("/add_usuario", methods=["POST"])
def add_usuario():
    data = load_data()
    usuario = {
        "id": len(data["usuarios"]) + 1,
        "nombre": request.form["nombre"]
    }
    data["usuarios"].append(usuario)
    save_data(data)
    return redirect(url_for("usuarios"))

@app.route("/editar_usuario", methods=["POST"])
def editar_usuario():
    data = load_data()
    usuario_id = int(request.form["usuario_id"])
    nuevo_nombre = request.form["nuevo_nombre"]
    for usuario in data["usuarios"]:
        if usuario["id"] == usuario_id:
            usuario["nombre"] = nuevo_nombre
    save_data(data)
    return redirect(url_for("usuarios"))

@app.route("/eliminar_usuario", methods=["POST"])
def eliminar_usuario():
    data = load_data()
    usuario_id = int(request.form["usuario_id"])
    data["usuarios"] = [u for u in data["usuarios"] if u["id"] != usuario_id]
    save_data(data)
    return redirect(url_for("usuarios"))


@app.route("/prestar", methods=["POST"])
def prestar():
    data = load_data()
    casco_id = int(request.form["casco_id"])
    usuario_id = int(request.form["usuario_id"])
    for casco in data["cascos"]:
        if casco["id"] == casco_id:
            casco["prestado"] = True
            casco["usuario"] = usuario_id
    save_data(data)
    return redirect(url_for("prestamos"))

@app.route("/devolver", methods=["POST"])
def devolver():
    data = load_data()
    casco_id = int(request.form["casco_id"])
    for casco in data["cascos"]:
        if casco["id"] == casco_id:
            casco["prestado"] = False
            casco["usuario"] = None
    save_data(data)
    return redirect(url_for("prestamos"))


if __name__ == "__main__":
    app.run(debug=True)
