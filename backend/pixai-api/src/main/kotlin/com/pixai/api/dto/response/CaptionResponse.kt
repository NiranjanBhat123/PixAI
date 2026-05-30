package com.pixai.api.dto.response

import io.swagger.v3.oas.annotations.media.Schema

@Schema(description = "A single caption suggestion")
data class CaptionSuggestionResponse(
    @Schema(description = "The suggested caption text") val caption: String,
    @Schema(description = "Tone of the caption e.g. funny, poetic, minimal") val tone: String
)

@Schema(description = "Caption suggestions result")
data class CaptionResponse(
    @Schema(description = "Brief description of the image as seen by AI") val imageDescription: String,
    @Schema(description = "List of caption suggestions") val suggestions: List<CaptionSuggestionResponse>
)