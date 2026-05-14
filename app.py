from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Rutas absolutas — funciona local y en Render
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'artesaMarket.db')

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'))
app.secret_key = 'clave_secreta_artesa_2026'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catalogo')
def catalogo():
    return render_template('catalogo.html')

@app.route('/artesanos')
def artesanos():
    return render_template('artesanos.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo_input = request.form.get('email') or request.form.get('correo')
        password = request.form.get('password')

        if not correo_input:
            flash("Por favor, ingresa tu correo electrónico", "error")
            return render_template('login.html')

        correo = correo_input.strip().lower()
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE correo = ?", (correo,))
        usuario = cursor.fetchone()
        conexion.close()

        if usuario and check_password_hash(usuario[3], password):
            session.clear()
            session['user_id'] = usuario[0]
            session['nombre'] = usuario[1]
            session['rol'] = usuario[4]
            return redirect(url_for('index'))
        else:
            flash("Correo o contraseña incorrectos", "error")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada", "success")
    return redirect(url_for('index'))

@app.route('/vender')
def vender():
    return render_template('vender.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre   = request.form.get('nombre')
        correo   = request.form.get('correo')
        password = request.form.get('password')
        rol      = request.form.get('rol')

        password_encriptada = generate_password_hash(password)
        conexion = None
        try:
            conexion = sqlite3.connect(DB_PATH, timeout=10)
            cursor = conexion.cursor()
            cursor.execute(
                "INSERT INTO usuarios (nombre, correo, password, rol) VALUES (?, ?, ?, ?)",
                (nombre, correo, password_encriptada, rol)
            )
            conexion.commit()
            flash("¡Registro exitoso! Bienvenido.", "success")
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            flash("Error: Este correo ya está registrado.", "danger")
            return redirect(url_for('registro'))
        except Exception as e:
            flash(f"Error inesperado: {e}", "danger")
            return redirect(url_for('registro'))
        finally:
            if conexion:
                conexion.close()

    return render_template('registro.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = not bool(os.environ.get('PORT'))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
