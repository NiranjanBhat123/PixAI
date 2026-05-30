package com.pixai.domain.conversation

import java.time.Instant

data class Conversation(
    val id: String? = null,

    val imageId: String,

    val status: ConversationStatus = ConversationStatus.ACTIVE,

    val createdAt: Instant = Instant.now(),

    val updatedAt: Instant = Instant.now()
)