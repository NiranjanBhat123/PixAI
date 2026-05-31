package com.pixai.api.dto.response

import com.pixai.domain.ai.CaptionResult
import com.pixai.domain.ai.EditResult
import com.pixai.domain.ai.StyleResult
import com.pixai.domain.conversation.Conversation
import com.pixai.domain.ai.ImageResult

object AiResponseMapper {

    fun toConversationResponse(conversation: Conversation): ConversationResponse {
        return ConversationResponse(
            id = conversation.id!!,
            status = conversation.status.name,
            createdAt = conversation.createdAt
        )
    }

    fun toCaptionResponse(result: CaptionResult): CaptionResponse {
        return CaptionResponse(
            imageDescription = result.imageDescription,
            suggestions = result.suggestions.map {
                CaptionSuggestionResponse(caption = it.caption, tone = it.tone)
            }
        )
    }

    fun toEditResponse(result: EditResult): EditResponse {
        return EditResponse(
            overallAssessment = result.overallAssessment,
            suggestions = result.suggestions.map {
                EditSuggestionResponse(
                    parameter = it.parameter,
                    currentEstimate = it.currentEstimate,
                    suggestedValue = it.suggestedValue,
                    reason = it.reason
                )
            }
        )
    }

    fun toStyleResponse(result: StyleResult): StyleResponse {
        return StyleResponse(
            suggestions = result.suggestions.map {
                StyleSuggestionResponse(
                    style = it.style,
                    description = it.description,
                    appeal = it.appeal
                )
            }
        )
    }


    fun toImageResultResponse(result: ImageResult): ImageResultResponse {
    return ImageResultResponse(
        imageBase64 = result.imageBase64,
        format = result.format,
        message = result.message
    )
}
}