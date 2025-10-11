
# ============================================================================
# services/classifier_keyword.py - Clasificador original (baseline)
# ============================================================================

from services.classifier_interface import IMessageClassifier, ClassificationResult
from typing import List

class KeywordClassifier(IMessageClassifier):
    """
    Clasificador original basado en palabras clave.
    Sirve como baseline para comparar con modelos NLP.
    """
    
    def __init__(self):
        self.sales_keywords = [
            'comprar', 'precio', 'costo', 'cotización', 'presupuesto', 'venta',
            'producto', 'servicio', 'oferta', 'descuento', 'buy', 'price', 'quote'
        ]
        
        self.support_keywords = [
            'problema', 'error', 'bug', 'ayuda', 'soporte', 'técnico', 'falla',
            'no funciona', 'support', 'help', 'issue', 'technical'
        ]
    
    def classify(self, mensaje: str) -> ClassificationResult:
        mensaje_lower = mensaje.lower()
        
        # Contar coincidencias
        sales_matches = [kw for kw in self.sales_keywords if kw in mensaje_lower]
        support_matches = [kw for kw in self.support_keywords if kw in mensaje_lower]
        
        sales_score = len(sales_matches)
        support_score = len(support_matches)
        total_score = sales_score + support_score
        
        # Determinar categoría
        if sales_score > support_score and sales_score > 0:
            categoria = "ventas"
            confianza = min(sales_score / 3, 1.0)  # Normalizar
            palabras = sales_matches
        elif support_score > sales_score and support_score > 0:
            categoria = "soporte"
            confianza = min(support_score / 3, 1.0)
            palabras = support_matches
        else:
            categoria = "otro"
            confianza = 0.5
            palabras = []
        
        # Calcular probabilidades
        if total_score > 0:
            prob_ventas = sales_score / total_score
            prob_soporte = support_score / total_score
            prob_otro = 0.0
        else:
            prob_ventas = 0.33
            prob_soporte = 0.33
            prob_otro = 0.34
        
        return ClassificationResult(
            categoria=categoria,
            confianza=confianza,
            probabilidades={
                "ventas": prob_ventas,
                "soporte": prob_soporte,
                "otro": prob_otro
            },
            palabras_clave=palabras
        )
    
    def train(self, mensajes: List[str], categorias: List[str]) -> None:
        # No requiere entrenamiento
        pass
    
    def is_trained(self) -> bool:
        return True  # Siempre está "entrenado"
