#  Contact Management Backend

Backend profesional para gestión de mensajes de contacto con clasificación automática por IA y sistema de automatizaciones.

## Características Principales

- **API REST** con FastAPI y documentación automática
- **Clasificación automática** de mensajes con IA/NLP
- **Automatizaciones inteligentes** según categoría detectada
- **Base de datos** con SQLAlchemy y migraciones
- **Sistema de filtros** y paginación avanzada
- **Estadísticas** y monitoreo incluidos
- **Docker** ready para deployment
- **Validación robusta** con Pydantic
- **CORS configurado** para frontend

## Tecnologías Utilizadas

- **Framework:** FastAPI 0.104+
- **Base de datos:** SQLite (desarrollo) / PostgreSQL (producción)
- **ORM:** SQLAlchemy 2.0
- **Validación:** Pydantic v2
- **IA/NLP:** Clasificación por palabras clave (extensible)
- **Deployment:** Docker + Docker Compose
- **Testing:** pytest + httpx

## Funcionalidades Implementadas

### 1. Recepción de Mensajes
- `POST /contact` - Recibe mensajes desde formulario web
- Validación automática de datos (email, longitud de campos)
- Generación automática de ID y timestamp

### 2. Clasificación por IA
- Análisis automático del contenido del mensaje
- Clasificación en: **Ventas**, **Soporte**, **Otro**
- Sistema extensible para integrar modelos más avanzados

### 3. Automatizaciones
- **Ventas:** Envío automático de email al equipo comercial
- **Soporte:** Notificación al microservicio de soporte técnico
- **Otro:** Sin acción adicional

### 4. Consulta y Filtros
- `GET /contacts` - Lista todos los mensajes
- Filtrado por categoría: `/contacts?categoria=ventas`
- Paginación: `/contacts?limit=50&offset=100`
- Ordenamiento por fecha (más recientes primero)

## Instalación y Uso

### Opción 1: Instalación Local

```bash
# Clonar repositorio
git clone https://github.com/luis930114/messages_contacts.git
cd contact-backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar aplicación
python main.py
# O usando uvicorn directamente:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Opción 2: Docker (Recomendado)

```bash
# Desarrollo con Docker Compose
docker-compose up --build

# Solo la aplicación
docker build -t contact-backend .
docker run -p 8000:8000 contact-backend
```

## Documentación de la API

Una vez iniciada la aplicación, accede a:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## 🧪 Ejemplos de Uso

### Crear un contacto
```bash
curl -X POST "http://localhost:8000/contact" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Pérez",
    "email": "juan@example.com",
    "mensaje": "Hola, me interesa conocer los precios de sus servicios"
  }'
```

### Consultar contactos de ventas
```bash
curl "http://localhost:8000/contacts?categoria=ventas"
```

### Obtener estadísticas
```bash
curl "http://localhost:8000/stats"
```

## API Reference

### SERVICIOS REST

#### Crear un contacto

```http
  POST api/v1/contact
    Crear un nuevo usuario
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `nombre` | `string` | **Required**. Your nombre |
| `email` | `string` | **Required**. Your email |
| `mensaje` | `string` | **Required**. Your mensaje |

#### Ver todos los contacto

```http
  GET api/v1/contact
    Ver todos los contactos
```

#### Ver contactos por categoria

```http
  GET api/v1/contacts?categoria={categoria_nombre}
    Ver contactos por categoria
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `categoria_nombre` | `string` | **Required**. Tiene las opciones de ser ventas, soporte y otros |


#### Ver un contacto por su id

```http
  GET api/v1/contacts7{id}
    Ver un contacto por su id
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `id` | `string` | **Required**. Id del contacto que quiere buscar |

#### Ver estadisticas

```http
  GET /api/v1/stats
    Ver estadisticas como son el total de contactos y el total por categorías.
```

### SERVICIOS GRAPHQL

Para ingresar a utilizar los servicios de GraphQl ingresamos por el end point /graphql y podemos utilizar los siguientes queries:

#### Obtener lista de contactos con filtros y paginación
```graphql
  query {
    contacts(
      filter: { categoria: {categoria}, searchText: "interesa" }
      pagination: { limit: 10, offset: 0 }
    ) {
      nodes {
        id
        nombre
        email
        categoria
        mensajePreview
      }
      totalCount
      hasNextPage
    }
  }
```

#### Obtener un contacto específico por ID

```graphql
query {
          contact(id: {id}) {
            id
            nombre
            email
            mensaje
            categoria
            diasDesdeCreacion
          }
        }
```

#### Obtener estadísticas
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

####  Clasificar un mensaje sin guardarlo
```graphql
        query {
          classifyMessage(mensaje: "Hola, quiero comprar sus servicios") {
            categoriaDetectada
            confianzaScore
            palabrasClaveEncontradas
          }
        }
```

#### Crear un nuevo contacto
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

#### Eliminar un contacto por ID
```graphql
        mutation {
          deleteContact(id: 1)
        }
```


## Configuración Avanzada

### Variables de Entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `DATABASE_URL` | URL de conexión a la BD | `sqlite:///./contacts.db` |
| `SMTP_SERVER` | Servidor SMTP para emails | `smtp.gmail.com` |
| `SMTP_PORT` | Puerto SMTP | `587` |
| `EMAIL_USER` | Usuario de email | - |
| `EMAIL_PASSWORD` | Contraseña de email | - |
| `SUPPORT_SERVICE_URL` | URL del servicio de soporte | `http://localhost:8001/support-service` |

### Extender la Clasificación IA

El sistema actual usa clasificación por palabras clave. Para integrar modelos más avanzados:

```python
# Ejemplo con HuggingFace Transformers
from transformers import pipeline

class AdvancedMessageClassifier:
    def __init__(self):
        self.classifier = pipeline(
            "text-classification",
            model="your-model/contact-classifier"
        )
    
    def classify_message(self, message: str) -> str:
        result = self.classifier(message)
        # Mapear resultado a nuestras categorías
        return self.map_category(result[0]['label'])
```

## Deployment en Producción

### Render.com (Recomendado)
1. Conecta tu repositorio en Render
2. Configura las variables de entorno
3. Deploy automático con cada push


## Testing

```bash
# Ejecutar todos los tests
pytest

```bash
# Ejecutar los tests de los modelos
pytest test/test_models.py

## Próximas Mejoras

- [ ] Integración con OpenAI/Claude para clasificación más precisa
- [ ] Sistema de webhooks para notificaciones en tiempo real  
- [ ] Dashboard administrativo con métricas
- [ ] Rate limiting y autenticación
- [ ] Logs estructurados con ELK stack
- [ ] Métricas con Prometheus/Grafana


## Licencia

MIT License - ver archivo `LICENSE` para detalles.

---

**Desarrollado por [@luis930114](https://github.com/luis930114) usando FastAPI y Python**
