from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.http.response import HttpResponseRedirect
from account.models import User
from page.models import Page


class ForgotPassword(TemplateView):
    template_name = "auth/forgot_password.html"

    def get_context_data(self, **kwargs):
        context = super(ForgotPassword, self).get_context_data(**kwargs)
        context['pages'] = Page.actives.all()
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('homepage'))
        return super(ForgotPassword, self).get(request=request, **kwargs)


class NewPasswordView(DetailView):
    model = User
    template_name = "auth/new_password.html"
    slug_url_kwarg = 'secret_key'
    slug_field = 'secret_key'

    def get_context_data(self, **kwargs):
        context = super(NewPasswordView, self).get_context_data(**kwargs)
        context['pages'] = Page.actives.all()
        return context