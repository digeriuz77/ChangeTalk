def calculate_change_talk_score(analysis_result):
    SENTIMENT_WEIGHT = 0.3
    CHANGE_TALK_WEIGHT = 0.7
    
    normalized_sentiment = (analysis_result['sentiment'] + 1) / 2
    normalized_change_talk = min(analysis_result['change_talk_score'] / 10, 1)
    
    change_talk_score = (
        SENTIMENT_WEIGHT * normalized_sentiment +
        CHANGE_TALK_WEIGHT * normalized_change_talk
    )
    return change_talk_score
