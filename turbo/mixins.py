from django.db import models
from asgiref.sync import async_to_sync

from channels.layers import get_channel_layer

from turbo import get_broadcast_channel


class BroadcastableMixin(object):
    def save(self, *args, **kwargs):
        channel_layer = get_channel_layer()
        action = "CREATE" if self._state.adding else "UPDATE"
        print("SAVING...")
        super().save(*args, **kwargs)
        for stream in self.streams:
            if hasattr(self, stream):
                channel = get_broadcast_channel(self._meta.label.lower(), stream, getattr(self, stream))
                print(f"SENDING ON {channel}")
                async_to_sync(channel_layer.group_send)(
                    channel,
                    {
                        "type": "notify",
                        "model": self._meta.label,
                        "pk": self.pk,
                        "stream": stream,
                        "action": action,
                        "target-singular": self._meta.verbose_name.lower(),
                        "target-plural": self._meta.verbose_name_plural.lower()
                    })
