from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.http.response import HttpResponseRedirect
from page.models import Page


class ForgotPassword(TemplateView):
    template_name = "account/forgot_password.html"

    def get_context_data(self, **kwargs):
        context = super(ForgotPassword, self).get_context_data(**kwargs)
        context['pages'] = Page.actives.all()
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('homepage'))
        return super(ForgotPassword, self).get(request=request, **kwargs)