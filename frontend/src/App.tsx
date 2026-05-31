import { useRef, useEffect, useCallback, useState } from "react";
import { useConversation } from "./hooks/UserConversation";
import type { ChatMessage, EditSuggestion, StyleSuggestion } from "./types/Index";
import "./App.css";

// ─── Small utility components ────────────────────────────────────────

function Spinner() {
  return (
    <span className="spinner" aria-label="Loading">
      <span />
      <span />
      <span />
    </span>
  );
}

function Timestamp({ date }: { date: Date }) {
  return (
    <time className="msg-time">
      {date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
    </time>
  );
}

// ─── Message bubble renderers ────────────────────────────────────────

function ImageUploadBubble({ msg }: { msg: ChatMessage }) {
  return (
    <div className="msg msg--user">
      <div className="bubble bubble--user">
        {msg.uploadedImageUrl && (
          <img
            src={msg.uploadedImageUrl}
            alt="Uploaded"
            className="uploaded-img"
          />
        )}
        <span className="img-filename">{msg.text}</span>
      </div>
      <Timestamp date={msg.timestamp} />
    </div>
  );
}

function TextBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === "user";
  return (
    <div className={`msg msg--${isUser ? "user" : "assistant"}`}>
      {!isUser && <div className="avatar">✦</div>}
      <div className={`bubble bubble--${isUser ? "user" : "assistant"}`}>
        {msg.text}
      </div>
      <Timestamp date={msg.timestamp} />
    </div>
  );
}

function CaptionsBubble({ msg }: { msg: ChatMessage }) {
  const data = msg.captionData!;
  return (
    <div className="msg msg--assistant">
      <div className="avatar">✦</div>
      <div className="bubble bubble--assistant bubble--wide">
        <p className="bubble-label">Image read</p>
        <p className="img-desc">{data.imageDescription}</p>
        <p className="bubble-label" style={{ marginTop: "1rem" }}>Caption suggestions</p>
        <div className="caption-grid">
          {data.suggestions.map((s, i) => (
            <div key={i} className="caption-card">
              <span className="tone-badge">{s.tone}</span>
              <p className="caption-text">"{s.caption}"</p>
            </div>
          ))}
        </div>
      </div>
      <Timestamp date={msg.timestamp} />
    </div>
  );
}

function EditsBubble({
  msg,
  onConfirm,
}: {
  msg: ChatMessage;
  onConfirm: (params: Record<string, number>) => void;
}) {
  const data = msg.editData!;

  // Build a map of parameter → suggestedValue for the confirm action
  const suggested: Record<string, number> = {};
  data.suggestions.forEach((s: EditSuggestion) => {
    suggested[s.parameter.toLowerCase()] = s.suggestedValue;
  });

  const defaults = {
    brightness: 0,
    contrast: 0,
    saturation: 0,
    sharpness: 0,
    warmth: 0,
  };
  const params = { ...defaults, ...suggested };

  return (
    <div className="msg msg--assistant">
      <div className="avatar">✦</div>
      <div className="bubble bubble--assistant bubble--wide">
        <p className="bubble-label">Overall assessment</p>
        <p className="img-desc">{data.overallAssessment}</p>
        <p className="bubble-label" style={{ marginTop: "1rem" }}>Suggested adjustments</p>
        <div className="edits-list">
          {data.suggestions.map((s: EditSuggestion, i: number) => (
            <div key={i} className="edit-row">
              <div className="edit-header">
                <span className="edit-param">{s.parameter}</span>
                <span className="edit-values">
                  {s.currentEstimate} → <strong>{s.suggestedValue > 0 ? `+${s.suggestedValue}` : s.suggestedValue}</strong>
                </span>
              </div>
              <p className="edit-reason">{s.reason}</p>
            </div>
          ))}
        </div>
        <div className="confirm-row">
          <button
            className="btn btn--primary"
            onClick={() => onConfirm(params)}
          >
            Apply these edits
          </button>
          <span className="confirm-hint">or scroll up to try something else</span>
        </div>
      </div>
      <Timestamp date={msg.timestamp} />
    </div>
  );
}

function ImageResultBubble({ msg }: { msg: ChatMessage }) {
    const data = msg.imageResultData!;
  const src = `data:image/${data.format || "jpeg"};base64,${data.image_base64}`;

  const handleDownload = () => {
    const a = document.createElement("a");
    a.href = src;
    a.download = `pixai-result.${data.format || "jpg"}`;
    a.click();
  };

  return (
    <div className="msg msg--assistant">
      <div className="avatar">✦</div>
      <div className="bubble bubble--assistant bubble--wide">
        {msg.text && <p className="img-desc">{msg.text}</p>}
        <img src={src} alt="Edited" className="result-img" />
        <button className="btn btn--ghost" onClick={handleDownload}>
          ↓ Download
        </button>
      </div>
      <Timestamp date={msg.timestamp} />
    </div>
  );
}

