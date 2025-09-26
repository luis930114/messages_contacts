import strawberry
from typing import List, Optional
from datetime import datetime
from enum import Enum

@strawberry.enum
class CategoryEnum(Enum):
    VENTAS = "ventas"
    SOPORTE = "soporte" 
    OTRO = "otro"

@strawberry.enum
class PriorityEnum(Enum):
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

@strawberry.type
class Contact:
    """
    Tipo GraphQL para representar un contacto
    """
    id: int
    nombre: str
    email: str
    mensaje: str
    categoria: CategoryEnum
    fecha_creacion: datetime
    
    @strawberry.field
    def mensaje_preview(self) -> str:
        """Campo calculado: preview del mensaje (primeros 100 caracteres)"""
        return self.mensaje[:100] + "..." if len(self.mensaje) > 100 else self.mensaje
    
    @strawberry.field  
    def dias_desde_creacion(self) -> int:
        """Campo calculado: días transcurridos desde la creación"""
        return (datetime.utcnow() - self.fecha_creacion).days

@strawberry.type
class ContactStats:
    """
    Estadísticas del sistema de contactos
    """
    total_contacts: int
    ventas_count: int
    soporte_count: int
    otro_count: int
    
    @strawberry.field
    def ventas_percentage(self) -> float:
        """Porcentaje de contactos de ventas"""
        return (self.ventas_count / self.total_contacts * 100) if self.total_contacts > 0 else 0.0
    
    @strawberry.field
    def soporte_percentage(self) -> float:
        """Porcentaje de contactos de soporte"""
        return (self.soporte_count / self.total_contacts * 100) if self.total_contacts > 0 else 0.0

@strawberry.type
class ClassificationResult:
    """
    Resultado de la clasificación de un mensaje
    """
    mensaje: str
    categoria_detectada: CategoryEnum
    confianza_score: float
    palabras_clave_encontradas: List[str]
    
@strawberry.type
class AutomationResult:
    """
    Resultado de la ejecución de automatizaciones
    """
    contact_id: int
    categoria: CategoryEnum
    success: bool
    action_performed: str
    message: str
    priority: Optional[PriorityEnum] = None

@strawberry.type
class ContactConnection:
    """
    Tipo de conexión para paginación estilo Relay
    """
    nodes: List[Contact]
    total_count: int
    has_next_page: bool
    has_previous_page: bool

@strawberry.input
class ContactInput:
    """
    Input para crear un nuevo contacto
    """
    nombre: str
    email: str
    mensaje: str

@strawberry.input  
class ContactFilter:
    """
    Filtros para la consulta de contactos
    """
    categoria: Optional[CategoryEnum] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    search_text: Optional[str] = None

@strawberry.input
class PaginationInput:
    """
    Input para paginación
    """
    limit: int = 20
    offset: int = 0

@strawberry.type
class ContactCreateResponse:
    """
    Respuesta para la creación de contactos
    """
    success: bool
    contact: Optional[Contact] = None
    error: Optional[str] = None
    automation_result: Optional[AutomationResult] = None