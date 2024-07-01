import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize

# Download required NLTK data
nltk.download('vader_lexicon', quiet=True)
nltk.download('punkt', quiet=True)

class OARSAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.change_talk_keywords = [
            'change', 'improve', 'better', 'start', 'stop', 'more', 'less', 'different',
            'want', 'need', 'desire', 'plan', 'could', 'should', 'would', 'will'
        ]

    def analyze_sentiment(self, text):
        return self.sia.polarity_scores(text)['compound']

    def identify_change_talk(self, text):
        words = word_tokenize(text.lower())
        return sum(1 for word in words if word in self.change_talk_keywords)

    def analyze_input(self, user_input, chat_history):
        sentiment = self.analyze_sentiment(user_input)
        change_talk_score = self.identify_change_talk(user_input)
        
        return {
            'sentiment': sentiment,
            'change_talk_score': change_talk_score
        }
