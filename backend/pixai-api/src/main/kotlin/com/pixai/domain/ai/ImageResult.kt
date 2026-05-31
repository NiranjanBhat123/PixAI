package com.pixai.domain.ai

data class ImageResult(
    val imageBase64: String,
    val format: String,
    val message: String
)