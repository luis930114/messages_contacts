# ============================================================================
# services/classifier_interface.py - Interfaz común para todos los clasificadores
# ============================================================================

from abc import ABC, abstractmethod
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ClassificationResult:
    """Resultado de clasificación con metadata"""
    categoria: str  # ventas, soporte, otro
    confianza: float  # 0.0 a 1.0
    probabilidades: Dict[str, float]  # Probabilidad por categoría
    palabras_clave: List[str] = None  # Palabras que influyeron

class IMessageClassifier(ABC):
    """
    Interfaz abstracta para clasificadores de mensajes.
    
    Permite cambiar entre diferentes implementaciones (keyword, ML, NLP)
    sin modificar el resto del código.
    """
    
    @abstractmethod
    def classify(self, mensaje: str) -> ClassificationResult:
        """
        Clasificar un mensaje
        
        Args:
            mensaje: Texto a clasificar
            
        Returns:
            ClassificationResult con categoría, confianza y metadata
        """
        pass
    
    @abstractmethod
    def train(self, mensajes: List[str], categorias: List[str]) -> None:
        """
        Entrenar el modelo (si es necesario)
        
        Args:
            mensajes: Lista de mensajes de entrenamiento
            categorias: Lista de categorías correspondientes
        """
        pass
    
    @abstractmethod
    def is_trained(self) -> bool:
        """Verificar si el modelo está entrenado"""
        pass
