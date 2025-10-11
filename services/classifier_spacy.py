from services.classifier_interface import IMessageClassifier, ClassificationResult
import spacy
from spacy.training import Example
from spacy.util import minibatch
import random
from typing import List
import os

class SpacyClassifier(IMessageClassifier):
    """
    Clasificador usando spaCy con Text Categorization.
    
    Ventajas:
    - Entiende contexto lingüístico
    - Reconocimiento de entidades (NER)
    - Soporte multiidioma robusto
    - Análisis morfológico avanzado
    """
    
    def __init__(self, model_name: str = "es_core_news_sm"):
        """
        Inicializar clasificador spaCy
        
        Args:
            model_name: Modelo de spaCy a usar
                - es_core_news_sm: Español pequeño
                - es_core_news_md: Español mediano
                - en_core_web_sm: Inglés pequeño
        """
        try:
            # Intentar cargar modelo
            self.nlp = spacy.load(model_name)
        except OSError:
            # Si no está instalado, descargar
            print(f"Descargando modelo {model_name}...")
            os.system(f"python -m spacy download {model_name}")
            self.nlp = spacy.load(model_name)
        
        # Agregar componente de clasificación de texto si no existe
        if "textcat" not in self.nlp.pipe_names:
            textcat = self.nlp.add_pipe("textcat", last=True)
            textcat.add_label("ventas")
            textcat.add_label("soporte")
            textcat.add_label("otro")
        else:
            textcat = self.nlp.get_pipe("textcat")
        
        self._is_trained = False
        
        # Entrenar con datos por defecto
        self._train_with_default_data()
    
    def classify(self, mensaje: str) -> ClassificationResult:
        if not self.is_trained():
            raise ValueError("El modelo no está entrenado")
        
        # Procesar mensaje con spaCy
        doc = self.nlp(mensaje)
        
        # Obtener scores de categorías
        scores = doc.cats
        
        # Categoría con mayor score
        categoria = max(scores, key=scores.get)
        confianza = scores[categoria]
        
        # Extraer entidades y tokens relevantes
        palabras_clave = self._extract_keywords(doc)
        
        return ClassificationResult(
            categoria=categoria,
            confianza=confianza,
            probabilidades=scores,
            palabras_clave=palabras_clave
        )
    
    def train(self, mensajes: List[str], categorias: List[str], n_iter: int = 20) -> None:
        """
        Entrenar modelo spaCy
        
        Args:
            mensajes: Textos de entrenamiento
            categorias: Categorías correspondientes
            n_iter: Número de iteraciones de entrenamiento
        """
        # Preparar datos de entrenamiento
        train_data = []
        for mensaje, categoria in zip(mensajes, categorias):
            cats = {"ventas": 0.0, "soporte": 0.0, "otro": 0.0}
            cats[categoria] = 1.0
            train_data.append((mensaje, {"cats": cats}))
        
        # Obtener componente textcat
        textcat = self.nlp.get_pipe("textcat")
        
        # Entrenar
        optimizer = self.nlp.create_optimizer()
        
        for i in range(n_iter):
            random.shuffle(train_data)
            losses = {}
            
            # Crear batches
            batches = minibatch(train_data, size=8)
            
            for batch in batches:
                texts, annotations = zip(*batch)
                
                # Crear ejemplos
                examples = []
                for text, annot in zip(texts, annotations):
                    doc = self.nlp.make_doc(text)
                    example = Example.from_dict(doc, annot)
                    examples.append(example)
                
                # Actualizar modelo
                self.nlp.update(examples, sgd=optimizer, drop=0.2, losses=losses)
            
            if (i + 1) % 5 == 0:
                print(f"Iteración {i+1}/{n_iter}, Loss: {losses.get('textcat', 0):.4f}")
        
        self._is_trained = True
    
    def _train_with_default_data(self):
        """Entrenar con dataset por defecto"""
        mensajes = [
            # Ventas (español)
            "Hola, me interesa conocer los precios",
            "Quiero comprar sus servicios",
            "¿Cuánto cuesta?",
            "Necesito una cotización",
            "Me gustaría contratar",
            # Soporte (español)
            "Tengo un problema técnico",
            "La aplicación no funciona",
            "Necesito ayuda urgente",
            "Hay un error en el sistema",
            "No puedo acceder",
            # Otro (español)
            "¿Dónde están ubicados?",
            "Información general",
            "Hola",
            "¿Tienen vacantes?",
            "Me interesa colaborar"
        ]
        
        categorias = [
            "ventas", "ventas", "ventas", "ventas", "ventas",
            "soporte", "soporte", "soporte", "soporte", "soporte",
            "otro", "otro", "otro", "otro", "otro"
        ]
        
        self.train(mensajes, categorias, n_iter=10)
    
    def _extract_keywords(self, doc) -> List[str]:
        """Extraer palabras clave usando análisis spaCy"""
        keywords = []
        
        # Extraer sustantivos y verbos importantes
        for token in doc:
            if token.pos_ in ["NOUN", "VERB", "ADJ"] and not token.is_stop:
                keywords.append(token.lemma_)
        
        # Extraer entidades nombradas
        for ent in doc.ents:
            keywords.append(ent.text)
        
        return list(set(keywords))[:5]  # Top 5 únicas
    
    def is_trained(self) -> bool:
        return self._is_trained
