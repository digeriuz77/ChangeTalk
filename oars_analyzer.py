import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import re

nltk.download('vader_lexicon', quiet=True)

class OARSAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.change_talk_keywords = ['change', 'improve', 'better', 'start', 'stop', 'more', 'less', 'different']

    def analyze_sentiment(self, text):
        return self.sia.polarity_scores(text)['compound']

    def identify_change_talk(self, text):
        return any(keyword in text.lower() for keyword in self.change_talk_keywords)

    def generate_reflection(self, text):
        # Simple reflection for now, can be expanded with more advanced NLP techniques
        return f"It sounds like you're saying that {text}"

    def generate_affirmation(self, text):
        sentiment = self.analyze_sentiment(text)
        if sentiment > 0:
            return "That's great! You're making positive steps."
        elif sentiment < 0:
            return "I appreciate your honesty in sharing that. It takes courage to confront challenges."
        else:
            return "Thank you for sharing that. Your perspective is valuable."

    def generate_open_question(self, text):
        # Simple open question generation, can be expanded
        return f"Can you tell me more about why you feel that way about {text}?"

    def analyze_input(self, user_input, chat_history):
        sentiment = self.analyze_sentiment(user_input)
        change_talk = self.identify_change_talk(user_input)
        reflection = self.generate_reflection(user_input)
        affirmation = self.generate_affirmation(user_input)
        open_question = self.generate_open_question(user_input)

        return {
            'sentiment': sentiment,
            'change_talk': change_talk,
            'reflection': reflection,
            'affirmation': affirmation,
            'open_question': open_question
        }
