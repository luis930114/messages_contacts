from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from config import Base

class ContactDB(Base):
    """
    Modelo de base de datos para contactos
    """
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    mensaje = Column(Text, nullable=False)
    categoria = Column(String(50), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Contact(id={self.id}, nombre='{self.nombre}', categoria='{self.categoria}')>"