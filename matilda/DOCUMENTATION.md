# @maincode-ai/matilda-agent-sdk

**Version 0.1.0**

A TypeScript SDK for building agentic applications on Matilda. Provides agent abstractions, client-side tool execution, multi-turn sessions, automatic retry with exponential backoff, DSML tool-call interception, and durable stream resume — all on top of the Matilda-native chat contract.

The agent SDK wraps the [client SDK](../client-sdk/DOCUMENTATION.md) and adds:

- **Agent** — a named, configurable persona with dynamic instructions and purpose-based routing
- **Runner** — runs agent turns with streaming, retry, and a client-side tool execution loop
- **Session** — multi-turn conversations with auto-managed `conversationId` and turn accumulation
- **Client tools** — register handlers the agent can invoke mid-turn; the SDK handles the roundtrip loop
- **DSML interception** — tool calls emitted as text tokens (`<｜DSML｜tool_call>`) are automatically captured and surfaced as native tool events
- **Durable stream resume** — reconnect to a detached stream from the last cursor

Agent runs send `persist: false` by default — conversations do not appear in the Matilda web app's chat history.

## What's included

- **Agent** — named persona with static or dynamic instructions, purpose-based routing
- **Runner** — `run()`, `stream()`, `streamText()`, `runText()`, `runObject()`, `streamObject()` with retry and tool execution
- **Session** — multi-turn conversations with automatic `conversationId` reuse
- **Client tools** — `ToolHandlers` with automatic roundtrip loop and advertised-tool guard
- **Files** — upload (single and parallel), retrieve metadata
- **Conversations** — list, retrieve, rename, and set message feedback
- **Auth** — managed PKCE browser login, RFC 8628 device flow, token restore, persistent token storage

## What's NOT included

- **Server-side tool execution** — server-side tools (web search, code execution, etc.) are handled by Matilda core. The agent SDK's tool loop is for client-side tools only.
- **Model/provider selection** — Matilda core owns routing, safety, and policy.

---

## Table of Contents

