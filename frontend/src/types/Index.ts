// ─── Shared wrapper ────────────────────────────────────────────────
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

// ─── Conversation ───────────────────────────────────────────────────
export type ConversationStatus = "ACTIVE" | "COMPLETED";

export interface ConversationData {
  id: string;
  status: ConversationStatus;
  created_at: string;
}

// ─── Captions ───────────────────────────────────────────────────────
export interface CaptionSuggestion {
  caption: string;
  tone: string;
}

export interface CaptionData {
  imageDescription: string;
  suggestions: CaptionSuggestion[];
}

// ─── Edits ──────────────────────────────────────────────────────────
export interface EditSuggestion {
  parameter: string;
  currentEstimate: string;
  suggestedValue: number;
  reason: string;
}

export interface EditData {
  overallAssessment: string;
  suggestions: EditSuggestion[];
}

export interface ApplyEditsRequest {
  brightness: number;
  contrast: number;
  saturation: number;
  sharpness: number;
  warmth: number;
}

// ─── Styles ──────────────────────────────────────────────────────────
export interface StyleSuggestion {
  style: string;
  description: string;
  appeal: string;
}

export interface StyleData {
  suggestions: StyleSuggestion[];
}

// ─── Image Result (apply edits / generate style) ────────────────────
export interface ImageResultData {
  image_base64: string;
  format: string;
  message: string;
}

// ─── Chat message types (UI-only, not from API) ──────────────────────
export type MessageRole = "user" | "assistant";
export type MessageKind =
  | "text"
  | "image-upload"
  | "captions"
  | "edits"
  | "edit-result"
  | "styles"
  | "style-result"
  | "options-prompt";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  kind: MessageKind;
  // text content for simple messages
  text?: string;
  // structured payloads
  captionData?: CaptionData;
  editData?: EditData;
  styleData?: StyleData;
  imageResultData?: ImageResultData;
  // the original uploaded image (data URL) for display
  uploadedImageUrl?: string;
  timestamp: Date;
}