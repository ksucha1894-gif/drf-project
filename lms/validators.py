from rest_framework import serializers


class URLValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, data):
        url = data.get(self.field)
        if url and not url.startswith("https://www.youtube.com"):
            raise serializers.ValidationError("Ссылка должна вести на youtube.com")
