import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class MessageClassifier:
    """
    Servicio de clasificación de mensajes usando NLP.
    
    Implementación actual: Clasificación por palabras clave
    Extensible para: OpenAI, HuggingFace, modelos custom, etc.
    """
    
    def __init__(self):
        self.sales_keywords = [
            'comprar', 'precio', 'costo', 'cotización', 'presupuesto', 'venta',
            'producto', 'servicio', 'oferta', 'descuento', 'comercial', 'adquirir',
            'cuánto cuesta', 'me interesa', 'quisiera', 'necesito', 'contratar',
            'buy', 'price', 'quote', 'purchase', 'sale', 'offer', 'discount',
            'cost', 'interested', 'need', 'want', 'hire'
        ]
        
        self.support_keywords = [
            'problema', 'error', 'bug', 'ayuda', 'soporte', 'técnico', 'falla',
            'no funciona', 'roto', 'arreglar', 'reparar', 'urgente', 'emergencia',
            'support', 'help', 'issue', 'technical', 'assistance', 'trouble',
            'fix', 'repair', 'maintenance', 'broken', 'not working', 'urgent'
        ]
        
        self.sales_patterns = [
            'cuánto', 'precio', '$', 'comprar', 'contratar', 'me interesa',
            'quisiera saber', 'necesito información'
        ]
        
        self.support_patterns = [
            'no funciona', 'problema con', 'error en', 'ayuda con',
            'no puedo', 'está roto', 'falla'
        ]
    
    def classify_message(self, message: str) -> str:
        """
        Clasifica un mensaje en una de las tres categorías:
        - ventas: Consultas comerciales, precios, compras
        - soporte: Problemas técnicos, ayuda, errores
        - otro: Todo lo demás
        
        Args:
            message (str): Mensaje a clasificar
            
        Returns:
            str: Categoría detectada ('ventas', 'soporte', 'otro')
        """
        message_lower = message.lower()
        
        sales_score = self._calculate_keyword_score(message_lower, self.sales_keywords)
        support_score = self._calculate_keyword_score(message_lower, self.support_keywords)
        
        sales_pattern_score = self._calculate_pattern_score(message_lower, self.sales_patterns) * 2
        support_pattern_score = self._calculate_pattern_score(message_lower, self.support_patterns) * 2
        
        final_sales_score = sales_score + sales_pattern_score
        final_support_score = support_score + support_pattern_score
        
        if final_sales_score > final_support_score and final_sales_score > 0:
            category = "ventas"
        elif final_support_score > final_sales_score and final_support_score > 0:
            category = "soporte"
        else:
            category = "otro"
        
        logger.info(f"Clasificación: '{category}' (ventas: {final_sales_score}, soporte: {final_support_score})")
        return category
    
    def _calculate_keyword_score(self, message: str, keywords: List[str]) -> int:
        """Calcula puntuación basada en palabras clave exactas"""
        return sum(1 for keyword in keywords if keyword in message)
    
    def _calculate_pattern_score(self, message: str, patterns: List[str]) -> int:
        """Calcula puntuación basada en patrones más específicos"""
        return sum(1 for pattern in patterns if pattern in message)
    
    def get_classification_details(self, message: str) -> Dict:
        """
        Devuelve detalles de la clasificación para debugging
        """
        message_lower = message.lower()
        
        sales_matches = [kw for kw in self.sales_keywords if kw in message_lower]
        support_matches = [kw for kw in self.support_keywords if kw in message_lower]
        
        return {
            "message_preview": message[:100] + "..." if len(message) > 100 else message,
            "sales_matches": sales_matches,
            "support_matches": support_matches,
            "final_category": self.classify_message(message)
        }