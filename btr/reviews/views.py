from django.shortcuts import render
from django.views import View

from btr.vk import TopicComments
from dotenv import load_dotenv
import os


load_dotenv()


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
