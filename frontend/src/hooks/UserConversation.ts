import { useState, useCallback, useRef } from "react";
import type { ChatMessage, ApplyEditsRequest } from "../types/Index";
import {
  createConversation,
  getCaptions,
  getEditSuggestions,
  applyEdits,
  getStyleSuggestions,
  generateStyle,
  endConversation,
  applyStyleFilter
} from "../api/pixai";

// ─── Types ───────────────────────────────────────────────────────────
export type ConversationPhase =
  | "idle"          // no conversation started
  | "active"        // image uploaded, awaiting user choice
  | "loading"       // waiting for API
  | "completed";    // user ended the conversation

// ─── Helper ──────────────────────────────────────────────────────────
function makeId(): string {
  return Math.random().toString(36).slice(2, 10);
}

function makeMessage(
  partial: Omit<ChatMessage, "id" | "timestamp">
): ChatMessage {
  return { ...partial, id: makeId(), timestamp: new Date() };
}

// ─── Hook ────────────────────────────────────────────────────────────
export function useConversation() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    makeMessage({
      role: "assistant",
      kind: "text",
      text: "Hey! Drop your photo here and let's see what we can do with it ✦",
    }),
  ]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [phase, setPhase] = useState<ConversationPhase>("idle");
  const [error, setError] = useState<string | null>(null);

  // Ref to track uploaded image URL for display in later messages
  const uploadedImageUrlRef = useRef<string | null>(null);

  // ── Internal helpers ─────────────────────────────────────────────

  const pushMessage = useCallback((msg: Omit<ChatMessage, "id" | "timestamp">) => {
    setMessages((prev) => [...prev, makeMessage(msg)]);
  }, []);

  const pushError = useCallback((err: unknown, context: string) => {
    const message =
      err instanceof Error ? err.message : "Something went wrong.";
    console.error(`[useConversation] ${context}:`, err);
    setError(message);
    pushMessage({
      role: "assistant",
      kind: "text",
      text: `⚠️ ${message}`,
    });
  }, [pushMessage]);

  // ── Public actions ───────────────────────────────────────────────

  /**
   * Upload an image → create a conversation → show follow-up options
   */
  const uploadImage = useCallback(async (file: File) => {
    setError(null);
    setPhase("loading");

    // Show user's image in chat immediately (optimistic)
    const localUrl = URL.createObjectURL(file);
    uploadedImageUrlRef.current = localUrl;

    pushMessage({
      role: "user",
      kind: "image-upload",
      uploadedImageUrl: localUrl,
      text: file.name,
    });

    pushMessage({
      role: "assistant",
      kind: "text",
      text: "Uploading your image…",
    });

    try {
      const res = await createConversation(file);
      const id = res.data.id;
      setConversationId(id);
      setPhase("active");

      // Replace "uploading" message with the options prompt
      setMessages((prev) => {
        // Remove the last "Uploading…" assistant message
        const withoutLoading = prev.slice(0, -1);
        return [
          ...withoutLoading,
          makeMessage({
            role: "assistant",
            kind: "options-prompt",
            text: "Great shot! What would you like to do with it?",
          }),
        ];
      });
    } catch (err) {
      setPhase("idle");
      pushError(err, "uploadImage");
    }
  }, [pushMessage, pushError]);

  /**
   * Request caption suggestions from the AI
   */
  const requestCaptions = useCallback(async () => {
    if (!conversationId) return;
    setError(null);
    setPhase("loading");

    pushMessage({ role: "user", kind: "text", text: "Suggest some captions ✍️" });
    pushMessage({ role: "assistant", kind: "text", text: "Analyzing your image for caption ideas…" });

    try {
      const res = await getCaptions(conversationId);
      setPhase("active");
      setMessages((prev) => [
        ...prev.slice(0, -1), // remove "Analyzing…"
        makeMessage({
          role: "assistant",
          kind: "captions",
          captionData: res.data,
        }),
        makeMessage({
          role: "assistant",
          kind: "options-prompt",
          text: "Anything else I can help with?",
        }),
      ]);
    } catch (err) {
      setPhase("active");
      pushError(err, "requestCaptions");
    }
  }, [conversationId, pushMessage, pushError]);

  /**
   * Request edit suggestions, then let user confirm
   */
  const requestEdits = useCallback(async () => {
    if (!conversationId) return;
    setError(null);
    setPhase("loading");

    pushMessage({ role: "user", kind: "text", text: "Suggest some edits 🎨" });
    pushMessage({ role: "assistant", kind: "text", text: "Reading the light and tone of your photo…" });

    try {
      const res = await getEditSuggestions(conversationId);
      setPhase("active");
      setMessages((prev) => [
        ...prev.slice(0, -1),
        makeMessage({
          role: "assistant",
          kind: "edits",
          editData: res.data,
        }),
      ]);
    } catch (err) {
      setPhase("active");
      pushError(err, "requestEdits");
    }
  }, [conversationId, pushMessage, pushError]);

  /**
   * Apply the AI-suggested edits (user confirmed)
   */
  const confirmEdits = useCallback(async (params: ApplyEditsRequest) => {
    if (!conversationId) return;
    setError(null);
    setPhase("loading");

    pushMessage({ role: "user", kind: "text", text: "Apply those edits!" });
    pushMessage({ role: "assistant", kind: "text", text: "Applying adjustments to your photo…" });

    try {
      const res = await applyEdits(conversationId, params);
      setPhase("active");
      setMessages((prev) => [
        ...prev.slice(0, -1),
        makeMessage({
          role: "assistant",
          kind: "edit-result",
          imageResultData: res.data,
          text: res.data.message,
        }),
        makeMessage({
          role: "assistant",
          kind: "options-prompt",
          text: "Anything else?",
        }),
      ]);
    } catch (err) {
      setPhase("active");
      pushError(err, "confirmEdits");
    }
  }, [conversationId, pushMessage, pushError]);

  /**
   * Request style suggestions
   */
  const requestStyles = useCallback(async () => {
    if (!conversationId) return;
    setError(null);
    setPhase("loading");

    pushMessage({ role: "user", kind: "text", text: "Show me some style ideas 🎭" });
    pushMessage({ role: "assistant", kind: "text", text: "Imagining alternative versions of your photo…" });

    try {
      const res = await getStyleSuggestions(conversationId);
      setPhase("active");
      setMessages((prev) => [
        ...prev.slice(0, -1),
        makeMessage({
          role: "assistant",
          kind: "styles",
          styleData: res.data,
        }),
      ]);
    } catch (err) {
      setPhase("active");
      pushError(err, "requestStyles");
    }
  }, [conversationId, pushMessage, pushError]);

  /**
   * Generate a specific style
   */
