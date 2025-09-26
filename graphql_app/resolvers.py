import strawberry
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from models.database import ContactDB
from services.classifier import MessageClassifier
from services.automation import AutomationService
from database.connection import get_db
from .types import (
    Contact, ContactStats, ClassificationResult, AutomationResult,
    ContactConnection, ContactInput, ContactFilter, PaginationInput,
    ContactCreateResponse, CategoryEnum, PriorityEnum
)

logger = logging.getLogger(__name__)

classifier = MessageClassifier()
automation_service = AutomationService()

def get_db_session() -> Session:
    """Helper para obtener sesión de BD en GraphQL"""
    return next(get_db())


@strawberry.type
class Query:
    """
    Consultas GraphQL disponibles
    """
    
    @strawberry.field
    def contacts(
        self, 
        filter: Optional[ContactFilter] = None,
        pagination: Optional[PaginationInput] = None
    ) -> ContactConnection:
        """
        Obtener lista de contactos con filtros y paginación
        
        Ejemplo de uso:
        ```graphql
        query {
          contacts(
            filter: { categoria: VENTAS, search_text: "precio" }
            pagination: { limit: 10, offset: 0 }
          ) {
            nodes {
              id
              nombre
              email
              categoria
              mensaje_preview
            }
            total_count
            has_next_page
          }
        }
        ```
        """
        db = get_db_session()
        
        try:
            query = db.query(ContactDB)
            
            if filter:
                if filter.categoria:
                    query = query.filter(ContactDB.categoria == filter.categoria.value)
                
                if filter.fecha_desde:
                    query = query.filter(ContactDB.fecha_creacion >= filter.fecha_desde)
                
                if filter.fecha_hasta:
                    query = query.filter(ContactDB.fecha_creacion <= filter.fecha_hasta)
                
                if filter.search_text:
                    search_term = f"%{filter.search_text}%"
                    query = query.filter(
                        ContactDB.mensaje.ilike(search_term) |
                        ContactDB.nombre.ilike(search_term) |
                        ContactDB.email.ilike(search_term)
                    )
            
            total_count = query.count()
            
            if pagination:
                limit = min(pagination.limit, 100) 
                offset = pagination.offset
            else:
                limit, offset = 20, 0
            
            contacts = query.order_by(ContactDB.fecha_creacion.desc())\
                           .offset(offset)\
                           .limit(limit)\
                           .all()
            
            graphql_contacts = [
                Contact(
                    id=c.id,
                    nombre=c.nombre,
                    email=c.email,
                    mensaje=c.mensaje,
                    categoria=CategoryEnum(c.categoria),
                    fecha_creacion=c.fecha_creacion
                ) for c in contacts
            ]
            
            has_next = (offset + limit) < total_count
            has_prev = offset > 0
            
            logger.info(f"GraphQL: {len(contacts)} contactos consultados")
            
            return ContactConnection(
                nodes=graphql_contacts,
                total_count=total_count,
                has_next_page=has_next,
                has_previous_page=has_prev
            )
            
        finally:
            db.close()
    
    @strawberry.field
    def contact(self, id: int) -> Optional[Contact]:
        """
        Obtener un contacto específico por ID
        
        Ejemplo:
        ```graphql
        query {
          contact(id: 1) {
            id
            nombre
            email
            mensaje
            categoria
            dias_desde_creacion
          }
        }
        ```
        """
        db = get_db_session()
        
        try:
            contact_db = db.query(ContactDB).filter(ContactDB.id == id).first()
            
            if not contact_db:
                return None
            
            return Contact(
                id=contact_db.id,
                nombre=contact_db.nombre,
                email=contact_db.email,
                mensaje=contact_db.mensaje,
                categoria=CategoryEnum(contact_db.categoria),
                fecha_creacion=contact_db.fecha_creacion
            )
            
        finally:
            db.close()
    
    @strawberry.field
    def stats(self) -> ContactStats:
        """
        Obtener estadísticas del sistema
        
        Ejemplo:
        ```graphql
        query {
          stats {
            totalContacts
            ventasCount
            soporteCount
            ventasPercentage
            soportePercentage
          }
        }
        ```
        """
        db = get_db_session()
        
        try:
            total = db.query(ContactDB).count()
            ventas = db.query(ContactDB).filter(ContactDB.categoria == "ventas").count()
            soporte = db.query(ContactDB).filter(ContactDB.categoria == "soporte").count()
            otro = db.query(ContactDB).filter(ContactDB.categoria == "otro").count()
            
            return ContactStats(
                total_contacts=total,
                ventas_count=ventas,
                soporte_count=soporte,
                otro_count=otro
            )
            
        finally:
            db.close()
    
    @strawberry.field
    def classify_message(self, mensaje: str) -> ClassificationResult:
        """
        Clasificar un mensaje sin guardarlo (útil para testing)
        
        Ejemplo:
        ```graphql
        query {
          classifyMessage(mensaje: "Hola, quiero comprar sus servicios") {
            categoriaDetectada
            confianzaScore
            palabrasClaveEncontradas
          }
        }
        ```
        """
        details = classifier.get_classification_details(mensaje)
        
        return ClassificationResult(
            mensaje=mensaje,
            categoria_detectada=CategoryEnum(details["final_category"]),
            confianza_score=0.85,  # Podrías calcular esto basado en matches
            palabras_clave_encontradas=details["sales_matches"] + details["support_matches"]
        )
    
