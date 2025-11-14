from flask_mail import Message 
import random
from flask import current_app
from config import mail


def enviar_OTP( email, nombre):
    otp= random.randint(100000, 999999)
    msg = Message('Verificación de Email', sender= current_app.config.get('MAIL_DEFAULT_SENDER'), recipients=[email])
    msg.body= "¡Hola " + nombre + "!\n \n Tu código de verificación es: " + str(otp) + ". \n \n Recuerda que tu código expira en 5 minutos"
    mail.send(msg)
    return otp
