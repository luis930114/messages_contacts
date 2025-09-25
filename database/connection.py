from sqlalchemy.orm import Session
from config import SessionLocal, engine, Base
import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

def get_db():
    """
    Dependency injection para obtener sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """
    Inicializa las tablas de la base de datos
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error inicializando base de datos: {str(e)}")
        raise

def check_database_connection():
    """
    Verifica la conexión a la base de datos
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        logger.error(f"Error de conexión a base de datos: {str(e)}")
        return False