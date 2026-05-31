package com.pixai.application.conversation

import com.pixai.application.mcp.McpToolService
import com.pixai.common.exception.PixAIException
import com.pixai.domain.ai.CaptionResult
import com.pixai.domain.ai.EditResult
import com.pixai.domain.ai.StyleResult
import com.pixai.domain.ai.ImageResult
import com.pixai.domain.conversation.Conversation
import com.pixai.domain.conversation.ConversationStatus
import com.pixai.domain.image.Image
import com.pixai.api.dto.request.ApplyEditsRequest
import com.pixai.infrastructure.persistence.mapper.ConversationMapper
import com.pixai.infrastructure.persistence.mapper.ImageMapper
import com.pixai.infrastructure.persistence.repository.ConversationRepository
import com.pixai.infrastructure.persistence.repository.ImageRepository
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import reactor.core.publisher.Mono
import java.time.Instant
import java.util.Base64

// --- Interface ---
interface ConversationService {
    fun createConversation(
        imageBytes: ByteArray,
        filename: String,
        contentType: String
    ): Mono<Conversation>

    fun getConversation(conversationId: String): Mono<Conversation>
    fun getCaptions(conversationId: String): Mono<CaptionResult>
    fun getEdits(conversationId: String): Mono<EditResult>
    fun getStyles(conversationId: String): Mono<StyleResult>
    fun applyEdits(conversationId: String, request: ApplyEditsRequest): Mono<ImageResult>
    fun generateStyle(conversationId: String, style: String, description: String): Mono<ImageResult>
    fun endConversation(conversationId: String): Mono<Conversation>

}

// --- Implementation ---
@Service
class ConversationServiceImpl(
    private val conversationRepository: ConversationRepository,
    private val imageRepository: ImageRepository,
    private val mcpToolService: McpToolService
) : ConversationService {

    private val logger = LoggerFactory.getLogger(ConversationServiceImpl::class.java)

    override fun createConversation(
        imageBytes: ByteArray,
        filename: String,
        contentType: String
    ): Mono<Conversation> {
        logger.info("Creating new conversation for image: {}", filename)

        // Step 1: Save a placeholder conversation to get an ID
        val newConversation = Conversation(
            imageId = "",  // will be updated after image is saved
            status = ConversationStatus.ACTIVE
        )

        return conversationRepository.save(ConversationMapper.toDocument(newConversation))
            .flatMap { savedConversationDoc ->
                val conversationId = savedConversationDoc.id!!

                // Step 2: Save image with the conversationId
                val image = Image(
                    conversationId = conversationId,
                    filename = filename,
                    contentType = contentType,
                    base64Data = Base64.getEncoder().encodeToString(imageBytes),
                    sizeBytes = imageBytes.size.toLong(),
                    createdAt = Instant.now()
                )

                imageRepository.save(ImageMapper.toDocument(image))
                    .flatMap { savedImageDoc ->
                        // Step 3: Update conversation with real imageId
                        val updatedDoc = savedConversationDoc.copy(
                            imageId = savedImageDoc.id!!,
                            updatedAt = Instant.now()
                        )
                        conversationRepository.save(updatedDoc)
                    }
            }
            .map { ConversationMapper.toDomain(it) }
            .doOnSuccess { logger.info("Conversation created: {}", it.id) }
    }

    override fun getConversation(conversationId: String): Mono<Conversation> {
        return conversationRepository.findById(conversationId)
            .switchIfEmpty(
                Mono.error(PixAIException("Conversation not found: $conversationId"))
            )
            .map { ConversationMapper.toDomain(it) }
    }

    override fun getCaptions(conversationId: String): Mono<CaptionResult> {
        logger.info("Getting captions for conversation: {}", conversationId)
        return fetchImageBase64(conversationId)
            .flatMap { mcpToolService.suggestCaptions(it) }
    }

    override fun getEdits(conversationId: String): Mono<EditResult> {
        logger.info("Getting edit suggestions for conversation: {}", conversationId)
        return fetchImageBase64(conversationId)
            .flatMap { mcpToolService.suggestEdits(it) }
    }

    override fun getStyles(conversationId: String): Mono<StyleResult> {
        logger.info("Getting style suggestions for conversation: {}", conversationId)
        return fetchImageBase64(conversationId)
            .flatMap { mcpToolService.suggestStyles(it) }
    }

    override fun applyEdits(conversationId: String, request: ApplyEditsRequest): Mono<ImageResult> {
    logger.info("Applying edits for conversation: {}", conversationId)
    return fetchImageBase64(conversationId).flatMap { imageBase64 ->
        val params = mapOf(
            "brightness" to request.brightness,
            "contrast" to request.contrast,
            "saturation" to request.saturation,
            "sharpness" to request.sharpness,
            "warmth" to request.warmth
        )
        mcpToolService.applyImageEdits(imageBase64, params)
    }
}

override fun generateStyle(conversationId: String, style: String, description: String): Mono<ImageResult> {
    logger.info("Generating style '{}' for conversation: {}", style, conversationId)
    return fetchImageBase64(conversationId)
        .flatMap { mcpToolService.generateStyledImage(it, style, description) }
}

override fun endConversation(conversationId: String): Mono<Conversation> {
    logger.info("Ending conversation: {}", conversationId)
    return conversationRepository.findById(conversationId)
        .switchIfEmpty(Mono.error(PixAIException("Conversation not found: $conversationId")))
        .flatMap { doc ->
            val updated = doc.copy(
                status = ConversationStatus.COMPLETED,
                updatedAt = Instant.now()
            )
            conversationRepository.save(updated)
        }
        .map { ConversationMapper.toDomain(it) }
        .doOnSuccess { logger.info("Conversation ended: {}", it.id) }
}

    // Private helper — fetches image base64 for a conversation
    private fun fetchImageBase64(conversationId: String): Mono<String> {
        return conversationRepository.findById(conversationId)
            .switchIfEmpty(
                Mono.error(PixAIException("Conversation not found: $conversationId"))
            )
            .flatMap { conversationDoc ->
                imageRepository.findByConversationId(conversationDoc.id!!)
                    .switchIfEmpty(
                        Mono.error(PixAIException("Image not found for conversation: $conversationId"))
                    )
            }
            .map { it.base64Data }
    }
}