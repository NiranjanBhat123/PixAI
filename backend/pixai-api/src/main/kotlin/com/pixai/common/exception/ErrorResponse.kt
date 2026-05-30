package com.pixai.common.exception

data class ErrorResponse(
    val success: Boolean = false,
    val message: String,
    val timestamp: Long = System.currentTimeMillis()
)