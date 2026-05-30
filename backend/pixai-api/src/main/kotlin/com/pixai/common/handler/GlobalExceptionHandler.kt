package com.pixai.common.handler

import com.pixai.common.exception.ErrorResponse
import com.pixai.common.exception.PixAIException
import org.slf4j.LoggerFactory
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.ExceptionHandler
import org.springframework.web.bind.annotation.RestControllerAdvice
import org.springframework.web.server.ServerWebInputException
import reactor.core.publisher.Mono

@RestControllerAdvice
class GlobalExceptionHandler {

    private val logger = LoggerFactory.getLogger(GlobalExceptionHandler::class.java)

    @ExceptionHandler(PixAIException::class)
    fun handlePixAIException(
        ex: PixAIException
    ): Mono<ResponseEntity<ErrorResponse>> {
        logger.warn("PixAI business exception: {}", ex.message)
        return Mono.just(
            ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(ErrorResponse(message = ex.message ?: "Unknown error"))
        )
    }

    @ExceptionHandler(ServerWebInputException::class)
    fun handleValidationException(
        ex: ServerWebInputException
    ): Mono<ResponseEntity<ErrorResponse>> {
        logger.warn("Validation exception: {}", ex.message)
        return Mono.just(
            ResponseEntity
                .status(HttpStatus.BAD_REQUEST)
                .body(ErrorResponse(message = "Invalid request: ${ex.reason}"))
        )
    }

    @ExceptionHandler(Exception::class)
    fun handleGenericException(
        ex: Exception
    ): Mono<ResponseEntity<ErrorResponse>> {
        logger.error("Unexpected error: {}", ex.message, ex)
        return Mono.just(
            ResponseEntity
                .status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ErrorResponse(message = "Internal server error"))
        )
    }
}