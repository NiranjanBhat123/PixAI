package com.pixai.infrastructure.persistence.mapper

import com.pixai.domain.image.Image
import com.pixai.infrastructure.persistence.document.ImageDocument

object ImageMapper {

    fun toDomain(document: ImageDocument): Image {
        return Image(
            id = document.id,
            conversationId = document.conversationId,
            filename = document.filename,
            contentType = document.contentType,
            base64Data = document.base64Data,
            sizeBytes = document.sizeBytes,
            createdAt = document.createdAt
        )
    }

    fun toDocument(image: Image): ImageDocument {
        return ImageDocument(
            id = image.id,
            conversationId = image.conversationId,
            filename = image.filename,
            contentType = image.contentType,
            base64Data = image.base64Data,
            sizeBytes = image.sizeBytes,
            createdAt = image.createdAt
        )
    }
}