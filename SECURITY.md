# Security Documentation

## Security Features

This application implements multiple layers of security to ensure data protection and system integrity.

### 1. Authentication & Authorization

#### API Key Authentication
- **Enabled in Production**: All API endpoints require valid API keys
- **Configuration**: Set `REQUIRE_API_KEY=True` and provide keys via `API_KEYS` environment variable
- **Header**: Include `X-API-Key: your-api-key` in all API requests
- **Generation**: Use `python -c "import secrets; print(secrets.token_urlsafe(32))"` to generate secure keys

### 2. Rate Limiting

#### Protection Against Abuse
- **Default Limits**: 100 requests per 60 seconds per IP address
- **Configuration**: Adjust via `RATE_LIMIT_CALLS` and `RATE_LIMIT_PERIOD`
- **Response Headers**: 
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Timestamp when limit resets
- **429 Response**: Returns when limit exceeded with `Retry-After` header

### 3. Security Headers

All responses include comprehensive security headers:

- **X-Content-Type-Options**: `nosniff` - Prevents MIME type sniffing
- **X-Frame-Options**: `DENY` - Prevents clickjacking attacks
- **X-XSS-Protection**: `1; mode=block` - Enables XSS filtering
- **Strict-Transport-Security**: `max-age=31536000; includeSubDomains` - Enforces HTTPS
- **Content-Security-Policy**: Restricts resource loading to prevent XSS
- **Permissions-Policy**: Disables unnecessary browser features
- **Referrer-Policy**: `strict-origin-when-cross-origin` - Controls referrer information

### 4. Input Validation

#### File Upload Security
- **Type Validation**: Only PDF files allowed
- **Size Limits**: 10MB maximum (configurable via `MAX_UPLOAD_SIZE`)
- **Content-Type Validation**: Verifies MIME type
- **Filename Sanitization**: Blocks path traversal attempts
- **Temporary File Handling**: Secure cleanup after processing

#### Request Validation
- **Pydantic Models**: Strong typing and automatic validation
- **SQL Injection Protection**: SQLAlchemy parameterized queries
- **XSS Protection**: Input sanitization and output encoding

### 5. CORS Configuration

#### Cross-Origin Resource Sharing
- **Production**: Restricted to specific allowed origins
- **Development**: Includes localhost for testing
- **Methods**: Configurable allowed HTTP methods
- **Credentials**: Optional credential support
- **Headers**: Controlled header access

### 6. Error Handling

#### Secure Error Responses
- **Production Mode**: Generic error messages (no internal details exposed)
- **Development Mode**: Detailed errors for debugging
- **Logging**: All errors logged with full context server-side
- **Status Codes**: Proper HTTP status codes for all scenarios

### 7. Database Security

#### Connection Security
- **Connection Pooling**: Limited pool size to prevent exhaustion
- **Parameterized Queries**: SQLAlchemy ORM prevents SQL injection
- **Password Encryption**: Strong password hashing with bcrypt
- **Migrations**: Version-controlled schema changes with Alembic

### 8. Secrets Management

#### Environment Variables
- **No Hardcoded Secrets**: All secrets via environment variables
- **Production Validation**: Startup checks for insecure defaults
- **Separate Configurations**: Different configs for dev/staging/prod
- **.env Files**: Ignored by git, never committed

### 9. Logging & Monitoring

#### Security Logging
- **Request Logging**: All API requests logged with metadata
- **Error Logging**: Full error context with stack traces
- **Security Events**: Authentication failures, rate limit hits
- **Format**: JSON format for production (easily parsed)

### 10. Docker Security

#### Container Hardening
- **Non-Root User**: Application runs as unprivileged user
- **Minimal Images**: Alpine-based images for smaller attack surface
- **No Unnecessary Tools**: Only required packages installed
- **Health Checks**: Automatic container health monitoring
- **Network Isolation**: Containers on isolated bridge network
- **Port Binding**: Production ports bound to localhost only

## Production Deployment Checklist

### Pre-Deployment Security Checks

- [ ] **Change Default Credentials**
  - [ ] Database password changed from default
  - [ ] Redis password set
  - [ ] Secret key changed to strong random value

- [ ] **Configure API Keys**
  - [ ] Generate strong API keys (32+ characters)
  - [ ] Set `REQUIRE_API_KEY=True`
  - [ ] Distribute keys securely to clients

- [ ] **Environment Configuration**
  - [ ] `ENVIRONMENT=production`
  - [ ] `DEBUG=False`
  - [ ] CORS origins set to actual domains (no localhost)
  - [ ] Database URL uses production credentials
  - [ ] AWS credentials configured

- [ ] **TLS/HTTPS**
  - [ ] SSL certificates obtained and configured
  - [ ] Force HTTPS redirects enabled
  - [ ] Certificate auto-renewal configured

- [ ] **Network Security**
  - [ ] Database port not publicly exposed
  - [ ] Redis port not publicly exposed
  - [ ] Firewall rules configured
  - [ ] VPC/private network configured

- [ ] **Monitoring & Logging**
  - [ ] Centralized logging configured
  - [ ] Error alerting set up
  - [ ] Performance monitoring enabled
  - [ ] Security event monitoring active

- [ ] **Backups**
  - [ ] Database backup strategy implemented
  - [ ] Backup restoration tested
  - [ ] Backup encryption enabled

- [ ] **Dependency Security**
  - [ ] All dependencies updated to latest stable
  - [ ] Vulnerability scan performed
  - [ ] Security advisories reviewed

## Security Best Practices

### For Developers

1. **Never commit secrets** - Use environment variables
2. **Keep dependencies updated** - Regular security patches
3. **Validate all input** - Never trust user input
4. **Use parameterized queries** - Prevent SQL injection
5. **Log security events** - Track authentication failures
6. **Test error handling** - Ensure no sensitive data leaks

### For Operations

1. **Rotate credentials regularly** - API keys, database passwords
2. **Monitor logs** - Watch for suspicious activity
3. **Keep systems patched** - Operating system and dependencies
4. **Implement backups** - Regular automated backups
5. **Use HTTPS everywhere** - No unencrypted communication
6. **Limit access** - Principle of least privilege

### For API Consumers

1. **Store API keys securely** - Never in client-side code
2. **Use HTTPS only** - Encrypted communication
3. **Handle rate limits** - Implement exponential backoff
4. **Validate responses** - Don't trust API responses blindly
5. **Report vulnerabilities** - Responsible disclosure

## Vulnerability Reporting

If you discover a security vulnerability, please email security@yourdomain.com with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

**Do not** create public issues for security vulnerabilities.

## Security Updates

This document is reviewed and updated regularly. Last review: 2024-12-12

## Compliance

This application implements security controls aligned with:

- OWASP Top 10 Web Application Security Risks
- CIS Docker Benchmarks
- NIST Cybersecurity Framework
- SOC 2 Type II controls (in progress)

## Additional Resources

- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
