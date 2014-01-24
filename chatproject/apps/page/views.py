from django.views.generic.detail import DetailView
from .models import Page


class PageDetailView(DetailView):

    model = Page

    def get_context_data(self, **kwargs):
        context = super(PageDetailView, self).get_context_data(**kwargs)
        context['pages'] = Page.actives.all()
        return context