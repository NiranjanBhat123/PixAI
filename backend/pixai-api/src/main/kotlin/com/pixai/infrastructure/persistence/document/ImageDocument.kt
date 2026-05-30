package com.pixai.infrastructure.persistence.document

import org.springframework.data.annotation.Id
import org.springframework.data.mongodb.core.index.Indexed
import org.springframework.data.mongodb.core.mapping.Document
import java.time.Instant

@Document(collection = "images")
data class ImageDocument(
    @Id
    val id: String? = null,
    @Indexed
    val conversationId: String,
    val filename: String,
    val contentType: String,
    val base64Data: String,
    val sizeBytes: Long,
    val createdAt: Instant
)