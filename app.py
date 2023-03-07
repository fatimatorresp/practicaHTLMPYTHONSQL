from flask import Flask, render_template, request, redirect,url_for, flash,  session
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,date

app = Flask(__name__) 
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root@127.0.0.1/practica'
db = SQLAlchemy(app)
app.secret_key = 'your_secret_key'

class Usuario(db.Model):
    dni = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(10), nullable=False)
    apellido = db.Column(db.String(10), nullable=False)
    userDelete = db.Column(db.String(1), default=None)

    def __init__(self,dni,nombre,apellido):
        self.dni= dni
        self.nombre = nombre
        self.apellido= apellido

class Vehiculo(db.Model):
    placa = db.Column(db.String(7), primary_key=True)
    marca = db.Column(db.String(10), nullable=False)
    modelo = db.Column(db.String(10), nullable=False)
    dni = db.Column(db.Integer, db.ForeignKey("usuario.dni"))
    
    def __init__(self, placa, marca, modelo, dni):
        self.placa = placa
        self.marca = marca
        self.modelo = modelo
        self.dni = dni

class Estacionamiento(db.Model):
    placa = db.Column(db.String, db.ForeignKey("vehiculo.placa"))
    dni = db.Column(db.Integer, db.ForeignKey("usuario.dni"))
    fechaInicio = db.Column(db.Date, nullable=False)
    fechaFin = db.Column(db.Date,  nullable=True)
    horaEntrada = db.Column(db.Time, nullable=False)
    horaSalida = db.Column(db.Time, nullable=True)
    id_estacionamiento = db.Column(db.Integer, primary_key=True, autoincrement=True)

    def __init__(self, placa, dni, horaEntrada, horaSalida= None, fechaFin=None):
        self.placa = placa
        self.dni = dni
        # self.fechaInicio = fechaInicio
        self.fechaFin = None
        self.horaEntrada = horaEntrada
        self.horaSalida = None



    


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inicio')
def inicio():
    return render_template('inicio.html')

@app.route('/registrar')
def registrar():
    return render_template('registrar.html')

@app.route('/login')
def login():
    return render_template('index.html')

@app.route('/listado') #listado de todos los clientes
def listado():   
    result = db.session.query(Usuario, Vehiculo).join(Vehiculo, Usuario.dni == Vehiculo.dni).all()
    return render_template('listado.html', registro=result)


@app.route('/submitRegistro', methods=['POST']) #registrar
def registro():
    if request.method == 'POST':
        dni = request.form['dni']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        placa = request.form['placa']
        marca = request.form['marca']
        modelo = request.form['modelo']
        dni =request.form['dni']
        nuevoUsuario= Usuario(dni, nombre, apellido)
        db.session.add(nuevoUsuario)
        db.session.commit()
        nuevoVehiculo = Vehiculo(placa, marca, modelo, dni)
        db.session.add(nuevoVehiculo)
        db.session.commit()
        db.session.close()
        flash('Vehiculo Registrado')
        return redirect(url_for('listado')) 
        



@app.route('/ingresar', methods=['GET', 'POST']) #login index
def ingresar():
    if request.method == 'POST':
        dni = request.form['dni']
        contraseña = request.form['contraseña']
        datos= db.session.execute('SELECT * FROM usuario WHERE dni = :dni  AND contraseña = :contraseña',{'dni':dni, 'contraseña': contraseña}).fetchone()
        db.session.commit()
        if datos and datos[5] != 'X':
            if contraseña:
                session['logged_in'] = True
                session['dni'] = datos[0]
                flash('Ingresaste Sastifactoriamente!')
                return redirect(url_for('listado'))
        else:
            flash('Dni o Contraseña Incorrecta')
            return redirect(url_for('index'))
            error_message = 'DNI o Contraseña Incorrecta'
            return redirect(url_for('index'))
    else:
        return 'Error de inicio de sesion'

@app.route('/editar/<dni>') #editar el registro
def get_editar(dni):
    usuarios = Usuario.query.filter_by(dni=dni).first()
    vehiculos = Vehiculo.query.filter_by(dni=dni).first()
    return render_template('editar.html', usuario = usuarios, vehiculo=vehiculos)

@app.route('/actualizar/<dni>', methods = ['GET','POST']) #actualiza el registro
def actualizar(dni):
    if request.method == 'POST':
        editarUsuario = Usuario.query.filter_by(dni=dni).first()
        editarVehiculo = Vehiculo.query.filter_by(dni=dni).first()
        editarUsuario.dni = request.form['dni']
        editarUsuario.nombre = request.form['nombre']
        editarUsuario.apellido = request.form['apellido']
        editarVehiculo.placa = request.form['placa']
        editarVehiculo.marca = request.form['marca']
        editarVehiculo.modelo = request.form['modelo']
        db.session.commit()
        flash('Actualizacion Sastifactoria')
        return redirect(url_for('listado'))

@app.route('/Eliminar/<int:dni>', methods=['GET', 'POST']) #eliminado con X e inabilitamos
def Eliminar(dni):
    record = Usuario.query.get(dni)
    record.userDelete = "X"       
    db.session.commit()
    flash('El usuario ha sido eliminado con éxito')
    return redirect(url_for('listado'))

# metodos Estacionamiento
@app.route('/ingresarEntrada', methods=['POST'])
def ingresarEntrada():
    dni = request.form['dni']
    action = request.form['action']
    vehiculo = db.session.query(Vehiculo).filter_by(dni=dni).first()
    if vehiculo:
        # Comprobar si ya hay un registro activo para este vehículo
        registro_activo = db.session.query(Estacionamiento).filter_by(dni=dni, horaSalida=None).first()
        if registro_activo:
            flash('Este vehículo ya tiene un registro activo.')
        else:
            now = datetime.now()
            fechaInicio = date.today()
            horaEntrada = now.strftime("%H:%M:%S")
            nuevoIngresoVehiculo = Estacionamiento(
                placa=vehiculo.placa,
                dni=dni,
                # fechaInicio=fechaInicio,
                horaEntrada=horaEntrada,
                # fechaFin=None,
                horaSalida=None
            )
            db.session.add(nuevoIngresoVehiculo)
            db.session.commit()
            flash('Registro de entrada exitoso')
    else:
        flash('No se encuentra el usuario')
    return redirect(url_for('listadoEsta'))

@app.route('/ingresarSalida', methods=['POST'])
def ingresarSalida():
    dni = request.form['dni']
    action = request.form['action']
    vehiculo = db.session.query(Vehiculo).filter_by(dni=dni).first()
    if vehiculo:
        registro_activo = db.session.query(Estacionamiento).filter_by(dni=dni, horaSalida=None,fechaFin=None).first()
        if registro_activo:
            now = datetime.now()
            fechaFin = date.today()
            horaSalida = now.strftime("%H:%M:%S")
            registro_activo.fechaFin = fechaFin
            registro_activo.horaSalida = horaSalida
            db.session.commit()
            flash('Registro de salida exitoso')
        else:
            flash('No se encontró registro de entrada correspondiente')
    else:
        flash('No se encuentra el usuario')
    return redirect(url_for('listadoEsta'))


@app.route('/listadoEsta') #listado de todos los clientes
def listadoEsta():   
    resultado= db.session.query(Estacionamiento).all()
    return render_template('listadoEsta.html', practica=resultado)
   
    

if __name__ == '__main__':
    toolbar = DebugToolbarExtension(app)
    app.run(debug=True)