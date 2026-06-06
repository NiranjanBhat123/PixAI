package com.pixai.api.dto.request

import io.swagger.v3.oas.annotations.media.Schema

@Schema(description = "Request to apply a Pillow-based style filter")
data class ApplyStyleFilterRequest(
    @Schema(
        description = "Style filter to apply",
        example = "pencil_sketch",
        allowableValues = ["pencil_sketch", "vintage", "oil_painting", "emboss"]
    )
    val filter: String
)