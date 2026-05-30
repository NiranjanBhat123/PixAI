package com.pixai.api.dto.response

import io.swagger.v3.oas.annotations.media.Schema
import java.time.Instant

@Schema(description = "Conversation details")
data class ConversationResponse(
    @Schema(description = "Unique conversation ID") val id: String,
    @Schema(description = "Current status of the conversation") val status: String,
    @Schema(description = "When the conversation was created") val createdAt: Instant
)