from rest_framework import serializers
from .models import Conversation, Message, ConversationAnalysis

class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    """
    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'created_at']

class ConversationAnalysisSerializer(serializers.ModelSerializer):
    """
    Serializer for the ConversationAnalysis model.
    """
    class Meta:
        model = ConversationAnalysis
        # List all 10+ fields from our model
        fields = [
            'id', 'clarity_score', 'relevance_score', 'accuracy_score',
            'completeness_score', 'sentiment', 'empathy_score',
            'response_time_avg', 'resolution', 'escalation_need',
            'fallback_frequency', 'overall_score', 'created_at'
        ]

class ConversationReportSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for GET /api/reports/
    Shows the conversation, its messages, and its analysis all nested.
    """
    # Use the 'related_name' from the models
    messages = MessageSerializer(many=True, read_only=True)
    analysis = ConversationAnalysisSerializer(read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'title', 'created_at', 'messages', 'analysis']

class ConversationUploadSerializer(serializers.Serializer):
    """
    Write-only serializer for POST /api/conversations/
    Accepts the chat JSON format from the PDF.
    """
    messages = serializers.ListField(
        child=serializers.DictField()
    )

    def create(self, validated_data):
        messages_data = validated_data.get('messages')
        
        # Create the parent conversation
        conversation_title = f"Chat on {validated_data.get('timestamp', '...')}"
        conversation = Conversation.objects.create(title=conversation_title)

        # Create all message objects
        messages_to_create = []
        for msg_data in messages_data:
            sender = msg_data.get('sender')
            text = msg_data.get('message')
            
            if sender and text:
                messages_to_create.append(
                    Message(
                        conversation=conversation,
                        sender=sender,
                        text=text
                    )
                )
        
        # Create messages in a single batch query
        Message.objects.bulk_create(messages_to_create)
        
        return conversation