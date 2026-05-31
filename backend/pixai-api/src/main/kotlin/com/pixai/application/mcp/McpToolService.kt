package com.pixai.application.mcp

import com.fasterxml.jackson.databind.ObjectMapper
import com.pixai.common.exception.PixAIException
import com.pixai.domain.ai.CaptionResult
import com.pixai.domain.ai.EditResult
import com.pixai.domain.ai.StyleResult
import com.pixai.domain.ai.ImageResult
import com.pixai.config.McpConfig
import io.modelcontextprotocol.spec.McpSchema
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import reactor.core.publisher.Mono
import java.time.Duration

interface McpToolService {
    fun suggestCaptions(imageBase64: String): Mono<CaptionResult>
    fun suggestEdits(imageBase64: String): Mono<EditResult>
    fun suggestStyles(imageBase64: String): Mono<StyleResult>
    fun applyImageEdits(imageBase64: String, params: Map<String, Any>): Mono<ImageResult>
    fun generateStyledImage(imageBase64: String, style: String, description: String): Mono<ImageResult>
}

@Service
class McpToolServiceImpl(
    private val mcpConfig: McpConfig,       // ← inject McpConfig, not McpAsyncClient
    private val objectMapper: ObjectMapper
) : McpToolService {

    private val logger = LoggerFactory.getLogger(McpToolServiceImpl::class.java)

    // Volatile so all threads see the latest reconnected client
    @Volatile
    private var client = mcpConfig.buildAndInitClient()

    private fun callTool(toolName: String, args: Map<String, Any>): Mono<String> {
        logger.info("Calling MCP tool: {}", toolName)
        val operationTimeout = if (toolName.contains("styled_image"))
            Duration.ofSeconds(120) else Duration.ofSeconds(45)

        return attemptCall(toolName, args, operationTimeout)
            .onErrorResume { ex ->
                // Stale session → reconnect once and retry
                if (ex.message?.contains("404") == true || ex.message?.contains("session") == true) {
                    logger.warn("Stale session detected for tool '{}', reconnecting...", toolName)
                    reconnect()
                    attemptCall(toolName, args, operationTimeout)
                } else {
                    Mono.error(ex)
                }
            }
            .onErrorMap { ex ->
                if (ex is PixAIException) ex
                else {
                    val message = if (ex.message?.contains("timeout") == true)
                        "MCP tool '$toolName' timed out. Try again with a smaller image."
                    else
                        "MCP tool '$toolName' failed: ${ex.message}"
                    PixAIException(message)
                }
            }
    }

    private fun attemptCall(toolName: String, args: Map<String, Any>, timeout: Duration): Mono<String> {
        val request = McpSchema.CallToolRequest(toolName, args)
        return Mono.from(client.callTool(request))
            .timeout(timeout)
            .map { result ->
                val text = result.content
                    .filterIsInstance<McpSchema.TextContent>()
                    .firstOrNull()?.text
                    ?: throw PixAIException("Empty response from MCP tool: $toolName")
                logger.info("MCP tool '{}' responded with {} chars", toolName, text.length)
                text
            }
    }

    @Synchronized
    private fun reconnect() {
        try {
            logger.info("Reconnecting MCP client...")
            client = mcpConfig.buildAndInitClient()
            logger.info("MCP client reconnected successfully")
        } catch (e: Exception) {
            logger.error("MCP reconnection failed: {}", e.message)
            throw PixAIException("Could not reconnect to MCP server: ${e.message}")
        }
    }

    override fun suggestCaptions(imageBase64: String): Mono<CaptionResult> =
        callTool("suggest_captions", mapOf("image_base64" to imageBase64))
            .map { objectMapper.readValue(it, CaptionResult::class.java) }

    override fun suggestEdits(imageBase64: String): Mono<EditResult> =
        callTool("suggest_edits", mapOf("image_base64" to imageBase64))
            .map { objectMapper.readValue(it, EditResult::class.java) }

    override fun suggestStyles(imageBase64: String): Mono<StyleResult> =
        callTool("suggest_styles", mapOf("image_base64" to imageBase64))
            .map { objectMapper.readValue(it, StyleResult::class.java) }

    override fun applyImageEdits(imageBase64: String, params: Map<String, Any>): Mono<ImageResult> =
        callTool("apply_image_edits", mapOf("image_base64" to imageBase64) + params)
            .map { objectMapper.readValue(it, ImageResult::class.java) }

    override fun generateStyledImage(imageBase64: String, style: String, description: String): Mono<ImageResult> =
        callTool(
            "generate_styled_image",
            mapOf("image_base64" to imageBase64, "style" to style, "style_description" to description)
        ).map { objectMapper.readValue(it, ImageResult::class.java) }
}