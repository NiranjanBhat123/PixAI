package com.pixai.config

import io.modelcontextprotocol.client.McpAsyncClient
import io.modelcontextprotocol.client.McpClient
import io.modelcontextprotocol.client.transport.HttpClientSseClientTransport
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import reactor.core.publisher.Mono
import java.time.Duration

@Configuration
class McpConfig(
    @Value("\${pixai.mcp.server.url:http://localhost:8000}")
    private val mcpServerUrl: String
) {

    private val logger = LoggerFactory.getLogger(McpConfig::class.java)

    @Bean
    fun mcpAsyncClient(): McpAsyncClient {
        logger.info("Creating MCP async client for server: {}", mcpServerUrl)

        val transport = HttpClientSseClientTransport
            .builder(mcpServerUrl)
            .build()

        val client = McpClient.async(transport)
            .requestTimeout(Duration.ofSeconds(30))
            .build()

        Mono.from(client.initialize())
            .doOnSuccess { logger.info("MCP client initialized. Server: {}", it.serverInfo) }
            .doOnError { logger.error("MCP client initialization failed: {}", it.message) }
            .block(Duration.ofSeconds(15))

        return client
    }
}