from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.views.generic import TemplateView
from page.models import Page


class HomePageView(TemplateView):
    template_name = "chat/homepage.html"

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['pages'] = Page.actives.all()
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            user = request.user
            return HttpResponseRedirect(reverse('anon-profile',
                                                args=(user.username,)))
        return super(HomePageView, self).get(request, *args, **kwargs)
