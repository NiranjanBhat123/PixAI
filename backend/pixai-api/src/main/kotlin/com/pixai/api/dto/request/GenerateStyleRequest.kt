package com.pixai.api.dto.request

import io.swagger.v3.oas.annotations.media.Schema

@Schema(description = "Request to generate a styled version of the image")
data class GenerateStyleRequest(
    @Schema(description = "Style to apply", example = "ghibli",
        allowableValues = ["ghibli", "black_and_white", "pencil_sketch", "cartoon"])
    val style: String,

    @Schema(description = "Optional custom description for the style")
    val styleDescription: String = ""
)