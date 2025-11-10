from django.urls import path
from .views import ConversationUploadView, ReportListView, AnalysisTriggerView


urlpatterns = [
    path('conversations/', ConversationUploadView.as_view(), name='conversation-upload'),
    path('reports/', ReportListView.as_view(), name='report-list'),
    path('analyse/', AnalysisTriggerView.as_view(), name='analysis-trigger'),
]