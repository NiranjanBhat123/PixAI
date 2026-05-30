package com.pixai.infrastructure.persistence.repository

import com.pixai.infrastructure.persistence.document.ConversationDocument
import org.springframework.data.mongodb.repository.ReactiveMongoRepository

interface ConversationRepository : ReactiveMongoRepository<ConversationDocument, String>