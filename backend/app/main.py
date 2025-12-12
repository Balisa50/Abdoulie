import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.routers import audit_results, clients, contracts, health, invoices, invoice
from app.security import RateLimitMiddleware, SecurityHeadersMiddleware
from app.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API key authentication: {'enabled' if settings.require_api_key else 'disabled'}")
    logger.info(f"Rate limiting: {'enabled' if settings.enable_rate_limiting else 'disabled'}")
    yield
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production or settings.debug else None,
        redoc_url="/redoc" if not settings.is_production or settings.debug else None,
        openapi_url="/openapi.json" if not settings.is_production or settings.debug else None,
    )

    # Security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # Rate limiting middleware
    app.add_middleware(
        RateLimitMiddleware,
        calls=settings.rate_limit_calls,
        period=settings.rate_limit_period,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Trusted host middleware (production only)
    if settings.is_production:
        allowed_hosts = ["*"]  # Configure with actual hosts in production
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

    # Exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle validation errors with sanitized output."""
        if settings.is_production and not settings.debug:
            # Don't expose validation details in production
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": "Invalid request data"},
            )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle general exceptions with sanitized output."""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)

        if settings.is_production and not settings.debug:
            # Don't expose internal errors in production
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"},
            )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )

    # Include routers
    app.include_router(health.router)
    app.include_router(invoice.router)
    app.include_router(invoices.router)
    app.include_router(clients.router)
    app.include_router(contracts.router)
    app.include_router(audit_results.router)

    return app


app = create_app()
