from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'


class BriefingView(TemplateView):
    template_name = 'briefing/show.html'
