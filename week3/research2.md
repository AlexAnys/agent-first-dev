# Stage 2 Research: Remote MCP Server with Authentication

## 1. Overview

This document contains research findings for Stage 2 of the Gmail MCP Server project:
- **Remote HTTP Transport**: Making the MCP server publicly accessible
- **Authentication Integration**: Implementing OAuth 2.0 authorization per MCP specification
- **Deployment Options**: Cloudflare Workers and Vercel

---

## 2. MCP Authorization Specification (RFC Compliance)

Reference: [MCP Authorization Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)

### 2.1 Protocol Requirements

| Transport Type | Authorization Approach |
|---------------|------------------------|
| **HTTP-based transport** | SHOULD conform to MCP Authorization specification |
| **STDIO transport** | SHOULD NOT follow this spec; retrieve credentials from environment |
| **Alternative transports** | MUST follow security best practices for their protocol |

### 2.2 Standards Compliance

The MCP Authorization specification is built on these OAuth 2.0 standards:

| Standard | Description |
|----------|-------------|
| OAuth 2.1 IETF DRAFT ([draft-ietf-oauth-v2-1-13](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13)) | Core authorization framework |
| [RFC 8414](https://datatracker.ietf.org/doc/html/rfc8414) | OAuth 2.0 Authorization Server Metadata |
| [RFC 7591](https://datatracker.ietf.org/doc/html/rfc7591) | OAuth 2.0 Dynamic Client Registration Protocol |
| [RFC 9728](https://datatracker.ietf.org/doc/html/rfc9728) | OAuth 2.0 Protected Resource Metadata |
| [RFC 8707](https://www.rfc-editor.org/rfc/rfc8707.html) | Resource Indicators for OAuth 2.0 |

### 2.3 Authorization Flow Overview

**Roles:**
- **MCP Server**: Acts as OAuth 2.1 resource server
- **MCP Client**: Acts as OAuth 2.1 client
- **Authorization Server**: Issues tokens (can be third-party like GitHub, Google, Auth0)

**Key Requirements:**

1. Authorization servers **MUST** implement OAuth 2.1 with appropriate security measures
2. Authorization servers and MCP clients **SHOULD** support Dynamic Client Registration ([RFC 7591](https://datatracker.ietf.org/doc/html/rfc7591))
3. MCP servers **MUST** implement OAuth 2.0 Protected Resource Metadata ([RFC 9728](https://datatracker.ietf.org/doc/html/rfc9728))
4. Authorization servers **MUST** provide OAuth 2.0 Authorization Server Metadata ([RFC 8414](https://datatracker.ietf.org/doc/html/rfc8414))

### 2.4 Authorization Server Discovery

MCP uses Protected Resource Metadata for authorization server discovery:

1. Client fetches `/.well-known/oauth-protected-resource` from MCP server
2. Response contains `authorization_servers` array with issuer URLs
3. Client fetches authorization server metadata from each issuer

**Example Protected Resource Metadata Response:**
```json
{
  "resource": "https://mcp.example.com",
  "authorization_servers": ["https://auth.example.com"],
  "bearer_methods_supported": ["header"]
}
```

**Error Response (401 Unauthorized):**
```
HTTP 401 Unauthorized
WWW-Authenticate: Bearer realm="mcp", resource="https://mcp.example.com"
```

### 2.5 Access Token Usage

**Token Requirements:**
- MCP clients **MUST** use the `Authorization` request header:
  ```
  Authorization: Bearer <access-token>
  ```
- Access tokens **MUST NOT** be included in the URI query string

**Example Request:**
```http
GET /mcp HTTP/1.1
Host: mcp.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### 2.6 Resource Parameter Implementation

Per [RFC 8707](https://www.rfc-editor.org/rfc/rfc8707.html), the `resource` parameter:

1. **MUST** be included in both authorization and token requests
2. **MUST** identify the MCP server that the client intends to use the token with
3. **MUST** use the canonical URI of the MCP server

**Valid Canonical URI Examples:**
- `https://mcp.example.com/mcp`
- `https://mcp.example.com`
- `https://mcp.example.com:8443`

**Invalid Examples:**
- `mcp.example.com` (missing scheme)
- `https://mcp.example.com#fragment` (contains fragment)

### 2.7 Security Considerations

| Security Aspect | Requirement |
|-----------------|-------------|
| **Token Audience Binding** | MCP servers MUST validate tokens were specifically issued for their use |
| **Communication Security** | All endpoints MUST be served over HTTPS |
| **Redirect URIs** | MUST be localhost or use HTTPS |
| **Authorization Code Protection** | Use PKCE as per OAuth 2.1 |
| **Token Theft Prevention** | Use refresh token rotation |

**Critical Security Issues to Avoid:**
1. **Audience Validation Failures**: Always verify token audience claims
2. **Token Passthrough**: Never forward unvalidated tokens to downstream services (Confused Deputy Problem)

---

## 3. Remote MCP Server on Cloudflare

Reference: [Cloudflare Remote MCP Server Guide](https://developers.cloudflare.com/agents/guides/remote-mcp-server/)

### 3.1 Deployment Options

Cloudflare offers two deployment approaches:

| Option | Description | Use Case |
|--------|-------------|----------|
| **Without Authentication** | Public server, anyone can connect | Prototyping, public tools |
| **With Authentication** | OAuth-protected, user sign-in required | Production, sensitive data |

### 3.2 Quick Deploy (Without Auth)

**Using CLI (npm):**
```bash
npm create cloudflare@latest -- my-mcp-server --template=cloudflare/ai/demos/remote-mcp-authless
cd my-mcp-server
npm start  # Runs on http://localhost:8788/sse
```

**Deploy to Production:**
```bash
npx wrangler@latest deploy
```

The server will be live at: `https://your-worker-name.your-account.workers.dev/sse`

### 3.3 Connecting Claude Desktop via mcp-remote Proxy

Since Claude Desktop doesn't natively support remote MCP transport, use the `mcp-remote` proxy:

**Claude Desktop Configuration:**
```json
{
  "mcpServers": {
    "gmail": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://your-worker-name.your-account.workers.dev/sse"
      ]
    }
  }
}
```

### 3.4 Adding Authentication (GitHub OAuth Example)

**Step 1: Create MCP Server with OAuth Template:**
```bash
npm create cloudflare@latest -- my-mcp-server-github-auth \
  --template=cloudflare/ai/demos/remote-mcp-github-oauth
cd my-mcp-server-github-auth
```

**Step 2: Server Structure (src/index.ts):**
```typescript
import GitHubHandler from "./github-handler";

export default new OAuthProvider({
  apiRoute: "/sse",
  apiHandler: MyMCP.Router,
  defaultHandler: GitHubHandler,
  authorizeEndpoint: "/authorize",
  tokenEndpoint: "/token",
  clientRegistrationEndpoint: "/register",
});
```

**Step 3: Create GitHub OAuth Apps:**

| Environment | Settings |
|-------------|----------|
| **Local Development** | Homepage: `http://localhost:8788`, Callback: `http://localhost:8788/callback` |
| **Production** | Homepage: `https://worker-name.account-name.workers.dev`, Callback: `https://worker-name.account-name.workers.dev/callback` |

**Step 4: Configure Secrets:**

*Local (.dev.vars file):*
```bash
touch .dev.vars
echo 'GITHUB_CLIENT_ID="your-client-id"' >> .dev.vars
echo 'GITHUB_CLIENT_SECRET="your-client-secret"' >> .dev.vars
```

*Production:*
```bash
wrangler secret put GITHUB_CLIENT_ID
wrangler secret put GITHUB_CLIENT_SECRET
npx wrangler secret put COOKIE_ENCRYPTION_KEY  # openssl rand -hex 32
```

**Step 5: Set up KV Namespace:**
```bash
npx wrangler kv namespace create "OAUTH_KV"
# Update wrangler.jsonc with the resulting KV ID
```

```json
{
  "kvNamespaces": [
    {
      "binding": "OAUTH_KV",
      "id": "<YOUR_KV_NAMESPACE_ID>"
    }
  ]
}
```

**Step 6: Deploy:**
```bash
npm run deploy
```

### 3.5 Supported OAuth Providers

Cloudflare supports multiple OAuth providers:

- GitHub
- Google
- Slack
- Auth0
- Stytch
- WorkOS
- Any OAuth 2.0 compliant provider

---

## 4. Remote MCP Server on Vercel

Reference: [Vercel MCP Deployment Guide](https://vercel.com/docs/mcp/deploy-mcp-servers-to-vercel)

### 4.1 Vercel Advantages for MCP

| Feature | Benefit |
|---------|---------|
| **Fluid Compute** | Optimized for irregular usage patterns |
| **Optimized Concurrency** | Handle message bursts efficiently |
| **Dynamic Scaling** | Scale with demand |
| **Instance Sharing** | Cost-effective resource usage |
| **Instant Rollback** | Quick revert if issues arise |
| **Preview Deployments** | Test changes safely before production |
| **Vercel Firewall** | Multi-layered security |
| **Rolling Releases** | Gradual rollout to users |

### 4.2 Deploy Templates

Vercel provides ready-to-use templates:

| Template | Description |
|----------|-------------|
| **MCP with Next.js** | Run MCP server on Vercel with Next.js |
| **ChatGPT app with Next.js** | ChatGPT app with MCP integration |
| **x402 AI Starter** | Fullstack template with MCP and AI SDK |
| **Vercel Functions MCP** | Lightweight MCP with Vercel Functions |

### 4.3 Basic MCP Server Setup

**API Route Example (`app/api/mcp/route.ts`):**
```typescript
import { createMCP } from '@vercel/mcp';

const mcp = createMCP({
  name: 'My MCP Server',
  tools: {
    rollDice: {
      description: 'Roll a dice',
      parameters: { sides: { type: 'number', default: 6 } },
      handler: async ({ sides }) => {
        return Math.floor(Math.random() * sides) + 1;
      }
    }
  }
});

export const { GET, POST } = mcp;
```

### 4.4 Enabling OAuth Authorization

**Step 1: Wrap MCP Handler with Auth:**
```typescript
import { createMCP, withAuth } from '@vercel/mcp';

const mcp = createMCP({ /* ... */ });

const authenticatedMCP = withAuth(mcp, {
  verifyToken: async (token) => {
    // Implement token verification logic
    const decoded = await verifyJWT(token);
    return decoded.valid;
  },
  requiredScopes: ['read:emails'],
  metadataPath: '/.well-known/oauth-protected-resource'
});

export const { GET, POST } = authenticatedMCP;
```

**Step 2: Expose OAuth Metadata Endpoint:**

Create `app/.well-known/oauth-protected-resource/route.ts`:
```typescript
export async function GET() {
  return Response.json({
    resource: 'https://your-app.vercel.app',
    authorization_servers: ['https://your-auth-server.com'],
    bearer_methods_supported: ['header'],
    scopes_supported: ['read:emails', 'write:emails']
  });
}
```

This endpoint allows MCP clients to:
- Discover how to authorize with your server
- Know which authorization servers can issue valid tokens
- Understand what scopes are supported

### 4.5 Cursor IDE Configuration

**Streamable HTTP Transport Format (`~/.cursor/mcp.json`):**
```json
{
  "mcpServers": {
    "gmail": {
      "url": "https://your-app.vercel.app/api/mcp",
      "transport": "streamable-http"
    }
  }
}
```

---

## 5. MCP Inspector for Debugging

Reference: [MCP Inspector Documentation](https://modelcontextprotocol.io/docs/tools/inspector)

### 5.1 Installation and Basic Usage

```bash
# Run inspector
npx @modelcontextprotocol/inspector@latest

# The inspector runs at http://localhost:5173
```

### 5.2 Inspecting Different Server Types

**NPM Package:**
```bash
npx -y @modelcontextprotocol/inspector npx <package-name> <args>
```

**PyPI Package:**
```bash
npx @modelcontextprotocol/inspector uvx <package-name> <args>
```

**Local Python Server:**
```bash
npx @modelcontextprotocol/inspector \
  uv \
  --directory path/to/server \
  run \
  package-name \
  args...
```

**Example for Gmail MCP Server:**
```bash
npx @modelcontextprotocol/inspector \
  uv \
  --directory /path/to/week3 \
  run \
  python -m server.main
```

### 5.3 Feature Overview

| Feature | Description |
|---------|-------------|
| **Server Connection Pane** | Select transport (STDIO, SSE, Streamable HTTP), configure environment |
| **Resources Tab** | List resources, view metadata, inspect content |
| **Prompts Tab** | Display prompt templates, test with arguments |
| **Tools Tab** | List tools, view schemas, test with custom inputs |
| **Notifications Pane** | View server logs and notifications |

### 5.4 Testing OAuth Flow

For servers with authentication:

1. Run inspector: `npx @modelcontextprotocol/inspector@latest`
2. Open `http://localhost:5173`
3. Set Transport Type to **SSE**
4. Enter MCP server URL (e.g., `http://localhost:8788/sse`)
5. Click **Open OAuth Settings**
6. Click **Quick OAuth Flow**
7. Complete authorization in browser
8. Click **Connect** to test tools

### 5.5 Development Workflow Best Practices

**1. Start Development:**
- Launch Inspector with your server
- Verify basic connectivity
- Check capability negotiation

**2. Iterative Testing:**
- Make server changes
- Rebuild the server
- Reconnect the Inspector
- Test affected features
- Monitor messages

**3. Test Edge Cases:**
- Invalid inputs
- Missing prompt arguments
- Concurrent operations
- Verify error handling and error responses

---

## 6. Implementation Plan for Stage 2

### 6.1 Architecture Decision

| Platform | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| **Vercel** | Free tier, Next.js native, simple deployment | Need to convert Python to TypeScript | ✓ Recommended for this project |
| **Cloudflare** | Workers at edge, SSE native, good OAuth templates | Also requires TypeScript | Alternative option |

**Decision**: For the Gmail MCP Server (Python/FastMCP), we have two options:

**Option A: Keep Python + Deploy Elsewhere**
- Use Railway, Render, or Fly.io for Python hosting
- Implement OAuth manually using FastMCP's auth providers

**Option B: Port to TypeScript + Vercel**
- Rewrite using `@vercel/mcp` package
- Leverage Vercel's free tier and built-in OAuth support

### 6.2 Stage 2 Tasks (Python Approach)

**Task 1: HTTP Transport Configuration**
```python
# main.py
if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "http":
        mcp.run(transport="http", host="0.0.0.0", port=8000)
    else:
        mcp.run()  # STDIO default
```

**Task 2: OAuth Metadata Endpoint**
```python
from fastmcp import FastMCP
from fastmcp.server.resources import Resource

mcp = FastMCP("Gmail MCP Server")

@mcp.resource(uri="/.well-known/oauth-protected-resource")
def oauth_metadata() -> dict:
    return {
        "resource": os.getenv("MCP_SERVER_URL", "http://localhost:8000"),
        "authorization_servers": [os.getenv("OAUTH_ISSUER_URL")],
        "bearer_methods_supported": ["header"],
        "scopes_supported": ["gmail.readonly"]
    }
```

**Task 3: Bearer Token Validation**
```python
from fastmcp.server.auth.providers.bearer import BearerAuthProvider

auth = BearerAuthProvider(
    token_verifier=verify_google_token,
    required_scopes=["gmail.readonly"]
)

mcp = FastMCP("Gmail MCP Server", auth=auth)

async def verify_google_token(token: str) -> dict:
    """Verify Google OAuth token and extract claims."""
    # Use google-auth library to verify token
    from google.oauth2 import id_token
    from google.auth.transport import requests
    
    try:
        claims = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            os.getenv("GOOGLE_CLIENT_ID")
        )
        return {"user_id": claims["sub"], "email": claims["email"]}
    except ValueError as e:
        raise AuthenticationError(f"Invalid token: {e}")
```

**Task 4: CORS Configuration (for browser clients)**
```python
from fastmcp import FastMCP
from fastmcp.server.http import HTTPServer

mcp = FastMCP("Gmail MCP Server")

# Enable CORS
mcp.settings.cors_origins = ["*"]  # Or specific origins
mcp.settings.cors_methods = ["GET", "POST", "OPTIONS"]
mcp.settings.cors_headers = ["Authorization", "Content-Type"]
```

### 6.3 Files to Create/Modify

```
week3/
├── server/
│   ├── __init__.py
│   ├── main.py              # Add HTTP transport option
│   ├── gmail_client.py      # Existing
│   ├── tools.py             # Existing
│   ├── auth.py              # NEW: OAuth token verification
│   └── middleware.py        # NEW: CORS, logging middleware
├── .env.example             # Add OAuth-related vars
└── README.md                # Update with remote deployment docs
```

### 6.4 Environment Variables for Stage 2

```bash
# .env additions for Stage 2
MCP_TRANSPORT=http           # "stdio" or "http"
MCP_SERVER_URL=https://your-domain.com
MCP_PORT=8000

# OAuth Configuration
OAUTH_ISSUER_URL=https://accounts.google.com
OAUTH_AUDIENCE=your-client-id
OAUTH_REQUIRED_SCOPES=gmail.readonly

# For remote deployment
DEPLOYMENT_ENV=production    # "development" or "production"
```

---

## 7. Testing Strategy for Remote MCP

### 7.1 Local Testing with Inspector

```bash
# Terminal 1: Start MCP server in HTTP mode
MCP_TRANSPORT=http uv run python -m server.main

# Terminal 2: Run MCP Inspector
npx @modelcontextprotocol/inspector@latest
# Connect to http://localhost:8000/mcp
```

### 7.2 Test Cases for Remote Server

| Test Case | Expected Behavior |
|-----------|-------------------|
| Unauthenticated request | Return 401 with WWW-Authenticate header |
| Invalid token | Return 401 with error message |
| Valid token, wrong audience | Return 401 with audience error |
| Valid token, insufficient scope | Return 403 Forbidden |
| Valid token, correct scope | Allow tool execution |
| Protected resource metadata | Return correct JSON at `/.well-known/oauth-protected-resource` |

### 7.3 Integration Test Example

```python
import pytest
import httpx

async def test_unauthenticated_request():
    """Remote server should reject unauthenticated requests."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/mcp",
            json={"method": "tools/list"}
        )
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers

async def test_protected_resource_metadata():
    """Server should expose OAuth metadata."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/.well-known/oauth-protected-resource"
        )
        assert response.status_code == 200
        data = response.json()
        assert "authorization_servers" in data
        assert "bearer_methods_supported" in data
```

---

## 8. Deployment Checklist

### 8.1 Pre-Deployment

- [ ] All tools work correctly in STDIO mode
- [ ] HTTP transport tested locally with Inspector
- [ ] OAuth flow tested with Inspector
- [ ] Environment variables documented
- [ ] CORS configured correctly
- [ ] Protected resource metadata endpoint working
- [ ] Token validation implemented and tested
- [ ] Error responses follow MCP spec

### 8.2 Deployment Steps (Example: Railway)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Set environment variables
railway vars set MCP_TRANSPORT=http
railway vars set GOOGLE_CLIENT_ID=xxx
railway vars set GOOGLE_CLIENT_SECRET=xxx
railway vars set OAUTH_ISSUER_URL=https://accounts.google.com

# 5. Deploy
railway up
```

### 8.3 Post-Deployment Verification

- [ ] Server accessible at public URL
- [ ] Inspector can connect via SSE/HTTP
- [ ] OAuth flow works with real tokens
- [ ] Claude Desktop works via mcp-remote proxy
- [ ] Error responses are user-friendly
- [ ] Logs are being captured

---

## 9. References

### Documentation Links

- **MCP Authorization Specification:**
  - [Authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
  - [Security Best Practices](https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices)

- **Deployment Guides:**
  - [Cloudflare Remote MCP Server](https://developers.cloudflare.com/agents/guides/remote-mcp-server/)
  - [Vercel MCP Deployment](https://vercel.com/docs/mcp/deploy-mcp-servers-to-vercel)

- **MCP Inspector:**
  - [Inspector Documentation](https://modelcontextprotocol.io/docs/tools/inspector)
  - [Inspector GitHub Repository](https://github.com/modelcontextprotocol/inspector)

- **OAuth Standards:**
  - [OAuth 2.1 Draft](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-v2-1-13)
  - [RFC 9728 - Protected Resource Metadata](https://datatracker.ietf.org/doc/html/rfc9728)
  - [RFC 8414 - Authorization Server Metadata](https://datatracker.ietf.org/doc/html/rfc8414)
  - [RFC 8707 - Resource Indicators](https://www.rfc-editor.org/rfc/rfc8707.html)

---

## 10. Next Steps

1. **Test HTTP Transport Locally**: Configure FastMCP for HTTP mode
2. **Implement OAuth Metadata Endpoint**: Per MCP spec requirements
3. **Add Bearer Token Validation**: Using Google OAuth tokens
4. **Test with MCP Inspector**: Verify OAuth flow works
5. **Choose Deployment Platform**: Vercel, Railway, or Cloudflare
6. **Deploy and Test**: Verify public accessibility
7. **Update README.md**: Document remote setup instructions
8. **Configure Claude Desktop**: Use mcp-remote proxy for remote connection
