from flask import Flask, render_template, request, redirect, url_for, session
from models.usuario import Usuario
from services.usuario_service import UsuarioService
from services.rutina_service import RutinaService

app = Flask(__name__)
app.secret_key = "clave_secreta_segura"

usuario_service = UsuarioService()
rutina_service = RutinaService()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        edad = int(request.form['edad'])
        peso = float(request.form['peso'])
        altura = float(request.form['altura'])
        genero = request.form['genero']
        objetivo = request.form['objetivo']

        usuario = Usuario(nombre, edad, peso, altura, genero, objetivo)
        usuario_service.guardar_usuario(usuario.__dict__)

        session['usuario'] = usuario.__dict__
        return redirect(url_for('generar_rutina'))

    return render_template('registro.html')

@app.route('/generar_rutina')
def generar_rutina():
    usuario = session.get('usuario')
    if not usuario:
        return redirect(url_for('registro'))

    objetivo = usuario['objetivo']
    rutina, dias = rutina_service.generar_rutina_con_dias(objetivo)
    rutina_service.guardar_rutina(usuario['nombre'], objetivo, rutina, dias)

    return render_template('rutina.html', usuario=usuario, rutina=rutina, dias=dias)

@app.route('/historial/<nombre>')
def historial(nombre):
    datos = rutina_service.obtener_rutinas()
    filtrado = [r for r in datos if r.get("usuario") == nombre]
    return render_template('historial.html', usuario_nombre=nombre, historial=filtrado)

if __name__ == '__main__':
    app.run(debug=True)
