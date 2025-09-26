from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional

class ContactCreate(BaseModel):
    """
    Schema para crear un nuevo contacto
    """
    nombre: str
    email: EmailStr
    mensaje: str
    
    @validator('nombre')
    def validate_nombre(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('El nombre debe tener al menos 2 caracteres')
        return v.strip()
    
    @validator('mensaje')
    def validate_mensaje(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('El mensaje debe tener al menos 10 caracteres')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "nombre": "Juan Pérez",
                "email": "juan@example.com",
                "mensaje": "Hola, me interesa conocer más sobre sus servicios de desarrollo web"
            }
        }

class ContactResponse(BaseModel):
    """
    Schema para respuesta de contacto
    """
    id: int
    nombre: str
    email: str
    mensaje: str
    categoria: str
    fecha_creacion: datetime
    
    class Config:
        json_schema_extra ={
        "example": {
            "nombre": "Juan Pérez",
            "email": "juan@example.com",
            "mensaje": "Mensaje de ejemplo"
        }
    }

class ContactStats(BaseModel):
    """
    Schema para estadísticas del sistema
    """
    total_contacts: int
    categories: dict