from rest_framework import serializers

from chat_support.models import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    dialog = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ChatMessage
        fields = ('body', 'dialog')

