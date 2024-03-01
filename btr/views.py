import os

from django.http import JsonResponse
from dotenv import load_dotenv

from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from btr.vk import TopicComments


load_dotenv()


class IndexView(TemplateView):
    template_name = 'index.html'


class BlogView(TemplateView):
    template_name = 'blog/404.html'


class BriefingView(TemplateView):
    template_name = 'briefing/briefing.html'


class ContactsView(TemplateView):
    template_name = 'contacts/contacts.html'


class VKCommentsView(View):
    template_name = 'reviews/reviews.html'
    access_token = os.getenv('VK_ACCESS_TOKEN')
    app_id = os.getenv('VK_APP_ID')
    app_secret = os.getenv('VK_APP_SECRET')
    group_id = '211850637'
    topic_id = '49522524'

    def get(self, request, *args, **kwargs):
        vk = TopicComments(
            self.group_id,
            self.topic_id,
            self.access_token
        )

        context = {
            'comments': vk.get_comments(),
            'group_id': self.group_id,
            'topic_id': self.topic_id,
            'app_id': self.app_id,
        }

        return render(request, self.template_name, context)


def health(request):
    return JsonResponse({"status": "ok"})
