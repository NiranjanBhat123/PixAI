package com.pixai.domain.image

import java.time.Instant

data class Image(
    val id: String? = null,
    val conversationId: String,
    val filename: String,
    val contentType: String,
    val base64Data: String,
    val sizeBytes: Long,
    val createdAt: Instant = Instant.now()
)