from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Spedizione(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destinatario = db.Column(db.String(150), nullable=False)
    descrizione = db.Column(db.String(300), nullable=False)
    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    nome_utente = db.Column(db.String(100), nullable=False)
    seriale_pc = db.Column(db.String(100), nullable=False)
    modello_pc = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    consegnato = db.Column(db.Boolean, default=False)
