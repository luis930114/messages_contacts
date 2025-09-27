import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from httpx import AsyncClient

from main import app
from config import Base
from database.connection import get_db

# Base de datos de prueba en memoria
TEST_DATABASE_URL = "sqlite:///./test_contacts.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    """Override de la dependencia de BD para tests"""
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Crear BD de prueba para cada test"""
    # Crear todas las tablas
    Base.metadata.create_all(bind=test_engine)
    
    session = TestSessionLocal()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Cliente de prueba con BD mockeada"""
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()

@pytest.fixture
async def async_client(db_session):
    """Cliente async para pruebas de GraphQL"""
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture
def sample_contact_data():
    """Datos de ejemplo para contactos"""
    return {
        "nombre": "Juan Pérez",
        "email": "juan@test.com",
        "mensaje": "Hola, me interesa conocer más sobre sus servicios de desarrollo web"
    }

@pytest.fixture
def sample_support_contact():
    """Contacto de soporte para pruebas"""
    return {
        "nombre": "María García", 
        "email": "maria@test.com",
        "mensaje": "Tengo un problema urgente con mi sistema, necesito ayuda técnica"
    }

@pytest.fixture
def sample_sales_contact():
    """Contacto de ventas para pruebas"""
    return {
        "nombre": "Carlos López",
        "email": "carlos@test.com", 
        "mensaje": "Quisiera saber cuánto cuesta sus servicios y obtener una cotización"
    }