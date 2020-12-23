from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from django.apps import apps
from django.template.loader import render_to_string

from turbo import get_broadcast_channel


class TurboStreamsConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.accept()

    def notify(self, event, *args, **kwargs):
        print("LOUD AND CLEAR!")
        model_label = event["model"]
        pk = event["pk"]
        stream = event["stream"]
        action = event["action"]
        target = event["target-plural"]

        model = apps.get_model(model_label)
        instance = model.objects.get(pk=pk)
        app, model_name = model_label.lower().split(".")

        self.send_json({
            "data": render_to_string('turbo/stream.html', {
                "object": instance,
                model_name.lower(): instance,
                "action": "append",
                "dom_target": target,
                "model_template": f"{app}/{model_name}.html"
            })
        })

    def receive_json(self, content, **kwargs):
        model_label = content.get("model")
        stream = content.get("stream")
        value = content.get("value")
        channel = get_broadcast_channel(model_label.lower(), stream, value)
        print(f"RECEIVED SUBSCRIPTION: {channel}")
        self.groups.append(channel)
        async_to_sync(self.channel_layer.group_add)(channel, self.channel_name)
