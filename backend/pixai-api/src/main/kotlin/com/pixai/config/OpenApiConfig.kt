package com.pixai.config

import io.swagger.v3.oas.models.OpenAPI
import io.swagger.v3.oas.models.info.Contact
import io.swagger.v3.oas.models.info.Info
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration

@Configuration
class OpenApiConfig {

    @Bean
    fun customOpenApi(): OpenAPI {
        return OpenAPI()
            .info(
                Info()
                    .title("PixAI API")
                    .version("v1")
                    .description("PixAI Image Assistant API")
                    .contact(
                        Contact()
                            .name("Niranjan")
                            .email("niranjan@example.com")
                    )
            )
    }
}