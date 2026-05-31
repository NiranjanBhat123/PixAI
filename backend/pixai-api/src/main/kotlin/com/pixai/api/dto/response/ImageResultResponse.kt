package com.pixai.api.dto.response

import io.swagger.v3.oas.annotations.media.Schema

@Schema(description = "Result containing the generated or edited image")
data class ImageResultResponse(
    @Schema(description = "Base64 encoded image") val imageBase64: String,
    @Schema(description = "Image format e.g. jpeg") val format: String,
    @Schema(description = "Description of what was done") val message: String
)