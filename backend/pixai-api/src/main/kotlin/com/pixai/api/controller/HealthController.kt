package com.pixai.api.controller

import com.pixai.api.dto.ApiResponse
import com.pixai.api.dto.HealthResponse
import com.pixai.common.exception.PixAIException
import io.swagger.v3.oas.annotations.Operation
import io.swagger.v3.oas.annotations.tags.Tag
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController
import reactor.core.publisher.Mono

@Tag(name = "Health", description = "Health check endpoints")
@RestController
@RequestMapping("/api/v1/health")
class HealthController {

    @Operation(summary = "Check service health")
    @GetMapping
    fun health(): Mono<ApiResponse<HealthResponse>> {
        return Mono.just(
            ApiResponse(
                success = true,
                data = HealthResponse(
                    status = "UP",
                    service = "PixAI"
                )
            )
        )
    }

    @Operation(summary = "Test error handling")
    @GetMapping("/error")
    fun error(): Mono<Nothing> {
        return Mono.error(PixAIException("Testing Global Exception Handler"))
    }
}