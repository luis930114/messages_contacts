# ============================================================================
# services/classifier_factory.py - Factory para crear clasificadores
# ============================================================================

from services.classifier_interface import IMessageClassifier
from services.classifier_keyword import KeywordClassifier
from services.classifier_sklearn import SklearnClassifier
from services.classifier_spacy import SpacyClassifier
from services.classifier_huggingface import HuggingFaceClassifier
from typing import Literal
import os
import logging

ClassifierType = Literal["keyword", "sklearn", "spacy", "huggingface"]

logger = logging.getLogger(__name__)

class ClassifierFactory:
    """
    Factory para crear diferentes tipos de clasificadores.
    
    Permite cambiar fácilmente entre implementaciones.
    """
    
    @staticmethod
    def create(
        classifier_type: ClassifierType = None
    ) -> IMessageClassifier:
        """
        Crear clasificador según tipo
        
        Args:
            classifier_type: Tipo de clasificador
                - "keyword": Basado en palabras clave (original)
                - "sklearn": Machine Learning con scikit-learn
                - "spacy": NLP con spaCy
                - "huggingface": Transformers con HuggingFace
                
        Returns:
            Instancia del clasificador
        """
        # Si no se especifica, leer de variable de entorno
        if classifier_type is None:
            classifier_type = os.getenv("CLASSIFIER_TYPE", "sklearn")
            logger.info(f"tipo de clasificador: {classifier_type}")
        
        if classifier_type == "keyword":
            return KeywordClassifier()
        elif classifier_type == "sklearn":
            return SklearnClassifier()
        elif classifier_type == "spacy":
            return SpacyClassifier()
        elif classifier_type == "huggingface":
            return HuggingFaceClassifier()
        else:
            raise ValueError(f"Tipo de clasificador inválido: {classifier_type}")
