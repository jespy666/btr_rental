from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'


class BriefingView(TemplateView):
    template_name = 'briefing/show.html'


class ContactsView(TemplateView):
    template_name = 'contacts/show.html'


class GalleryView(TemplateView):
    template_name = 'gallery.html'
