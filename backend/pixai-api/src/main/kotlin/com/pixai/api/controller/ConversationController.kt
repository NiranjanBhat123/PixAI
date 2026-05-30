package com.pixai.api.controller

import com.pixai.api.dto.ApiResponse
import com.pixai.api.dto.response.AiResponseMapper
import com.pixai.api.dto.response.CaptionResponse
import com.pixai.api.dto.response.ConversationResponse
import com.pixai.api.dto.response.EditResponse
import com.pixai.api.dto.response.StyleResponse
import com.pixai.application.conversation.ConversationService
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.Parameter
import io.swagger.v3.oas.annotations.media.Content
import io.swagger.v3.oas.annotations.media.Schema
import io.swagger.v3.oas.annotations.responses.ApiResponses
import io.swagger.v3.oas.annotations.tags.Tag
import org.slf4j.LoggerFactory
import org.springframework.http.HttpStatus
import org.springframework.http.MediaType
import org.springframework.http.codec.multipart.FilePart
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RequestPart
import org.springframework.web.bind.annotation.ResponseStatus
import org.springframework.web.bind.annotation.RestController
import reactor.core.publisher.Mono

@Tag(name = "Conversations", description = "Manage image conversations and AI suggestions")
@RestController
@RequestMapping("/api/v1/conversations")
class ConversationController(
    private val conversationService: ConversationService
) {

    private val logger = LoggerFactory.getLogger(ConversationController::class.java)

    @Operation(
        summary = "Upload an image and start a conversation",
        description = "Accepts a JPEG or PNG image and creates a new AI conversation session"
    )
    @ApiResponses(
        io.swagger.v3.oas.annotations.responses.ApiResponse(
            responseCode = "201",
            description = "Conversation created successfully",
            content = [Content(schema = Schema(implementation = ConversationResponse::class))]
        )
    )
    @PostMapping(consumes = [MediaType.MULTIPART_FORM_DATA_VALUE])
    @ResponseStatus(HttpStatus.CREATED)
    fun createConversation(
        @Parameter(description = "Image file (JPEG or PNG)")
        @RequestPart("image") filePart: FilePart
    ): Mono<ApiResponse<ConversationResponse>> {
        logger.info("Received image upload: {}", filePart.filename())

        return filePart.content()
            .flatMap { dataBuffer ->
                val bytes = ByteArray(dataBuffer.readableByteCount())
                dataBuffer.read(bytes)
                reactor.core.publisher.Mono.just(bytes)
            }
            .reduce { acc, next -> acc + next }   // combine all chunks into one byte array
            .flatMap { imageBytes ->
                val contentType = filePart.headers().contentType?.toString() ?: "image/jpeg"
                conversationService.createConversation(
                    imageBytes = imageBytes,
                    filename = filePart.filename(),
                    contentType = contentType
                )
            }
            .map { conversation ->
                ApiResponse(
                    success = true,
                    data = AiResponseMapper.toConversationResponse(conversation),
                    message = "Conversation started! You can now request captions, edits, or style suggestions."
                )
            }
    }

    @Operation(summary = "Get conversation details")
    @GetMapping("/{conversationId}")
    fun getConversation(
        @Parameter(description = "Conversation ID") @PathVariable conversationId: String
    ): Mono<ApiResponse<ConversationResponse>> {
        logger.info("Fetching conversation: {}", conversationId)
        return conversationService.getConversation(conversationId)
            .map { ApiResponse(success = true, data = AiResponseMapper.toConversationResponse(it)) }
    }

    @Operation(
        summary = "Get AI caption suggestions",
        description = "Analyzes the uploaded image and returns 4 creative captions with different tones"
    )
    @PostMapping("/{conversationId}/captions")
    fun getCaptions(
        @Parameter(description = "Conversation ID") @PathVariable conversationId: String
    ): Mono<ApiResponse<CaptionResponse>> {
        logger.info("Caption request for conversation: {}", conversationId)
        return conversationService.getCaptions(conversationId)
            .map { ApiResponse(success = true, data = AiResponseMapper.toCaptionResponse(it)) }
    }

    @Operation(
        summary = "Get AI edit suggestions",
        description = "Analyzes brightness, contrast, saturation and suggests specific adjustments"
    )
    @PostMapping("/{conversationId}/edits")
    fun getEdits(
        @Parameter(description = "Conversation ID") @PathVariable conversationId: String
    ): Mono<ApiResponse<EditResponse>> {
        logger.info("Edit suggestions request for conversation: {}", conversationId)
        return conversationService.getEdits(conversationId)
            .map { ApiResponse(success = true, data = AiResponseMapper.toEditResponse(it)) }
    }

    @Operation(
        summary = "Get AI style suggestions",
        description = "Suggests artistic versions: Ghibli, B&W, pencil sketch, cartoon"
    )
    @PostMapping("/{conversationId}/styles")
    fun getStyles(
        @Parameter(description = "Conversation ID") @PathVariable conversationId: String
    ): Mono<ApiResponse<StyleResponse>> {
        logger.info("Style suggestions request for conversation: {}", conversationId)
        return conversationService.getStyles(conversationId)
            .map { ApiResponse(success = true, data = AiResponseMapper.toStyleResponse(it)) }
    }
}