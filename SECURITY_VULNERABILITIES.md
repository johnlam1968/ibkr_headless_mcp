# IBKR MCP Server Security Vulnerabilities & Mitigation Strategies

**Date**: February 11, 2026  
**Project**: IBKR Headless MCP Server  
**Focus**: Security analysis of `src/endpoint_server.py`

---

## Executive Summary

This document captures security analysis and discussions about vulnerabilities in IBKR MCP server implementation using FastMCP and Docker. The analysis covers application-level vulnerabilities, container security, operating system protections, and recommendations for home/development environments.

**Current Setup**:
- **Deployment**: Docker container
- **Firewall**: UFW (Uncomplicated Firewall)
- **Network**: Home router with NAT
- **Environment**: Development/testing on personal machine

**Security Posture**: **Secure for home/development use** with recommended improvements for production.

---

## Table of Contents

1. [Critical Security Issues](#critical-security-issues)
2. [Application-Level Vulnerabilities](#application-level-vulnerabilities)
3. [Docker vs Bare Python Comparison](#docker-vs-bare-python-comparison)
4. [Additional Protection Layers](#additional-protection-layers)
5. [Current Setup Assessment](#current-setup-assessment)
6. [Recommended Priority Fixes](#recommended-priority-fixes)

---

## Critical Security Issues

### 1. Overly Permissive CORS & Host Configuration

**Location**: `src/endpoint_server.py` (lines ~57-67)

```python
allowed_hosts=[
    "localhost:*",
    "127.0.0.1:*",
    "mcp-server:*",
    "172.19.0.0/16:*",
    "172.22.0.0/16:*",
    "*"  # ⚠️ ALLOWS ALL HOSTS - MAJOR VULNERABILITY
],
allowed_origins=["*"]  # ⚠️ ALLOWS ALL ORIGINS - MAJOR VULNERABILITY
```

**Risk**: 
- Cross-Site Request Forgery (CSRF)
- Any malicious website can make requests to your IBKR API
- Browser-based attacks (if user visits malicious site while authenticated)

**Impact**: High - Could lead to unauthorized trading or account access

**Mitigation**:
```python
# Recommended configuration
allowed_hosts=[
    "localhost:*",
    "127.0.0.1:*",
    "mcp-server:*",
    "172.19.0.0/16:*",
    "172.22.0.0/16:*",
    # Remove "*" wildcard
],
allowed_origins=[]  # Disable CORS for MCP-only use
```

---

### 2. No Authentication/Authorization

**Risk**: 
- Anyone who can reach port 8000 can call IBKR endpoints
- Local network users (family, guests) can access API
- If router is misconfigured, exposure increases

**Impact**: High - Unauthorized access to trading account, financial loss

**Mitigation Options**:

#### Option A: Simple API Key
```python
import secrets

API_KEY = os.getenv("MCP_API_KEY", secrets.token_urlsafe(32))

# Add middleware to check API key
if request.headers.get("X-API-Key") != API_KEY:
    raise HTTPException(401, "Invalid API key")
```

#### Option B: OAuth2 for MCP
```python
# More complex but production-grade
from authlib.integrations.flask_client import OAuth
```

---

### 3. No Rate Limiting

**Risk**: 
- Denial of Service (DoS) attacks
- IBKR API rate limit violations
- Account suspension due to excessive requests

**Impact**: Medium - Service interruption, account penalties

**Mitigation**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@limiter.limit("10/minute")
async def call_endpoint(path: str, params: Dict):
    # endpoint implementation
```

---

## Application-Level Vulnerabilities

### 1. Path Traversal in Secret File Loading

**Location**: `src/endpoint_server.py` (lines ~14-43)

```python
file_path = os.environ[file_var]
if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        content = f.read().strip()
```

**Risk**: If `*_FILE` environment variables can be manipulated, could read arbitrary files

**Mitigation in Docker**: Filesystem isolation provides some protection

**Additional Mitigation**:
```python
# Validate file paths
SECRETS_BASE = "/run/media/john/377383bc-7d5c-4ae9-853c-3477d0806098/.secrets/"

if not file_path.startswith(SECRETS_BASE):
    raise ValueError("Invalid secret file path")
```

---

### 2. No Input Validation Beyond Whitelist

**Location**: `src/endpoint_server.py` (line ~168)

```python
if path not in ALLOWED_ENDPOINTS:
    return json.dumps({"error": "Endpoint '{path}' is not allowed..."})
```

**Risk**: Whitelist is good, but no validation of `params` values

**Mitigation**:
```python
from pydantic import BaseModel, constr, conint

class EndpointParams(BaseModel):
    path: constr(regex=r'^[a-zA-Z0-9_/]+$')
    symbol: constr(max_length=10, regex=r'^[A-Z0-9.-]+$')
    sectype: Literal["STK", "IND", "BOND"]
    conid: conint(gt=0)
```

---

### 3. Error Information Disclosure

**Location**: `src/endpoint_server.py` (line ~129)

```python
print(f"⚠️ IBKR Connection Error: {type(e).__name__}: {str(e)}")
```

**Risk**: Stack traces and error messages exposed in logs could reveal internal structure

**Impact**: Low - Information leakage

**Mitigation**:
```python
import structlog
logger = structlog.get_logger()

logger.error("IBKR connection error", 
             error_type=type(e).__name__,
             exc_info=e)  # Only log exceptions, not to stdout
```

---

## Docker vs Bare Python Comparison

### Security Comparison

| Security Control | Docker | Bare Python |
|-----------------|--------|-------------|
| Filesystem isolation | ✅ Containerized | ❌ Host access |
| Network isolation | ✅ Namespaced | ❌ Shared |
| Resource limits | ✅ cgroups | ⚠️ Possible but complex |
| Read-only root | ✅ Possible | ❌ Not possible |
| Secret injection | ✅ Environment/volumes | ⚠️ Environment/files |
| Quick rollback | ✅ Image versioning | ❌ Complex |
| Immutable deployment | ✅ Yes | ❌ No |

### Increased Risks with Bare Python

#### 1. Dependency Vulnerabilities
- **Docker**: Fixed, known versions in container
- **Bare Python**: Host system dependencies, potential version conflicts
- **Risk**: Higher with bare Python

#### 2. File System Access
- **Docker**: Limited to container filesystem + mounted volumes
- **Bare Python**: Full access to host filesystem
- **Risk**: If compromised, attacker gets full host access

#### 3. Network Isolation
- **Docker**: Containerized network namespace
- **Bare Python**: Shares host network stack
- **Risk**: Network-based attacks easier

#### 4. Python Environment Contamination
- **Docker**: Clean Python environment per container
- **Bare Python**: Shared with other Python applications
- **Risk**: Malicious packages in `site-packages`

### Real-World Attack Scenarios

#### Scenario 1: Dependency Vulnerability
- **Docker**: Vulnerability limited to container
- **Bare Python**: Vulnerability affects all Python apps on host

#### Scenario 2: Process Memory Dump
- **Docker**: Requires container escape first
- **Bare Python**: Any process with sufficient privileges
- **Risk**: IBKR OAuth tokens more exposed

### Recommendation

**For production use with IBKR**:
1. ✅ **Use Docker** - Better isolation, consistency, security
2. ❌ **Avoid bare Python** - Higher risk, harder to secure

---

## Additional Protection Layers

### 1. Operating System Level

#### A. AppArmor (Mandatory Access Control)

**Purpose**: Profile-based mandatory access control for Linux

**Setup Steps**:

1. Install AppArmor:
```bash
# Arch Linux
sudo pacman -S apparmor apparmor-utils
sudo systemctl enable --now apparmor
```

2. Create Profile:
```bash
sudo nano /etc/apparmor.d/usr.bin.python3.ibkr-mcp
```

3. Profile Content:
```apparmor
#include <tunables/global>

/usr/bin/python3.ibkr-mcp {
  #include <abstractions/base>
  #include <abstractions/python>  
  network inet tcp,
  network inet6 tcp,
  deny network raw,
  deny network packet,
  /usr/lib/python3.*/** r,
  /home/john/CodingProjects/llm_public/.venv/** r,
  /home/john/CodingProjects/llm_public/src/** r,
  /run/media/john/377383bc-7d5c-4ae9-853c-3477d0806098/.secrets/oauth_files/** r,
  deny /run/media/john/377383bc-7d5c-4ae9-853c-3477d0806098/.secrets/oauth_files/** w,
  /tmp/** rw,
  /var/tmp/** rw,
  /var/log/ibkr-mcp.log w,
  deny /** w,
  deny capability sys_module,
  deny capability sys_ptrace,
  deny capability sys_admin,
  deny capability sys_boot,
  deny capability sys_chroot,
  deny capability sys_nice,
  deny capability sys_resource,
  deny capability sys_time,
  capability setuid,
  capability setgid,
  capability net_bind_service,
}
```

4. Load and Enable:
```bash
sudo apparmor_parser -r /etc/apparmor.d/usr.bin.python3.ibkr-mcp
sudo aa-enforce /usr/bin/python3.ibkr-mcp
```

#### B. SELinux (For RHEL/Fedora/CentOS)

Alternative to AppArmor with label-based mandatory access control.

#### C. Namespace Isolation

```bash
# Create isolated namespaces without Docker
unshare --pid --fork --mount --net --ipc --uts --user
```

#### D. Cgroups (Control Groups)

```bash
# Limit resources
cgcreate -g cpu,memory:/ibkr-mcp
echo "100000" > /sys/fs/cgroup/cpu/ibkr-mcp/cpu.cfs_quota_us
```

---

### 2. Network Level

#### A. Firewall Rules (UFW)

```bash
# Recommended UFW rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.1.0/24 to any port 8000  # Local network
sudo ufw allow from 172.22.0.0/16 to any port 8000  # Docker network
sudo ufw allow from 172.18.0.0/16 to any port 8000  # Docker network
sudo ufw allow from 172.19.0.0/16 to any port 8000  # OpenClaw network
sudo ufw enable
```

#### B. Reverse Proxy with Security Features

```nginx
# Nginx configuration
location /mcp {
    allow 192.168.1.0/24;
    allow 172.22.0.0/16;
    deny all;
    
    limit_req zone=mcp burst=10 nodelay;
    
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
}
```

#### C. VPN/Zero Trust Network

- **WireGuard**: Encrypted tunnel for MCP traffic
- **Tailscale**: Mesh VPN with access controls
- **Cloudflare Tunnel**: Secure external access

---

### 3. Process/Service Level

#### A. Systemd Sandboxing

```ini
# /etc/systemd/system/ibkr-mcp.service
[Unit]
Description=IBKR MCP Server with AppArmor
After=network.target apparmor.service

[Service]
Type=simple
User=john
Group=john
WorkingDirectory=/home/john/CodingProjects/llm_public
ExecStart=/usr/bin/aa-exec -p python3.ibkr-mcp -- /home/john/CodingProjects/llm_public/.venv/bin/python -m src.endpoint_server
Restart=on-failure
RestartSec=5

# Security options
AppArmorProfile=python3.ibkr-mcp
ProtectSystem=strict
ReadWritePaths=/home/john/CodingProjects/llm_public
NoNewPrivileges=yes
PrivateTmp=yes
PrivateDevices=yes
ProtectKernelTunables=yes
ProtectKernelModules=yes
ProtectControlGroups=yes
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
RestrictNamespaces=yes
RestrictRealtime=yes
MemoryDenyWriteExecute=yes
LockPersonality=yes

[Install]
WantedBy=multi-user.target
```

#### B. Resource Limits in Docker

```yaml
# docker-compose.yml
services:
  mcp-server:
    # ... existing config
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

---

### 4. Monitoring & Detection

#### A. Audit Logging

```python
import structlog
logger = structlog.get_logger()

async def call_endpoint(path: str, params: Dict):
    logger.info("endpoint_called", 
                path=path, 
                params=params, 
                client_ip=request.client.host,
                timestamp=datetime.utcnow().isoformat())
```

#### B. Intrusion Detection

- **Fail2ban**: Block brute force attempts
- **Wazuh**: Security monitoring
- **Auditd**: System call auditing

#### C. Metrics & Alerting

- **Prometheus**: Rate limit violations, error rates
- **Grafana**: Dashboard for monitoring
- **AlertManager**: Notifications for suspicious activity

---

## Current Setup Assessment

### User's Current Protection Layers

#### 1. Router Level (Outer Perimeter) ✅
- **Firewall**: Blocks unsolicited inbound traffic
- **NAT**: Network Address Translation hides internal IPs
- **Port Forwarding**: Only allowing port 8000 to machine
- **Protection Level**: Good for home use

#### 2. UFW Level (Host Firewall) ✅
- **Status**: Installed and enabled
- **Rules**: Configured for specific networks
- **Protection Level**: Good for home use

#### 3. Docker Level (Process Isolation) ✅
- **Filesystem isolation**: Limited to container + mounted volumes
- **Network isolation**: Separate network namespace
- **Secret management**: Volume mounts for OAuth files
- **Protection Level**: Excellent

### What UFW + Router + Docker Protects Against

✅ External network attacks  
✅ Port scanning from internet  
✅ Remote exploitation attempts  
✅ Network-based container escapes (to some degree)  

### What UFW + Router + Docker Does NOT Protect Against

❌ CSRF/XSS attacks (via browser)  
❌ Local network abuse (compromised Wi-Fi, guest devices)  
❌ Application-level vulnerabilities  
❌ Insider threats  
❌ User error (malicious local script)  

### Real-World Scenarios

#### Scenario 1: Family Member on Network
- **Without auth**: Can access IBKR API
- **With API key**: Protected (if they don't have key)
- **Recommendation**: Add simple authentication

#### Scenario 2: Guest Connects to Wi-Fi
- **UFW Protection**: ❌ Doesn't help (same network)
- **Docker Protection**: ❌ Doesn't help (container still accessible)
- **Solution**: Authentication + CORS restriction

#### Scenario 3: Router Misconfiguration
- **If port 8000 exposed to internet**: Risk increases significantly
- **Recommendation**: Verify router doesn't forward port 8000

---

## Recommended Priority Fixes

### High Priority (Easy Fixes)

#### 1. Restrict CORS
**File**: `src/endpoint_server.py`

**Current** (Line ~67):
```python
allowed_origins=["*"]  # ⚠️ Allows all origins
```

**Fix**:
```python
allowed_origins=[]  # Disable CORS for MCP-only use
```

#### 2. Remove Wildcard Host
**File**: `src/endpoint_server.py`

**Current** (Line ~63):
```python
"*"  # ⚠️ Allows all hosts
```

**Fix**: Remove this line entirely

#### 3. Add Docker Resource Limits
**File**: `docker-compose.yml`

**Add**:
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 512M
    reservations:
      cpus: '0.5'
      memory: 256M
```

### Medium Priority

#### 4. Simple API Key Authentication
**File**: `src/endpoint_server.py`

**Add**:
```python
import secrets

# Add after imports
API_KEY = os.getenv("MCP_API_KEY", secrets.token_urlsafe(32))

# Add to FastMCP initialization
@server.middleware
async def auth_middleware(request):
    api_key = request.headers.get("X-API-Key")
    if api_key != API_KEY:
        raise HTTPException(401, "Unauthorized")
```

#### 5. UFW Specific Rules
**Command**:
```bash
# Only allow specific IP ranges
sudo ufw delete allow 8000  # If exists
sudo ufw allow from 192.168.1.100 to any port 8000  # Your machine only
sudo ufw allow from 172.22.0.0/16 to any port 8000  # Docker network
```

#### 6. Rate Limiting
**File**: `src/endpoint_server.py`

**Add**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
server.state.limiter = limiter

# Add decorator to endpoint
@limiter.limit("10/minute")
async def call_endpoint(path: str, params: Optional[Dict[str, Any]]) -> str:
```

### Long-Term Improvements

1. Implement OAuth2 for MCP
2. Add transaction confirmation for trades
3. Regular security audits (code + dependencies)
4. Add security headers (CSP, HSTS)
5. Implement audit logging
6. Use secrets manager (HashiCorp Vault)
7. Regular dependency updates

---

## Defense in Depth Strategy

### Layer 1: Network Perimeter
- Firewall rules ✅ (UFW + Router)
- VPN/Zero Trust ⚠️ (Optional)
- DDoS protection ⚠️ (Optional for home use)

### Layer 2: Host Security
- SELinux/AppArmor ⚠️ (Optional for home use)
- Regular patching ✅
- Minimal installation ✅ (Docker)

### Layer 3: Application Security
- Authentication/Authorization ❌ (Not implemented)
- Input validation ⚠️ (Partial - whitelist only)
- Rate limiting ❌ (Not implemented)

### Layer 4: Data Protection
- Secret management ✅ (Docker volumes)
- Encryption at rest/in transit ✅ (HTTPS)
- Audit logging ❌ (Not implemented)

### Layer 5: Monitoring & Response
- Intrusion detection ⚠️ (Optional for home use)
- Real-time alerts ❌ (Not implemented)
- Incident response plan ⚠️ (Recommended)

---

## Bottom Line

### Security Posture Summary

| Risk Level | Current | Recommended Action |
|-----------|---------|-------------------|
| **External Attack** | LOW | Router + UFW + Docker = Good ✅ |
| **Local Network Abuse** | MODERATE | Add API key authentication |
| **Application Vulnerabilities** | MODERATE | Fix CORS (`allowed_origins=[]`) |
| **Resource Exhaustion** | LOW | Add Docker limits |
| **Insider Threat** | MODERATE | Authentication + audit logging |

### Final Assessment

**Secure for**:
- ✅ Home development/testing
- ✅ Personal use on trusted network
- ✅ Protection against external attackers

**Improvements recommended for**:
- ⚠️ Multi-user environments (family, guests)
- ⚠️ Production deployment
- ⚠️ Port forwarding to internet

### Most Critical Fixes

1. **Remove `"*"` from `allowed_hosts`**
2. **Set `allowed_origins=[]`** (disable CORS)
3. **Add simple API key** if shared network

---

## Appendices

### A. Quick Fix Script

```bash
#!/bin/bash
# Quick security fixes for IBKR MCP server

# 1. Update UFW rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.1.0/24 to any port 8000
sudo ufw allow from 172.22.0.0/16 to any port 8000
sudo ufw enable

# 2. Add Docker resource limits
cat >> docker-compose.yml << 'EOF'

  deploy:
    resources:
      limits:
        cpus: '1.0'
        memory: 512M
      reservations:
        cpus: '0.5'
        memory: 256M
EOF

# 3. Restart container
docker-compose down
docker-compose up -d
```

### B. Docker Security Best Practices

1. Use read-only volumes where possible
2. Run as non-root user
3. Use official base images
4. Scan images for vulnerabilities
5. Keep images updated
6. Use .dockerignore to reduce image size

### C. Security Checklist

- [ ] CORS restricted or disabled
- [ ] Authentication implemented
- [ ] Rate limiting configured
- [ ] Input validation implemented
- [ ] Secret files protected (read-only)
- [ ] Error messages sanitized
- [ ] Audit logging enabled
- [ ] Resource limits configured
- [ ] Firewall rules configured
- [ ] Dependencies regularly updated

---

**Document Version**: 1.0  
**Last Updated**: February 11, 2026  
**Next Review**: March 11, 2026