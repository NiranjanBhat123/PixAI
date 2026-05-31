import type {
  ApiResponse,
  ConversationData,
  CaptionData,
  EditData,
  StyleData,
  ImageResultData,
  ApplyEditsRequest,
} from "../types/Index";

const BASE_URL = "http://localhost:8081/api/v1";

// ─── Generic fetch helper ────────────────────────────────────────────
async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  const res = await fetch(`${BASE_URL}${path}`, options);

  if (!res.ok) {
    const errorText = await res.text().catch(() => "Unknown error");
    throw new Error(`API error ${res.status}: ${errorText}`);
  }

  return res.json() as Promise<ApiResponse<T>>;
}

// ─── 1. Upload image and create conversation ─────────────────────────
export async function createConversation(
  imageFile: File
): Promise<ApiResponse<ConversationData>> {
  const formData = new FormData();
  formData.append("image", imageFile);

  return apiFetch<ConversationData>("/conversations", {
    method: "POST",
    body: formData,
    // Don't set Content-Type — browser sets multipart boundary automatically
  });
}

// ─── 2. Get caption suggestions ──────────────────────────────────────
export async function getCaptions(
  conversationId: string
): Promise<ApiResponse<CaptionData>> {
  return apiFetch<CaptionData>(`/conversations/${conversationId}/captions`, {
    method: "POST",
  });
}

// ─── 3. Get edit suggestions ─────────────────────────────────────────
export async function getEditSuggestions(
  conversationId: string
): Promise<ApiResponse<EditData>> {
  return apiFetch<EditData>(`/conversations/${conversationId}/edits`, {
    method: "POST",
  });
}

// ─── 4. Apply edits ──────────────────────────────────────────────────
export async function applyEdits(
  conversationId: string,
  params: ApplyEditsRequest
): Promise<ApiResponse<ImageResultData>> {
  return apiFetch<ImageResultData>(
    `/conversations/${conversationId}/edits/apply`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    }
  );
}

// ─── 5. Get style suggestions ────────────────────────────────────────
export async function getStyleSuggestions(
  conversationId: string
): Promise<ApiResponse<StyleData>> {
  return apiFetch<StyleData>(`/conversations/${conversationId}/styles`, {
    method: "POST",
  });
}

// ─── 6. Generate styled image ────────────────────────────────────────
export async function generateStyle(
  conversationId: string,
  style: string,
  styleDescription: string
): Promise<ApiResponse<ImageResultData>> {
  return apiFetch<ImageResultData>(
    `/conversations/${conversationId}/styles/generate`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ style, styleDescription }),
    }
  );
}

// ─── 7. End conversation ─────────────────────────────────────────────
export async function endConversation(
  conversationId: string
): Promise<ApiResponse<ConversationData>> {
  return apiFetch<ConversationData>(
    `/conversations/${conversationId}/end`,
    { method: "PATCH" }
  );
}