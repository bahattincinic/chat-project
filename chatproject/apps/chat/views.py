from django.views.generic import TemplateView
from page.models import Page


class HomePageView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['pages'] = Page.actives.all()
        return context

    def get_template_names(self):
        user = self.request.user
        if user.is_authenticated():
            return "chat/auth_homepage.html"
        return "chat/anon_homepage.html"

