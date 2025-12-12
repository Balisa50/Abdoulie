# API Documentation

## Base URL

- Local development: `http://localhost:8000`
- Production: TBD

## Authentication

(To be implemented)

## Endpoints

### Health Check

#### GET /health

Returns the health status of the backend service.

**Response:**
```json
{
  "status": "healthy",
  "app": "Tesseract SaaS MVP",
  "version": "0.1.0",
  "timestamp": "2024-01-01T00:00:00.000000+00:00"
}
```

**Status Codes:**
- 200: Service is healthy

---

### Root

#### GET /

Returns basic information about the API.

**Response:**
```json
{
  "message": "Welcome to Tesseract SaaS MVP",
  "version": "0.1.0",
  "docs": "/docs"
}
```

**Status Codes:**
- 200: Success

---

## Interactive Documentation

The backend provides interactive API documentation powered by FastAPI:

- **Swagger UI**: http://localhost:8000/docs
  - Interactive API testing interface
  - Try out endpoints directly from the browser
  
- **ReDoc**: http://localhost:8000/redoc
  - Alternative documentation view
  - More readable format

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message here"
}
```

Common status codes:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error

## Rate Limiting

(To be implemented)

## Versioning

API version is included in responses. Future versions may use URL versioning:
- v1: `/api/v1/...`
- v2: `/api/v2/...`

## CORS

CORS is enabled for the following origins:
- http://localhost:3000 (frontend development)
- http://frontend:3000 (Docker internal)

Additional origins can be configured in `backend/app/settings.py`.

## Future Endpoints

The following endpoints are planned for implementation:

### Authentication
- POST /auth/register
- POST /auth/login
- POST /auth/logout
- GET /auth/me

### Users
- GET /users
- GET /users/{id}
- PUT /users/{id}
- DELETE /users/{id}

### Resources
(Additional resource endpoints to be defined)
