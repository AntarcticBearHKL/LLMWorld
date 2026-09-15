import { ApiError } from "@/api/client"

const detailFromBody = (body: string): string | null => {
  try {
    const parsed: unknown = JSON.parse(body)
    if (typeof parsed === "object" && parsed !== null && "detail" in parsed) {
      const detail: unknown = parsed.detail
      if (typeof detail === "string") return detail
    }
  } catch {
    return null
  }
  return null
}

/** FastAPI 的错误体是 {"detail": "..."}，这里取出可读信息，取不到就退回原文。 */
export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return detailFromBody(error.message) ?? error.message
  if (error instanceof Error) return error.message
  return "Request failed"
}
