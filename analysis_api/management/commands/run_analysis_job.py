import logging
from django.core.management.base import BaseCommand
from analysis_api.models import Conversation, ConversationAnalysis
from analysis_api.analyzer import analyze_conversation

# Get an instance of a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Runs the post-conversation analysis for all new chats.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting analysis of new chats...'))

        # Find conversation IDs that have already been analyzed
        analyzed_convo_ids = ConversationAnalysis.objects.values_list('conversation_id', flat=True)

        # Find conversations that are NOT in that list
        new_conversations = Conversation.objects.exclude(id__in=analyzed_convo_ids)

        count = 0
        for convo in new_conversations:
            try:
                # Run the analysis logic from Phase 2
                analysis_data = analyze_conversation(convo)

                # Save the new analysis object
                ConversationAnalysis.objects.create(
                    conversation=convo,
                    **analysis_data
                )
                count += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Failed to analyze conversation {convo.id}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully analyzed {count} new conversations.'))