# Matilda SDK reference

This directory pins the public Maincode Matilda JavaScript SDKs used as the
protocol reference for LLMWorld's Python adapter.

| Package | Pinned version |
| --- | ---: |
| `@maincode-ai/matilda-client-sdk` | `0.3.1` |
| `@maincode-ai/matilda-agent-sdk` | `0.2.1` |

Install the exact locked dependency tree with Node.js 20 or newer:

```powershell
npm ci
```

The authoritative current implementation and type declarations are then under
`node_modules/@maincode-ai/`. `DOCUMENTATION.md` (agent SDK 0.1.0) and
`DOCUMENTATION (1).md` (client SDK 0.2.0) are retained as older, more detailed
API notes; use the installed packages and their `.d.ts` files when the old notes
disagree with the current contract.

## LLMWorld Python transport

All project call sites go through `SubAgent.single_call()` or
`SubAgent.parallel_call()`. For Matilda, the transport analyzes every prompt and
automatically turns content above the server's per-message limit into ordered
segments. If the complete JSON body also approaches the edge's request-size
limit, segments are sent as successive turns under one generated
`conversation_id`; intermediate acknowledgements are hidden and only the final
answer is returned. Callers continue to pass and receive the same strings/results,
and a batch may contain any mixture or number of short and long prompts.

The defaults can be overridden through environment variables:

| Variable | Default | Purpose |
| --- | ---: | --- |
| `MATILDA_MESSAGE_CHAR_LIMIT` | `50000` | Current server per-message character limit. |
| `MATILDA_MESSAGE_CHUNK_CHARS` | `48000` | Target payload size before segment markers. |
| `MATILDA_TRANSFER_CHUNK_BYTES` | `52000` | JSON-encoded UTF-8 byte ceiling for one lossless segment. |
| `MATILDA_REQUEST_BODY_TARGET_BYTES` | `60000` | Conservative body target below the observed ~64KB edge rejection. |
| `LLM_MAX_CONCURRENCY` | `10` | Global and per-batch LLM request ceiling. |

Segmentation removes both transport obstacles, not the model's finite context
window. All turns still consume one shared context; if Matilda reports that it
trimmed earlier messages, the adapter fails explicitly instead of returning an
answer based on incomplete input.
