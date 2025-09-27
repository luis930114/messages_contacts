import pytest
from datetime import datetime
from pydantic import ValidationError

from models.schemas import ContactCreate, ContactResponse
from models.database import ContactDB

class TestContactSchemas:
    """Tests para esquemas Pydantic"""
    
    def test_contact_create_valid(self, sample_contact_data):
        """Test creación de contacto válido"""
        contact = ContactCreate(**sample_contact_data)
        
        assert contact.nombre == "Juan Pérez"
        assert contact.email == "juan@test.com"
        assert "desarrollo web" in contact.mensaje.lower()
    
    def test_contact_create_invalid_email(self, sample_contact_data):
        """Test con email inválido"""
        sample_contact_data["email"] = "email-invalido"
        
        with pytest.raises(ValidationError) as exc_info:
            ContactCreate(**sample_contact_data)
        
        assert "value is not a valid email address" in str(exc_info.value)
    
    def test_contact_create_short_name(self, sample_contact_data):
        """Test con nombre muy corto"""
        sample_contact_data["nombre"] = "A"
        
        with pytest.raises(ValidationError) as exc_info:
            ContactCreate(**sample_contact_data)
        
        assert "al menos 2 caracteres" in str(exc_info.value)
    
    def test_contact_create_short_message(self, sample_contact_data):
        """Test con mensaje muy corto"""
        sample_contact_data["mensaje"] = "Hola"
        
        with pytest.raises(ValidationError) as exc_info:
            ContactCreate(**sample_contact_data)
        
        assert "al menos 10 caracteres" in str(exc_info.value)
    
    def test_contact_create_strips_whitespace(self):
        """Test que se eliminan espacios en blanco"""
        data = {
            "nombre": "  Juan Pérez  ",
            "email": "juan@test.com",
            "mensaje": "  Mensaje de prueba  "
        }
        
        contact = ContactCreate(**data)
        assert contact.nombre == "Juan Pérez"
        assert contact.mensaje == "Mensaje de prueba"

class TestContactDatabase:
    """Tests para modelo de base de datos"""
    
    def test_contact_db_creation(self, db_session):
        """Test creación de contacto en BD"""
        contact = ContactDB(
            nombre="Test User",
            email="test@test.com",
            mensaje="Mensaje de prueba",
            categoria="ventas"
        )
        
        db_session.add(contact)
        db_session.commit()
        db_session.refresh(contact)
        
        assert contact.id is not None
        assert contact.fecha_creacion is not None
        assert isinstance(contact.fecha_creacion, datetime)
    
    def test_contact_db_repr(self, db_session):
        """Test representación string del modelo"""
        contact = ContactDB(
            nombre="Test User",
            email="test@test.com", 
            mensaje="Test message",
            categoria="soporte"
        )
        
        repr_str = repr(contact)
        assert "Test User" in repr_str
        assert "soporte" in repr_str
