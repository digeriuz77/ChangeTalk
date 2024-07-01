def calculate_change_talk_score(analysis_result):
    # Weights for different components (adjust as needed)
    SENTIMENT_WEIGHT = 0.3
    CHANGE_TALK_WEIGHT = 0.4
    COHERENCE_WEIGHT = 0.15
    SEMANTIC_SIMILARITY_WEIGHT = 0.15

    # Normalize sentiment score to 0-1 range
    normalized_sentiment = (analysis_result['sentiment'] + 1) / 2

    # Normalize change talk score (assuming max possible score is 10)
    normalized_change_talk = min(analysis_result['change_talk_score'] / 10, 1)

    # Calculate weighted score
    change_talk_score = (
        SENTIMENT_WEIGHT * normalized_sentiment +
        CHANGE_TALK_WEIGHT * normalized_change_talk +
        COHERENCE_WEIGHT * analysis_result['coherence'] +
        SEMANTIC_SIMILARITY_WEIGHT * analysis_result['semantic_similarity']
    )

    return change_talk_score
