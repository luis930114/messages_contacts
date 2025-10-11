# ============================================================================
# services/classifier_huggingface.py - Clasificador con HuggingFace
# ============================================================================

from services.classifier_interface import IMessageClassifier, ClassificationResult
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from typing import List
import torch

class HuggingFaceClassifier(IMessageClassifier):
    """
    Clasificador usando modelos pre-entrenados de HuggingFace.
    
    Ventajas:
    - Estado del arte en NLP
    - Modelos multilingües (BERT, RoBERTa, etc.)
    - Comprensión profunda del contexto
    - Transfer learning de millones de textos
    
    Desventajas:
    - Requiere más recursos (RAM/GPU)
    - Más lento que scikit-learn
    """
    
    def __init__(self, model_name: str = "distilbert-base-multilingual-cased"):
        """
        Inicializar clasificador HuggingFace
        
        Args:
            model_name: Modelo a usar
                - distilbert-base-multilingual-cased: Ligero, multiidioma
                - bert-base-multilingual-cased: Más preciso, multiidioma
                - xlm-roberta-base: Excelente para multiidioma
        """
        self.model_name = model_name
        self.categories = ["ventas", "soporte", "otro"]
        
        # Cargar tokenizer y modelo base
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Nota: En producción, necesitarías fine-tunar el modelo
        # Por ahora usamos zero-shot classification
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"  # Modelo para zero-shot
        )
        
        self._is_trained = True  # Zero-shot no requiere entrenamiento
    
    def classify(self, mensaje: str) -> ClassificationResult:
        """
        Clasificar usando zero-shot classification
        """
        # Definir hipótesis para cada categoría
        hypothesis_template = "Este mensaje trata sobre {}."
        candidate_labels = {
            "ventas": "ventas, compras, precios, cotizaciones",
            "soporte": "soporte técnico, problemas, errores, ayuda",
            "otro": "información general, otros temas"
        }
        
        # Clasificar
        result = self.classifier(
            mensaje,
            list(candidate_labels.keys()),
            hypothesis_template=hypothesis_template,
            multi_label=False
        )
        
        # Extraer resultados
        categoria = result['labels'][0]
        confianza = result['scores'][0]
        
        # Crear diccionario de probabilidades
        probabilidades = {
            label: score 
            for label, score in zip(result['labels'], result['scores'])
        }
        
        # Extraer palabras clave (simplificado)
        palabras_clave = self._extract_keywords_simple(mensaje)
        
        return ClassificationResult(
            categoria=categoria,
            confianza=confianza,
            probabilidades=probabilidades,
            palabras_clave=palabras_clave
        )
    
    def train(self, mensajes: List[str], categorias: List[str]) -> None:
        """
        Para fine-tuning real del modelo (avanzado)
        
        Nota: Esto requeriría:
        1. Preparar dataset en formato adecuado
        2. Configurar training arguments
        3. Usar Trainer de HuggingFace
        4. GPU para entrenamiento eficiente
        """
        print("Fine-tuning de HuggingFace requiere implementación avanzada")
        print("Usando zero-shot classification por defecto")
    
    def _extract_keywords_simple(self, mensaje: str) -> List[str]:
        """Extraer palabras clave simple (sin análisis profundo)"""
        # Tokenizar
        tokens = mensaje.lower().split()
        
        # Palabras importantes comunes
        important_words = [
            'comprar', 'precio', 'costo', 'problema', 'error',
            'ayuda', 'soporte', 'información'
        ]
        
        keywords = [word for word in tokens if word in important_words]
        return keywords[:5]
    
    def is_trained(self) -> bool:
        return self._is_trained
