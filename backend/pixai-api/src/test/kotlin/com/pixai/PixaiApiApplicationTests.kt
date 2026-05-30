package com.pixai

import com.pixai.application.mcp.McpToolService
import io.modelcontextprotocol.client.McpAsyncClient
import org.junit.jupiter.api.Test
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.mock.mockito.MockBean

@SpringBootTest(
    webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT,
    properties = [
        "spring.data.mongodb.uri=mongodb://localhost:27017/pixai-test",
        "spring.ai.mcp.client.enabled=false"
    ]
)
class PixaiApiApplicationTests {

    @MockBean
    lateinit var mcpAsyncClient: McpAsyncClient

    @MockBean
    lateinit var mcpToolService: McpToolService

    @Test
    fun contextLoads() {
        // Verifies Spring context starts correctly
    }
}