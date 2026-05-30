package com.pixai.api.dto.response

import io.swagger.v3.oas.annotations.media.Schema

@Schema(description = "A single style suggestion")
data class StyleSuggestionResponse(
    @Schema(description = "Style type e.g. ghibli, black_and_white") val style: String,
    @Schema(description = "How this style would look on this specific image") val description: String,
    @Schema(description = "Why this style suits this image") val appeal: String
)

@Schema(description = "Style suggestions result")
data class StyleResponse(
    @Schema(description = "List of style suggestions ranked by suitability") val suggestions: List<StyleSuggestionResponse>
)