from django.db import models

class Conversation(models.Model):
    
    title = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"

class Message(models.Model):
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=20) 
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.text[:50]}..."

class ConversationAnalysis(models.Model):
    
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name="analysis") 

    
    clarity_score = models.FloatField(null=True, blank=True)
    relevance_score = models.FloatField(null=True, blank=True)
    accuracy_score = models.FloatField(null=True, blank=True)
    completeness_score = models.FloatField(null=True, blank=True)

    
    sentiment = models.CharField(max_length=20, null=True, blank=True)
    empathy_score = models.FloatField(null=True, blank=True)
    response_time_avg = models.FloatField(null=True, blank=True)

    
    resolution = models.BooleanField(null=True, blank=True)
    escalation_need = models.BooleanField(null=True, blank=True)

    
    fallback_frequency = models.IntegerField(default=0)

    
    overall_score = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for Conversation {self.conversation.id}"
