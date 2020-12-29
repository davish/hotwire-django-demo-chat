from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.urls import reverse
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.shortcuts import render, get_object_or_404
from chat.models import Room, Message


class RoomList(ListView):
    model = Room
    context_object_name = 'rooms'


class RoomDetail(DetailView):
    model = Room
    context_object_name = 'room'


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ["text", "confirm"]

    def clean_confirm(self):
        if not self.cleaned_data["confirm"]:
            raise ValidationError(["You must confirm message"], code="invlaid")
        return self.cleaned_data["confirm"]


class MessageCreate(CreateView):
    model = Message
    form_class = MessageForm

    def get_success_url(self):
        return reverse("send", kwargs={"pk": self.kwargs["pk"]})

    def form_valid(self, form):
        room = get_object_or_404(Room, pk=self.kwargs["pk"])
        form.instance.room = room
        return super().form_valid(form)
        # return render(self.request, 'chat/message_update.html', {"message": form.instance}, content_type='text/html; turbo-stream;')


