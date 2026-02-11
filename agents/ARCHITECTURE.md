# MCP Server HTTP Migration - Technical Specification

**Date**: February 5, 2026  
**Status**: Planning Phase Complete  
**Next Step**: Implementation

---

## 1. Executive Summary

This document outlines the technical specifications for migrating the existing `llm_public` MCP (Model Context Protocol) server from STDIO transport to HTTP transport. The migration enables AI agents to interact with the server via HTTP endpoints while maintaining the existing security posture and leveraging the proven `ibkr_oauth.py` implementation for IBKR API authentication.

### Key Objectives

- Migrate from STDIO to HTTP transport (streamable-http)
- Implement REST API wrapper for agent communication
- Maintain security boundaries (agents cannot access code or host system)
- Use existing `ibkr_oauth.py` for OAuth 1.0a authentication (more secure than third-party alternatives)
- Containerize with Docker for deployment
- Apply input validation and endpoint whitelisting

### Architecture Decision

**Language Choice**: Python (vs TypeScript/ibkr-client)

Python was chosen over TypeScript with `ibkr-client` because:
- Superior secrets management (isolated files vs single oauth1.json)
- Full control over security-critical code
- Smaller Docker footprint (~150MB vs ~900MB)
- Fewer dependencies (smaller attack surface)
- Proven `ibkr_oauth.py` implementation (415 lines of auditable code)

---

## 2. Security Model

### 2.1 Threat Model

The server operates under the following assumptions:

1. **Trusted Network**: Agents operate within a trusted network boundary
2. **No Trading Endpoints**: Only read-only endpoints are exposed
3. **Code Isolation**: Agents cannot view or modify server code
4. **Secrets Isolation**: Sensitive credentials are stored on host, mounted as read-only volumes

### 2.2 Security Boundaries

```
┌─────────────────────────────────────────────────────────────────┐
│                      SECURITY BOUNDARIES                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   AI AGENTS ──HTTP──▶ [CONTAINER FIREWALL] ──▶ [APP LAYER]     │
│                                          │                      │
│                                          ▼                      │
│                                 [INPUT VALIDATION]              │
│                                 [ENDPOINT WHITELIST]            │
│                                 [ERROR SANITIZATION]           │
│                                          │                      │
│                                          ▼                      │
│                              [IBKR OAUTH CLIENT]                │
│                              [Secrets via Mounted Volumes]      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Secrets Management

**Approach**: Environment variables pointing to host paths

```bash
# .env file structure
IBIND_USE_OAUTH=True
IBIND_OAUTH1A_CONSUMER_KEY_FILE=/run/secrets/consumer_key
IBIND_OAUTH1A_ENCRYPTION_KEY_FP=/run/secrets/private_encryption.pem
IBIND_OAUTH1A_SIGNATURE_KEY_FP=/run/secrets/private_signature.pem
IBIND_OAUTH1A_ACCESS_TOKEN_FILE=/run/secrets/access_token
IBIND_OAUTH1A_DH_PRIME_FILE=/run/secrets/dh_prime
```

**Security Benefits**:
- Secrets never baked into Docker image
- Read-only mounts prevent container modification
- Host filesystem permissions apply
- No secrets in version control

---

## 3. Endpoint Whitelist

### 3.1 Allowed Endpoints

Only the following IBKR API endpoints are exposed:

```python
ALLOWED_ENDPOINTS = {
    # Account Management
    "iserver/account",
    
    # Security Definitions
    "iserver/secdef/search",
    "iserver/secdef/info",
    "iserver/contract",
    "iserver/secdef/bond-filters",
    
    # Trading Services
    "trsrv/secdef",
    "trsrv/futures",
    "trsrv/stocks",
    
    # Market Data
    "iserver/marketdata/snapshot",
    "iserver/marketdata/history",
    
    # Alerts
    "iserver/account/{accountId}/alerts"
}
```

### 3.2 Blocked Endpoints (Not Exposed)

All trading/order endpoints are intentionally blocked:

- `iserver/place/order` - Order placement
- `iserver/account/{id}/order` - Order management
- Any other trading-related endpoints

### 3.3 Rationale

The whitelist approach ensures:
- **No accidental exposure** of trading capabilities
- **Defense in depth** - multiple validation layers
- **Audit trail** - all endpoint calls logged
- **Principal of least privilege** - minimal endpoint exposure

---

## 4. API Specification

### 4.1 REST API Endpoints

#### POST /api/call_endpoint

Main endpoint for IBKR API calls.

**Request**:
```json
POST /api/call_endpoint
Content-Type: application/json

