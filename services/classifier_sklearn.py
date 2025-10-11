from services.classifier_interface import IMessageClassifier, ClassificationResult
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
import os
from typing import List
import numpy as np

class SklearnClassifier(IMessageClassifier):
    """
    Clasificador usando scikit-learn con TF-IDF y Naive Bayes.
    
    Ventajas:
    - Más preciso que keywords
    - Rápido y ligero
    - No requiere GPU
    - Fácil de entrenar con datos nuevos
    """
    
    def __init__(self, model_path: str = "models/sklearn_classifier.pkl"):
        self.model_path = model_path
        self.pipeline = None
        self.categories = ["ventas", "soporte", "otro"]
        
        # Intentar cargar modelo pre-entrenado
        if os.path.exists(model_path):
            self.load_model()
        else:
            # Crear pipeline nuevo
            self.pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=1000,
                    ngram_range=(1, 2),  # Unigramas y bigramas
                    stop_words='english',  # Filtrar palabras comunes
                    lowercase=True
                )),
                ('clf', MultinomialNB(alpha=0.1))  # Clasificador Naive Bayes
            ])
            
            # Entrenar con datos por defecto
            self._train_with_default_data()
    
    def classify(self, mensaje: str) -> ClassificationResult:
        if not self.is_trained():
            raise ValueError("El modelo no está entrenado")
        
        # Predecir categoría
        categoria = self.pipeline.predict([mensaje])[0]
        
        # Obtener probabilidades
        probabilidades = self.pipeline.predict_proba([mensaje])[0]
        
        # Mapear probabilidades a categorías
        prob_dict = {
            cat: float(prob) 
            for cat, prob in zip(self.pipeline.classes_, probabilidades)
        }
        
        # Confianza es la probabilidad de la categoría predicha
        confianza = float(max(probabilidades))
        
        # Extraer palabras importantes (feature importance)
        palabras_clave = self._extract_important_words(mensaje)
        
        return ClassificationResult(
            categoria=categoria,
            confianza=confianza,
            probabilidades=prob_dict,
            palabras_clave=palabras_clave
        )
    
    def train(self, mensajes: List[str], categorias: List[str]) -> None:
        """Entrenar el modelo con datos personalizados"""
        if len(mensajes) != len(categorias):
            raise ValueError("Mensajes y categorías deben tener la misma longitud")
        
        if len(mensajes) < 10:
            raise ValueError("Se necesitan al menos 10 ejemplos para entrenar")
        
        # Entrenar pipeline
        self.pipeline.fit(mensajes, categorias)
        
        # Guardar modelo
        self.save_model()
    
    def _train_with_default_data(self):
        """Entrenar con dataset básico por defecto"""
        mensajes_entrenamiento = [
            # Ventas
            "Hola, me interesa conocer los precios de sus servicios",
            "Quiero comprar sus productos",
            "¿Cuánto cuesta el desarrollo de una aplicación?",
            "Necesito una cotización para mi proyecto",
            "Me gustaría contratar sus servicios de consultoría",
            "¿Tienen ofertas o descuentos disponibles?",
            "Quisiera información sobre sus paquetes de servicio",
            "Estoy interesado en adquirir su producto premium",
            "¿Cuál es el precio de la licencia anual?",
            "Necesito presupuesto para desarrollo web",
            # Soporte
            "Tengo un problema con mi cuenta",
            "La aplicación no funciona correctamente",
            "Necesito ayuda técnica urgente",
            "Hay un error en el sistema de pagos",
            "No puedo acceder a mi dashboard",
            "El servicio está caído desde esta mañana",
            "Reporto un bug en la funcionalidad de reportes",
            "Necesito soporte para configurar mi cuenta",
            "La integración con la API falla constantemente",
            "Ayuda con problemas de autenticación",
            # Otro
            "¿En qué ciudad están ubicados?",
            "Me gustaría trabajar con ustedes",
            "¿Cuál es su horario de atención?",
            "Información general sobre la empresa",
            "Hola, solo quería saludar",
            "¿Tienen vacantes disponibles?",
            "Me interesa una alianza estratégica",
            "¿Cuál es su visión como empresa?",
            "Información sobre responsabilidad social",
            "¿Participan en eventos del sector?"
        ]
        
        categorias_entrenamiento = [
            "ventas", "ventas", "ventas", "ventas", "ventas",
            "ventas", "ventas", "ventas", "ventas", "ventas",
            "soporte", "soporte", "soporte", "soporte", "soporte",
            "soporte", "soporte", "soporte", "soporte", "soporte",
            "otro", "otro", "otro", "otro", "otro",
            "otro", "otro", "otro", "otro", "otro"
        ]
        
        self.train(mensajes_entrenamiento, categorias_entrenamiento)
    
    def _extract_important_words(self, mensaje: str, top_n: int = 5) -> List[str]:
        """Extraer palabras más importantes del mensaje"""
        try:
            # Obtener feature names del vectorizador
            vectorizer = self.pipeline.named_steps['tfidf']
            feature_names = vectorizer.get_feature_names_out()
            
            # Transformar mensaje
            vector = vectorizer.transform([mensaje])
            
            # Obtener índices de features con mayor peso
            indices = vector.toarray()[0].argsort()[-top_n:][::-1]
            
            # Obtener palabras correspondientes
            palabras = [feature_names[i] for i in indices if vector.toarray()[0][i] > 0]
            
            return palabras
        except:
            return []
    
    def save_model(self):
        """Guardar modelo entrenado"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.pipeline, f)
    
    def load_model(self):
        """Cargar modelo pre-entrenado"""
        with open(self.model_path, 'rb') as f:
            self.pipeline = pickle.load(f)
    
    def is_trained(self) -> bool:
        return self.pipeline is not None and hasattr(self.pipeline.named_steps['clf'], 'classes_')
