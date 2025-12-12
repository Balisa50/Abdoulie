#!/bin/bash
#
# Security Audit Script for Tesseract SaaS MVP
# Checks for common security misconfigurations
#

set -e

echo "=================================="
echo "Tesseract SaaS MVP Security Audit"
echo "=================================="
echo ""

ERRORS=0
WARNINGS=0

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ERRORS=$((ERRORS + 1))
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

info() {
    echo -e "[INFO] $1"
}

# Check if .env file exists
if [ ! -f .env ] && [ ! -f .env.production ]; then
    error ".env or .env.production file not found"
else
    success "Environment file found"
fi

# Load environment variables
if [ -f .env.production ]; then
    ENV_FILE=".env.production"
elif [ -f .env ]; then
    ENV_FILE=".env"
fi

if [ -n "$ENV_FILE" ]; then
    export $(cat "$ENV_FILE" | grep -v '^#' | xargs)
fi

echo ""
echo "1. Checking Environment Configuration..."
echo "----------------------------------------"

# Check ENVIRONMENT setting
if [ "$ENVIRONMENT" = "production" ]; then
    success "Environment set to production"
    
    # Check DEBUG mode
    if [ "$DEBUG" = "True" ] || [ "$DEBUG" = "true" ]; then
        error "DEBUG mode is enabled in production! Set DEBUG=False"
    else
        success "DEBUG mode is disabled"
    fi
    
    # Check SECRET_KEY
    if [ -z "$SECRET_KEY" ]; then
        error "SECRET_KEY is not set"
    elif [ "$SECRET_KEY" = "CHANGE_THIS_IN_PRODUCTION_USE_STRONG_RANDOM_SECRET" ]; then
        error "SECRET_KEY is still using default value"
    elif [ ${#SECRET_KEY} -lt 32 ]; then
        warning "SECRET_KEY should be at least 32 characters"
    else
        success "SECRET_KEY is properly configured"
    fi
    
    # Check API key requirement
    if [ "$REQUIRE_API_KEY" != "True" ]; then
        warning "API key authentication is not required (REQUIRE_API_KEY=False)"
    else
        success "API key authentication is enabled"
    fi
    
    # Check if API keys are set
    if [ -z "$API_KEYS" ]; then
        error "No API keys configured"
    else
        success "API keys are configured"
    fi
    
else
    info "Environment set to: ${ENVIRONMENT:-development}"
    warning "Not running in production mode - some checks skipped"
fi

echo ""
echo "2. Checking Database Configuration..."
echo "--------------------------------------"

# Check database credentials
if echo "$DATABASE_URL" | grep -q "tesseract:tesseract"; then
    error "Using default database credentials"
else
    success "Database credentials appear to be customized"
fi

echo ""
echo "3. Checking AWS Configuration..."
echo "--------------------------------"

# Check AWS credentials
if [ "$AWS_ACCESS_KEY_ID" = "test" ] || [ "$AWS_SECRET_ACCESS_KEY" = "test" ]; then
    if [ "$ENVIRONMENT" = "production" ]; then
        error "Using test AWS credentials in production"
    else
        warning "Using test AWS credentials (OK for development)"
    fi
else
    success "AWS credentials are configured"
fi

echo ""
echo "4. Checking CORS Configuration..."
echo "----------------------------------"

if echo "$CORS_ORIGINS" | grep -q "localhost"; then
    if [ "$ENVIRONMENT" = "production" ]; then
        error "CORS allows localhost in production"
    else
        success "CORS allows localhost (OK for development)"
    fi
else
    success "CORS properly configured"
fi

echo ""
echo "5. Checking File Permissions..."
echo "--------------------------------"

# Check .env file permissions
if [ -f "$ENV_FILE" ]; then
    PERMS=$(stat -c %a "$ENV_FILE" 2>/dev/null || stat -f %A "$ENV_FILE" 2>/dev/null)
    if [ "$PERMS" != "600" ] && [ "$PERMS" != "400" ]; then
        warning "Environment file has loose permissions ($PERMS). Should be 600 or 400"
    else
        success "Environment file has secure permissions ($PERMS)"
    fi
fi

echo ""
echo "6. Checking Docker Configuration..."
echo "------------------------------------"

# Check if docker-compose is using production config
if [ -f docker-compose.prod.yml ]; then
    success "Production docker-compose file exists"
else
    warning "Production docker-compose file not found"
fi

# Check if containers are running as root
if command -v docker &> /dev/null; then
    if docker ps --format '{{.Names}}' | grep -q tesseract-backend; then
        USER_CHECK=$(docker exec tesseract-backend whoami 2>/dev/null || echo "unknown")
        if [ "$USER_CHECK" = "root" ]; then
            warning "Backend container running as root"
        else
            success "Backend container running as non-root user"
        fi
    fi
fi

echo ""
echo "7. Checking for Sensitive Files..."
echo "-----------------------------------"

# Check if sensitive files are in .gitignore
if [ -f .gitignore ]; then
    if grep -q "^\.env$" .gitignore; then
        success ".env files are in .gitignore"
    else
        error ".env files are NOT in .gitignore"
    fi
else
    error ".gitignore file not found"
fi

# Check if .env files are committed to git
if command -v git &> /dev/null; then
    if git ls-files | grep -q "\.env$"; then
        error ".env file is tracked by git!"
    else
        success ".env files are not tracked by git"
    fi
fi

echo ""
echo "8. Checking Rate Limiting..."
echo "----------------------------"

if [ "$ENABLE_RATE_LIMITING" = "True" ] || [ "$ENABLE_RATE_LIMITING" = "true" ]; then
    success "Rate limiting is enabled"
else
    if [ "$ENVIRONMENT" = "production" ]; then
        warning "Rate limiting is disabled in production"
    else
        info "Rate limiting is disabled (OK for development)"
    fi
fi

echo ""
echo "9. Checking SSL/TLS Configuration..."
echo "-------------------------------------"

# Check if running behind HTTPS (in production)
if [ "$ENVIRONMENT" = "production" ]; then
    info "Ensure HTTPS is configured via reverse proxy (Nginx/Traefik)"
    info "SSL certificates should be properly configured"
fi

echo ""
echo "10. Checking Dependencies..."
echo "----------------------------"

# Check for known vulnerabilities (if safety is installed)
if command -v safety &> /dev/null; then
    cd backend
    if safety check --json > /dev/null 2>&1; then
        success "No known vulnerabilities in Python dependencies"
    else
        warning "Potential vulnerabilities found in dependencies. Run: cd backend && safety check"
    fi
    cd ..
else
    info "Install 'safety' for dependency vulnerability scanning: pip install safety"
fi

echo ""
echo "=================================="
echo "Security Audit Summary"
echo "=================================="
echo -e "${RED}Errors:   $ERRORS${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
echo ""

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}⛔ CRITICAL ISSUES FOUND - DO NOT DEPLOY${NC}"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  WARNINGS FOUND - Review before deploying${NC}"
    exit 0
else
    echo -e "${GREEN}✅ All checks passed - Ready for deployment${NC}"
    exit 0
fi