# ============================================================================
# MUTATION RESOLVERS  
# ============================================================================

@strawberry.type
class Mutation:
    """
    Mutaciones GraphQL disponibles
    """
    
    @strawberry.mutation
    async def create_contact(self, input: ContactInput) -> ContactCreateResponse:
        """
        Crear un nuevo contacto con clasificación y automatización
        
        Ejemplo:
        ```graphql
        mutation {
          createContact(input: {
            nombre: "Juan Pérez"
            email: "juan@test.com"
            mensaje: "Necesito ayuda con un problema técnico"
          }) {
            success
            contact {
              id
              nombre
              categoria
              diasDesdeCreacion
            }
            automationResult {
              actionPerformed
              success
              priority
            }
            error
          }
        }
        ```
        """
        db = get_db_session()
        
        try:
            if len(input.nombre.strip()) < 2:
                return ContactCreateResponse(
                    success=False,
                    error="El nombre debe tener al menos 2 caracteres"
                )
            
            if len(input.mensaje.strip()) < 10:
                return ContactCreateResponse(
                    success=False,
                    error="El mensaje debe tener al menos 10 caracteres"
                )
            
            # 1. Clasificar mensaje
            categoria = classifier.classify_message(input.mensaje)
            logger.info(f"GraphQL: Mensaje clasificado como {categoria}")
            
            # 2. Crear en BD
            db_contact = ContactDB(
                nombre=input.nombre.strip(),
                email=input.email,
                mensaje=input.mensaje.strip(),
                categoria=categoria
            )
            
            db.add(db_contact)
            db.commit()
            db.refresh(db_contact)
            
            # 3. Ejecutar automatización
            automation_result = await automation_service.execute_automation(db_contact)
            
            # 4. Convertir a tipos GraphQL
            contact_gql = Contact(
                id=db_contact.id,
                nombre=db_contact.nombre,
                email=db_contact.email,
                mensaje=db_contact.mensaje,
                categoria=CategoryEnum(db_contact.categoria),
                fecha_creacion=db_contact.fecha_creacion
            )
            
            automation_gql = AutomationResult(
                contact_id=db_contact.id,
                categoria=CategoryEnum(categoria),
                success=automation_result["success"],
                action_performed=automation_result.get("action", "none"),
                message=automation_result.get("message", ""),
                priority=PriorityEnum(automation_result["priority"]) if automation_result.get("priority") else None
            )
            
            logger.info(f"GraphQL: Contacto {db_contact.id} creado exitosamente")
            
            return ContactCreateResponse(
                success=True,
                contact=contact_gql,
                automation_result=automation_gql
            )
            
        except Exception as e:
            db.rollback()
            error_msg = f"Error creando contacto: {str(e)}"
            logger.error(f"GraphQL: {error_msg}")
            
            return ContactCreateResponse(
                success=False,
                error=error_msg
            )
            
        finally:
            db.close()
    
    @strawberry.mutation
    def delete_contact(self, id: int) -> bool:
        """
        Eliminar un contacto por ID
        
        Ejemplo:
        ```graphql
        mutation {
          deleteContact(id: 1)
        }
        ```
        """
        db = get_db_session()
        
        try:
            contact = db.query(ContactDB).filter(ContactDB.id == id).first()
            
            if not contact:
                logger.warning(f"GraphQL: Intento de eliminar contacto inexistente {id}")
                return False
            
            db.delete(contact)
            db.commit()
            
            logger.info(f"GraphQL: Contacto {id} eliminado")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"GraphQL: Error eliminando contacto {id}: {str(e)}")
            return False
            
        finally:
            db.close()

