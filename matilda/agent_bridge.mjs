import process from "node:process";

import {
  Agent,
  DEFAULT_AGENT_STALL_TIMEOUT_MS,
  DEFAULT_MAX_RETRIES,
  MATILDA_CURRENT_API_VERSION,
  MatildaAgentStreamError,
  MatildaCore,
  Runner,
  SafetyReplaceError,
  resumeAgentStream,
} from "@maincode-ai/matilda-agent-sdk";


function readStdin() {
  return new Promise((resolve, reject) => {
    let text = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => { text += chunk; });
    process.stdin.on("end", () => {
      try {
        resolve(JSON.parse(text));
      } catch (error) {
        reject(new Error(`Invalid bridge request JSON: ${error.message}`));
      }
    });
    process.stdin.on("error", reject);
  });
}


function errorPayload(error) {
  const result = error?.result;
  return {
    ok: false,
    error: {
      name: error?.name || "Error",
      message: error?.message || String(error),
      code: error?.code || (Number.isInteger(error?.status) ? `http_${error.status}` : null),
      status: Number.isInteger(error?.status) ? error.status : null,
      raw: typeof error?.raw === "string" ? error.raw : null,
      responseText: typeof error?.responseText === "string" ? error.responseText : null,
      errors: Array.isArray(error?.errors) ? error.errors : null,
    },
    partial: result ? {
      finalOutput: result.finalOutput,
      events: result.events,
      streamId: result.streamId,
      lastEventId: result.lastEventId,
      usage: result.usage,
      truncatedReason: result.truncatedReason,
    } : null,
    sdk: {
      agent: "0.2.1",
      apiVersion: MATILDA_CURRENT_API_VERSION,
      defaultStallTimeoutMs: DEFAULT_AGENT_STALL_TIMEOUT_MS,
      defaultMaxRetries: DEFAULT_MAX_RETRIES,
    },
  };
}


function emptyCollectedResult(agentName) {
  return {
    agentName,
    finalOutput: "",
    events: [],
    errors: [],
    streamId: undefined,
    lastEventId: undefined,
    usage: undefined,
    truncatedReason: undefined,
    safetyReplace: undefined,
    resumedAfter: undefined,
    replaceCount: 0,
  };
}


function collectEvent(result, event) {
  result.events.push(event);
  if (event.type === "message.delta") result.finalOutput += event.delta;
  if (event.type === "replace") {
    result.finalOutput = "";
    result.replaceCount += 1;
  }
  if (event.type === "stream.started") result.streamId = event.streamId;
  if (event.type === "cursor") result.lastEventId = event.lastEventId;
  if (event.type === "usage") result.usage = event.usage;
  if (event.type === "truncated") result.truncatedReason = event.reason;
  if (event.type === "error") result.errors.push({ code: event.code, message: event.message });
  if (event.type === "safety.replace") {
    result.finalOutput = event.message || "";
    result.safetyReplace = { message: event.message || "", categories: event.categories || [] };
  }
}


async function collectAgentRun(runner, agent, prompt, options, core) {
  const result = emptyCollectedResult(agent.name);
  let thrown = null;
  try {
    for await (const event of runner.stream(agent, prompt, options)) {
      collectEvent(result, event);
    }
  } catch (error) {
    thrown = error;
  }

  const resumableError = result.errors.find((item) =>
    ["stalled", "stream_aborted"].includes(item.code)
  );
  if ((resumableError || thrown) && result.streamId) {
    try {
      const priorErrorCount = result.errors.length;
      await resumeAgentStream(
        result.streamId,
        result.lastEventId,
        { onEvent: (event) => collectEvent(result, event) },
        { core },
      );
      result.errors.splice(0, priorErrorCount);
      result.resumedAfter = resumableError?.code || thrown?.code || thrown?.name || "network_error";
      thrown = null;
    } catch (resumeError) {
      if (!thrown) thrown = resumeError;
    }
  }
  if (thrown) throw thrown;
  if (result.errors.length) throw new MatildaAgentStreamError(result);
  if (result.safetyReplace) {
    throw new SafetyReplaceError(result.safetyReplace.message, result.safetyReplace.categories);
  }
  return result;
}


