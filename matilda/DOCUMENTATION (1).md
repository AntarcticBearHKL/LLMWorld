# @maincode-ai/matilda-client-sdk

**Version 0.2.0**

A small, self-contained public TypeScript SDK for building Matilda clients. Ships a dual ESM + CommonJS build with bundled type definitions and zero `@matilda/*` runtime dependencies. Requires Node.js ≥ 20.

The SDK follows the OpenAI client shape where it helps: constructor config, resource groups, request options, typed API errors, and async-iterable streaming. It does **not** expose model or provider selection — Matilda core owns routing, safety, resumable SSE, server-side tool execution, and policy.

## What's included

- **Chat** — non-streaming, full-event streaming, text-only streaming, schema-constrained structured output, and durable stream resume
- **Conversations** — list, retrieve, rename, and set message feedback
- **Files** — upload (single and parallel), retrieve metadata
- **Feedback** — report harmful content and submit response feedback
- **Devices** — register, list, and unregister push notification devices
- **Auth** — managed PKCE browser login, RFC 8628 device flow, token refresh, and persistent token storage
- **API Keys** — create, list, and revoke `mc_live_` API keys via SDK methods or the `matilda-key` CLI

## What's NOT included

- **Local tool-execution loop** — for client-side tool execution (`clientTools`, local approval/sandbox loops, tool-result continuation), use the Matilda agent SDK
- **Session class** — multi-turn conversations are managed via `conversationId` (see [§15. Multi-Turn Conversations](#15-multi-turn-conversations))

---

## Table of Contents

1. [Installation](#1-installation)
2. [Quick Start](#2-quick-start)
3. [Configuration](#3-configuration)
4. [Authentication](#4-authentication)
5. [Chat — Non-Streaming](#5-chat--non-streaming)
6. [Chat — Streaming (Full Events)](#6-chat--streaming-full-events)
7. [Chat — Text-Only Helpers](#7-chat--text-only-helpers)
8. [Chat — Structured Output](#8-chat--structured-output)
9. [Chat — Durable Streaming (Resume)](#9-chat--durable-streaming-resume)
10. [Conversations (History)](#10-conversations-history)
11. [Files](#11-files)
12. [Feedback](#12-feedback)
13. [Devices (Push Notifications)](#13-devices-push-notifications)
14. [Error Handling](#14-error-handling)
15. [Multi-Turn Conversations](#15-multi-turn-conversations)
16. [Suggested Tasks / Recipes](#16-suggested-tasks--recipes)

---

## 1. Installation

```sh
npm install @maincode-ai/matilda-client-sdk
# or: pnpm add @maincode-ai/matilda-client-sdk
# or: yarn add @maincode-ai/matilda-client-sdk
```

Requires Node.js ≥ 20.

`zod` (v3.25+) is a required peer dependency — install it alongside the SDK. It is used by the structured-output helpers ([§8](#8-chat--structured-output)):

```sh
npm install zod
```

### ESM import

```ts
import Matilda from '@maincode-ai/matilda-client-sdk';
```

### CommonJS require

```ts
const { Matilda } = require('@maincode-ai/matilda-client-sdk');
```

### Auth subpath (Node-only)

The standalone auth helpers are available via a subpath import:

```ts
import { loginWithBrowser, loginWithDeviceFlow } from '@maincode-ai/matilda-client-sdk/auth';
```

For the full Node auth surface (token manager, file store, loopback receiver, login flow controller):

```ts
import {
  createLoginFlow,
  createTokenManager,
  createFileTokenStore,
  fetchAuthServerMetadata,
  memoryStorage,
} from '@maincode-ai/matilda-client-sdk/auth/node';
```

---

## 2. Quick Start

### Minimal: send a message

```ts
import Matilda from '@maincode-ai/matilda-client-sdk';

const client = new Matilda({
  baseUrl: 'https://matilda.maincode.com/api',
  accessToken: process.env.MATILDA_ACCESS_TOKEN!,
});

const response = await client.chat.create({ input: 'Summarize this thread.' });
console.log(response.outputText);
```

> **Note:** The `accessToken` option above is fine for quick testing, but for production use we recommend the managed auth flows (`loginWithBrowser` or `loginWithDeviceFlow`) which auto-wire a `TokenManager` with automatic token refresh. See [§4. Authentication](#4-authentication).

### Minimal: streaming

```ts
for await (const event of client.chat.stream({ input: 'Write a short plan.' })) {
  if (event.type === 'response.output_text.delta') {
    process.stdout.write(event.delta);
  }
}
```

### Authenticated: device flow + chat

```ts
import Matilda from '@maincode-ai/matilda-client-sdk';

const client = new Matilda({ baseUrl: 'https://matilda.maincode.com/api' });

// Authenticate via RFC 8628 device flow — prints a code to stderr
await client.auth.loginWithDeviceFlow({ clientId: 'matilda-code' });

// Token is now managed automatically — no manual header wiring
const response = await client.chat.create({ input: 'Hello, Matilda!' });
console.log(response.outputText);
```

---

## 3. Configuration

### `MatildaClientOptions`

Extends `ClientConfig`. All fields are optional except `baseUrl`.

| Field | Type | Default | Description |
|---|---|---|---|
| `baseUrl` | `string` | `'/api'` | The Matilda API base URL. Must be absolute for auth flows. |
| `accessToken` | `string` | — | A static access token. Use this for simple setups, or use `getToken` for managed refresh. |
| `getToken` | `GetToken` | — | Dynamic token provider. Called on every request. The SDK's `TokenManager` implements this. |
| `apiVersion` | `string \| null` | — | API version sent via the `X-Matilda-API-Version` header. Omit to use the current version. |
| `urlPolicy` | `TrustedApiBaseUrlPolicy` | — | URL validation policy for `trustApiBaseUrl()`. |
| `publicConfigEndpoint` | `PublicConfigEndpoint` | — | Which public runtime config endpoint to use. |
| `getCsrfToken` | `() => string \| null` | — | CSRF token provider for web BFF cookie auth. |
| `reportedRequestMetadata` | `ReportedRequestMetadataConfig \| null` | — | SDK identification metadata. Auto-set to `{ sdkName: 'matilda-client', version }`. |

#### `TrustedApiBaseUrlPolicy`

| Field | Type | Description |
|---|---|---|
| `allowRelative` | `boolean` | Allow relative URLs (e.g. `/api`). |
| `allowedHosts` | `readonly string[]` | Allowlist of hostnames. |
| `allowLocalHttp` | `boolean` | Allow `http://localhost` / `127.0.0.1` (development). |
| `requiredPathPrefix` | `string` | Require a specific path prefix (e.g. `/api`). |
| `requireHttps` | `boolean` | Enforce HTTPS (loopback exempt). |

#### `PublicConfigEndpoint`

```ts
type PublicConfigEndpoint =
  | 'web-bff'
  | 'core-api-relative'
  | 'core-api-localhost'
  | 'core-api-localhost-3000'
  | 'core-api-android-emulator'
  | 'core-api-production';
```

### Environment URLs

| Environment | Base URL |
|---|---|
| Production | `https://matilda.maincode.com/api` |
| Staging | `https://staging.matilda.maincode.com/api` |

### Instance isolation

Each `Matilda` instance holds its own independent config. Multiple instances in the same process are fully isolated — constructor options and `configure()` writes are scoped to that instance.

```ts
const staging = new Matilda({ baseUrl: 'https://staging.matilda.maincode.com/api' });
const prod = new Matilda({ baseUrl: 'https://matilda.maincode.com/api' });

console.log(staging.config.baseUrl); // https://staging.matilda.maincode.com/api
console.log(prod.config.baseUrl);    // https://matilda.maincode.com/api

// Reconfiguring one never affects the other:
staging.configure({ baseUrl: 'https://override.example/api' });
console.log(staging.config.baseUrl); // https://override.example/api
console.log(prod.config.baseUrl);    // https://matilda.maincode.com/api (unchanged)
```

### `configure(options)`

Updates the instance config in place. Returns `this` for chaining.

```ts
client.configure({ accessToken: newToken }).chat.create(/* … */);
```

| Parameter | Type | Description |
|---|---|---|
| `options` | `MatildaClientOptions` | New config to merge. |

### `config` (getter)

Returns the current `ClientConfig`.

```ts
const cfg = client.config;
console.log(cfg.baseUrl, cfg.accessToken);
```

### `trustApiBaseUrl(rawUrl, policy?)`

Validates and brands a URL as a trusted API base URL.

| Parameter | Type | Description |
|---|---|---|
| `rawUrl` | `string` | The URL to validate. |
| `policy` | `TrustedApiBaseUrlPolicy` | Optional override policy. |

Returns a `TrustedApiBaseUrl` (a branded string).

---

## 4. Authentication

The SDK provides a managed auth tier: on successful login, a `TokenManager` is auto-configured on the client instance. Every subsequent request automatically carries a managed access token with single-flight, skew-aware auto-refresh.

### OAuth client IDs

The following client IDs are registered in the Matilda OAuth client registry:

| Client ID | Use case | Notes |
|---|---|---|
| `matilda-code` | Public CLI / agent SDK | PKCE + device flow. The default choice for most integrations. |
| `matilda-desktop` | Desktop app (Electron) | PKCE only (no device flow). |
| `matilda-admin-mcp` | Admin MCP server | Admin-scoped access. |

### `auth.loginWithBrowser(opts)`

Managed PKCE browser login (RFC 8252 loopback). Starts a temporary local server, opens the browser, receives the auth code, exchanges it for tokens, and auto-wires a `TokenManager`.

```ts
const tokens = await client.auth.loginWithBrowser({
  clientId: 'matilda-code',
  openBrowser: (url) => console.log(`Open: ${url}`),
});
console.log(tokens.accessToken);
```

#### `BrowserLoginOptions`

| Field | Type | Default | Description |
|---|---|---|---|
| `clientId` | `string` | **(required)** | OAuth client alias (e.g. `'matilda-code'`). |
| `scope` | `string` | `'openid offline_access'` | Space-separated OAuth scopes. |
| `identityProviderId` | `string` | — | Route straight to a federated IdP (e.g. Google SSO) instead of the hosted login page. |
| `callbackPort` | `number` | random ephemeral | Fixed loopback port. Recommended for FusionAuth redirect validation. |
| `timeoutMs` | `number` | `300_000` (5 min) | How long to wait for the browser callback. |
| `openBrowser` | `(url: string) => void \| Promise<void>` | — | Called with the authorize URL. If omitted, caller handles browser opening. |
| `successRedirect` | `string` | `'https://matilda.maincode.com/cli/signed-in'` | URL the browser is 302-redirected to on success. |
| `errorRedirect` | `string` | — | URL for the error case; otherwise a bare 400 text response. |
| `fetchImpl` | `typeof fetch` | `global fetch` | Override fetch (testing, custom transport). |
| `tokenStore` | `StorageAdapter` | `memoryStorage()` | Custom token persistence. |
| `tokenLock` | `<T>(fn: () => Promise<T>) => Promise<T>` | — | Cross-process critical-section lock for token refresh (e.g. from `createFileTokenStore`). |
| `onEvent` | `(e: LoginFlowEvent) => void` | — | Subscribe to login flow state events. |

#### Returns

`Promise<TokenSet>` — the token set from the login flow. The `TokenManager` is also auto-configured on the client instance.

### `auth.loginWithDeviceFlow(opts)`

Managed RFC 8628 device flow. Requests a device code, prints the user code and verification URL to stderr (by default), and polls until the user authorises.

```ts
const tokens = await client.auth.loginWithDeviceFlow({
  clientId: 'matilda-code',
  onEvent: (e) => {
    if (e.type === 'user_code') {
      console.log(`Visit ${e.verificationUri} and enter code: ${e.userCode}`);
    }
  },
});
```

If no `onEvent` handler is provided, the SDK prints the user code and verification URL to stderr automatically.

#### `DeviceLoginOptions`

| Field | Type | Default | Description |
|---|---|---|---|
| `clientId` | `string` | **(required)** | OAuth client alias. |
| `scope` | `string` | `'openid offline_access'` | Space-separated OAuth scopes. |
| `timeoutMs` | `number` | `300_000` (5 min) | Polling timeout. |
| `signal` | `AbortSignal` | — | Abort the polling loop. |
| `fetchImpl` | `typeof fetch` | `global fetch` | Override fetch. |
| `tokenStore` | `StorageAdapter` | `memoryStorage()` | Custom token persistence. |
| `tokenLock` | `<T>(fn: () => Promise<T>) => Promise<T>` | — | Cross-process lock for token refresh. |
| `onEvent` | `(e: LoginFlowEvent) => void` | `defaultDeviceOnEvent` | Subscribe to login flow events. If omitted, prints user code to stderr. |

#### Returns

`Promise<TokenSet>`

### `auth.refreshToken(refreshToken, clientId)`

Manually refresh an access token using a refresh token. This bypasses the `TokenManager` — use it only when you need raw token exchange.

```ts
const tokens = await client.auth.refreshToken(oldRefreshToken, 'matilda-code');
```

| Parameter | Type | Description |
|---|---|---|
| `refreshToken` | `string` | The refresh token to exchange. |
| `clientId` | `string` | OAuth client alias. |

Returns `Promise<TokenSet>`.

### `auth.getTokens()`

Returns the current token set from the managed `TokenManager`, or `null` if not authenticated.

```ts
const tokens = await client.auth.getTokens();
if (tokens) {
  console.log(`Token expires at: ${new Date(tokens.expiresAt).toISOString()}`);
}
```

Returns `Promise<TokenSet | null>`.

### `auth.logout()`

Clears the token store, destroys the `TokenManager`, and disconnects the client's `getToken` provider.

```ts
await client.auth.logout();
```

Returns `Promise<void>`.

### Token persistence

By default, tokens are stored in memory (`memoryStorage()`). For cross-process persistence (e.g. CLI sessions), use `createFileTokenStore` from the `/auth/node` subpath:

```ts
import Matilda from '@maincode-ai/matilda-client-sdk';
import { createFileTokenStore } from '@maincode-ai/matilda-client-sdk/auth/node';
import { homedir } from 'node:os';
import { join } from 'node:path';

const tokenPath = join(homedir(), '.matilda', 'tokens.json');
const { store, lock } = createFileTokenStore(tokenPath);

const client = new Matilda({ baseUrl: 'https://matilda.maincode.com/api' });

await client.auth.loginWithBrowser({
  clientId: 'matilda-code',
  tokenStore: store,
  tokenLock: lock,
});
```

The file store uses a `0600` JSON file with a lockfile-based single-writer lock to prevent cross-process refresh races.

### `StorageAdapter` interface

```ts
interface StorageAdapter {
  get(key: string): string | null | Promise<string | null>;
  set(key: string, value: string): void | Promise<void>;
  remove(key: string): void | Promise<void>;
}
```

Implement this to store tokens in a database, keychain, or any custom backend.

### `TokenManager` interface

```ts
interface TokenManager {
  getAccessToken(opts?: { forceRefresh?: boolean }): Promise<string>;
  getTokens(): Promise<TokenSet | null>;
  setTokens(tokens: TokenSet): Promise<void>;
  clear(): Promise<void>;
}
```

Created via `createTokenManager(deps)` from `/auth/node`. The SDK auto-creates one on login.

### `TokenSet` interface

```ts
interface TokenSet {
  accessToken: string;
  refreshToken?: string;
  idToken?: string;       // OIDC id_token when 'openid' scope is granted
  expiresAt: number;      // epoch milliseconds
}
```

### `AuthError` class

```ts
class AuthError extends Error {
  readonly code: string;       // OAuth error code (e.g. 'invalid_grant', 'authorization_pending')
  readonly retryable: boolean; // true for transient 5xx/network; false for revoked tokens
}
```

### `LoginFlowEvent` type

```ts
type LoginFlowEvent =
  | { type: 'state'; status: 'idle' | 'awaiting_user' | 'exchanging' | 'authenticated' | 'error' }
  | { type: 'authorize_url'; url: string }
  | { type: 'user_code'; userCode: string; verificationUri: string; verificationUriComplete?: string };
```

### Standalone auth subpath (`/auth`)

The `/auth` subpath provides the raw PKCE and device-flow helpers without the managed `TokenManager`. These are **deprecated** in favour of the managed `client.auth.*` methods, but remain available for integrators who need direct protocol access:

| Export | Description |
|---|---|
| `loginWithBrowser(coreAuthUrl, opts)` | Raw PKCE browser login. Returns `TokenSet`. |
| `loginWithDeviceFlow(coreAuthUrl, opts)` | Raw device flow. Returns `TokenSet`. |
| `refreshToken(coreAuthUrl, clientId, refreshToken)` | Raw token refresh. Returns `TokenSet`. |
| `createPkcePair()` | Generate PKCE `code_verifier` + `code_challenge` (S256). |
| `buildAuthorizeUrl(coreAuthUrl, opts)` | Construct the authorize URL. |

The `/auth/node` subpath adds the Node-only adapters on top of the isomorphic core:

| Export | Description |
|---|---|
| `createLoginFlow(opts)` | Headless login controller for loopback + device transports. |
| `createTokenManager(deps)` | Per-session token manager with single-flight refresh. |
| `createFileTokenStore(filePath)` | `0600` JSON file store with cross-process lock. |
| `createLoopbackReceiver(opts)` | RFC 8252 loopback redirect receiver. |
| `fetchAuthServerMetadata(issuer, fetchImpl?, opts?)` | RFC 8414 metadata discovery. |
| `memoryStorage()` | In-memory `StorageAdapter`. |
| `beginLogin(authorizationEndpoint, params)` | Stateless "begin" half of a redirect/BFF login. |
| `completeLogin(tokenEndpoint, params, fetchImpl?)` | Stateless "complete" half. |

### API Key Management

The SDK provides convenience methods for managing `mc_live_` API keys. These hit the same `JwtGuard`-protected endpoints the developer dashboard uses — the session JWT from a prior `loginWithBrowser()` or `loginWithDeviceFlow()` call is carried automatically by the `TokenManager`.

#### `auth.createApiKey(opts)`

Mints a new API key. The secret is returned **only at creation time** — store it immediately.

```ts
await client.auth.loginWithDeviceFlow({ clientId: 'matilda-code' });

const key = await client.auth.createApiKey({
  name: 'ci-runner',
  // scopes: ['api:code'],                    // omit → server default
  // expiresAt: '2026-12-31T23:59:59Z',       // omit → never expires
});

console.log(key.secret);        // mc_live_...  — shown only once
console.log(key.keyPrefix);     // mc_live_abcd
console.log(key.id);            // UUID for revocation
```

##### `CreateApiKeyOptions`

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | `string` | **(required)** | Human-readable key name (1–80 chars). |
| `scopes` | `string[]` | server default | Permission scopes (e.g. `['api:code']`). |
| `expiresAt` | `string` | — | ISO 8601 expiry timestamp. Omit for no expiry. |

Returns `Promise<ApiKeyWithSecret>`.

#### `auth.listApiKeys()`

Lists all non-revoked API keys for the authenticated user. Secrets are never included — only the `keyPrefix` for identification.

```ts
const keys = await client.auth.listApiKeys();
for (const key of keys) {
  console.log(`${key.keyPrefix}  ${key.name}  ${key.revokedAt ? 'REVOKED' : 'ACTIVE'}`);
}
```

Returns `Promise<ApiKey[]>`.

#### `auth.revokeApiKey(id)`

Revokes a key by ID. The key immediately stops working for authentication.

```ts
await client.auth.revokeApiKey(key.id);
```

| Parameter | Type | Description |
|---|---|---|
| `id` | `string` | The key UUID (from `createApiKey` or `listApiKeys`). |

Returns `Promise<ApiKey>` (the revoked key with `revokedAt` set).

#### `ApiKey` interface

```ts
interface ApiKey {
  id: string;
  name: string;
  keyPrefix: string;           // e.g. 'mc_live_abcd1234'
  scopes: string[];
  createdAt: string;           // ISO 8601
  lastUsedAt: string | null;
  revokedAt: string | null;
  expiresAt: string | null;
}
```

#### `ApiKeyWithSecret` interface

Extends `ApiKey` with the one-time secret:

```ts
interface ApiKeyWithSecret extends ApiKey {
  secret: string;              // full key, e.g. 'mc_live_...' — shown only at creation
}
```

### CLI — `matilda-key`

The package ships a `matilda-key` CLI binary that mints API keys via device-flow login. This is the easiest way for social-login (Google/Apple) users to get an API key without writing code.

#### Installation

The binary is available via `npx` (no global install required) or after installing the package:

```sh
npx matilda-key create-api-key --name "my-key"
# or, if installed globally:
matilda-key create-api-key --name "my-key"
```

#### Usage

```sh
matilda-key create-api-key --name <key-name> [--scopes ...] [--expires-at ...] [--api-base-url ...] [--client-id ...]
```

| Flag | Required | Default | Description |
|---|---|---|---|
| `--name` | yes | — | API key name (1–80 chars). |
| `--scopes` | no | server default | Comma-separated scopes (e.g. `api:code,api:chat`). |
| `--expires-at` | no | never | ISO 8601 expiry date. |
| `--api-base-url` | no | `https://matilda.maincode.com/api` | API base URL. |
| `--client-id` | no | `matilda-code` | OAuth client ID / alias. |

The `MATILDA_API_BASE_URL` environment variable is also honoured as a fallback for `--api-base-url`.

#### What happens when you run it

1. **Device-flow login** — a verification URL and code are printed to **stderr**. Open the URL, sign in with Google or Apple, enter the code.
2. **Key minting** — once authenticated, an API key is created from the session JWT.
3. **Output** — key metadata (ID, name, prefix, scopes, expiry) is printed to **stderr**. The secret is printed to **stdout**.

The stdout/stderr separation is deliberate: the secret on stdout is clean and pipeable, while the login flow and metadata remain visible on the terminal via stderr.

#### Piping the secret

```sh
# Capture into an env var (login flow still visible on terminal):
MATILDA_API_KEY=$(matilda-key create-api-key --name "ci-runner")

# Pipe to a file:
matilda-key create-api-key --name "ci-runner" > /tmp/key.txt

# Use in CI:
export MATILDA_API_KEY="$(cat /tmp/key.txt)"
```

#### Full example

```sh
$ matilda-key create-api-key --name "ci-runner" --scopes api:code

Starting device-flow login...

  Open https://matilda.maincode.com/device and enter code: ABCD-1234

  [state] awaiting_user_verification
  [state] token_received
Login successful!

Minting API key "ci-runner"...

API key created successfully.
  ID:          8f3a2b1c-...
  Name:        ci-runner
  Prefix:      mc_live_abcd1234
  Scopes:      api:code
  Expires:     never
  Created at:  2026-08-18T10:30:00.000Z

Secret printed to stdout. Store it securely — it won't be shown again.
```

The secret (`mc_live_...`) is on stdout; everything else is on stderr.

---

## 5. Chat — Non-Streaming

### `chat.create(params, options?)`

Sends a chat message and returns the complete response. Internally this runs the stream and collects all events.

```ts
const response = await client.chat.create({
  input: 'What is the capital of Australia?',
  conversationId: 'conv-123',
  responseMode: 'instant',
});

console.log(response.outputText);
console.log(response.usage);
```

#### `ChatCreateParams`

| Field | Type | Default | Description |
|---|---|---|---|
| `input` | `string` | — | The user's message. Required if `messages` is not provided. |
| `messages` | `ApiMessage[]` | — | Explicit message array. Overrides `input`. Each message: `{ role: 'user' \| 'assistant', content: string }`. |
| `conversationId` | `string` | — | Associates this message with a conversation thread for multi-turn chat. |
| `fileIds` | `string[]` | — | File IDs to attach (from `files.upload()`). |
| `responseMode` | `ChatResponseMode` | `'auto'` | Response depth: `'auto'`, `'instant'`, or `'deep'`. |
| `responseSchema` | `string` | — | Raw JSON Schema (as a string) to grammar-constrain the response to. Prefer `chat.streamObject` / `chat.createObject`, which convert a zod schema for you (see [§8. Chat — Structured Output](#8-chat--structured-output)). |

#### `MatildaRequestOptions`

Extends `RequestOptions`. All fields optional.

| Field | Type | Description |
|---|---|---|
| `fingerprint` | `string \| null` | Device fingerprint for rate limiting. |
| `accessToken` | `string \| null` | Override the client-level access token for this request. |
| `signal` | `AbortSignal` | Abort the request. |
| `stallTimeoutMs` | `number` | SSE stall watchdog timeout in ms. Default: `45_000`. Pass `0` to disable. |
| `onEvent` | `(event: MatildaChatStreamEvent) => void` | Catch-all stream event hook — fires for every event. Only honoured by convenience methods that consume the stream for you (`chat.create()`, `chat.createObject()`); use `chat.stream()` when you want to process events yourself. |

#### `MatildaChatResponse`

| Field | Type | Description |
|---|---|---|
| `outputText` | `string` | The full assistant response text. |
| `events` | `MatildaChatStreamEvent[]` | Every event emitted during the stream. |
| `streamId` | `string \| undefined` | Durable stream ID (from `stream_init` event). |
| `lastEventId` | `string \| undefined` | Last Redis stream entry ID (for resume). |
| `usage` | `UsageEvent \| undefined` | Token usage data. |
| `errors` | `Array<{ code: ChatErrorCode; message: string }>` | Any errors emitted during the stream. |
| `truncatedReason` | `string \| undefined` | Why the response was truncated (e.g. `'max_tokens'`). |

#### `ChatResponseMode`

```ts
type ChatResponseMode = 'auto' | 'instant' | 'deep';
```

- `'auto'` — Server decides the optimal response depth.
- `'instant'` — Optimised for low latency.
- `'deep'` — Optimised for thoroughness.

---

## 6. Chat — Streaming (Full Events)

### `chat.stream(params, options?)`

Returns an async generator that yields `MatildaChatStreamEvent` objects as they arrive over SSE. This is the full event stream — tool calls, usage, status changes, safety replacements, and more.

```ts
for await (const event of client.chat.stream({ input: 'Explain quantum computing.' })) {
  switch (event.type) {
    case 'response.created':
      console.log(`Stream started: ${event.streamId}`);
      break;
    case 'response.output_text.delta':
      process.stdout.write(event.delta);
      break;
    case 'response.tool_call.started':
      console.log(`\nTool: ${event.tool}`);
      break;
    case 'response.usage':
      console.log(`\nTokens: ${event.usage.output_tokens}`);
      break;
    case 'response.completed':
      console.log('\n--- Done ---');
      break;
    case 'response.error':
      console.error(`Error: ${event.code} — ${event.message}`);
      break;
  }
}
```

### `MatildaChatStreamEvent`

A discriminated union of 14 event types:

#### `response.created`

Emitted once at stream start with the durable stream ID.

```ts
{ type: 'response.created'; streamId: string }
```

#### `response.output_text.delta`

A text chunk from the assistant.

```ts
{ type: 'response.output_text.delta'; delta: string }
```

#### `response.output_text.replace`

The server replaced the output (e.g. safety filter). The `content` field holds the replacement text; `categories` lists the safety categories that triggered the replacement.

```ts
{ type: 'response.output_text.replace'; content?: string; categories?: string[] }
```

#### `response.status`

Stream lifecycle status change.

```ts
{ type: 'response.status'; status: 'thinking' | 'streaming' | 'queued' | 'idle' | 'done' | 'error' | string }
```

#### `response.queued`

Queue position update while waiting for a free slot.

```ts
{ type: 'response.queued'; state: string; position: number; estimatedWaitSeconds: number }
```

#### `response.tool_call.started`

A server-side tool invocation began.

```ts
{ type: 'response.tool_call.started'; tool: string; inputOrArgs?: string | Record<string, unknown>; output?: string }
```

#### `response.tool_call.progress`

Progress update from a running tool.

```ts
{ type: 'response.tool_call.progress'; tool: string; message: string }
```

#### `response.tool_call.completed`

A tool invocation finished.

```ts
{ type: 'response.tool_call.completed'; tool: string; status: 'success' | 'error'; input?: string; output?: string }
```

#### `response.generation_status`

Generation phase update.

```ts
{ type: 'response.generation_status'; phase: string }
```

#### `response.usage`

Token usage data for the turn.

```ts
{ type: 'response.usage'; usage: UsageEvent }
```

Where `UsageEvent` is:

```ts
interface UsageEvent {
  output_tokens: number;
  context_pct?: number;              // context window usage (0-100)
  context_messages_trimmed?: number; // messages trimmed to fit context budget
  context_budget_tokens?: number;    // total context budget in tokens
}
```

#### `response.cursor`

Durable stream cursor (Redis stream entry ID). Persist this to resume from this point.

```ts
{ type: 'response.cursor'; lastEventId: string }
```

#### `response.truncated`

The response was cut short.

```ts
{ type: 'response.truncated'; reason: string }
```

#### `response.completed`

The stream finished successfully.

```ts
{ type: 'response.completed' }
```

#### `response.error`

An error occurred during the stream.

```ts
{ type: 'response.error'; code: ChatErrorCode; message: string }
```

---

## 7. Chat — Text-Only Helpers

These helpers filter the event stream to just text — useful when you only need the response text and don't care about tool calls, usage, or status events.

### `chat.streamText(params, options?)`

Returns an async generator that yields raw string deltas. Throws `SafetyReplaceError` when the server replaces the output (safety filter). Throws `Error` on stream errors.

```ts
try {
  for await (const chunk of client.chat.streamText({ input: 'Write a haiku.' })) {
    process.stdout.write(chunk);
  }
} catch (err) {
  if (err instanceof SafetyReplaceError) {
    console.error(`\nSafety replace: ${err.categories.join(', ')}`);
  } else {
    console.error(err);
  }
}
```

> **Why throw on safety replace?** The original text has already been yielded to the consumer by the time the replace event arrives. Throwing forces the consumer to handle the replacement explicitly — silently dropping it would lose the replacement message.

### `chat.createText(params, options?)`

Non-streaming convenience that returns just the final output text. Safety replace is handled naturally — the replacement text is returned. Throws if the stream produced any error events.

```ts
const text = await client.chat.createText({ input: 'What is 2 + 2?' });
console.log(text); // "4"
```

### `SafetyReplaceError`

```ts
class SafetyReplaceError extends Error {
  readonly categories: string[];
  // message = replacement content (or empty string)
}
```

---

## 8. Chat — Structured Output

Structured output constrains the model's response to a JSON Schema, server-side (grammar-constrained decoding), and then validates it client-side against your zod schema. Pass a zod schema, receive a fully-typed object — no prompt engineering, no brittle JSON extraction.

### `chat.streamObject(params, schema, options?)`

Streams exactly like `chat.stream()` — you receive every `MatildaChatStreamEvent` — plus one final event with the parsed, schema-validated object. The `schema` argument is any zod schema (`z` is bundled with the SDK); the SDK converts it to JSON Schema and constrains generation server-side.

```ts
import { z } from 'zod';

const recipe = z.object({
  name: z.string(),
  prepTimeMinutes: z.number(),
  ingredients: z.array(z.string()),
});

for await (const event of client.chat.streamObject(
  { input: 'Give me a recipe for pavlova.' },
  recipe,
)) {
  if (event.type === 'response.output_text.delta') {
    process.stdout.write(event.delta); // raw JSON streaming in
  }
  if (event.type === 'object') {
    console.log('\nValidated:', event.object); // typed as z.infer<typeof recipe>
  }
}
```

The final event:

```ts
{ type: 'object'; object: T } // T = z.infer<typeof schema>
```

### `chat.createObject(params, schema, options?)`

Non-streaming convenience. Returns a `MatildaObjectResponse<T>` — everything `chat.create()` returns, plus the validated `object`.

```ts
const response = await client.chat.createObject(
  { input: 'Extract the invoice total: $1,250.00 AUD due 30 Sep.', conversationId },
  z.object({ total: z.number(), currency: z.string() }),
);

console.log(response.object.total);    // 1250 (number)
console.log(response.object.currency); // "AUD" (string)
console.log(response.outputText);      // raw JSON text as returned
```

#### `MatildaObjectResponse<T>`

Extends `MatildaChatResponse` with one additional field:

| Field | Type | Description |
|---|---|---|
| `object` | `T` | The response text parsed as JSON and validated against your schema. |

### Raw JSON Schema via `responseSchema`

If you don't want zod validation, pass a stringified JSON Schema directly as `responseSchema` on any chat call:

```ts
const response = await client.chat.create({
  input: 'List three Australian birds.',
  responseSchema: JSON.stringify({
    type: 'object',
    properties: { birds: { type: 'array', items: { type: 'string' } } },
    required: ['birds'],
    additionalProperties: false,
  }),
});
JSON.parse(response.outputText); // guaranteed valid, schema-conforming JSON
```

With `responseSchema` set, the response text is guaranteed to be valid JSON conforming to the schema — but parsing and validation are up to you.

### OpenAI-compatible endpoint

The OpenAI-compatible endpoint (`POST /api/v1/chat/completions`) also honours structured output via the standard `response_format` parameter, so the OpenAI JS SDK's structured-output option works against Matilda as-is:

- `{ "type": "json_schema", "json_schema": { "name": "...", "schema": {...} } }` — grammar-constrained to your schema (the schema is applied with `strict: true` server-side; the `strict` and `name` fields you supply are re-wrapped downstream).
- `{ "type": "json_object" }` — guarantees valid JSON output without a schema (OpenAI JSON mode).

> **Safety replace and structured output.** If the server replaces the output mid-stream (safety filter), `streamObject` throws `SafetyReplaceError` — the replacement text is in `.message` and the triggering categories in `.categories`. Deltas already yielded to your consumer are not rolled back; if you render streamed JSON, handle `response.output_text.replace` events (or choose non-streaming `createObject`) to avoid showing half-rendered output that is later discarded.

> **Truncation throws.** If the stream is truncated before the JSON completes, both helpers throw `MatildaObjectParseError` with the partial text in `.raw`. See [§14. Error Handling](#14-error-handling).

> **Stream errors throw.** If the server emits an error event mid-stream, both helpers throw an `Error` with the server's error code and message (`${code}: ${message}`).

---

## 9. Chat — Durable Streaming (Resume)

Durable streaming lets a client disconnect mid-stream and resume from where it left off. The server buffers events in a Redis stream, keyed by a `streamId` advertised at stream start.

### Durable streaming lifecycle

1. Start a stream — `chat.stream()` emits a `response.created` event with a `streamId`.
2. Persist the `streamId` and `conversationId` immediately.
3. If disconnected, call `chat.activeStream(conversationId)` to check if the stream is still live.
4. Call `chat.resume({ streamId, lastEventId })` to replay buffered events from `lastEventId` onwards.

### `chat.resume(params, options?)`

Resumes a previously detached stream by replaying buffered events from `lastEventId`. Returns an async generator of `MatildaChatStreamEvent`.

```ts
for await (const event of client.chat.resume({
  streamId: savedStreamId,
  lastEventId: savedLastEventId,
})) {
  if (event.type === 'response.output_text.delta') {
    process.stdout.write(event.delta);
  }
}
```

#### `ChatResumeParams`

| Field | Type | Default | Description |
|---|---|---|---|
| `streamId` | `string` | **(required)** | The stream ID from `response.created`. |
| `lastEventId` | `string` | — | The last Redis stream entry ID received. Omit to replay from the start. |

### `chat.activeStream(conversationId, options?)`

Checks whether a conversation has an active stream.

```ts
const result = await client.chat.activeStream('conv-123');
// { stream_id: 'abc-123' | null, status: 'active' | 'done' | 'error' | null }
```

Returns `Promise<ActiveStreamLookup>`:

```ts
interface ActiveStreamLookup {
  stream_id: string | null;
  status: 'active' | 'done' | 'error' | null;
}
```

### `chat.notifyOnCompletion(streamId, enabled?, options?)`

Request a push notification when a backgrounded stream completes.

```ts
await client.chat.notifyOnCompletion(streamId, true);
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `streamId` | `string` | **(required)** | The stream to watch. |
| `enabled` | `boolean` | `true` | Enable or disable the notification. |

Returns `Promise<{ status: string }>`.

### Full resume example

```ts
import Matilda from '@maincode-ai/matilda-client-sdk';

const client = new Matilda({
  baseUrl: 'https://matilda.maincode.com/api',
  accessToken: process.env.MATILDA_ACCESS_TOKEN!,
});

let streamId: string | null = null;
let lastEventId: string | undefined;

// Start streaming
for await (const event of client.chat.stream({
  input: 'Write a long essay about Australia.',
  conversationId: 'conv-123',
})) {
  if (event.type === 'response.created') {
    streamId = event.streamId;
  }
  if (event.type === 'response.cursor') {
    lastEventId = event.lastEventId;
  }
  if (event.type === 'response.output_text.delta') {
    process.stdout.write(event.delta);
  }
}

// Later — check if the stream is still active, then resume
const active = await client.chat.activeStream('conv-123');
if (active.status === 'active' && streamId) {
  console.log('\n--- Resuming ---');
  for await (const event of client.chat.resume({ streamId, lastEventId })) {
    if (event.type === 'response.output_text.delta') {
      process.stdout.write(event.delta);
    }
  }
}
```

---

## 10. Conversations (History)

### `conversations.list(options?)`

Lists conversations with pagination.

```ts
const result = await client.conversations.list({ limit: 20, offset: 0 });
for (const conv of result.conversations) {
  console.log(`${conv.id}: ${conv.title} (updated ${conv.updatedAt})`);
}
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| `limit` | `number` | — | Maximum number of conversations to return. |
| `offset` | `number` | — | Pagination offset. |
| `fingerprint` | `string \| null` | — | Device fingerprint. |
| `accessToken` | `string \| null` | — | Override access token. |

Returns `Promise<ConversationListResponse>`:

```ts
interface ConversationListResponse {
  conversations: ConversationSummary[];
  total: number;
  limit: number;
  offset: number;
}

interface ConversationSummary {
  id: string;
  userId: string;
  title: string;
  createdAt: string;
  updatedAt: string;
}
```

### `conversations.retrieve(conversationId, options?)`

Retrieves a full conversation thread with all messages.

```ts
const conv = await client.conversations.retrieve('conv-123');
for (const msg of conv.messages) {
  console.log(`[${msg.role}] ${msg.content}`);
}
```

Returns `Promise<ConversationRecord>`:

```ts
interface ConversationRecord extends ConversationSummary {
  messages: ConversationMessage[];
}

interface ConversationMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  feedback?: 'positive' | 'negative' | null;
  attachments?: FileAttachment[];
  tokensUsed?: number | null;
  parentId?: string | null;
  generationOrdinal?: number;
  status?: 'completed' | 'failed' | 'interrupted';
  errorCode?: string | null;
  createdAt: string;
}
```

### `conversations.update(conversationId, patch, options?)`

Updates a conversation's metadata (currently only title).

```ts
await client.conversations.update('conv-123', { title: 'My Chat About AI' });
```

| Parameter | Type | Description |
|---|---|---|
| `conversationId` | `string` | The conversation to update. |
| `patch` | `{ title?: string }` | Fields to update. |

Returns `Promise<void>`.

### `conversations.setMessageFeedback(conversationId, messageId, feedback, options?)`

Sets thumbs-up or thumbs-down feedback on a specific message.

```ts
await client.conversations.setMessageFeedback('conv-123', 'msg-456', 'positive');
```

| Parameter | Type | Description |
|---|---|---|
| `conversationId` | `string` | The conversation containing the message. |
| `messageId` | `string` | The message to rate. |
| `feedback` | `'positive' \| 'negative'` | The feedback value. |

Returns `Promise<{ ok: boolean }>`.

---

## 11. Files

### `files.upload(file, options?)`

Uploads a single file. Files at or above the server's chunked threshold use the parallel multipart protocol; smaller files use single-shot upload.

```ts
const file = new File(['Hello, world!'], 'hello.txt', { type: 'text/plain' });
const result = await client.files.upload(file, {
  onProgress: (pct) => console.log(`Upload: ${pct}%`),
});
console.log(`File ID: ${result.fileId}, Status: ${result.status}`);
```

#### `FileUploadOptions`

Extends `MatildaRequestOptions`:

| Field | Type | Description |
|---|---|---|
| `onProgress` | `(pct: number) => void` | Progress callback (0–100). |
| `fingerprint` | `string \| null` | Device fingerprint. |
| `accessToken` | `string \| null` | Override access token. |
| `signal` | `AbortSignal` | Abort the upload. |

Returns `Promise<FileCompleteResponse>`:

```ts
interface FileCompleteResponse {
  fileId: string;
  status: FileAttachmentStatus;
  failureReason?: FileFailureReason;
}

type FileAttachmentStatus = 'pending' | 'scanning' | 'processing' | 'ready' | 'failed' | 'rejected';
```

### `files.uploadMany(files, options?)`

Uploads multiple files in parallel. One file's failure does not abort the others. Inspect each `PromiseSettledResult` for per-file outcomes.

```ts
const files = [
  new File(['doc 1'], 'doc1.txt', { type: 'text/plain' }),
  new File(['doc 2'], 'doc2.txt', { type: 'text/plain' }),
];

const results = await client.files.uploadMany(files);
for (let i = 0; i < results.length; i++) {
  const result = results[i];
  if (result.status === 'fulfilled') {
    console.log(`File ${i}: ${result.value.fileId} (${result.value.status})`);
  } else {
    console.error(`File ${i} failed:`, result.reason);
  }
}
```

Returns `Promise<PromiseSettledResult<FileCompleteResponse>[]>`.

### `files.retrieve(fileId, options?)`

Retrieves metadata for a previously uploaded file.

```ts
const file = await client.files.retrieve('file-abc123');
console.log(`${file.filename} — ${file.status} (${file.sizeBytes} bytes)`);
if (file.extractedText) {
  console.log(`Extracted: ${file.extractedText.slice(0, 100)}...`);
}
```

Returns `Promise<FileAttachment>`:

```ts
interface FileAttachment {
  id: string;
  filename: string;
  contentType: string;
  sizeBytes: number;
  status: FileAttachmentStatus;
  extractedText?: string;
  thumbnailUrl?: string;
  localUri?: string;
  failureReason?: FileFailureReason;
  createdAt: string;
}

interface FileFailureReason {
  code: string;
  message: string;
  retryable: boolean;
}
```

### Using files in chat

Upload a file, then reference its `fileId` in a chat message:

```ts
const fileResult = await client.files.upload(
  new File(['Quarterly report content...'], 'report.txt', { type: 'text/plain' }),
);

const response = await client.chat.create({
  input: 'Summarise this report.',
  fileIds: [fileResult.fileId],
});
console.log(response.outputText);
```

---

## 12. Feedback

### `feedback.report(params, options?)`

Reports a message for harmful, inaccurate, off-topic, or privacy-violating content.

```ts
await client.feedback.report({
  messageId: 'msg-456',
  conversationId: 'conv-123',
  reason: 'inaccurate',
  comment: 'The capital of Australia is Canberra, not Sydney.',
});
```

#### Parameters

| Field | Type | Description |
|---|---|---|
| `messageId` | `string` | The message being reported. |
| `conversationId` | `string` | The conversation containing the message. |
| `reason` | `'harmful' \| 'inaccurate' \| 'off_topic' \| 'privacy' \| 'other'` | Report reason. |
| `comment` | `string` | Optional additional context. |

Returns `Promise<{ reportId: string; acknowledgedAt: string }>`.

### `feedback.response(params, options?)`

Submits general response feedback (positive/negative sentiment with platform context).

```ts
await client.feedback.response({
  messageId: 'msg-456',
  conversationId: 'conv-123',
  comment: 'Great answer!',
  platform: 'web',
  appVersion: '1.0.0',
});
```

#### Parameters

| Field | Type | Description |
|---|---|---|
| `messageId` | `string` | The message being rated. |
| `conversationId` | `string` | The conversation containing the message. |
| `comment` | `string` | Optional feedback text. |
| `platform` | `'web' \| 'ios' \| 'android' \| 'unknown'` | Client platform. |
| `appVersion` | `string` | App version string. |
| `buildNumber` | `string` | Build number. |

Returns `Promise<{ feedbackId: string; acknowledgedAt: string }>`.

---

## 13. Devices (Push Notifications)

### `devices.register(device, options?)`

Registers a push notification device.

```ts
await client.devices.register({
  expo_push_token: 'ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]',
  device_id: 'device-uuid-123',
  platform: 'ios',
  app_version: '1.0.0',
});
```

#### `PushDevice`

| Field | Type | Description |
|---|---|---|
| `expo_push_token` | `string` | Expo push notification token. |
| `device_id` | `string` | Unique device identifier. |
| `platform` | `'ios' \| 'android'` | Device platform. |
| `app_version` | `string` | App version. |

Returns `Promise<{ status: string }>`.

### `devices.list(options?)`

Lists all registered push devices for the current user.

```ts
const devices = await client.devices.list();
for (const device of devices) {
  console.log(`${device.platform}: ${device.expo_push_token}`);
}
```

Returns `Promise<PushDevice[]>`.

### `devices.unregister(expoPushToken, options?)`

Unregisters a push device by its Expo push token.

```ts
await client.devices.unregister('ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]');
```

Returns `Promise<{ deleted: boolean }>`.

---

## 14. Error Handling

### `MatildaAPIError`

Thrown on non-2xx HTTP responses from the API.

```ts
class MatildaAPIError extends Error {
  readonly status: number;       // HTTP status code
  readonly responseText: string; // Raw response body
}
```

### `SafetyReplaceError`

Thrown by `chat.streamText()`, `chat.streamObject()`, and `chat.createObject()` when the server replaces the output via a safety filter. The `message` property contains the replacement text (or empty string), and `categories` lists the safety categories that triggered the replacement.

```ts
class SafetyReplaceError extends Error {
  readonly categories: string[];
}
```

### `MatildaObjectParseError`

Thrown by `chat.streamObject()` and `chat.createObject()` when the response cannot be parsed as JSON or fails zod validation — e.g. when a stream is truncated. `raw` contains the full response text; `cause` is the underlying `JSON.parse` or zod error. See [§8. Chat — Structured Output](#8-chat--structured-output).

```ts
class MatildaObjectParseError extends Error {
  readonly raw: string;
  readonly cause: unknown;
}
```

### `AuthError`

Thrown by auth flows. The `code` field is an OAuth error code (e.g. `'invalid_grant'`, `'authorization_pending'`, `'expired_token'`, `'access_denied'`). The `retryable` field distinguishes transient failures (5xx, network) from permanent ones (revoked refresh token).

```ts
class AuthError extends Error {
  readonly code: string;
  readonly retryable: boolean;
}
```

### Chat error codes (`ChatErrorCode`)

These codes are emitted via the `response.error` stream event and appear in `MatildaChatResponse.errors`:

| Code | Description |
|---|---|
| `internal_error` | Server-side failure. |
| `upstream_unavailable` | The AI model is not responding. |
| `rate_limited` | Too many requests. |
| `content_blocked` | Safety filter blocked the content. |
| `stream_aborted` | The stream was interrupted before completion. |
| `deadline_exceeded` | The response did not finish before the deadline. |
| `context_too_large` | The conversation is too long for the model. |
| `stalled` | No SSE events for the configured stall window. |
| `stream_expired` | The durable stream buffer expired (resume path only). |
| `unknown` | Unclassified error (old server without typed codes). |

### Stall watchdog

The streaming parser arms an idle-event watchdog. If no SSE event arrives for `stallTimeoutMs` milliseconds, the stream is considered dead and aborted with a `'stalled'` error.

- **Default:** `45_000` ms (3× the server's 15-second keep-alive ping cadence)
- **Disable:** Pass `stallTimeoutMs: 0` in `MatildaRequestOptions` (not recommended — mobile loses background-to-foreground hung-stream recovery)

### Error handling example

```ts
import Matilda, { MatildaAPIError, SafetyReplaceError } from '@maincode-ai/matilda-client-sdk';

try {
  const text = await client.chat.createText({ input: 'Hello!' });
  console.log(text);
} catch (err) {
  if (err instanceof MatildaAPIError) {
    if (err.status === 401) {
      console.error('Session expired — re-authenticate.');
    } else if (err.status === 429) {
      console.error('Rate limited — slow down.');
    } else {
      console.error(`API error ${err.status}: ${err.responseText}`);
    }
  } else if (err instanceof SafetyReplaceError) {
    console.error(`Safety filter: ${err.categories.join(', ')}`);
  } else {
    console.error('Unexpected error:', err);
  }
}
```

---

## 15. Multi-Turn Conversations

The client SDK does not have a `Session` class. Multi-turn conversations are managed by passing a `conversationId` to each chat call. The server reconstructs the full conversation history server-side from the session store.

### Pattern

1. Generate a conversation ID (any unique string, e.g. a UUID).
2. Pass it to every `chat.create()` or `chat.stream()` call.
3. The server maintains the conversation history — you only send the latest message.

```ts
import { randomUUID } from 'node:crypto';
import Matilda from '@maincode-ai/matilda-client-sdk';

const client = new Matilda({ baseUrl: 'https://matilda.maincode.com/api' });

// Authenticate with device flow — token refresh is handled automatically
if (!(await client.auth.getTokens())) {
  await client.auth.loginWithDeviceFlow({ clientId: 'matilda-code' });
}

const conversationId = randomUUID();

// Turn 1
const r1 = await client.chat.create({ input: 'What is the capital of France?', conversationId });
console.log(r1.outputText); // "Paris"

// Turn 2 — server remembers the previous turn
const r2 = await client.chat.create({ input: 'What about Germany?', conversationId });
console.log(r2.outputText); // "Berlin"

// Turn 3
const r3 = await client.chat.create({ input: 'And Italy?', conversationId });
console.log(r3.outputText); // "Rome"
```

### Contrasting with the agent SDK

The Matilda agent SDK provides a `Session` class that wraps an `Agent` with auto-managed `conversationId`, a `turns[]` array, and session-level defaults. If you need client-side tool execution, approval loops, or session state management, consider the agent SDK. For simple chatbot integrations, the client SDK's `conversationId` pattern is sufficient.

### Retrieving conversation history

```ts
// List all conversations
const list = await client.conversations.list({ limit: 50 });

// Retrieve a specific conversation with full message history
const conv = await client.conversations.retrieve(conversationId);
for (const msg of conv.messages) {
  console.log(`[${msg.role}] ${msg.content}`);
}
```

---

## 16. Suggested Tasks / Recipes

### Recipe 1: CLI chatbot

A complete interactive CLI chatbot with device-flow auth and streaming.

```ts
import * as readline from 'node:readline/promises';
import { stdin, stdout } from 'node:process';
import Matilda from '@maincode-ai/matilda-client-sdk';
import { createFileTokenStore } from '@maincode-ai/matilda-client-sdk/auth/node';
import { homedir } from 'node:os';
import { join } from 'node:path';

const { store, lock } = createFileTokenStore(join(homedir(), '.matilda', 'tokens.json'));

const client = new Matilda({ baseUrl: 'https://matilda.maincode.com/api' });

// Authenticate if needed
if (!(await client.auth.getTokens())) {
  console.log('Starting device flow authentication...');
  await client.auth.loginWithDeviceFlow({
    clientId: 'matilda-code',
    tokenStore: store,
    tokenLock: lock,
  });
  console.log('Authenticated!');
}

// Start chatting
const rl = readline.createInterface({ input: stdin, output: stdout });
const conversationId = crypto.randomUUID();

while (true) {
  const input = await rl.question('\nYou: ');
  if (!input.trim() || input.toLowerCase() === 'exit') break;

  process.stdout.write('Matilda: ');
  for await (const chunk of client.chat.streamText({ input, conversationId })) {
    process.stdout.write(chunk);
  }
  process.stdout.write('\n');
}

rl.close();
```

### Recipe 2: File Q&A

Upload a document and ask questions about it.

```ts
import { readFileSync } from 'node:fs';
import { randomUUID } from 'node:crypto';
import Matilda from '@maincode-ai/matilda-client-sdk';

const client = new Matilda({ baseUrl: 'https://matilda.maincode.com/api' });

// Authenticate with device flow — token refresh is handled automatically
if (!(await client.auth.getTokens())) {
  await client.auth.loginWithDeviceFlow({ clientId: 'matilda-code' });
}

// Upload a file
const buffer = readFileSync('./report.pdf');
const file = new File([buffer], 'report.pdf', { type: 'application/pdf' });
const upload = await client.files.upload(file, {
  onProgress: (pct) => process.stdout.write(`\rUploading: ${pct}%`),
});
console.log(`\nUploaded: ${upload.fileId} (${upload.status})`);

// A conversationId is required for follow-ups to share history — omitting it
// auto-creates a new conversation per call.
const conversationId = randomUUID();

// Ask a question about it
const response = await client.chat.create({
  input: 'Summarise the key findings in this report.',
  fileIds: [upload.fileId],
  conversationId,
});
console.log(response.outputText);

// Follow-up question in the same conversation
const followUp = await client.chat.create({
  input: 'What are the recommendations?',
  fileIds: [upload.fileId],
  conversationId,
});
console.log(followUp.outputText);
```

### Recipe 3: Conversation history browser

List, paginate, and inspect conversation history.

```ts
import Matilda from '@maincode-ai/matilda-client-sdk';

const client = new Matilda({ baseUrl: 'https://matilda.maincode.com/api' });

// Authenticate with device flow — token refresh is handled automatically
if (!(await client.auth.getTokens())) {
  await client.auth.loginWithDeviceFlow({ clientId: 'matilda-code' });
}

// List first page
let offset = 0;
const limit = 10;
let page = await client.conversations.list({ limit, offset });

console.log(`Total conversations: ${page.total}\n`);

for (const conv of page.conversations) {
  console.log(`[${conv.id}] ${conv.title}`);
  console.log(`  Updated: ${conv.updatedAt}`);
  console.log();
}

// Load next page
offset += limit;
if (offset < page.total) {
  page = await client.conversations.list({ limit, offset });
  for (const conv of page.conversations) {
    console.log(`[${conv.id}] ${conv.title}`);
  }
}

// Retrieve a full conversation
if (page.conversations.length > 0) {
  const full = await client.conversations.retrieve(page.conversations[0].id);
  console.log(`\n--- ${full.title} ---`);
  for (const msg of full.messages) {
    console.log(`\n[${msg.role.toUpperCase()}]`);
    console.log(msg.content);
    if (msg.feedback) {
      console.log(`  Feedback: ${msg.feedback}`);
    }
  }
}
```

### Recipe 4: Durable stream recovery

Start a stream, simulate a disconnect, and resume from the last cursor.

```ts
import Matilda from '@maincode-ai/matilda-client-sdk';

const client = new Matilda({ baseUrl: 'https://matilda.maincode.com/api' });

// Authenticate with device flow — token refresh is handled automatically
if (!(await client.auth.getTokens())) {
  await client.auth.loginWithDeviceFlow({ clientId: 'matilda-code' });
}

const conversationId = crypto.randomUUID();
let streamId: string | null = null;
let lastEventId: string | undefined;
let receivedText = '';

// Start streaming — simulate disconnect after a few events
console.log('Starting stream...');
try {
  for await (const event of client.chat.stream({
    input: 'Write a very long, detailed essay about the history of computing.',
    conversationId,
  })) {
    if (event.type === 'response.created') streamId = event.streamId;
    if (event.type === 'response.cursor') lastEventId = event.lastEventId;
    if (event.type === 'response.output_text.delta') {
      receivedText += event.delta;
      // Simulate disconnect after 500 chars
      if (receivedText.length > 500) {
        console.log('\n--- Simulated disconnect ---');
        break;
      }
    }
    if (event.type === 'response.completed') {
      console.log('Stream completed naturally.');
    }
  }
} catch (err) {
  console.log('Disconnected:', err);
}

console.log(`Received ${receivedText.length} chars before disconnect.`);

// Check if the stream is still active
if (streamId) {
  const active = await client.chat.activeStream(conversationId);
  console.log(`Stream status: ${active.status}`);

  if (active.status === 'active') {
    console.log('\n--- Resuming ---');
    for await (const event of client.chat.resume({ streamId, lastEventId })) {
      if (event.type === 'response.output_text.delta') {
        receivedText += event.delta;
        process.stdout.write(event.delta);
      }
      if (event.type === 'response.completed') {
        console.log('\n\n--- Resume complete ---');
        console.log(`Total received: ${receivedText.length} chars`);
      }
    }
  }
}
```

### Recipe 5: Multi-environment setup

Run staging and production clients in the same process. Each instance manages its own auth independently.

```ts
import Matilda from '@maincode-ai/matilda-client-sdk';

const staging = new Matilda({ baseUrl: 'https://staging.matilda.maincode.com/api' });
const production = new Matilda({ baseUrl: 'https://matilda.maincode.com/api' });

// Authenticate each instance independently — device flow or browser login
if (!(await staging.auth.getTokens())) {
  await staging.auth.loginWithDeviceFlow({
    clientId: 'matilda-code',
  });
}
if (!(await production.auth.getTokens())) {
  await production.auth.loginWithBrowser({ clientId: 'matilda-code' });
}

// Run the same prompt against both environments
const [stagingResponse, prodResponse] = await Promise.all([
  staging.chat.createText({ input: 'Explain quantum entanglement.' }),
  production.chat.createText({ input: 'Explain quantum entanglement.' }),
]);

console.log('Staging:', stagingResponse);
console.log('Production:', prodResponse);

// Instances are fully isolated — each manages its own token lifecycle
// Reconfiguring one never affects the other:
staging.configure({ baseUrl: 'https://override.example/api' });
// production.config.baseUrl is unchanged
```

### Recipe 6: Custom token store

Implement `StorageAdapter` to store tokens in a database or other custom backend.

```ts
import Matilda from '@maincode-ai/matilda-client-sdk';
import type { StorageAdapter } from '@maincode-ai/matilda-client-sdk';

// Example: a database-backed token store
class DatabaseTokenStore implements StorageAdapter {
  constructor(private db: Database) {}

  async get(key: string): Promise<string | null> {
    const row = await this.db.query('SELECT value FROM tokens WHERE key = $1', [key]);
    return row?.value ?? null;
  }

  async set(key: string, value: string): Promise<void> {
    await this.db.query(
      'INSERT INTO tokens (key, value) VALUES ($1, $2) ON CONFLICT (key) DO UPDATE SET value = $2',
      [key, value],
    );
  }

  async remove(key: string): Promise<void> {
    await this.db.query('DELETE FROM tokens WHERE key = $1', [key]);
  }
}

const tokenStore = new DatabaseTokenStore(myDatabase);

const client = new Matilda({ baseUrl: 'https://matilda.maincode.com/api' });

await client.auth.loginWithDeviceFlow({
  clientId: 'matilda-code',
  tokenStore,
  // No cross-process lock needed — the database handles concurrency
});

// Tokens are now persisted in the database and survive process restarts
const response = await client.chat.create({ input: 'Hello!' });
console.log(response.outputText);
```

---

## Exports Reference

### Default export

```ts
import Matilda from '@maincode-ai/matilda-client-sdk';
```

The `Matilda` class — the main SDK entry point.

### Named exports

| Export | Type | Description |
|---|---|---|
| `Matilda` | `class` | Main client class. |
| `MatildaAPIError` | `class` | HTTP error (status, responseText). |
| `SafetyReplaceError` | `class` | Safety filter replacement error (categories). |
| `MatildaObjectParseError` | `class` | Structured output parse/validation failure (raw, cause). |
| `MatildaClientOptions` | `interface` | Constructor options (extends `ClientConfig`). |
| `MatildaRequestOptions` | `interface` | Per-request options (signal, stallTimeoutMs, etc.). |
| `ChatCreateParams` | `interface` | Chat request params (input, messages, conversationId, fileIds, responseMode, responseSchema). |
| `MatildaChatStreamEvent` | `type` | Discriminated union of 14 stream event types. |
| `MatildaChatResponse` | `interface` | Collected response from `chat.create()`. |
| `MatildaObjectResponse<T>` | `interface` | `chat.createObject()` response (extends `MatildaChatResponse`, adds `object`). |
| `MatildaObjectEvent<T>` | `type` | `chat.streamObject()` events — all stream events, plus a final `{ type: 'object' }`. |
| `ChatResumeParams` | `interface` | Durable stream resume params (streamId, lastEventId). |
| `FileUploadOptions` | `interface` | File upload options (onProgress + request options). |
| `BrowserLoginOptions` | `interface` | Browser login (PKCE) options. |
| `DeviceLoginOptions` | `interface` | Device flow options. |
| `CreateApiKeyOptions` | `interface` | API key creation params (name, scopes, expiresAt). |
| `ApiKey` | `interface` | API key metadata (no secret). |
| `ApiKeyWithSecret` | `interface` | API key with one-time secret. |
| `TokenSet` | `interface` | OAuth token set (accessToken, refreshToken, idToken, expiresAt). |
| `StorageAdapter` | `interface` | Pluggable token storage. |
| `TokenManager` | `interface` | Token manager interface. |
| `LoginFlowEvent` | `type` | Login flow state events. |
| `DEFAULT_SUCCESS_REDIRECT` | `const` | Default browser-login success redirect URL. |
| `client` | `const` | Pre-created singleton `Matilda` instance (using default config). |

### Re-exported types

From `@matilda/api-client`:

| Type | Description |
|---|---|
| `MatildaCore` | `class` | The underlying HTTP client that powers all resource groups. |
| `configureClient` | `function` | Configure a shared client instance. |
| `fetchPublicRuntimeConfig` | `function` | Fetch runtime config from the server. |
| `getClientConfig` | `function` | Get the current shared client config. |
| `trustApiBaseUrl` | `function` | Validate and brand a URL as trusted. |
| `ClientConfig` | Base client configuration. |
| `RequestOptions` | Base request options (fingerprint, accessToken). |
| `ChatResponseMode` | `'auto' \| 'instant' \| 'deep'`. |
| `ChatErrorCode` | Chat error code union. |
| `GetToken` | Token provider function type. |
| `TrustedApiBaseUrl` | Branded trusted URL type. |
| `TrustedApiBaseUrlPolicy` | URL validation policy. |
| `PublicConfigEndpoint` | Public config endpoint union. |
| `PublicRuntimeConfig` | Runtime config from server. |

From `@matilda/shared-types`:

| Type | Description |
|---|---|
| `ApiMessage` | Wire-format message (`{ role, content }`). |
| `ChatMessage` | Domain message with full metadata. |
| `ConversationSummary` | Conversation list item. |
| `ConversationListResponse` | Paginated conversation list. |
| `ConversationRecord` | Full conversation with messages. |
| `FileAttachment` | File metadata. |
| `FileCompleteResponse` | Upload completion response. |
| `PushDevice` | Push notification device. |
| `UsageEvent` | Token usage event. |
| `ActiveStreamLookup` | Active stream check result. |

### Deprecated exports

| Export | Description |
|---|---|
| `PkceLoginOptions` | Use `BrowserLoginOptions` instead. |
| `DeviceFlowOptions` | Use `DeviceLoginOptions` instead. |

---

*Built and maintained by [Maincode](https://maincode.com.au) — Australia's sovereign AI company.*
