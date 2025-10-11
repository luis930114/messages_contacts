import logging
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from config import SMTP_CONFIG, SUPPORT_SERVICE_URL
from models.database import ContactDB

logger = logging.getLogger(__name__)

class AutomationService:
    """
    Servicio para ejecutar automatizaciones según la categoría del mensaje.
    
    Automatizaciones implementadas:
    - Ventas: Envío de email al equipo comercial
    - Soporte: Notificación al microservicio de soporte
    - Otro: Sin acción adicional
    """
    
    def __init__(self):
        self.smtp_config = SMTP_CONFIG
        self.support_service_url = SUPPORT_SERVICE_URL
    
    async def execute_automation(self, contact: ContactDB) -> Dict[str, Any]:
        """
        Ejecuta la automatización correspondiente según la categoría
        
        Args:
            contact: Objeto ContactDB con los datos del contacto
            
        Returns:
            Dict con el resultado de la automatización
        """
        try:
            result = {"contact_id": contact.id, "category": contact.categoria, "success": False}
            
            if contact.categoria == "ventas":
                result.update(await self._handle_sales_automation(contact))
            elif contact.categoria == "soporte":
                result.update(await self._handle_support_automation(contact))
            else:
                result.update({
                    "success": True,
                    "message": "No automation required for 'otro' category",
                    "action": "none"
                })
            
            logger.info(f"Automatización ejecutada para contacto {contact.id} - {contact.categoria}")
            return result
            
        except Exception as e:
            error_msg = f"Error en automatización para contacto {contact.id}: {str(e)}"
            logger.error(error_msg)
            return {
                "contact_id": contact.id,
                "category": contact.categoria,
                "success": False,
                "error": error_msg
            }
    
    async def _handle_sales_automation(self, contact: ContactDB) -> Dict[str, Any]:
        """
        Maneja automatización para mensajes de ventas
        """
        try:
            await self._log_sales_email(contact)
            
            return {
                "success": True,
                "action": "sales_email_sent",
                "message": f"Email de ventas enviado para {contact.nombre}",
                "recipient": "sales@company.com"
            }
            
        except Exception as e:
            raise Exception(f"Error en automatización de ventas: {str(e)}")
    
    async def _handle_support_automation(self, contact: ContactDB) -> Dict[str, Any]:
        """
        Maneja automatización para mensajes de soporte
        """
        try:
            payload = {
                "contact_id": contact.id,
                "customer_name": contact.nombre,
                "customer_email": contact.email,
                "message": contact.mensaje,
                "priority": self._determine_priority(contact.mensaje),
                "created_at": contact.fecha_creacion.isoformat(),
                "source": "contact_form"
            }
            
            # En desarrollo/demo: Solo logging
            await self._log_support_notification(payload)
            
            return {
                "success": True,
                "action": "support_notification_sent",
                "message": f"Notificación de soporte enviada para {contact.nombre}",
                "priority": payload["priority"],
                "payload": payload
            }
            
        except Exception as e:
            raise Exception(f"Error en automatización de soporte: {str(e)}")
    
    async def _log_sales_email(self, contact: ContactDB):
        """Simula envío de email para demo"""
        logger.info("SIMULACIÓN - EMAIL DE VENTAS")
        logger.info(f"   To: sales@company.com")
        logger.info(f"   Subject: Nueva consulta de ventas - {contact.nombre}")
        logger.info(f"   Cliente: {contact.nombre} ({contact.email})")
        logger.info(f"   Mensaje: {contact.mensaje[:100]}...")
        logger.info(f"   Fecha: {contact.fecha_creacion}")
    
    async def _log_support_notification(self, payload: Dict):
        """Simula notificación a soporte para demo"""
        logger.info("SIMULACIÓN - NOTIFICACIÓN DE SOPORTE")
        logger.info(f"   URL: {self.support_service_url}")
        logger.info(f"   Cliente: {payload['customer_name']}")
        logger.info(f"   Prioridad: {payload['priority']}")
        logger.info(f"   Payload: {payload}")
        
    
    def _determine_priority(self, message: str) -> str:
        """
        Determina la prioridad del ticket de soporte basado en el mensaje
        """
        message_lower = message.lower()
        
        high_priority_keywords = [
            'urgente', 'emergencia', 'crítico', 'no funciona', 'caído',
            'urgent', 'emergency', 'critical', 'down', 'broken'
        ]
        
        if any(keyword in message_lower for keyword in high_priority_keywords):
            return "high"
        else:
            return "normal"