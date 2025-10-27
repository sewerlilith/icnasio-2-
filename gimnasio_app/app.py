from flask import Flask, render_template, request, redirect, url_for, session
from models.usuario import Usuario
from services.container import create_container

app = Flask(__name__)
app.secret_key = "clave_secreta_segura"

app.container = create_container({
    'usuarios_path': 'data/usuarios.json',
    'rutinas_path': 'data/rutinas.json'
})

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
        usuario_service = app.container.usuario_service()
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
    rutina_service = app.container.rutina_service()
    rutina, dias = rutina_service.generar_rutina_con_dias(objetivo)
    rutina_service.guardar_rutina(usuario['nombre'], objetivo, rutina, dias)

    # Calcular IMC (BMI) -- altura en cm en el formulario
    try:
        peso = float(usuario.get('peso', 0))
        altura_cm = float(usuario.get('altura', 0))
        altura_m = altura_cm / 100 if altura_cm > 0 else 0
        bmi = round(peso / (altura_m * altura_m), 1) if altura_m > 0 else None
    except Exception:
        bmi = None

    def bmi_category(b):
        if b is None:
            return None
        if b < 18.5:
            return 'Bajo peso'
        if b < 25:
            return 'Normal'
        if b < 30:
            return 'Sobrepeso'
        return 'Obesidad'

    return render_template('rutina.html', usuario=usuario, rutina=rutina, dias=dias, bmi=bmi, bmi_category=bmi_category(bmi))

@app.route('/historial/<nombre>')
def historial(nombre):
    rutina_service = app.container.rutina_service()
    datos = rutina_service.obtener_rutinas()
    filtrado = [r for r in datos if r.get("usuario") == nombre]
    return render_template('historial.html', usuario_nombre=nombre, historial=filtrado)

if __name__ == '__main__':
    app.run(debug=True)