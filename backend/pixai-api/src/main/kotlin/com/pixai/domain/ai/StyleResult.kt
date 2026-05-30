package com.pixai.domain.ai

data class StyleSuggestion(
    val style: String,
    val description: String,
    val appeal: String
)

data class StyleResult(
    val suggestions: List<StyleSuggestion>
)