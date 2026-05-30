package com.pixai.api.dto.response

import io.swagger.v3.oas.annotations.media.Schema

@Schema(description = "A single edit suggestion")
data class EditSuggestionResponse(
    @Schema(description = "Parameter to edit e.g. brightness, contrast") val parameter: String,
    @Schema(description = "Current estimated state") val currentEstimate: String,
    @Schema(description = "Suggested adjustment value between -1.0 and 1.0") val suggestedValue: Double,
    @Schema(description = "Why this edit would improve the image") val reason: String
)

@Schema(description = "Edit suggestions result")
data class EditResponse(
    @Schema(description = "Overall image quality assessment") val overallAssessment: String,
    @Schema(description = "List of edit suggestions") val suggestions: List<EditSuggestionResponse>
)