{
  "endpoint": "iserver/account",
  "params": {}
}
```

**Success Response (200)**:
```json
{
  "status": "success",
  "data": {
    "accounts": ["DU1234567", "DU7654321"]
  }
}
```

**Error Response (403 - Not Allowed)**:
```json
{
  "status": "error",
  "error": "Endpoint not allowed",
  "allowed_endpoints": [
    "iserver/account",
    "iserver/secdef/search",
    ...
  ]
}
```

**Error Response (400 - Bad Request)**:
```json
{
  "status": "error",
  "error": "Invalid request format"
}
```

#### GET /health

Container orchestration health check.

**Request**:
```bash
GET /health
```

**Response (200)**:
```json
{
  "status": "healthy",
  "oauth_connected": true
}
```

#### GET /api/endpoints

Returns list of allowed endpoints.

**Request**:
```bash
GET /api/endpoints
```

**Response (200)**:
```json
{
  "endpoints": [
    "iserver/account",
    "iserver/secdef/search",
    "iserver/secdef/info",
    "iserver/contract",
    "iserver/secdef/bond-filters",
    "trsrv/secdef",
    "trsrv/futures",
    "trsrv/stocks",
    "iserver/marketdata/snapshot",
    "iserver/marketdata/history",
    "iserver/account/{accountId}/alerts"
  ]
}
```

---

## 5. Technical Implementation

### 5.1 FastMCP HTTP Transport

#### Quick Test Approach

Modify `endpoint_server.py` to enable HTTP transport:

```python
# Current (stdio)
if __name__ == "__main__":
    server.run()

# HTTP transport
if __name__ == "__main__":
    server.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
        path="/mcp"
    )
```

#### Required Dependencies

```txt
mcp
ibind
python-dotenv
uvicorn
starlette
httpx
flask  # For REST API wrapper
gunicorn  # Production WSGI server
```

### 5.2 Docker Configuration

#### Dockerfile

```dockerfile
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

COPY src/ /build/src/

FROM python:3.11-slim-bookworm AS production

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --from=builder /build/src/ /app/

RUN groupadd --system appgroup && \
    useradd --system --uid 1000 --shell /usr/sbin/nologin --home-dir /app appuser && \
    mkdir -p /app/logs && \
    chown -R appuser:appgroup /app

USER appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "src.endpoint_server:app"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    container_name: mcp-server
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
    env_file:
      - .env
    volumes:
      - ${SECRETS_DIR:-./secrets}:/run/secrets:ro
      - ./logs:/app/logs
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 5.3 File Structure

```
llm_public/
├── src/
│   ├── endpoint_server.py      # [MODIFIED] Add HTTP endpoints
│   ├── ibkr_oauth.py           # [UNCHANGED] Secure OAuth implementation
│   └── endpoints.md            # [UNCHANGED] API documentation
├── Dockerfile                   # [NEW] Container definition
├── docker-compose.yml           # [NEW] Deployment configuration
├── .env.example                # [NEW] Environment template
├── .env                        # [NOT COMMITTED] Local configuration
├── .gitignore                  # [MODIFIED] Add secrets exclusion
├── requirements.txt            # [MODIFIED] Add web dependencies
├── nginx/
│   └── default.conf            # [OPTIONAL] Reverse proxy
├── agents/
│   └── ARCHITECTURE.md         # [THIS FILE]
└── README.md                   # [MODIFIED] Update for HTTP
```

---

## 6. Security Measures

### 6.1 Input Validation

```python
def validate_endpoint(func):
    @wraps(func)
    def wrapper(endpoint_path, *args, **kwargs):
        # Normalize path
        normalized = endpoint_path.rstrip('/')
        
        # Check whitelist
        if normalized not in ALLOWED_ENDPOINTS:
            return jsonify({
                "error": "Endpoint not allowed",
                "allowed_endpoints": list(ALLOWED_ENDPOINTS)
            }), 403
        
        # Validate parameters
        params = request.get_json() or {}
        return func(normalized, params)
    return wrapper

def validate_params(params):
    """Sanitize and validate request parameters."""
    if not isinstance(params, dict):
        return False, "params must be an object"
    
    # Check for malicious patterns
    forbidden = [';', '&&', '||', '$', '`']
    for key, value in params.items():
        if any(char in str(value) for char in forbidden):
            return False, f"Invalid character in parameter '{key}'"
    
    return True, None
```

### 6.2 Error Sanitization

```python
@app.errorhandler(Exception)
def handle_error(error):
    """Prevent information leakage in error messages."""
    return jsonify({
        "status": "error",
        "error": "Internal server error"
    }), 500
```

### 6.3 Request Size Limits

```python
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB limit
```

---

## 7. Testing Strategy

### 7.1 Quick HTTP Transport Test

```bash
# Install dependencies
pip install uvicorn starlette httpx

# Modify endpoint_server.py
# Change: server.run() → server.run(transport="streamable-http", host="0.0.0.0", port=8000)

# Start server
python src/endpoint_server.py

