package com.pixai.domain.ai

data class EditSuggestion(
    val parameter: String,
    val currentEstimate: String,
    val suggestedValue: Double,
    val reason: String
)

data class EditResult(
    val suggestions: List<EditSuggestion>,
    val overallAssessment: String
)