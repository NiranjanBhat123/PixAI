package com.pixai.infrastructure.persistence.mapper
import com.pixai.domain.conversation.Conversation
import com.pixai.infrastructure.persistence.document.ConversationDocument

object ConversationMapper {

    fun toDomain(
        document: ConversationDocument
    ): Conversation {

        return Conversation(
            id = document.id,
            imageId = document.imageId,
            status = document.status,
            createdAt = document.createdAt,
            updatedAt = document.updatedAt
        )
    }

    fun toDocument(
        conversation: Conversation
    ): ConversationDocument {

        return ConversationDocument(
            id = conversation.id,
            imageId = conversation.imageId,
            status = conversation.status,
            createdAt = conversation.createdAt,
            updatedAt = conversation.updatedAt
        )
    }
}