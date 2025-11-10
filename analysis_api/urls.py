from django.urls import path
from .views import ConversationUploadView, ReportListView, AnalysisTriggerView

# DO NOT ADD 'include' to this file
urlpatterns = [
    path('conversations/', ConversationUploadView.as_view(), name='conversation-upload'),
    path('reports/', ReportListView.as_view(), name='report-list'),
    path('analyse/', AnalysisTriggerView.as_view(), name='analysis-trigger'),
]