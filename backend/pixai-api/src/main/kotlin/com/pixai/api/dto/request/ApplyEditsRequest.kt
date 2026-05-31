package com.pixai.api.dto.request

import io.swagger.v3.oas.annotations.media.Schema

@Schema(description = "Parameters for applying image edits")
data class ApplyEditsRequest(
    @Schema(description = "Brightness adjustment -1.0 to 1.0", example = "0.15")
    val brightness: Double = 0.0,

    @Schema(description = "Contrast adjustment -1.0 to 1.0", example = "0.1")
    val contrast: Double = 0.0,

    @Schema(description = "Saturation adjustment -1.0 to 1.0", example = "0.1")
    val saturation: Double = 0.0,

    @Schema(description = "Sharpness adjustment -1.0 to 1.0", example = "0.2")
    val sharpness: Double = 0.0,

    @Schema(description = "Warmth adjustment -1.0 to 1.0", example = "-0.15")
    val warmth: Double = 0.0
)