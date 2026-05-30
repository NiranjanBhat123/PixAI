package com.pixai.infrastructure.persistence.repository

import com.pixai.infrastructure.persistence.document.ImageDocument
import org.springframework.data.mongodb.repository.ReactiveMongoRepository
import reactor.core.publisher.Mono

interface ImageRepository : ReactiveMongoRepository<ImageDocument, String> {
    fun findByConversationId(conversationId: String): Mono<ImageDocument>
}