# Test endpoints
curl http://localhost:8000/mcp  # MCP transport endpoint
```

### 7.2 Integration Tests

```python
def test_allowed_endpoints():
    """Verify whitelist enforcement."""
    for endpoint in ALLOWED_ENDPOINTS:
        response = client.post('/api/call_endpoint', json={
            'endpoint': endpoint,
            'params': {}
        })
        assert response.status_code != 403

def test_blocked_endpoints():
    """Verify non-whitelisted endpoints are blocked."""
    response = client.post('/api/call_endpoint', json={
        'endpoint': 'iserver/place/order',
        'params': {}
    })
    assert response.status_code == 403
```

### 7.3 Deployment Tests

```bash
# Build and run
docker-compose build
docker-compose up -d

# Test endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/call_endpoint \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "iserver/account", "params": {}}'
```

---

## 8. Comparison: Python vs TypeScript

### 8.1 Security Analysis

| Aspect | Python (ibkr_oauth.py) | TypeScript (ibkr-client) |
|--------|-------------------------|--------------------------|
| **Code Ownership** | Full control (415 lines) | Third-party dependency |
| **Secrets Management** | Isolated files (better) | Single oauth1.json |
| **Dependency Risk** | Minimal | ibkr-client + node-fetch |
| **OAuth Auditability** | Complete visibility | Must trust library |
| **Vulnerability Fixes** | Immediate | Wait for upstream |
| **Supply Chain Attacks** | Lower risk | Higher risk |

### 8.2 Docker Footprint

| Metric | Python | Node.js/TypeScript |
|--------|--------|-------------------|
| **Base Image** | ~150MB (slim) | ~900MB+ (full) |
| **Startup Time** | 1-2 seconds | 3-5 seconds |
| **Dependencies** | 10-20 | 50-100+ |
| **Memory Usage** | 50-100MB | 200-500MB |

### 8.3 Decision Rationale

Python was chosen because:
1. **Superior secrets isolation** - separate files vs single json
2. **Complete code control** - audit every line
3. **Smaller attack surface** - fewer dependencies
4. **Faster incident response** - fix vulnerabilities immediately
5. **Proven implementation** - 415 lines of tested OAuth code

---

## 9. Implementation Timeline

| Phase | Task | Estimated Time |
|-------|------|----------------|
| **1** | Create `Dockerfile` | 30 min |
| **2** | Create `docker-compose.yml` | 30 min |
| **3** | Modify `endpoint_server.py` (add HTTP) | 2-3 hours |
| **4** | Update `requirements.txt` | 10 min |
| **5** | Create `.env.example` | 10 min |
| **6** | Update `.gitignore` | 5 min |
| **7** | Test HTTP transport (quick) | 1 hour |
| **8** | Integration testing | 1-2 hours |
| **9** | Documentation | 30 min |

**Total Estimated Time**: ~6-8 hours

---

## 10. Rollback Plan

If issues arise during deployment:

```bash
# Stop container
docker-compose down

# Rollback to previous version
docker-compose -f docker-compose.yml.backup up -d

# Or restore stdio version
docker-compose down
git checkout endpoint_server.py
docker-compose build
docker-compose up -d
```

---

## 11. Future Enhancements

Post-migration enhancements (optional):

1. **Nginx Reverse Proxy**
   - TLS termination
   - Rate limiting
   - Load balancing

2. **Authentication Layer**
   - API key validation
   - OAuth 2.0 for agents

3. **Observability**
   - Prometheus metrics (`/metrics`)
   - Distributed tracing
   - Structured logging

4. **Scalability**
   - Kubernetes deployment
   - Horizontal scaling
   - Session management

---

## 12. References

### Internal Documentation
- `src/endpoint_server.py` - Existing MCP server implementation
- `src/ibkr_oauth.py` - OAuth 1.0a implementation (415 lines)
- `src/endpoints.md` - IBKR API documentation

### External Resources
- FastMCP Documentation: https://gofastmcp.com/
- MCP Protocol Specification: https://modelcontextprotocol.io/
- IBKR API Documentation: https://www.interactivebrokers.com/campus/ibkr-api-page/webapi-ref/

---

## 13. Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-05 | Use Python over TypeScript | Better secrets isolation, full code control, smaller Docker footprint |
| 2026-02-05 | Keep `ibkr_oauth.py` over `ibind.IbkrClient` | More secure, better secrets management, complete auditability |
| 2026-02-05 | Streamable HTTP transport | MCP-native, session management, tested implementation |
| 2026-02-05 | REST API wrapper for agents | Simplest integration, universal HTTP client support |
| 2026-02-05 | Endpoint whitelist only | Security first, no trading endpoints exposed |

---

**Document Status**: Ready for Implementation  
**Next Action**: Begin Phase 1 - Dockerfile creation
