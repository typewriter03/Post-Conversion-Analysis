import random
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from django.db.models import Avg

# --- Heuristic & Keyword Definitions ---

# Keywords to detect if AI is "giving up"
FALLBACK_PHRASES = [
    "i don't know",
    "i am sorry, i cannot assist",
    "i cannot answer that",
    "i am not able to help",
    "i'm not sure",
]

# Keywords to detect if user wants a human
ESCALATION_PHRASES = [
    "human",
    "agent",
    "talk to a person",
    "live support",
    "escalate",
    "representative",
]

# Keywords to detect if user's issue was solved
RESOLUTION_PHRASES = [
    "thanks",
    "thank you",
    "resolved",
    "fixed",
    "that helps",
    "perfect",
    "awesome",
]

# --- Analysis Helper Functions ---

def analyze_sentiment(user_messages_text):
    """
    Analyzes the overall sentiment of the user's messages.
    Returns 'positive', 'neutral', or 'negative'.
    """
    if not user_messages_text:
        return 'neutral'

    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = [analyzer.polarity_scores(text)['compound'] for text in user_messages_text]
    avg_score = sum(sentiment_scores) / len(sentiment_scores)

    if avg_score >= 0.05:
        return 'positive'
    elif avg_score <= -0.05:
        return 'negative'
    else:
        return 'neutral'

def check_resolution(all_messages_text):
    """
    Checks if the conversation appears to be resolved.
    Heuristic: Checks for resolution keywords in the last 2 user messages.
    """
    if not all_messages_text:
        return False
        
    # Check the last message regardless of sender
    last_message = all_messages_text[-1].lower()
    for phrase in RESOLUTION_PHRASES:
        if phrase in last_message:
            return True
    return False

def check_escalation(user_messages_text):
    """
    Checks if the user tried to escalate to a human.
    """
    for message in user_messages_text:
        for phrase in ESCALATION_PHRASES:
            if phrase in message.lower():
                return True
    return False

def count_fallbacks(ai_messages_text):
    """
    Counts how many times the AI used a fallback phrase.
    """
    count = 0
    for message in ai_messages_text:
        for phrase in FALLBACK_PHRASES:
            if phrase in message.lower():
                count += 1
    return count

def mock_complex_scores():
    """
    Mocks scores for complex parameters that would require advanced NLU.
    Returns a dictionary of scores (0-5 scale).
    """
    return {
        'clarity_score': round(random.uniform(3.5, 5.0), 2),
        'relevance_score': round(random.uniform(3.0, 4.8), 2),
        'accuracy_score': round(random.uniform(3.2, 4.9), 2),
        'completeness_score': round(random.uniform(3.0, 4.7), 2),
        'empathy_score': round(random.uniform(2.5, 4.5), 2),
    }

def mock_response_time(messages):
    """
    Mocks the average response time as allowed in the PDF
    """
    if len(messages) < 2:
        return 0.0
    # Mock an average response time in seconds
    return round(random.uniform(5.0, 45.0), 2)

def calculate_overall_score(scores_dict):
    """
    Computes a final User Satisfaction Score.
    We'll average the key quality and interaction scores.
    """
    key_scores = [
        scores_dict.get('clarity_score', 0),
        scores_dict.get('relevance_score', 0),
        scores_dict.get('accuracy_score', 0),
        scores_dict.get('completeness_score', 0),
        scores_dict.get('empathy_score', 0)
    ]
    
    # Give sentiment a weight
    sentiment = scores_dict.get('sentiment', 'neutral')
    if sentiment == 'positive':
        key_scores.append(5.0)
    elif sentiment == 'neutral':
        key_scores.append(3.0)
    else: # negative
        key_scores.append(1.0)

    # Give resolution a weight
    if scores_dict.get('resolution'):
        key_scores.append(5.0)
    else:
        key_scores.append(1.0)
        
    if not key_scores:
        return 0.0
        
    return round(sum(key_scores) / len(key_scores), 2)


# --- Main Analyzer Function ---

def analyze_conversation(conversation_obj):
    """
    Main function to perform post-conversation analysis.
    Takes a Conversation model object and returns a dict of results.
    """
    messages = conversation_obj.messages.all().order_by('created_at')
    
    if not messages.exists():
        return {} # No data to analyze

    # Separate messages for analysis
    user_messages_text = [msg.text for msg in messages if msg.sender == 'user']
    ai_messages_text = [msg.text for msg in messages if msg.sender == 'ai']
    all_messages_text = [msg.text for msg in messages]

    # Run all analysis sub-functions
    analysis_results = {}
    
    # 1. Interaction Parameters
    analysis_results['sentiment'] = analyze_sentiment(user_messages_text)
    analysis_results['response_time_avg'] = mock_response_time(messages)

    # 2. Resolution Parameters
    analysis_results['resolution'] = check_resolution(all_messages_text)
    analysis_results['escalation_need'] = check_escalation(user_messages_text)

    # 3. AI Ops Parameters
    analysis_results['fallback_frequency'] = count_fallbacks(ai_messages_text)

    # 4. Conversation Quality & Mocked Scores
    analysis_results.update(mock_complex_scores())
    
    # 5. Overall Score
    analysis_results['overall_score'] = calculate_overall_score(analysis_results)

    return analysis_results