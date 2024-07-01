def generate_system_message(user_profile, change_talk_score):
    base_message = (f"You are a {user_profile['chatbot_style'].lower()} motivational interviewing expert. "
                    f"Your goal is to help {user_profile['name']} explore and resolve their ambivalence about change. "
                    "Use OARS techniques (Open-ended questions, Affirmations, Reflective listening, and Summarizing) to guide the conversation.")

    if change_talk_score < 0.3:
        additional_instruction = ("The user is showing low readiness for change. Focus on building rapport, "
                                  "exploring their current situation, and gently introducing the idea of change.")
    elif change_talk_score < 0.7:
        additional_instruction = ("The user is showing some readiness for change. Emphasize change talk, explore "
                                  "reasons for change, and address any ambivalence.")
    else:
        additional_instruction = ("The user is showing high readiness for change. Focus on strengthening commitment "
                                  "to change and begin exploring specific plans for implementation.")

    return f"{base_message} {additional_instruction}"

def get_openai_messages(chat_history, user_profile, change_talk_score):
    system_message = generate_system_message(user_profile, change_talk_score)
    messages = [
        {"role": "system", "content": system_message},
        *chat_history
    ]
    return messages
