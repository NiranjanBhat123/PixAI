package com.pixai.domain.ai

import com.fasterxml.jackson.annotation.JsonProperty

data class EditSuggestion(
    @JsonProperty("parameter")
    val parameter: String,

    @JsonProperty("current_estimate")
    val currentEstimate: String,

    @JsonProperty("suggested_value")
    val suggestedValue: Double,

    @JsonProperty("reason")
    val reason: String
)

data class EditResult(
    @JsonProperty("overall_assessment")
    val overallAssessment: String,

    @JsonProperty("suggestions")
    val suggestions: List<EditSuggestion>
)