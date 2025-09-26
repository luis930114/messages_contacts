from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging

from models.schemas import ContactCreate, ContactResponse, ContactStats
from models.database import ContactDB
from services.classifier import MessageClassifier
from services.automation import AutomationService
from database.connection import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

# Servicios
classifier = MessageClassifier()
automation_service = AutomationService()

@router.post("/contact", response_model=ContactResponse, status_code=201)
async def create_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db)
):
    """
    Endpoint para recibir y procesar nuevos mensajes de contacto.
    
    Proceso:
    1. Valida los datos de entrada con Pydantic
    2. Clasifica el mensaje automáticamente con IA
    3. Almacena en base de datos
    4. Ejecuta automatizaciones según la categoría
    
    Returns:
        ContactResponse: Datos del contacto creado con categoría asignada
    """
    try:
        # 1. Clasificar mensaje con IA
        categoria = classifier.classify_message(contact.mensaje)
        logger.info(f"Mensaje clasificado como: {categoria}")
        
        # 2. Crear registro en base de datos
        db_contact = ContactDB(
            nombre=contact.nombre,
            email=contact.email,
            mensaje=contact.mensaje,
            categoria=categoria
        )
        
        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)
        
        # 3. Ejecutar automatización en background
        automation_result = await automation_service.execute_automation(db_contact)
        logger.info(f"Automatización: {automation_result}")
        
        logger.info(f"Contacto {db_contact.id} procesado exitosamente - {categoria}")
        return db_contact
        
    except Exception as e:
        if db:
            db.rollback()
        error_msg = f"Error procesando contacto: {str(e)}"
        logger.error(f"{error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/contacts", response_model=List[ContactResponse])
async def get_contacts(
    categoria: Optional[str] = Query(
        None, 
        description="Filtrar por categoría: ventas, soporte, otro",
        regex="^(ventas|soporte|otro)$"
    ),
    limit: int = Query(
        100, 
        ge=1, 
        le=1000, 
        description="Límite de resultados (1-1000)"
    ),
    offset: int = Query(
        0, 
        ge=0, 
        description="Desplazamiento para paginación"
    ),
    db: Session = Depends(get_db)
):
    """
    Endpoint para consultar mensajes con filtros opcionales.
    
    Features:
    - Filtrado por categoría
    - Paginación con limit/offset
    - Ordenamiento por fecha (más recientes primero)
    
    Args:
        categoria: Filtro opcional por categoría
        limit: Número máximo de resultados
        offset: Número de registros a saltar
        
    Returns:
        List[ContactResponse]: Lista de contactos que cumplen los criterios
    """
    try:
        query = db.query(ContactDB)
        
        # Aplicar filtro de categoría
        if categoria:
            query = query.filter(ContactDB.categoria == categoria.lower())
            logger.info(f"Filtro aplicado: categoria={categoria}")
        
        # Aplicar paginación y ordenamiento
        contacts = query.order_by(ContactDB.fecha_creacion.desc())\
                       .offset(offset)\
                       .limit(limit)\
                       .all()
        
        logger.info(f"Consulta realizada: {len(contacts)} contactos encontrados")
        return contacts
        
    except Exception as e:
        error_msg = f"Error consultando contactos: {str(e)}"
        logger.error(f"{error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: Session = Depends(get_db)):
    """
    Obtener un contacto específico por ID
    
    Args:
        contact_id: ID único del contacto
        
    Returns:
        ContactResponse: Datos completos del contacto
        
    Raises:
        HTTPException: 404 si el contacto no existe
    """
    contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contacto no encontrado")
    
    logger.info(f"Contacto {contact_id} consultado")
    return contact

@router.get("/stats", response_model=ContactStats)
async def get_stats(db: Session = Depends(get_db)):
    """
    Obtener estadísticas del sistema de contactos
    
    Returns:
        ContactStats: Estadísticas generales y por categoría
    """
    try:
        total = db.query(ContactDB).count()
        ventas = db.query(ContactDB).filter(ContactDB.categoria == "ventas").count()
        soporte = db.query(ContactDB).filter(ContactDB.categoria == "soporte").count()
        otro = db.query(ContactDB).filter(ContactDB.categoria == "otro").count()
        
        stats = {
            "total_contacts": total,
            "categories": {
                "ventas": ventas,
                "soporte": soporte,
                "otro": otro
            }
        }
        
        logger.info(f"Estadísticas consultadas: {total} contactos totales")
        return stats
        
    except Exception as e:
        error_msg = f"Error obteniendo estadísticas: {str(e)}"
        logger.error(f"{error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@router.get("/health")
async def health_check():
    """
    Health check endpoint para monitoreo de la aplicación
    
    Returns:
        dict: Estado de la aplicación y timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "Contact Management API",
        "version": "1.0.0"
    }

@router.get("/classify-preview")
async def classify_preview(message: str):
    """
    Endpoint de prueba para ver cómo se clasificaría un mensaje
    Útil para testing y debugging
    
    Args:
        message: Mensaje a clasificar
        
    Returns:
        dict: Detalles de la clasificación
    """
    if len(message.strip()) < 5:
        raise HTTPException(status_code=400, detail="El mensaje debe tener al menos 5 caracteres")
    
    details = classifier.get_classification_details(message)
    logger.info(f"Preview de clasificación solicitado")
    return details