const confirmStyle = useCallback(
  async (style: string, _description: string) => {
    if (!conversationId) return;
    setError(null);
    setPhase("loading");

    pushMessage({ role: "user", kind: "text", text: `Apply ${style} style` });
    pushMessage({
      role: "assistant",
      kind: "text",
      text: `Applying ${style} filter… ✨`,
    });

    try {
      const res = await applyStyleFilter(conversationId, style)  // ← changed
      setPhase("active");
      setMessages((prev) => [
        ...prev.slice(0, -1),
        makeMessage({
          role: "assistant",
          kind: "style-result",
          imageResultData: res.data,
          text: res.data.message,
        }),
        makeMessage({
          role: "assistant",
          kind: "options-prompt",
          text: "Want to try another style or something else?",
        }),
      ]);
    } catch (err) {
      setPhase("active");
      pushError(err, "confirmStyle");
    }
  },
  [conversationId, pushMessage, pushError]
);

  /**
   * End the current conversation
   */
  const endChat = useCallback(async () => {
    if (!conversationId) return;
    setPhase("loading");

    try {
      await endConversation(conversationId);
      setPhase("completed");
      pushMessage({
        role: "assistant",
        kind: "text",
        text: "Conversation ended. Hope you loved the results! 🎞️ Refresh to start a new one.",
      });
    } catch (err) {
      setPhase("active");
      pushError(err, "endChat");
    }
  }, [conversationId, pushMessage, pushError]);

  return {
    messages,
    conversationId,
    phase,
    error,
    uploadImage,
    requestCaptions,
    requestEdits,
    confirmEdits,
    requestStyles,
    confirmStyle,
    endChat,
  };
}