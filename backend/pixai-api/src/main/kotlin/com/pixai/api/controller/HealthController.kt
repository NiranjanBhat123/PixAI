package com.pixai.api.controller

import com.pixai.api.dto.ApiResponse
import com.pixai.api.dto.HealthResponse
import com.pixai.common.exception.PixAIException
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/v1/health")
class HealthController {

    @GetMapping
    fun health(): ApiResponse<HealthResponse> {
        return ApiResponse(
            success = true,
            data = HealthResponse(
                status = "UP",
                service = "PixAI"
            )
        )
    }

    @GetMapping("/error")
    fun error() {
        throw PixAIException("Testing Global Exception Handler")
    }
}