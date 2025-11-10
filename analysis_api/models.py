from django.db import models

class Conversation(models.Model):
    """
    Represents a single chat conversation.
    Based on [cite: 33]
    """
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"

class Message(models.Model):
    """
    Represents a single message within a conversation.
    Based on [cite: 36]
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=20) # "user" or "ai" [cite: 38]
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.text[:50]}..."

class ConversationAnalysis(models.Model):
    """
    Stores the analysis results for a single conversation.
    Based on [cite: 39]
    """
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name="analysis") # [cite: 40]

    # Conversation Quality Parameters [cite: 24, 41]
    clarity_score = models.FloatField(null=True, blank=True)
    relevance_score = models.FloatField(null=True, blank=True)
    accuracy_score = models.FloatField(null=True, blank=True)
    completeness_score = models.FloatField(null=True, blank=True)

    # Interaction Parameters [cite: 25, 42, 43]
    sentiment = models.CharField(max_length=20, null=True, blank=True)
    empathy_score = models.FloatField(null=True, blank=True)
    response_time_avg = models.FloatField(null=True, blank=True)

    # Resolution Parameters [cite: 25, 44]
    resolution = models.BooleanField(null=True, blank=True)
    escalation_need = models.BooleanField(null=True, blank=True)

    # AI Ops Parameters [cite: 25]
    fallback_frequency = models.IntegerField(default=0)

    # Overall Score [cite: 25, 45]
    overall_score = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for Conversation {self.conversation.id}"
