from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Conversation, ConversationAnalysis
from .serializers import (
    ConversationUploadSerializer, 
    ConversationReportSerializer,
    ConversationAnalysisSerializer
)
from .analyzer import analyze_conversation

class ConversationUploadView(generics.CreateAPIView):
    """
    Endpoint: POST /api/conversations/
    Accepts a JSON list of chat messages and stores them.
    [cite: 29, 48]
    """
    serializer_class = ConversationUploadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        
        # Return the basic info of the created conversation
        return Response(
            {"message": "Conversation uploaded successfully", "conversation_id": conversation.id},
            status=status.HTTP_201_CREATED
        )

class ReportListView(generics.ListAPIView):
    """
    Endpoint: GET /api/reports/
    Lists all conversation analysis results. 
    """
    queryset = Conversation.objects.all().prefetch_related('messages', 'analysis')
    serializer_class = ConversationReportSerializer

class AnalysisTriggerView(APIView):
    """
    Endpoint: POST /api/analyse/
    Triggers analysis on a specific conversation by its ID. 
    """
    def post(self, request, *args, **kwargs):
        conversation_id = request.data.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {"error": "conversation_id is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        conversation = get_object_or_404(Conversation, id=conversation_id)

        # Run the analysis logic from Phase 2
        try:
            analysis_data = analyze_conversation(conversation)
        except Exception as e:
            return Response(
                {"error": f"Analysis failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Save the analysis results to the database
        # update_or_create handles if analysis already exists
        analysis_obj, created = ConversationAnalysis.objects.update_or_create(
            conversation=conversation,
            defaults=analysis_data
        )

        serializer = ConversationAnalysisSerializer(analysis_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)