1. [Installation](#1-installation)
2. [Quick Start](#2-quick-start)
3. [Configuration](#3-configuration)
4. [Authentication](#4-authentication)
5. [Agent](#5-agent)
6. [Runner — Run (Non-Streaming)](#6-runner--run-non-streaming)
7. [Runner — Stream (Full Events)](#7-runner--stream-full-events)
8. [Runner — Text Helpers](#8-runner--text-helpers)
9. [Runner — Structured Output](#9-runner--structured-output)
10. [Client Tools](#10-client-tools)
11. [Session (Multi-Turn)](#11-session-multi-turn)
12. [Stream Resume](#12-stream-resume)
13. [Files](#13-files)
14. [Conversations](#14-conversations)
15. [Error Handling](#15-error-handling)
16. [Multi-Agent Patterns](#16-multi-agent-patterns)
17. [Suggested Tasks / Recipes](#17-suggested-tasks--recipes)
18. [Exports Reference](#18-exports-reference)

---

## 1. Installation

```sh
npm install @maincode-ai/matilda-agent-sdk
# or: pnpm add @maincode-ai/matilda-agent-sdk
# or: yarn add @maincode-ai/matilda-agent-sdk
```

Requires Node.js ≥ 20.

`zod` (v3.25+) is a required peer dependency — install it alongside the SDK. It is used by the structured-output helpers ([§9](#9-runner--structured-output)):

```sh
npm install zod
```

### ESM import

```ts
import { Agent, Runner, run, stream } from '@maincode-ai/matilda-agent-sdk';
```

### CommonJS require

```ts
const { Agent, Runner, run, stream } = require('@maincode-ai/matilda-agent-sdk');
```

---

## 2. Quick Start

### Minimal: run a single agent turn

```ts
import { run } from '@maincode-ai/matilda-agent-sdk';

const result = await run(
  { name: 'greeter', instructions: 'Be friendly and concise.' },
  'Say hello in three languages.',
);

console.log(result.finalOutput);
console.log(result.usage);
```

### Minimal: streaming

```ts
import { stream } from '@maincode-ai/matilda-agent-sdk';

for await (const event of stream(
  { name: 'storyteller', instructions: 'Write a short sci-fi haiku.' },
  'Write about a Dyson sphere.',
)) {
  if (event.type === 'message.delta') {
    process.stdout.write(event.delta);
  }
  if (event.type === 'done') {
    console.log('\n[done]');
  }
}
```

### Authenticated: device flow + run

```ts
import { Runner } from '@maincode-ai/matilda-agent-sdk';
import { MatildaCore } from '@maincode-ai/matilda-agent-sdk';

const runner = new Runner({
  core: new MatildaCore({ baseUrl: 'https://matilda.maincode.com/api' }),
});

// Authenticate via RFC 8628 device flow — prints a code to stderr
if (!(await runner.auth.getTokens())) {
  await runner.auth.loginWithDeviceFlow({ clientId: 'matilda-code' });
}

// Token is now managed automatically — refresh on 401 comes for free
const result = await runner.run(
  { name: 'helper', instructions: 'Be concise.' },
  'What is the capital of Australia?',
);
console.log(result.finalOutput);
```

---

## 3. Configuration

### `configureClient(options)`

Configures the default `MatildaCore` singleton used by `defaultRunner` and the convenience functions (`run`, `stream`, `streamText`, `runText`). Returns nothing.

```ts
import { configureClient } from '@maincode-ai/matilda-agent-sdk';

configureClient({
  baseUrl: 'https://matilda.maincode.com/api',
  getToken: async () => myAccessToken,
});
```

#### Options

Extends `ClientConfig`. All fields are optional except `baseUrl`.

| Field | Type | Default | Description |
|---|---|---|---|
| `baseUrl` | `string` | `'/api'` | The Matilda API base URL. Must be absolute for auth flows. |
| `accessToken` | `string` | — | A static access token. Use for quick testing only — prefer managed auth. |
| `getToken` | `GetToken` | — | Dynamic token provider. Called on every request. The SDK's `TokenManager` implements this. |
| `apiVersion` | `string \| null` | — | API version sent via the `X-Matilda-API-Version` header. Omit to use the current version. |
| `urlPolicy` | `TrustedApiBaseUrlPolicy` | — | URL validation policy for `trustApiBaseUrl()`. |
| `getCsrfToken` | `() => string \| null` | — | CSRF token provider for web BFF cookie auth. |

### `MatildaCore`

The underlying API client. The agent SDK re-exports it from `@matilda/api-client`. Each `Runner` can hold its own `MatildaCore` instance for isolation, or share the process-wide default.

```ts
import { MatildaCore, Runner } from '@maincode-ai/matilda-agent-sdk';

const core = new MatildaCore({
  baseUrl: 'https://matilda.maincode.com/api',
  accessToken: process.env.MATILDA_ACCESS_TOKEN!,
});

const runner = new Runner({ core });
```

### `Runner`

The main agent execution class. Optionally accepts an explicit `MatildaCore` for isolation.

```ts
import { Runner, MatildaCore } from '@maincode-ai/matilda-agent-sdk';

// Uses the default core singleton (configured via configureClient)
const defaultRunner = new Runner();

// Uses an isolated core — independent config, auth, and token lifecycle
const isolatedRunner = new Runner({
  core: new MatildaCore({ baseUrl: 'https://matilda.maincode.com/api' }),
});
```

| Constructor field | Type | Description |
|---|---|---|
| `core` | `MatildaCore` | Optional explicit core. If omitted, the default singleton is used. |

### Environment URLs

| Environment | Base URL |
|---|---|
| Production | `https://matilda.maincode.com/api` |

### Instance isolation

Each `Runner` holds its own `MatildaCore` (either explicit or the default singleton). Resources (`auth`, `files`, `conversations`) resolve their core lazily, so `configureClient()` replacing the default singleton is picked up correctly.

```ts
import { Runner, MatildaCore, configureClient } from '@maincode-ai/matilda-agent-sdk';

const runnerA = new Runner({
  core: new MatildaCore({ baseUrl: 'https://matilda.maincode.com/api' }),
});
const runnerB = new Runner({
  core: new MatildaCore({ baseUrl: 'https://matilda.maincode.com/api' }),
});

// Each runner is fully isolated — independent auth, config, and token lifecycle
await runnerA.auth.loginWithDeviceFlow({ clientId: 'matilda-code' });
await runnerB.auth.loginWithBrowser({ clientId: 'matilda-code' });
```

### Other re-exported configuration utilities

| Export | Description |
|---|---|
| `configureClient(options)` | Configure the default `MatildaCore` singleton. |
| `getClientConfig()` | Get the current default core's config. |
| `getDefaultCore()` | Get the default `MatildaCore` singleton. |
| `trustApiBaseUrl(rawUrl, policy?)` | Validate and brand a URL as a trusted API base URL. |
| `MATILDA_API_VERSION_HEADER` | The API version header name. |
| `MATILDA_CURRENT_API_VERSION` | The current API version string. |

---

## 4. Authentication

The agent SDK provides `AgentAuth` — a managed auth tier that wraps the client SDK's `TokenManager`. On successful login, a `TokenManager` is auto-configured on the runner's `MatildaCore`. Every subsequent request automatically carries a managed access token with single-flight, skew-aware auto-refresh.

### OAuth client ID

The agent SDK uses the `matilda-code` OAuth client ID, which supports both PKCE browser login and RFC 8628 device flow. All examples in this documentation use `matilda-code`.

### API keys

Agents can also authenticate with an `mc_live_` API key instead of OAuth — useful for CI and server-side deployments where there's no browser. Keys are minted with the client SDK's `matilda-key` CLI (social-login friendly — no code required):

```sh
npx matilda-key create-api-key --name "my-agent"
# mints an mc_live_… key after device-flow sign-in; see the client SDK docs for flags
```

Then supply it as a static access token:

```ts
configureClient({
  baseUrl: 'https://matilda.maincode.com/api',
  accessToken: process.env.MATILDA_API_KEY,
});
```

### `runner.auth.loginWithBrowser(opts)`

Managed PKCE browser login (RFC 8252 loopback). Starts a temporary local server, opens the browser, receives the auth code, exchanges it for tokens, and auto-wires a `TokenManager` on the runner's core.

```ts
const tokens = await runner.auth.loginWithBrowser({
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
| `identityProviderId` | `string` | — | Route straight to a federated IdP (e.g. Google SSO). |
| `callbackPort` | `number` | random ephemeral | Fixed loopback port. |
| `timeoutMs` | `number` | `300_000` (5 min) | How long to wait for the browser callback. |
| `openBrowser` | `(url: string) => void \| Promise<void>` | — | Called with the authorize URL. |
| `successRedirect` | `string` | `'https://matilda.maincode.com/cli/signed-in'` | URL the browser is 302-redirected to on success. |
| `errorRedirect` | `string` | — | URL for the error case. |
| `fetchImpl` | `typeof fetch` | `global fetch` | Override fetch. |
| `tokenStore` | `StorageAdapter` | `memoryStorage()` | Custom token persistence. |
| `tokenLock` | `<T>(fn: () => Promise<T>) => Promise<T>` | — | Cross-process critical-section lock for token refresh. |
| `onEvent` | `(e: LoginFlowEvent) => void` | — | Subscribe to login flow state events. |

Returns `Promise<TokenSet>`.

### `runner.auth.loginWithDeviceFlow(opts)`

Managed RFC 8628 device flow. Requests a device code, prints the user code and verification URL to stderr (by default), and polls until the user authorises.

```ts
const tokens = await runner.auth.loginWithDeviceFlow({
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
| `onEvent` | `(e: LoginFlowEvent) => void` | `defaultDeviceOnEvent` | Subscribe to login flow events. |

Returns `Promise<TokenSet>`.

### `runner.auth.restore(opts)`

Adopts tokens that were already persisted (e.g. by `createFileTokenStore`) without repeating the interactive login. Returns `null` when the store holds nothing usable, so a caller can fall back to `loginWith*`.

```ts
import { createFileTokenStore } from '@maincode-ai/matilda-agent-sdk';
import { homedir } from 'node:os';
import { join } from 'node:path';

const { store, lock } = createFileTokenStore(join(homedir(), '.matilda', 'tokens.json'));

const tokens = await runner.auth.restore({
  clientId: 'matilda-code',
  tokenStore: store,
  tokenLock: lock,
});

if (!tokens) {
  // No persisted tokens — fall back to interactive login
  await runner.auth.loginWithDeviceFlow({
    clientId: 'matilda-code',
    tokenStore: store,
    tokenLock: lock,
  });
}
```

#### Parameters

| Field | Type | Description |
|---|---|---|
| `clientId` | `string` | OAuth client alias. |
| `tokenStore` | `StorageAdapter` | Token persistence adapter. |
| `tokenLock` | `<T>(fn: () => Promise<T>) => Promise<T>` | Cross-process lock. |
| `fetchImpl` | `typeof fetch` | Override fetch. |
| `metadata` | `AuthServerMetadata` | Pre-fetched server metadata (skips discovery). |

Returns `Promise<TokenSet | null>`.

### `runner.auth.getTokens()`

Returns the current token set from the managed `TokenManager`, or `null` if not authenticated.

```ts
const tokens = await runner.auth.getTokens();
if (tokens) {
  console.log(`Token expires at: ${new Date(tokens.expiresAt).toISOString()}`);
}
```

Returns `Promise<TokenSet | null>`.

### `runner.auth.logout()`

Clears the token store, destroys the `TokenManager`, and restores the core's previous `getToken` provider (important when the core is the shared default singleton).

```ts
await runner.auth.logout();
```

Returns `Promise<void>`.

### Token persistence

By default, tokens are stored in memory (`memoryStorage()`). For cross-process persistence (e.g. CLI sessions), use `createFileTokenStore`:

```ts
import { Runner, MatildaCore, createFileTokenStore } from '@maincode-ai/matilda-agent-sdk';
import { homedir } from 'node:os';
import { join } from 'node:path';

const tokenPath = join(homedir(), '.matilda', 'tokens.json');
const { store, lock } = createFileTokenStore(tokenPath);

const runner = new Runner({
  core: new MatildaCore({ baseUrl: 'https://matilda.maincode.com/api' }),
});

await runner.auth.loginWithBrowser({
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

### `TokenManager` interface

```ts
interface TokenManager {
  getAccessToken(opts?: { forceRefresh?: boolean }): Promise<string>;
  getTokens(): Promise<TokenSet | null>;
  setTokens(tokens: TokenSet): Promise<void>;
  clear(): Promise<void>;
}
```

### `TokenSet` interface

```ts
interface TokenSet {
  accessToken: string;
  refreshToken?: string;
  idToken?: string;
  expiresAt: number;  // epoch milliseconds
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

---

## 5. Agent

An `Agent` is a named, immutable persona with optional instructions, context, purpose, and metadata. You can pass a plain `AgentOptions` object anywhere an `Agent` is accepted — the SDK normalises it.

### `Agent` class

```ts
import { Agent } from '@maincode-ai/matilda-agent-sdk';

const reviewer = new Agent({
  name: 'code-reviewer',
  purpose: 'code',
  instructions: 'Review code for correctness, security, and readability.',
  context: 'Project: matilda-core\nLanguage: TypeScript',
  metadata: { team: 'platform' },
});
```

The `Agent` class is immutable and reusable — construct once, run many times.

#### `AgentOptions`

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | `string` | **(required)** | Agent name. Must be non-empty. |
| `instructions` | `AgentInstructions` | — | Static string or dynamic function (see below). |
| `context` | `string` | — | Additional context appended to instructions under a `Context:` header. |
| `purpose` | `AgentPurpose` | `'code'` | Controls the default `responseMode` and how the server routes the request. |
| `responseMode` | `ChatResponseMode` | — | Override the response mode. If omitted, derived from `purpose`. |
| `metadata` | `Record<string, unknown>` | `{}` | Custom data available to dynamic instructions. Frozen on construction. |

### `AgentPurpose`

```ts
type AgentPurpose = 'code' | 'analysis' | 'general';
```

| Purpose | `responseMode` default |
|---|---|
| `'code'` | `'auto'` |
| `'analysis'` | `'deep'` |
| `'general'` | `'auto'` |

### Dynamic instructions

Instructions can be a function that receives runtime context, letting you customise behaviour per-call:

```ts
const agent = new Agent({
  name: 'code-reviewer',
  purpose: 'code',
  instructions: ({ input, metadata }) => {
    const lang = (metadata.language as string) ?? 'auto-detect';
    const strictness = (metadata.strictness as string) ?? 'normal';
    return [
      'Review the following code.',
      `Language: ${lang}`,
      `Strictness: ${strictness}`,
      'Focus on: correctness, security, and readability.',
    ].join('\n');
  },
});

const result = await run(agent, 'function add(a, b) { return a + b }', {
  metadata: { language: 'JavaScript', strictness: 'strict' },
});
```

#### `AgentInstructions`

```ts
type AgentInstructions =
  | string
  | ((context: AgentRunContext) => string | Promise<string>);
```

#### `AgentRunContext`

```ts
interface AgentRunContext {
  agentName: string;
  input: string;
  purpose: AgentPurpose;
  metadata: Readonly<Record<string, unknown>>;
}
```

### How agent messages are constructed

The SDK packs the agent's identity, instructions, context, and the user's prompt into a single user message with labelled sections:

```
Agent: code-reviewer

Instructions:
Review the following code.
Language: JavaScript
...

Context:
Project: matilda-core

Code task:
function add(a, b) { return a + b }
```

### `buildAgentChatRequest(opts)`

Low-level builder that constructs the `ChatRequest` object without executing it. Useful for testing, logging, or custom execution paths.

```ts
import { buildAgentChatRequest } from '@maincode-ai/matilda-agent-sdk';

const request = await buildAgentChatRequest({
  prompt: 'Fix the failing test',
  agent: { name: 'helper', purpose: 'code' },
  instructions: 'Be specific.',
  context: 'Project root: /repo',
  conversationId: 'conv-1',
  fileIds: ['file-1'],
  clientTools: [{ name: 'read_file', description: 'Read a file', parameters: { type: 'object' } }],
});

// request.messages, request.responseMode, request.conversation_id, etc.
```

#### `BuildAgentChatRequestOptions`

| Field | Type | Description |
|---|---|---|
| `prompt` | `string` | The user's message. Required. |
| `purpose` | `AgentPurpose` | Fallback purpose if agent doesn't specify one. |
| `agent` | `Agent \| AgentOptions` | Optional agent to use. Defaults to a generic agent. |
| `instructions` | `AgentInstructions` | Override the agent's instructions. |
| `context` | `string` | Override the agent's context. |
| `metadata` | `Record<string, unknown>` | Merge with agent's metadata. |
| `conversationId` | `string` | Associate with a conversation thread. |
| `fileIds` | `string[]` | File IDs to attach. |
| `clientTools` | `ClientTool[]` | Client tools to advertise. |
| `responseMode` | `ChatResponseMode` | Override response mode. |

Returns `Promise<ChatRequest>`.

---

## 6. Runner — Run (Non-Streaming)

### `runner.run(agent, input, options?)`

Runs an agent turn and returns the complete result. Internally streams and collects all events.

```ts
import { Runner } from '@maincode-ai/matilda-agent-sdk';

const runner = new Runner();

const result = await runner.run(
  { name: 'helper', instructions: 'Be concise.' },
  'What is the capital of Australia?',
  {
    conversationId: 'conv-123',
    responseMode: 'instant',
    callbacks: {
      onToken: (delta) => process.stdout.write(delta),
      onDone: () => console.log('\n[done]'),
    },
  },
);

console.log(result.finalOutput);
console.log(result.usage);
```

### `AgentRunOptions`

Extends `RequestOptions`. All fields optional.

| Field | Type | Default | Description |
|---|---|---|---|
| `signal` | `AbortSignal` | — | Abort the run. |
| `conversationId` | `string` | auto-generated | Associates this turn with a conversation thread. |
| `fileIds` | `string[]` | — | File IDs to attach (from `files.upload()`). |
| `clientTools` | `ClientTool[]` | — | Client tools to advertise for this turn. |
| `context` | `string` | — | Override the agent's context. |
| `responseMode` | `ChatResponseMode` | — | Override the response mode. |
| `responseSchema` | `string` | — | Raw JSON Schema (as a string) to grammar-constrain the response to. Prefer `runner.runObject` / `runner.streamObject`, which convert a zod schema for you (see [§9](#9-runner--structured-output)). |
| `stallTimeoutMs` | `number` | `45_000` | SSE stall watchdog timeout in ms. Pass `0` to disable. |
| `metadata` | `Record<string, unknown>` | — | Custom data available to dynamic instructions. |
| `toolHandlers` | `ToolHandlers` | — | Handlers for client tools (see [§10](#10-client-tools)). |
| `maxToolRoundtrips` | `number` | `25` | Maximum tool roundtrip cycles before stopping. |
| `maxRetries` | `number` | `0` | Maximum retries on retryable errors (5xx, 429, 408, network). |
| `throwOnStreamError` | `boolean` | `true` | Throw `MatildaAgentStreamError` if the stream emits an error event. |
| `callbacks` | `AgentCallbacks` | — | Callback hooks for events (see below). |
| `core` | `MatildaCore` | — | Override the runner's core for this run. |
| `fingerprint` | `string` | — | Device fingerprint for rate limiting. |
| `accessToken` | `string` | — | Override the core-level access token for this request. |

### `AgentCallbacks`

Simple callback hooks that fire as events arrive. An alternative to manually iterating `stream()`.

```ts
const result = await runner.run(agent, input, {
  callbacks: {
    onToken: (delta) => process.stdout.write(delta),
    onToolCall: (name, args) => console.log(`Tool: ${name}`),
    onToolResult: (name, result, isError) => console.log(`Result: ${result}`),
    onUsage: (usage) => console.log(`Tokens: ${usage.output_tokens}`),
    onError: (code, message) => console.error(`Error: ${code}`),
    onRetry: (attempt, error, delayMs) => console.log(`Retry ${attempt} in ${delayMs}ms`),
    onDone: () => console.log('Done'),
  },
});
```

| Callback | Signature | Fires when |
|---|---|---|
| `onEvent` | `(event: AgentRunEvent) => void` | Every event — catch-all, fires before the typed hooks below. Useful for telemetry, UI plumbing, or event logging. |
| `onToken` | `(delta: string) => void` | A text chunk arrives. |
| `onToolCall` | `(name: string, args: Record<string, unknown>) => void` | The agent calls a client tool. |
| `onToolResult` | `(name: string, result: string, isError: boolean) => void` | A client tool handler returns. |
| `onUsage` | `(usage: UsageEvent) => void` | Token usage data arrives. |
| `onError` | `(code: ChatErrorCode, message: string) => void` | A stream error occurs. |
| `onRetry` | `(attempt: number, error: { code: string; message: string }, delayMs: number) => void` | A retryable error triggers a retry. |
| `onDone` | `() => void` | The stream finishes. Fires per-turn in multi-turn tool loops. |

### `AgentRunResult`

| Field | Type | Description |
|---|---|---|
| `agentName` | `string` | The agent's name. |
| `finalOutput` | `string` | The full assistant response text. Accumulated from `message.delta` events. |
| `events` | `AgentRunEvent[]` | Every event emitted during the run. |
| `streamId` | `string \| undefined` | Durable stream ID (from `stream.started` event). |
| `lastEventId` | `string \| undefined` | Last stream event ID (for resume). |
| `usage` | `UsageEvent \| undefined` | Token usage. Accumulated across multi-roundtrip runs. |
| `errors` | `Array<{ code: ChatErrorCode; message: string }>` | Any errors emitted during the run. |
| `truncatedReason` | `string \| undefined` | Why the response was truncated (e.g. `'max_tokens'`, `'max_tool_roundtrips'`). |
| `safetyReplace` | `{ message: string; categories: string[] } \| undefined` | Set when the backend replaced the answer for safety. `finalOutput` holds the replacement text. |

### `throwOnStreamError: false`

By default, `run()` throws `MatildaAgentStreamError` if the stream emits an error event. Pass `throwOnStreamError: false` to suppress the throw and inspect errors on the returned result instead:

```ts
const result = await runner.run(agent, input, { throwOnStreamError: false });

if (result.errors.length > 0) {
  for (const err of result.errors) {
    console.log(`${err.code}: ${err.message}`);
  }
}
console.log('Partial output:', result.finalOutput || '(none)');
```

---

## 7. Runner — Stream (Full Events)

### `runner.stream(agent, input, options?)`

Returns an async generator that yields `AgentRunEvent` objects as they arrive. This is the full event stream — tool calls, usage, status changes, safety replacements, and more.

```ts
for await (const event of runner.stream(
  { name: 'explainer', instructions: 'Explain quantum computing.' },
  'What is quantum entanglement?',
)) {
  switch (event.type) {
    case 'run.started':
      console.log(`Agent "${event.agentName}" started.`);
      break;
    case 'stream.started':
      console.log(`Stream ${event.streamId} connected.`);
      break;
    case 'message.delta':
      process.stdout.write(event.delta);
      break;
    case 'client.tool.requested':
      console.log(`\nTool requested: ${event.name}`);
      break;
    case 'client.tool.result':
      console.log(`Tool result: ${event.result}`);
      break;
    case 'usage':
      console.log(`\nTokens: ${event.usage.output_tokens}`);
      break;
    case 'done':
      console.log('\n[done]');
      break;
    case 'error':
      console.error(`Error: ${event.code} — ${event.message}`);
      break;
  }
}
```

### `AgentRunEvent`

A discriminated union of 22 event types:

#### `run.started`

Emitted once at the start of a run with the agent's name.

```ts
{ type: 'run.started'; agentName: string }
```

#### `stream.started`

Emitted once when the SSE stream connects, with the durable stream ID.

```ts
{ type: 'stream.started'; streamId: string }
```

#### `message.delta`

A text chunk from the assistant.

```ts
{ type: 'message.delta'; delta: string }
```

#### `status.changed`

Stream lifecycle status change.

```ts
{ type: 'status.changed'; status: 'thinking' | 'streaming' | 'queued' | 'idle' | 'done' | 'error' | string }
```

#### `queue.status`

Queue position update while waiting for a free slot.

```ts
{ type: 'queue.status'; state: string; position: number; estimatedWaitSeconds: number }
```

#### `tool.started`

A server-side tool invocation began.

```ts
{ type: 'tool.started'; tool: string; inputOrArgs?: string | Record<string, unknown>; output?: string }
```

#### `tool.progress`

Progress update from a running server-side tool.

```ts
{ type: 'tool.progress'; tool: string; message: string }
```

#### `tool.completed`

A server-side tool invocation finished.

```ts
{ type: 'tool.completed'; tool: string; status: 'success' | 'error'; input?: string; output?: string }
```

#### `client.tool.requested`

The agent called a client tool. The SDK will execute the matching handler from `toolHandlers`.

```ts
{ type: 'client.tool.requested'; id?: string; name: string; args: Record<string, unknown> }
```

#### `client.tool.executing`

The SDK is about to execute the handler for a requested client tool.

```ts
{ type: 'client.tool.executing'; id?: string; name: string; args: Record<string, unknown> }
```

#### `client.tool.result`

A client tool handler returned a result.

```ts
{ type: 'client.tool.result'; id?: string; name: string; result: string; isError: boolean }
```

#### `client.tool.roundtrip`

Emitted after each tool roundtrip cycle, showing progress against the maximum.

```ts
{ type: 'client.tool.roundtrip'; turn: number; maxTurns: number }
```

#### `turn.retrying`

A retryable error occurred and the turn is being retried.

```ts
{ type: 'turn.retrying'; attempt: number; maxRetries: number; error: { code: string; message: string }; delayMs: number }
```

#### `generation.status`

Generation phase update.

```ts
{ type: 'generation.status'; phase: string }
```

#### `safety.replace`

The server replaced the output via a safety filter. `message` holds the replacement text; `categories` lists the safety categories.

```ts
{ type: 'safety.replace'; message?: string; categories: string[] }
```

#### `usage`

Token usage data for the turn.

```ts
{ type: 'usage'; usage: UsageEvent }
```

Where `UsageEvent` is:

```ts
interface UsageEvent {
  output_tokens: number;
  context_pct?: number;
  context_messages_trimmed?: number;
  context_budget_tokens?: number;
}
```

#### `cursor`

Durable stream cursor (event ID). Persist this to resume from this point.

```ts
{ type: 'cursor'; lastEventId: string }
```

#### `truncated`

The response was cut short.

```ts
{ type: 'truncated'; reason: string }
```

#### `replace`

A generic replace event from the server.

```ts
{ type: 'replace' }
```

#### `done`

The stream finished successfully.

```ts
{ type: 'done' }
```

#### `error`

An error occurred during the stream.

```ts
{ type: 'error'; code: ChatErrorCode; message: string }
```

---

## 8. Runner — Text Helpers

These helpers filter the event stream to just text — useful when you only need the response text and don't care about tool calls, usage, or status events.

### `runner.streamText(agent, input, options?)`

Returns an async generator that yields raw string deltas. Throws `SafetyReplaceError` when the server replaces the output (safety filter). Throws `Error` on stream errors.

```ts
try {
  for await (const chunk of runner.streamText(
    { name: 'poet', instructions: 'Write a haiku.' },
    'Write about the ocean.',
  )) {
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

### `runner.runText(agent, input, options?)`

Non-streaming convenience that returns just the final output text. Safety replace is handled by throwing `SafetyReplaceError`. Throws if the stream produced any error events.

```ts
const text = await runner.runText(
  { name: 'helper' },
  'What is 2 + 2?',
);
console.log(text); // "4"
```

### `SafetyReplaceError`

```ts
class SafetyReplaceError extends Error {
  readonly categories: string[];
  // message = replacement content (or empty string)
}
```

### Convenience functions

The SDK exports default-runner-backed convenience functions so you don't need to instantiate a `Runner` for simple use cases:

```ts
import { run, stream, streamText, runText } from '@maincode-ai/matilda-agent-sdk';

// These are equivalent to defaultRunner.run(), defaultRunner.stream(), etc.
const result = await run(agent, input, options);
const text = await runText(agent, input, options);

for await (const event of stream(agent, input, options)) { /* ... */ }
for await (const chunk of streamText(agent, input, options)) { /* ... */ }
```

These use the default `MatildaCore` singleton (configured via `configureClient()`). For isolated config or auth, instantiate your own `Runner`.

---

## 9. Runner — Structured Output

Structured output constrains the agent's response to a JSON Schema, server-side (grammar-constrained decoding), and validates it client-side against your zod schema. Pass a zod schema, receive a fully-typed object — no prompt engineering, no brittle JSON extraction.

### `runner.streamObject(agent, input, schema, options?)`

Streams exactly like `runner.stream()` — you receive every `AgentRunEvent` (including tool-loop and usage events) — plus one final event with the parsed, schema-validated object. Options are `AgentRunOptions`.

```ts
import { z } from 'zod';

const review = z.object({
  summary: z.string(),
  issues: z.array(z.object({
    severity: z.enum(['low', 'medium', 'high']),
    description: z.string(),
  })),
});

const reviewer = new Agent({
  name: 'reviewer',
  instructions: 'Review the code the user provides.',
});

for await (const event of runner.streamObject(reviewer, 'Review this function: ...', review)) {
  if (event.type === 'message.delta') process.stdout.write(event.delta);
  if (event.type === 'object') {
    console.log('\nValidated:', event.object); // typed as z.infer<typeof review>
  }
}
```

The final event:

```ts
{ type: 'object'; object: T } // T = z.infer<typeof schema>
```

### `runner.runObject(agent, input, schema, options?)`

Non-streaming convenience. Like `runner.run()`, it honours `callbacks`, `throwOnStreamError`, retries, and the tool loop — and returns an `AgentObjectResult<T>`: the full `AgentRunResult` plus the validated `object`.

```ts
const result = await runner.runObject(
  extractor,
  'Invoice total $1,250.00 AUD due 30 Sep.',
  z.object({ total: z.number(), currency: z.string() }),
);

console.log(result.object.total);    // 1250 (number)
console.log(result.object.currency); // "AUD" (string)
console.log(result.finalOutput);     // raw JSON text as returned
console.log(result.usage);           // token usage, as usual
```

#### `AgentObjectResult<T>`

Extends `AgentRunResult` with one additional field:

| Field | Type | Description |
|---|---|---|
| `object` | `T` | The response text parsed as JSON and validated against your schema. |

### Convenience functions

Default-runner-backed, like the other top-level helpers (`streamObject` / `runObject` use the default `MatildaCore` singleton):

```ts
import { streamObject, runObject } from '@maincode-ai/matilda-agent-sdk';

const result = await runObject(agent, input, schema, options);
for await (const event of streamObject(agent, input, schema, options)) { /* ... */ }
```

### Raw JSON Schema via `responseSchema`

`AgentRunOptions` (and therefore `SessionOptions`) accepts a stringified JSON Schema directly on any run or stream:

```ts
const result = await runner.run(agent, 'List three Australian birds.', {
  responseSchema: JSON.stringify({
    type: 'object',
    properties: { birds: { type: 'array', items: { type: 'string' } } },
    required: ['birds'],
    additionalProperties: false,
  }),
});
JSON.parse(result.finalOutput); // guaranteed valid, schema-conforming JSON
```

With `responseSchema` set, `finalOutput` is guaranteed to be valid JSON conforming to the schema — but parsing and validation are up to you.

> **Safety replace and structured output.** Like `runText()` / `streamText()`, the object helpers throw `SafetyReplaceError` when the server replaces the output mid-stream — the replacement text is in `.message` and the triggering categories in `.categories`. Token deltas already yielded to your consumer are not rolled back; `runObject()` is unaffected at the value level, since it throws before returning a result.

> **Truncation throws.** If the stream is truncated before the JSON completes, both helpers throw `MatildaObjectParseError` with the partial text in `.raw`. See [§15. Error Handling](#15-error-handling).

> **Stream errors throw.** If the server emits an `error` event mid-stream, `streamObject()` throws an `Error` with the server's error code and message, and `runObject()` throws `MatildaAgentStreamError` with the partial `result` attached — matching the behaviour of the text helpers.

---

## 10. Client Tools

Client tools are handlers you register that the agent can invoke mid-turn. The SDK handles the entire roundtrip loop: detecting tool calls, executing your handler, feeding the result back to the agent, and repeating until the agent stops calling tools or the roundtrip limit is reached.

### Tool execution loop

```
┌─────────────────────────────────────────────────────────┐
│  Turn 0                                                 │
│  1. Send messages + clientTools to server               │
│  2. Stream events — agent responds, may call tools      │
│  3. If tool calls detected:                             │
│     a. client.tool.requested → client.tool.executing    │
│     b. Execute handler from toolHandlers                │
│     c. client.tool.result                               │
│     d. Append result to messages as a user message      │
│     e. client.tool.roundtrip (turn + 1 / maxTurns)      │
│     f. Go to Turn 1                                     │
│  4. If no tool calls: run is done                       │
│  5. If turn >= maxToolRoundtrips: truncated             │
└─────────────────────────────────────────────────────────┘
```

### Declaring and handling tools

```ts
import { stream, type ToolHandlers } from '@maincode-ai/matilda-agent-sdk';

// 1. Declare the tools so the server knows they exist
const clientTools = [
  { name: 'get_weather', description: 'Get current weather for a city', parameters: { type: 'object' } },
  { name: 'calculate', description: 'Evaluate a math expression', parameters: { type: 'object' } },
];

// 2. Register handlers — the SDK calls these when the agent invokes a tool
const toolHandlers: ToolHandlers = {
  get_weather: async (args) => {
    const city = (args.city as string) ?? 'unknown';
    return { content: JSON.stringify({ city, temp: 22, condition: 'sunny' }) };
  },
  calculate: async (args) => {
    const expr = args.expression as string;
    try {
      const result = Function(`return (${expr})`)();
      return { content: String(result) };
    } catch {
      return { content: 'Invalid expression', isError: true };
    }
  },
};

// 3. Pass both to stream() or run()
for await (const event of stream(
  { name: 'assistant', instructions: 'Use the available tools to answer questions.' },
  'What is the weather in Sydney, and what is 15 * 23?',
  { toolHandlers, clientTools },
)) {
  if (event.type === 'client.tool.requested') {
    console.log(`→ Agent requested: ${event.name}(${JSON.stringify(event.args)})`);
  }
  if (event.type === 'client.tool.executing') {
    console.log(`⚙ Executing: ${event.name}`);
  }
  if (event.type === 'client.tool.result') {
    console.log(`← Result: ${event.result}${event.isError ? ' (error)' : ''}`);
  }
  if (event.type === 'client.tool.roundtrip') {
    console.log(`  Roundtrip ${event.turn}/${event.maxTurns}`);
  }
  if (event.type === 'message.delta') {
    process.stdout.write(event.delta);
  }
}
```

### `ToolHandler`

```ts
type ToolHandler = (
  args: Record<string, unknown>,
  ctx: ToolExecutionContext,
) => Promise<ToolResult>;
```

### `ToolExecutionContext`

```ts
interface ToolExecutionContext {
  toolCallId?: string;
  signal?: AbortSignal;  // The run's AbortSignal, if provided
}
```

### `ToolResult`

```ts
interface ToolResult {
  content: string;
  isError?: boolean;
}
```

### `ToolHandlers`

```ts
type ToolHandlers = Record<string, ToolHandler>;
```

### `maxToolRoundtrips`

Controls how many back-and-forth tool cycles the SDK allows before stopping. Default is `25` (`DEFAULT_MAX_TOOL_ROUNDTRIPS`). Lower it to prevent infinite loops or control cost.

```ts
const result = await runner.run(
  { name: 'tool-heavy-agent', instructions: 'Use tools to gather information.' },
  'Do a task that needs tools',
  {
    maxToolRoundtrips: 5,
    toolHandlers: { search: async () => ({ content: 'search results...' }) },
    clientTools: [{ name: 'search', description: 'Search', parameters: { type: 'object' } }],
  },
);

const roundtrips = result.events.filter((e) => e.type === 'client.tool.roundtrip');
console.log(`Roundtrips used: ${roundtrips.length} (max was 5)`);
```

### Advertised-tool guard

The SDK enforces that the agent can only call tools that were advertised for the current turn. If the model calls a tool that wasn't in `clientTools`, the SDK returns an error result instead of executing a handler:

```
Tool not offered this turn: <name>
```

This prevents a model from talking the runner into invoking a handler that was never offered — tool output is untrusted input.

### DSML tool-call interception

Some models emit tool calls as text tokens wrapped in DSML markup (`<｜DSML｜tool_call>{...}<｜DSML｜/tool_call>`) instead of using native function calling. The SDK automatically intercepts these text tokens, parses the JSON payload, and surfaces them as native `client.tool.requested` events — the consumer never sees the raw markup.

This interception is fully automatic and applies to all streaming paths.

### Human-in-the-loop

The tool execution loop makes human-in-the-loop trivial: a tool handler is just an async function, so it can block on stdin, a UI prompt, or any other input source.

```ts
import * as readline from 'node:readline/promises';

const toolHandlers: ToolHandlers = {
  ask_user: async (args) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    try {
      const answer = await rl.question(`\n  Agent asks: ${args.question}\n  > `);
      return { content: answer.trim() };
    } finally {
      rl.close;
    }
  },
};

const clientTools = [
  { name: 'ask_user', description: 'Ask the user a question', parameters: { type: 'object' } },
];

const result = await runner.run(
  { name: 'clarifier', instructions: 'Ask the user for clarification when needed.' },
  'Help me plan a trip',
  { toolHandlers, clientTools },
);
```

---

## 11. Session (Multi-Turn)

A `Session` wraps an `Agent` with auto-managed `conversationId` and accumulates turn results. The server maintains conversation history server-side using the `conversationId`, so each turn has full context.

### `createSession(agent, options?)`

```ts
import { createSession } from '@maincode-ai/matilda-agent-sdk';

const session = createSession({
  name: 'tutor',
  instructions: 'You are a patient programming tutor. Explain concepts simply.',
});

console.log('Conversation ID:', session.conversationId);

// Turn 1
const r1 = await session.run('What is a closure in JavaScript?');
console.log('Turn 1:', r1.finalOutput.slice(0, 100), '...');

// Turn 2 — the server remembers the previous exchange via conversationId
const r2 = await session.run('Can you show me a simple example?');
console.log('Turn 2:', r2.finalOutput.slice(0, 100), '...');

// The session accumulates all turn results
console.log('Total turns:', session.turns.length);
console.log('Last turn stream ID:', session.lastTurn?.streamId);
```

### `Session` class

#### `session.run(input, options?)`

Runs a turn and accumulates the result in `session.turns`.

| Parameter | Type | Description |
|---|---|---|
| `input` | `string` | The user's message. |
| `options` | `Omit<AgentRunOptions, 'conversationId'>` | Per-turn options. Merged with session defaults. |

Returns `Promise<AgentRunResult>`.

#### `session.stream(input, options?)`

Streams a turn, yielding `AgentRunEvent` as they arrive. The result is accumulated in `session.turns` when the stream completes.

```ts
for await (const event of session.stream('Explain async/await in one paragraph.')) {
  if (event.type === 'message.delta') {
    process.stdout.write(event.delta);
  }
}

console.log('\n[Turns accumulated]:', session.turns.length);
console.log('[Final output cached]:', session.lastTurn?.finalOutput.slice(0, 60), '...');
```

#### `session.conversationId`

The auto-generated (or provided) conversation ID. Reused across all turns.

#### `session.turns`

A readonly array of `AgentRunResult` — one per completed turn.

#### `session.lastTurn`

Getter for the most recent `AgentRunResult`, or `undefined` if no turns have run.

### `SessionOptions`

Extends `Omit<AgentRunOptions, 'conversationId'>`.

| Field | Type | Default | Description |
|---|---|---|---|
| `runner` | `Runner` | `defaultRunner` | Custom runner instance. |
| `conversationId` | `string` | auto-generated | Explicit conversation ID. |
| *(all `AgentRunOptions` fields)* | — | — | Session-level defaults applied to every turn. |

### Metadata passthrough

Metadata can be set at multiple levels: `Agent` construction, `Session` construction, or per-call. Per-call metadata merges with (and overrides) session defaults.

```ts
const session = createSession(
  {
    name: 'helper',
    instructions: ({ metadata }) =>
      `Environment: ${metadata.env ?? 'unknown'}. User: ${metadata.user ?? 'anonymous'}.`,
  },
  { metadata: { env: 'staging', user: 'demo-user' } },
);

// Session-level metadata is used by default
await session.run('Who am I?');

// Per-call metadata overrides session defaults
await session.run('Who am I now?', { metadata: { user: 'admin' } });
// → env=staging (from session), user=admin (overridden per-call)
```

### Custom runner

A `Session` can use a custom `Runner` for dependency injection in tests or isolated configuration:

```ts
import { Runner, Session } from '@maincode-ai/matilda-agent-sdk';

const myRunner = new Runner();
const session = new Session(
  { name: 'custom-runner-agent', instructions: 'Be brief.' },
  { runner: myRunner },
);

const result = await session.run('What is 2 + 2?');
```

---

## 12. Stream Resume

Durable streaming lets a client disconnect mid-stream and resume from where it left off. The server buffers events, keyed by a `streamId` advertised at stream start.

### `resumeAgentStream(streamId, lastEventId, handlers, options?)`

Resumes a previously detached stream by replaying buffered events from `lastEventId`. Returns the accumulated `AgentRunResult`.

```ts
import { resumeAgentStream, type AgentRunEvent } from '@maincode-ai/matilda-agent-sdk';

const result = await resumeAgentStream(
  savedStreamId,
  savedLastEventId,
  {
    onEvent: (event: AgentRunEvent) => {
      if (event.type === 'message.delta') process.stdout.write(event.delta);
    },
  },
);
console.log('Resumed output:', result.finalOutput);
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `streamId` | `string` | The stream ID from `stream.started` event (or `result.streamId`). |
| `lastEventId` | `string \| undefined` | The last cursor received (from `cursor` event or `result.lastEventId`). Omit to replay from the start. |
| `handlers` | `{ onEvent?: (event: AgentRunEvent) => void }` | Event handler callback. |
| `options` | `RequestOptions & { signal?: AbortSignal; core?: MatildaCore }` | Request options. |

Returns `Promise<AgentRunResult>`.

### 401 auto-refresh

If the resume request returns 401 and the core has a `getToken` provider, the SDK automatically refreshes the token and retries once.

### Full resume example

```ts
import { stream, resumeAgentStream } from '@maincode-ai/matilda-agent-sdk';

let streamId: string | undefined;
let lastEventId: string | undefined;
let receivedText = '';

// Start streaming — capture IDs for potential resume
for await (const event of stream({ name: 'resumable-agent' }, 'Tell me a fact.')) {
  if (event.type === 'stream.started') streamId = event.streamId;
  if (event.type === 'cursor') lastEventId = event.lastEventId;
  if (event.type === 'message.delta') {
    receivedText += event.delta;
    process.stdout.write(event.delta);
  }
}

console.log('\n[Stream completed — streamId:', streamId, 'cursor:', lastEventId, ']');

// Later — resume from the last cursor if the stream was interrupted
if (streamId) {
  const result = await resumeAgentStream(streamId, lastEventId, {
    onEvent: (event) => {
      if (event.type === 'message.delta') process.stdout.write(event.delta);
    },
  });
  console.log('\n[Resumed — output:', result.finalOutput.slice(0, 60), '...]');
}
```

---

## 13. Files

The `Runner` exposes a `files` resource for uploading and retrieving files. Uploaded files can be attached to agent runs via `fileIds`.

### `runner.files.upload(file, options?)`

Uploads a single file. Files at or above the server's chunked threshold use the parallel multipart protocol; smaller files use single-shot upload.

```ts
const file = new File(['Hello, world!'], 'hello.txt', { type: 'text/plain' });
const result = await runner.files.upload(file, {
  onProgress: (pct) => console.log(`Upload: ${pct}%`),
});
console.log(`File ID: ${result.fileId}, Status: ${result.status}`);
```

#### `FileUploadOptions`

Extends `RequestOptions`. All fields optional.

| Field | Type | Description |
|---|---|---|
| `onProgress` | `(pct: number) => void` | Progress callback (0–100). |
| `signal` | `AbortSignal` | Abort the upload. |
| `fingerprint` | `string \| null` | Device fingerprint. |
| `accessToken` | `string \| null` | Override access token. |

Returns `Promise<FileCompleteResponse>`:

```ts
interface FileCompleteResponse {
  fileId: string;
  status: FileAttachmentStatus;
  failureReason?: FileFailureReason;
}

type FileAttachmentStatus = 'pending' | 'scanning' | 'processing' | 'ready' | 'failed' | 'rejected';
```

### `runner.files.uploadMany(files, options?)`

Uploads multiple files in parallel. One file's failure does not abort the others.

```ts
const files = [
  new File(['doc 1'], 'doc1.txt', { type: 'text/plain' }),
  new File(['doc 2'], 'doc2.txt', { type: 'text/plain' }),
];

const results = await runner.files.uploadMany(files);
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

### `runner.files.retrieve(fileId, options?)`

Retrieves metadata for a previously uploaded file.

```ts
const file = await runner.files.retrieve('file-abc123');
console.log(`${file.filename} — ${file.status} (${file.sizeBytes} bytes)`);
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
```

### Using files in agent runs

Upload a file, then reference its `fileId` in an agent run:

```ts
const fileResult = await runner.files.upload(
  new File(['Quarterly report content...'], 'report.txt', { type: 'text/plain' }),
);

const result = await runner.run(
  { name: 'analyst', purpose: 'analysis', instructions: 'Summarise the report.' },
  'What are the key findings?',
  { fileIds: [fileResult.fileId] },
);
console.log(result.finalOutput);
```

---

## 14. Conversations

The `Runner` exposes a `conversations` resource for listing, retrieving, renaming, and providing feedback on conversations.

> **Note:** Agent runs send `persist: false` by default, so they do not appear in the Matilda web app's chat history. The conversations resource accesses conversations created by other clients (e.g. the web app). If you need agent runs to appear in chat history, you would need to override the `persist` flag — but this is not exposed as a public option in the agent SDK.

### `runner.conversations.list(options?)`

Lists conversations with pagination.

```ts
const result = await runner.conversations.list({ limit: 20, offset: 0 });
for (const conv of result.conversations) {
  console.log(`${conv.id}: ${conv.title} (updated ${conv.updatedAt})`);
}
```

| Parameter | Type | Description |
|---|---|---|
| `limit` | `number` | Maximum number of conversations to return. |
| `offset` | `number` | Pagination offset. |

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

### `runner.conversations.retrieve(conversationId, options?)`

Retrieves a full conversation thread with all messages.

```ts
const conv = await runner.conversations.retrieve('conv-123');
for (const msg of conv.messages) {
  console.log(`[${msg.role}] ${msg.content}`);
}
```

Returns `Promise<ConversationRecord>`:

```ts
interface ConversationRecord extends ConversationSummary {
  messages: ConversationMessage[];
}
```

### `runner.conversations.update(conversationId, patch, options?)`

Updates a conversation's metadata (currently only title).

```ts
await runner.conversations.update('conv-123', { title: 'My Chat About AI' });
```

Returns `Promise<void>`.

### `runner.conversations.setMessageFeedback(conversationId, messageId, feedback, options?)`

Sets thumbs-up or thumbs-down feedback on a specific message.

```ts
await runner.conversations.setMessageFeedback('conv-123', 'msg-456', 'positive');
```

| Parameter | Type | Description |
|---|---|---|
| `conversationId` | `string` | The conversation containing the message. |
| `messageId` | `string` | The message to rate. |
| `feedback` | `'positive' \| 'negative'` | The feedback value. |

Returns `Promise<{ ok: boolean }>`.

---

## 15. Error Handling

### `MatildaAgentRunError`

Thrown on HTTP-level failures (non-2xx response from the server).

```ts
class MatildaAgentRunError extends Error {
  readonly status: number;       // HTTP status code
  readonly responseText: string; // Raw response body
}
```

### `MatildaAgentStreamError`

Thrown by `run()` when the stream emits an error event (unless `throwOnStreamError: false`). Carries the full `AgentRunResult` with whatever was collected before the error.

```ts
class MatildaAgentStreamError extends Error {
  readonly code: ChatErrorCode;
  readonly errors: ReadonlyArray<{ code: ChatErrorCode; message: string }>;
  readonly result: AgentRunResult;
}
```

```ts
import { MatildaAgentStreamError, MatildaAgentRunError } from '@maincode-ai/matilda-agent-sdk';

try {
  await runner.run(agent, input);
} catch (err) {
  if (err instanceof MatildaAgentStreamError) {
    console.log('Stream error code:', err.code);
    console.log('Partial output before error:', err.result.finalOutput);
    console.log('All errors:', err.errors);
  } else if (err instanceof MatildaAgentRunError) {
    console.log('HTTP error status:', err.status);
    console.log('Response body:', err.responseText);
  } else {
    throw err;
  }
}
```

### `SafetyReplaceError`

Thrown by `streamText()`, `runText()`, `streamObject()`, and `runObject()` when the server replaces the output via a safety filter. The `message` property contains the replacement text (or empty string), and `categories` lists the safety categories.

```ts
class SafetyReplaceError extends Error {
  readonly categories: string[];
}
```

### `MatildaObjectParseError`

Thrown by `streamObject()` / `runObject()` when the response cannot be parsed as JSON or fails zod validation — e.g. a truncated stream (see [§9](#9-runner--structured-output)). `raw` holds the full response text; `cause` is the underlying `JSON.parse` or zod error. Safety replacement does not surface here — it throws `SafetyReplaceError` first.

```ts
class MatildaObjectParseError extends Error {
  readonly raw: string;
  readonly cause: unknown;
}
```

### `AuthError`

Thrown by auth flows. The `code` field is an OAuth error code. The `retryable` field distinguishes transient failures from permanent ones.

```ts
class AuthError extends Error {
  readonly code: string;
  readonly retryable: boolean;
}
```

### Chat error codes (`ChatErrorCode`)

These codes are emitted via the `error` stream event and appear in `AgentRunResult.errors`:

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

- **Default:** `45_000` ms (`DEFAULT_AGENT_STALL_TIMEOUT_MS`)
- **Disable:** Pass `stallTimeoutMs: 0` in `AgentRunOptions` (not recommended)

### Retry behaviour

The SDK retries retryable errors within a single turn. Retries are controlled by `maxRetries` (default: `0` — no retries).

**Retryable errors:**
- HTTP 429 (rate limited), 408 (request timeout), 5xx (server errors)
- Network errors: `UND_ERR_SOCKET`, `UND_ERR_FETCH_ERROR`, `ETIMEDOUT`, `ECONNRESET`
- SSE stall watchdog (`stalled` error code)
- `TimeoutError` (but not `AbortError`)

**Retry delay:** Exponential backoff with jitter, capped at 30 seconds.

**Important:** Retries only happen when no text has been yielded to the consumer yet. Retrying past that point would replay text the caller already has.

When a retry occurs, a `turn.retrying` event is emitted:

```ts
for await (const event of runner.stream(agent, input, { maxRetries: 3 })) {
  if (event.type === 'turn.retrying') {
    console.log(`Retry ${event.attempt}/${event.maxRetries} in ${event.delayMs}ms: ${event.error.message}`);
  }
}
```

### Error handling example

```ts
import {
  Runner,
  MatildaAgentStreamError,
  MatildaAgentRunError,
  SafetyReplaceError,
} from '@maincode-ai/matilda-agent-sdk';

const runner = new Runner();

try {
  const text = await runner.runText(agent, 'Hello!');
  console.log(text);
} catch (err) {
  if (err instanceof MatildaAgentStreamError) {
    console.error(`Stream error: ${err.code} — ${err.message}`);
    console.log('Partial output:', err.result.finalOutput);
  } else if (err instanceof MatildaAgentRunError) {
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

## 16. Multi-Agent Patterns

The SDK has no built-in orchestrator — multi-agent emerges from composition. The `Runner` is your execution primitive, and standard JavaScript patterns (chaining, `Promise.all`, tool-based delegation) build the architecture.

### Pattern 1: Sequential pipeline

Chain `run()` calls, feeding each agent's output to the next. Each stage has a single responsibility.

```ts
import { Agent, Runner } from '@maincode-ai/matilda-agent-sdk';

const runner = new Runner();

const researcher = new Agent({
  name: 'researcher',
  purpose: 'analysis',
  instructions: 'Produce a structured list of key facts for a blog post. Bullet points only.',
});

const writer = new Agent({
  name: 'writer',
  purpose: 'general',
  instructions: 'Given research notes, write an engaging blog post draft under 400 words.',
});

const editor = new Agent({
  name: 'editor',
  purpose: 'general',
  instructions: 'Polish the draft for clarity, grammar, and flow. Return the full revised post.',
});

const topic = 'Why developers are adopting AI coding assistants';

// Stage 1 → 2 → 3
const research = await runner.run(researcher, `Research this topic: ${topic}`);
const draft = await runner.run(writer, research.finalOutput);
const edited = await runner.run(editor, draft.finalOutput);

console.log(edited.finalOutput);

// Total token usage across the pipeline
const totalTokens =
  (research.usage?.output_tokens ?? 0) +
  (draft.usage?.output_tokens ?? 0) +
  (edited.usage?.output_tokens ?? 0);
console.log(`Total output tokens: ${totalTokens}`);
```

### Pattern 2: Parallel fan-out / fan-in

Run multiple specialist agents concurrently with `Promise.all()`, then feed their outputs to a synthesiser.

```ts
const securityReviewer = new Agent({
  name: 'security-reviewer',
  purpose: 'analysis',
  instructions: 'Review code for vulnerabilities. Report only security issues.',
});

const performanceReviewer = new Agent({
  name: 'performance-reviewer',
  purpose: 'analysis',
  instructions: 'Review code for efficiency. Report only performance issues.',
});

const synthesiser = new Agent({
  name: 'synthesiser',
  purpose: 'analysis',
  instructions: 'Given reviews from multiple reviewers, produce a prioritised action list.',
});

const code = 'function getUserData(userId, db) { /* ... */ }';

// Fan-out: three reviewers analyse concurrently
const [security, performance] = await Promise.all([
  runner.run(securityReviewer, `Review this code:\n\`\`\`javascript\n${code}\n\`\`\``),
  runner.run(performanceReviewer, `Review this code:\n\`\`\`javascript\n${code}\n\`\`\``),
]);

// Fan-in: synthesiser merges the reviews
const combinedInput = [
  '## Security Review', security.finalOutput,
  '## Performance Review', performance.finalOutput,
].join('\n');

const synthesis = await runner.run(synthesiser, combinedInput);
console.log(synthesis.finalOutput);
```

### Pattern 3: Router / delegator

A triage agent receives queries and decides which specialist to invoke. Each specialist is exposed as a client tool — when the agent calls a tool, the SDK handler runs the specialist agent via `run()` and returns its output.

```ts
import { Agent, Runner, type ToolHandlers, type AgentRunOptions } from '@maincode-ai/matilda-agent-sdk';

const runner = new Runner();

const billingSpecialist = new Agent({
  name: 'billing-specialist',
  instructions: 'You are a billing support specialist.',
});

const technicalSpecialist = new Agent({
  name: 'technical-specialist',
  instructions: 'You are a technical support specialist. Include code examples when relevant.',
});

const triageAgent = new Agent({
  name: 'triage',
  purpose: 'general',
  instructions: 'You are a customer support triage specialist.',
});

const triageTools = [
  {
    name: 'ask_billing_specialist',
    description: 'Route billing questions to the billing specialist.',
    parameters: { type: 'object' as const, properties: { question: { type: 'string' } }, required: ['question'] },
  },
  {
    name: 'ask_technical_specialist',
    description: 'Route technical questions to the technical specialist.',
    parameters: { type: 'object' as const, properties: { question: { type: 'string' } }, required: ['question'] },
  },
];

const toolHandlers: ToolHandlers = {
  ask_billing_specialist: async (args) => {
    const result = await runner.run(billingSpecialist, `Answer: ${args.question}`);
    return { content: result.finalOutput };
  },
  ask_technical_specialist: async (args) => {
    const result = await runner.run(technicalSpecialist, `Answer: ${args.question}`);
    return { content: result.finalOutput };
  },
};

const runOptions: AgentRunOptions = {
  toolHandlers,
  clientTools: triageTools,
  maxToolRoundtrips: 6,
  callbacks: {
    onToolCall: (name) => console.log(`Triage chose: ${name}`),
    onToolResult: (_name, result) => console.log(`Specialist responded.`),
    onToken: (delta) => process.stdout.write(delta),
  },
};

const triagePrompt = [
  'A customer asked:',
  '"I\'m getting a 401 Unauthorized error when calling the /api/chat endpoint."',
  'You MUST forward this to a specialist by calling a tool.',
  'After the specialist responds, relay their answer.',
].join('\n');

await runner.run(triageAgent, triagePrompt, runOptions);
```

> **Tip:** Keep the triage agent's instructions short — put the routing rules in the task prompt. If routing rules are in the `instructions` field, the server's Auto-mode system prompt may interpret them as a prompt-injection attempt rather than operating instructions.

---

## 17. Suggested Tasks / Recipes

### Recipe 1: CLI agent with device-flow auth and streaming

A complete interactive CLI agent with device-flow auth, streaming, and multi-turn sessions.

```ts
import * as readline from 'node:readline/promises';
import { stdin, stdout } from 'node:process';
import { Runner, MatildaCore, createFileTokenStore, createSession } from '@maincode-ai/matilda-agent-sdk';
import { homedir } from 'node:os';
import { join } from 'node:path';

const { store, lock } = createFileTokenStore(join(homedir(), '.matilda', 'tokens.json'));

const runner = new Runner({
  core: new MatildaCore({ baseUrl: 'https://matilda.maincode.com/api' }),
});

// Try to restore persisted tokens, fall back to interactive login
const restored = await runner.auth.restore({ clientId: 'matilda-code', tokenStore: store, tokenLock: lock });
if (!restored) {
  console.log('Starting device flow authentication...');
  await runner.auth.loginWithDeviceFlow({ clientId: 'matilda-code', tokenStore: store, tokenLock: lock });
  console.log('Authenticated!');
}

const session = createSession({
  name: 'cli-assistant',
  purpose: 'general',
  instructions: 'Be helpful, concise, and friendly.',
});

const rl = readline.createInterface({ input: stdin, output: stdout });

while (true) {
  const input = await rl.question('\nYou: ');
  if (!input.trim() || input.toLowerCase() === 'exit') break;

  process.stdout.write('Agent: ');
  for await (const event of session.stream(input)) {
    if (event.type === 'message.delta') process.stdout.write(event.delta);
  }
  process.stdout.write('\n');
}

rl.close();
```

### Recipe 2: Client tools (weather + calculator)

An agent that uses client tools to answer questions requiring external data.

```ts
import { Runner, MatildaCore, stream, type ToolHandlers } from '@maincode-ai/matilda-agent-sdk';

const runner = new Runner({
  core: new MatildaCore({ baseUrl: 'https://matilda.maincode.com/api' }),
});

if (!(await runner.auth.getTokens())) {
  await runner.auth.loginWithDeviceFlow({ clientId: 'matilda-code' });
}

const clientTools = [
  { name: 'get_weather', description: 'Get current weather for a city', parameters: { type: 'object' } },
  { name: 'calculate', description: 'Evaluate a math expression', parameters: { type: 'object' } },
];

const toolHandlers: ToolHandlers = {
  get_weather: async (args) => {
    const city = (args.city as string) ?? 'unknown';
    // In reality, call a weather API
    return { content: JSON.stringify({ city, temp: 22, condition: 'sunny' }) };
  },
  calculate: async (args) => {
    try {
      const result = Function(`return (${args.expression})`)();
      return { content: String(result) };
    } catch {
      return { content: 'Invalid expression', isError: true };
    }
  },
};

for await (const event of stream(
  { name: 'assistant', instructions: 'Use the available tools to answer.' },
  'What is the weather in Sydney, and what is 15 * 23?',
  { toolHandlers, clientTools },
)) {
  if (event.type === 'client.tool.requested') {
    console.log(`→ ${event.name}(${JSON.stringify(event.args)})`);
  }
  if (event.type === 'client.tool.result') {
    console.log(`← ${event.result}`);
  }
  if (event.type === 'message.delta') process.stdout.write(event.delta);
}
```

### Recipe 3: Multi-agent code review pipeline

Sequential pipeline: security review → performance review → synthesis.

```ts
import { Agent, Runner, MatildaCore } from '@maincode-ai/matilda-agent-sdk';

const runner = new Runner({
  core: new MatildaCore({ baseUrl: 'https://matilda.maincode.com/api' }),
});

if (!(await runner.auth.getTokens())) {
  await runner.auth.loginWithDeviceFlow({ clientId: 'matilda-code' });
}

const security = new Agent({
  name: 'security',
  purpose: 'analysis',
  instructions: 'Review for vulnerabilities. Be specific.',
});

const performance = new Agent({
  name: 'performance',
  purpose: 'analysis',
  instructions: 'Review for efficiency. Be specific.',
});

const synthesiser = new Agent({
  name: 'synthesiser',
  purpose: 'analysis',
  instructions: 'Merge reviews into a prioritised action list. Use 🔴 🟡 🟢 priority.',
});

const code = 'function getUserData(userId, db) { var query = "SELECT * FROM users WHERE id = " + userId; }';

const [sec, perf] = await Promise.all([
  runner.run(security, `Review:\n\`\`\`javascript\n${code}\n\`\`\``),
  runner.run(performance, `Review:\n\`\`\`javascript\n${code}\n\`\`\``),
]);

const combined = `## Security\n${sec.finalOutput}\n\n## Performance\n${perf.finalOutput}`;
const result = await runner.run(synthesiser, combined);
console.log(result.finalOutput);
```

### Recipe 4: Dynamic instructions with metadata

An agent whose instructions adapt based on runtime metadata.

```ts
import { Agent, Runner, MatildaCore, run } from '@maincode-ai/matilda-agent-sdk';

const runner = new Runner({
  core: new MatildaCore({ baseUrl: 'https://matilda.maincode.com/api' }),
});

if (!(await runner.auth.getTokens())) {
  await runner.auth.loginWithDeviceFlow({ clientId: 'matilda-code' });
}

const agent = new Agent({
  name: 'code-reviewer',
  purpose: 'code',
  instructions: ({ input, metadata }) => {
    const lang = (metadata.language as string) ?? 'auto-detect';
    const strictness = (metadata.strictness as string) ?? 'normal';
    return [
      'Review the following code.',
      `Language: ${lang}`,
      `Strictness: ${strictness}`,
      'Focus on: correctness, security, and readability.',
      'Cite line numbers when possible.',
    ].join('\n');
  },
});

const result = await run(agent, 'function add(a, b) { return a + b }', {
  metadata: { language: 'JavaScript', strictness: 'strict' },
});

console.log(result.finalOutput);
```

### Recipe 5: Stream resume with disconnect recovery

Start a stream, simulate a disconnect, and resume from the last cursor.

```ts
import { stream, resumeAgentStream, configureClient } from '@maincode-ai/matilda-agent-sdk';

configureClient({ baseUrl: 'https://matilda.maincode.com/api' });

let streamId: string | null = null;
let lastEventId: string | undefined;
let receivedText = '';

console.log('Starting stream...');
try {
  for await (const event of stream({ name: 'writer' }, 'Write a very long essay about Australia.')) {
    if (event.type === 'stream.started') streamId = event.streamId;
    if (event.type === 'cursor') lastEventId = event.lastEventId;
    if (event.type === 'message.delta') {
      receivedText += event.delta;
      // Simulate disconnect after 500 chars
      if (receivedText.length > 500) {
        console.log('\n--- Simulated disconnect ---');
        break;
      }
    }
  }
} catch (err) {
  console.log('Disconnected:', err);
}

console.log(`Received ${receivedText.length} chars before disconnect.`);

// Resume from the last cursor
if (streamId) {
  console.log('\n--- Resuming ---');
  const result = await resumeAgentStream(streamId, lastEventId, {
    onEvent: (event) => {
      if (event.type === 'message.delta') process.stdout.write(event.delta);
    },
  });
  console.log(`\nTotal output: ${result.finalOutput.length} chars`);
}
```

### Recipe 6: Custom Runner with file token store

A standalone Runner with persistent auth for CLI or long-running service use.

```ts
import {
  Runner,
  MatildaCore,
  createFileTokenStore,
  configureClient,
} from '@maincode-ai/matilda-agent-sdk';
import { homedir } from 'node:os';
import { join } from 'node:path';

const tokenPath = join(homedir(), '.matilda', 'tokens.json');
const { store, lock } = createFileTokenStore(tokenPath);

const runner = new Runner({
  core: new MatildaCore({ baseUrl: 'https://matilda.maincode.com/api' }),
});

// Restore persisted tokens or login interactively
const restored = await runner.auth.restore({ clientId: 'matilda-code', tokenStore: store, tokenLock: lock });
if (!restored) {
  await runner.auth.loginWithDeviceFlow({
    clientId: 'matilda-code',
    tokenStore: store,
    tokenLock: lock,
  });
}

// Runner is ready — tokens auto-refresh on 401
const result = await runner.run(
  { name: 'helper', instructions: 'Be concise.' },
  'What is the capital of Australia?',
);
console.log(result.finalOutput);

// Later: logout clears the token store
// await runner.auth.logout();
```

---

## 18. Exports Reference

### Classes

| Export | Description |
|---|---|
| `Agent` | Named persona with static or dynamic instructions. |
| `Runner` | Main execution class. Holds `auth`, `files`, `conversations` resources. |
| `Session` | Multi-turn conversation wrapper with auto-managed `conversationId`. |
| `AgentAuth` | Managed auth: login, restore, token refresh, logout. |
| `MatildaAgentRunError` | HTTP-level failure (status, responseText). |
| `MatildaAgentStreamError` | SSE stream error (code, errors, partial result). |
| `SafetyReplaceError` | Safety filter replacement error (categories). |
| `MatildaObjectParseError` | Structured output parse/validation failure (raw, cause). |
| `MatildaCore` | Underlying API client (re-exported from `@matilda/api-client`). |
| `FilesResource` | File upload/retrieve resource. |
| `ConversationsResource` | Conversation list/retrieve/update/feedback resource. |

### Functions

| Export | Description |
|---|---|
| `run(agent, input, options?)` | Run an agent turn via `defaultRunner`. Returns `Promise<AgentRunResult>`. |
| `stream(agent, input, options?)` | Stream agent events via `defaultRunner`. Returns `AsyncGenerator<AgentRunEvent>`. |
| `streamText(agent, input, options?)` | Stream text deltas via `defaultRunner`. Returns `AsyncGenerator<string>`. |
| `runText(agent, input, options?)` | Run and return just the text via `defaultRunner`. Returns `Promise<string>`. |
| `streamObject(agent, input, schema, options?)` | Stream with structured output via `defaultRunner`. Returns `AsyncGenerator<AgentObjectEvent<T>>`. |
| `runObject(agent, input, schema, options?)` | Run with structured output via `defaultRunner`. Returns `Promise<AgentObjectResult<T>>`. |
| `createSession(agent, options?)` | Create a `Session`. |
| `buildAgentChatRequest(opts)` | Build a `ChatRequest` without executing. |
| `resumeAgentStream(streamId, lastEventId, handlers, options?)` | Resume a detached durable stream. |
| `configureClient(options)` | Configure the default `MatildaCore` singleton. |
| `getClientConfig()` | Get the default core's config. |
| `getDefaultCore()` | Get the default `MatildaCore` singleton. |
| `trustApiBaseUrl(rawUrl, policy?)` | Validate and brand a URL as trusted. |
| `createFileTokenStore(path)` | `0600` JSON file token store with cross-process lock. |
| `memoryStorage()` | In-memory `StorageAdapter`. |

### Constants

| Export | Value | Description |
|---|---|---|
| `DEFAULT_AGENT_PURPOSE` | `'code'` | Default agent purpose. |
| `DEFAULT_AGENT_STALL_TIMEOUT_MS` | `45_000` | Default SSE stall watchdog timeout. |
| `DEFAULT_MAX_TOOL_ROUNDTRIPS` | `25` | Default maximum tool roundtrips. |
| `DEFAULT_MAX_RETRIES` | `0` | Default maximum retries. |
| `DEFAULT_SUCCESS_REDIRECT` | `'https://matilda.maincode.com/cli/signed-in'` | Default browser login success redirect. |
| `MATILDA_API_VERSION_HEADER` | — | API version header name. |
| `MATILDA_CURRENT_API_VERSION` | — | Current API version string. |

### Instances

| Export | Description |
|---|---|
| `defaultRunner` | A `Runner` using the default `MatildaCore` singleton. |

### Types

| Export | Description |
|---|---|
| `AgentPurpose` | `'code' \| 'analysis' \| 'general'` |
| `AgentInstructions` | `string \| ((ctx: AgentRunContext) => string \| Promise<string>)` |
| `AgentRunContext` | Context passed to dynamic instructions. |
| `AgentOptions` | Constructor options for `Agent`. |
| `AgentRunOptions` | Options for `runner.run()` / `runner.stream()`. |
| `AgentRunEvent` | 22-variant discriminated union of stream events. |
| `AgentRunResult` | Result of an agent run. |
| `AgentObjectEvent<T>` | `AgentRunEvent` plus a final `{ type: 'object'; object: T }`. |
| `AgentObjectResult<T>` | `AgentRunResult` plus the validated `object`. |
| `AgentObjectRunOptions<T>` | `AgentRunOptions` with an embedded zod `schema`. |
| `AgentCallbacks` | Callback hooks for `run()`. |
| `BuildAgentChatRequestOptions` | Options for `buildAgentChatRequest()`. |
| `ToolHandler` | `(args, ctx) => Promise<ToolResult>` |
| `ToolHandlers` | `Record<string, ToolHandler>` |
| `ToolExecutionContext` | Context passed to tool handlers. |
| `ToolResult` | `{ content: string; isError?: boolean }` |
| `SessionOptions` | Options for `Session` / `createSession()`. |
| `FileUploadOptions` | Options for `files.upload()`. |
| `CoreSource` | `MatildaCore \| (() => MatildaCore)` |
| `BrowserLoginOptions` | Options for `auth.loginWithBrowser()`. |
| `DeviceLoginOptions` | Options for `auth.loginWithDeviceFlow()`. |
| `TokenSet` | `{ accessToken, refreshToken?, idToken?, expiresAt }` |
| `TokenManager` | Token manager interface. |
| `StorageAdapter` | Token persistence interface. |
| `LoginFlowEvent` | Login flow state event type. |
| `FileTokenStore` | File token store return type. |
| `ClientConfig` | Core config type (re-exported). |
| `GetToken` | Token provider function type (re-exported). |
| `TrustedApiBaseUrl` | Branded string type (re-exported). |
| `TrustedApiBaseUrlPolicy` | URL validation policy (re-exported). |
| `ApiMessage` | `{ role, content }` (re-exported). |
| `ChatRequest` | Chat request type (re-exported). |
| `ChatResponseMode` | `'auto' \| 'instant' \| 'deep'` (re-exported). |
| `ChatSseEvent` | SSE event type (re-exported). |
| `ChatSseEventName` | SSE event name type (re-exported). |
| `SafetyReplaceEvent` | Safety replace event type (re-exported). |
| `UsageEvent` | Token usage type (re-exported). |
| `ConversationListResponse` | Conversation list response (re-exported). |
| `ConversationRecord` | Full conversation record (re-exported). |
| `ConversationSummary` | Conversation summary (re-exported). |
| `FileAttachment` | File metadata (re-exported). |
| `FileCompleteResponse` | File upload result (re-exported). |
| `UploadFilesOptions` | Multi-file upload options (re-exported). |

### Error classes re-exported

| Export | Description |
|---|---|
| `AuthError` | OAuth error (code, retryable). Re-exported from client SDK. |
