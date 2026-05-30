package com.pixai.application.mcp

import com.fasterxml.jackson.databind.ObjectMapper
import com.pixai.common.exception.PixAIException
import com.pixai.domain.ai.CaptionResult
import com.pixai.domain.ai.EditResult
import com.pixai.domain.ai.StyleResult
import io.modelcontextprotocol.client.McpAsyncClient
import io.modelcontextprotocol.spec.McpSchema
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import reactor.core.publisher.Mono

interface McpToolService {
    fun suggestCaptions(imageBase64: String): Mono<CaptionResult>
    fun suggestEdits(imageBase64: String): Mono<EditResult>
    fun suggestStyles(imageBase64: String): Mono<StyleResult>
}

@Service
class McpToolServiceImpl(
    private val mcpAsyncClient: McpAsyncClient,
    private val objectMapper: ObjectMapper
) : McpToolService {

    private val logger = LoggerFactory.getLogger(McpToolServiceImpl::class.java)

    private fun callTool(toolName: String, args: Map<String, Any>): Mono<String> {
        logger.info("Calling MCP tool: {}", toolName)
        val request = McpSchema.CallToolRequest(toolName, args)
        return Mono.from(mcpAsyncClient.callTool(request))
            .map { result ->
                val text = result.content
                    .filterIsInstance<McpSchema.TextContent>()
                    .firstOrNull()?.text
                    ?: throw PixAIException("Empty response from MCP tool: $toolName")
                logger.info("MCP tool {} responded with {} chars", toolName, text.length)
                text
            }
            .onErrorMap { ex ->
                if (ex is PixAIException) ex
                else PixAIException("MCP tool call failed for $toolName: ${ex.message}")
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
}