from datetime import datetime
from config import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id_usuario= db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email= db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  
    rol = db.Column(db.String(20), default='usuario') 

class municicipio(db.Model):
    __tablename__= 'municipios'
    id_municipio = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
class LineaTransporte(db.Model):
    __tablename__ = 'lineas'
    id_linea = db.Column(db.Integer, primary_key=True)
    nombre_organizacion = db.Column(db.String(120), nullable=False)
    nombre_propietario = db.Column(db.String(120), nullable=False)
    cedula_propietario = db.Column(db.String(50), unique=True)
    cantidad_vehiculos = db.Column(db.Integer, default=0)
    id_municipio= db.Column(db.Integer, db.ForeignKey('municipios.id_municipio'))
    municipio= db.relationship('municicipio', backref='lineas')

class Chofer(db.Model):
    __tablename__ = 'choferes'
    id_chofer = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    cedula = db.Column(db.String(50), unique=True, nullable=False)
    id_vehiculo= db.Column(db.Integer, db.ForeignKey('vehiculos.id_vehiculo'))
    vehiculo = db.relationship('Vehiculo', backref='choferes')

class Vehiculo(db.Model):
    __tablename__ = 'vehiculos'
    id_vehiculo = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(30), unique=True, nullable=False)
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    capacidad = db.Column(db.Integer)
    litraje = db.Column(db.Float)
    sindicato = db.Column(db.String(120))
    modalidad = db.Column(db.String(50))
    grupo = db.Column(db.String(50))
    estado = db.Column(db.String(50), default='activo')
    combustible = db.Column(db.String(50))
    linea_id = db.Column(db.Integer, db.ForeignKey('lineas.id_linea'))
    linea = db.relationship('LineaTransporte', backref='vehiculos')



class CambioLog(db.Model):
    __tablename__ = 'log_cambios'
    id_cambio= db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))
    tipo_cambio= db.Column(db.String(10))
    nombre_entidad= db.Column(db.String(120))
    tabla = db.Column(db.String(50))
    campo = db.Column(db.String(50))
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