async function main() {
  const request = await readStdin();
  if (typeof request.accessToken !== "string" || !request.accessToken) {
    throw new Error("accessToken is required");
  }
  if (typeof request.prompt !== "string") {
    throw new Error("prompt must be a string");
  }

  const core = new MatildaCore({
    baseUrl: request.baseUrl,
    accessToken: request.accessToken,
    apiVersion: request.apiVersion || MATILDA_CURRENT_API_VERSION,
    publicConfigEndpoint: "core-api-production",
  });
  const runner = new Runner({ core });
  const agent = new Agent({
    name: "LLMWorld Simulation Agent",
    purpose: request.thinking ? "analysis" : "general",
    instructions: "Follow the caller's task exactly. When JSON is requested, return only valid JSON.",
  });
  const options = {
    responseMode: request.thinking ? "deep" : "auto",
    stallTimeoutMs: DEFAULT_AGENT_STALL_TIMEOUT_MS,
    maxRetries: DEFAULT_MAX_RETRIES,
  };

  const inlinePromptLimit = 45_000;
  let runPrompt = request.prompt;
  let upload = null;
  if (request.prompt.length > inlinePromptLimit) {
    const file = new File([request.prompt], "llmworld_prompt.txt", {
      type: "text/plain;charset=utf-8",
    });
    const runtimeConfig = await core.fetchPublicRuntimeConfig();
    core.setCachedPublicRuntimeConfig(runtimeConfig);
    upload = await core.uploadFileChunked(file);
    if (["failed", "rejected"].includes(upload.status)) {
      const reason = upload.failureReason?.message || upload.status;
      throw new Error(`Matilda prompt-file upload failed: ${reason}`);
    }
    options.fileIds = [upload.fileId];
    runPrompt = [
      "The complete caller prompt is attached as llmworld_prompt.txt.",
      "Read the attached file in full and execute that prompt exactly once.",
      "Treat its entire text as the task; do not summarize it and do not discuss this transfer mechanism.",
    ].join(" ");
  }

  const started = performance.now();
  let result;
  let content;
  let object = null;

  if (request.jsonMode && request.jsonSchema) {
    const jsonSchemaString = typeof request.jsonSchema === "string"
      ? request.jsonSchema
      : JSON.stringify(request.jsonSchema);
    result = await collectAgentRun(runner, agent, runPrompt, { ...options, responseSchema: jsonSchemaString }, core);
    try {
      object = JSON.parse(result.finalOutput);
    } catch (cause) {
      const parseError = new Error(`Matilda returned invalid JSON: ${cause.message}`);
      parseError.name = "MatildaJsonParseError";
      parseError.raw = result.finalOutput;
      parseError.result = result;
      throw parseError;
    }
    content = result.finalOutput.trim();
  } else {
    result = await collectAgentRun(runner, agent, runPrompt, options, core);
    content = result.finalOutput;
  }

  process.stdout.write(JSON.stringify({
    ok: true,
    content,
    object,
    events: result.events,
    streamId: result.streamId,
    lastEventId: result.lastEventId,
    usage: result.usage || null,
    truncatedReason: result.truncatedReason || null,
    resumedAfter: result.resumedAfter || null,
    replaceCount: result.replaceCount,
    structuredRecovery: null,
    rawContent: request.jsonMode ? result.finalOutput : null,
    inputTransport: upload ? "sdk_file_attachment" : "inline",
    upload: upload ? {
      fileId: upload.fileId,
      status: upload.status,
      promptChars: request.prompt.length,
    } : null,
    durationMs: Math.round(performance.now() - started),
    sdk: {
      agent: "0.2.1",
      apiVersion: MATILDA_CURRENT_API_VERSION,
      defaultStallTimeoutMs: DEFAULT_AGENT_STALL_TIMEOUT_MS,
      defaultMaxRetries: DEFAULT_MAX_RETRIES,
    },
  }));
}


main().catch((error) => {
  process.stdout.write(JSON.stringify(errorPayload(error)));
  process.exitCode = 1;
});
