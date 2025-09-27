from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from database.connection import init_database, check_database_connection
from api.routes import router
from graphql_app.schema import graphql_router
from config import API_CONFIG

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('contact_backend.log',encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestión del ciclo de vida de la aplicación
    """
    logger.info("Iniciando Contact Management Backend...")

    init_database()
    
    if not check_database_connection():
        raise Exception("No se pudo conectar a la base de datos")
    
    
    logger.info("Contact Management Backend iniciado exitosamente!")
    logger.info(f"Servidor ejecutándose en http://{API_CONFIG['host']}:{API_CONFIG['port']}")
    logger.info(f"Documentación disponible en http://{API_CONFIG['host']}:{API_CONFIG['port']}/docs")
    logger.info(f"GraphQL playground: http://{API_CONFIG['host']}:{API_CONFIG['port']}/graphql")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")

# Crear aplicación FastAPI
app = FastAPI(
    title="Contact Management API",
    description="""
    Backend para gestión de mensajes de contacto con las siguientes características:
    
    **Clasificación Automática con IA**
    - Análisis inteligente del contenido de los mensajes
    - Categorización en: Ventas, Soporte, Otro
    
    **Automatizaciones Inteligentes**  
    - Envío automático de emails para consultas de ventas
    - Notificaciones al equipo de soporte técnico
    - Acciones personalizables según la categoría
    
    **Sistema de Consultas Avanzado**
    - Filtros por categoría, fecha, etc.
    - Paginación y ordenamiento
    - Estadísticas en tiempo real
    
    **Validación Robusta**
    - Validación automática de emails y datos
    - Manejo profesional de errores
    - Logging completo para auditoría
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1", tags=["contacts"])

app.include_router(graphql_router, prefix="/graphql", tags=["GraphQL API"])

@app.get("/")
async def root():
    """
    Endpoint raíz con información de ambas APIs
    """
    return {
        "message": "Contact Management API - Dual REST + GraphQL",
        "version": "1.0.0",
        "status": "active",
        "apis": {
            "rest": {
                "base_url": "/api/v1",
                "docs": "/docs",
                "redoc": "/redoc"
            },
            "graphql": {
                "endpoint": "/graphql",
                "playground": "/graphql (GraphiQL)",
                "features": ["queries", "mutations"]
            }
        },
        "health": "/api/v1/health"
    }



@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    logger.error(f"ValueError: {str(exc)}")
    return {"detail": str(exc)}

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}")
    return {"detail": "Error interno del servidor"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=API_CONFIG["host"], 
        port=API_CONFIG["port"], 
        reload=API_CONFIG["debug"],
        log_level="info"
    )
