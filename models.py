from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class Produk(db.Model):
    id = Column(Integer, primary_key=True)
    nama = Column(String(255), nullable=False)
    deskripsi = Column(Text, nullable=False)
    harga = Column(Integer, nullable=False)
    gambar = Column(String(255), nullable=False)

class Testimoni(db.Model):
    id = Column(Integer, primary_key=True)
    nama = Column(String(50), nullable=False)
    deskripsi = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)