function StylesBubble({
  msg,
  onSelect,
}: {
  msg: ChatMessage;
  onSelect: (style: string, description: string) => void;
}) {
  const data = msg.styleData!;
  return (
    <div className="msg msg--assistant">
      <div className="avatar">✦</div>
      <div className="bubble bubble--assistant bubble--wide">
        <p className="bubble-label">Style options</p>
        <div className="style-grid">
          {data.suggestions.map((s: StyleSuggestion, i: number) => (
            <button
              key={i}
              className="style-card"
              onClick={() => onSelect(s.style, s.description)}
            >
              <span className="style-name">{s.style}</span>
              <span className="style-desc">{s.description}</span>
              <span className="style-appeal">{s.appeal}</span>
            </button>
          ))}
        </div>
      </div>
      <Timestamp date={msg.timestamp} />
    </div>
  );
}

function OptionsPrompt({
  msg,
  onCaption,
  onEdit,
  onStyle,
}: {
  msg: ChatMessage;
  onCaption: () => void;
  onEdit: () => void;
  onStyle: () => void;
}) {
  return (
    <div className="msg msg--assistant">
      <div className="avatar">✦</div>
      <div className="bubble bubble--assistant bubble--wide">
        <p style={{ marginBottom: "0.75rem", opacity: 0.8 }}>{msg.text}</p>
        <div className="options-row">
          <button className="option-btn" onClick={onCaption}>
            <span className="option-icon">✍️</span>
            <span>Caption ideas</span>
          </button>
          <button className="option-btn" onClick={onEdit}>
            <span className="option-icon">🎨</span>
            <span>Edit photo</span>
          </button>
          <button className="option-btn" onClick={onStyle}>
            <span className="option-icon">🎭</span>
            <span>Artistic styles</span>
          </button>
        </div>
      </div>
      <Timestamp date={msg.timestamp} />
    </div>
  );
}

// ─── Drop zone ───────────────────────────────────────────────────────

function DropZone({ onFile }: { onFile: (file: File) => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    if (!file.type.startsWith("image/")) return;
    onFile(file);
  };

  return (
    <div
      className={`drop-zone ${dragging ? "drop-zone--dragging" : ""}`}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        handleFiles(e.dataTransfer.files);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        style={{ display: "none" }}
        onChange={(e) => handleFiles(e.target.files)}
      />
      <div className="drop-icon">⬡</div>
      <p className="drop-label">Drop your photo here</p>
      <p className="drop-hint">JPEG · PNG · WEBP</p>
    </div>
  );
}

// ─── Main App ────────────────────────────────────────────────────────

export default function App() {
  const {
    messages,
    phase,
    uploadImage,
    requestCaptions,
    requestEdits,
    confirmEdits,
    requestStyles,
    confirmStyle,
    endChat,
  } = useConversation();

  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to newest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleFile = useCallback(
    (file: File) => {
      if (phase !== "idle") return; // only one upload per conversation
      uploadImage(file);
    },
    [phase, uploadImage]
  );

  const isLoading = phase === "loading";
  const isCompleted = phase === "completed";

  return (
    <div className="app">
      {/* ── Header ── */}
      <header className="header">
        <div className="header-logo">
          <span className="logo-mark">✦</span>
          <span className="logo-text">PixAI</span>
        </div>
        {phase === "active" && (
          <button className="btn btn--danger-ghost" onClick={endChat}>
            End session
          </button>
        )}
      </header>

      {/* ── Chat feed ── */}
      <main className="chat-feed">
        {messages.map((msg) => {
          switch (msg.kind) {
            case "image-upload":
              return <ImageUploadBubble key={msg.id} msg={msg} />;

            case "captions":
              return <CaptionsBubble key={msg.id} msg={msg} />;

            case "edits":
              return (
                <EditsBubble
                  key={msg.id}
                  msg={msg}
                  onConfirm={(params) =>
                    confirmEdits({
                      brightness: params.brightness ?? 0,
                      contrast: params.contrast ?? 0,
                      saturation: params.saturation ?? 0,
                      sharpness: params.sharpness ?? 0,
                      warmth: params.warmth ?? 0,
                    })
                  }
                />
              );

            case "edit-result":
            case "style-result":
              return <ImageResultBubble key={msg.id} msg={msg} />;

            case "styles":
              return (
                <StylesBubble
                  key={msg.id}
                  msg={msg}
                  onSelect={confirmStyle}
                />
              );

            case "options-prompt":
              return (
                <OptionsPrompt
                  key={msg.id}
                  msg={msg}
                  onCaption={requestCaptions}
                  onEdit={requestEdits}
                  onStyle={requestStyles}
                />
              );

            default:
              return <TextBubble key={msg.id} msg={msg} />;
          }
        })}

        {/* Loading indicator */}
        {isLoading && (
          <div className="msg msg--assistant">
            <div className="avatar">✦</div>
            <div className="bubble bubble--assistant bubble--loading">
              <Spinner />
            </div>
          </div>
        )}

        {/* Drop zone — shown only when idle */}
        {phase === "idle" && (
          <div className="msg msg--assistant drop-wrapper">
            <div className="avatar">✦</div>
            <DropZone onFile={handleFile} />
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      {/* ── Footer ── */}
      <footer className="footer">
        {isCompleted ? (
          <p className="footer-note">Session ended · Refresh to start over</p>
        ) : (
          <p className="footer-note">
            {phase === "idle"
              ? "Upload a photo to begin"
              : phase === "loading"
              ? "Thinking…"
              : "Choose an action above"}
          </p>
        )}
      </footer>
    </div>
  );
}