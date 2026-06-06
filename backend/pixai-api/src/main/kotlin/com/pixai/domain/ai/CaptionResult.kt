package com.pixai.domain.ai

data class CaptionSuggestion(
    val caption: String,
    val tone: String
)

data class CaptionResult(
    val suggestions: List<CaptionSuggestion> = emptyList(),
    val imageDescription: String = "",
    val error: String? = null
)