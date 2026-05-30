package com.pixai.infrastructure.persistence.document  // was: persistance
import com.pixai.domain.conversation.ConversationStatus
import org.springframework.data.annotation.Id
import org.springframework.data.mongodb.core.mapping.Document
import java.time.Instant

@Document(collection = "conversations")
data class ConversationDocument(

    @Id
    val id: String? = null,

    val imageId: String,

    val status: ConversationStatus,

    val createdAt: Instant,

    val updatedAt: Instant
)