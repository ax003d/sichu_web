from django.contrib.auth.models import User
from django.contrib.sites.models import get_current_site
from django.template import Context, loader
from django.utils.http import int_to_base36
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.tokens import default_token_generator

from sichu import settings
from cabinet import utils
from cabinet.models import Follow, BookOwnership

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("E-mail"), max_length=75)

    def clean_email(self):
        """
        Validates that an active user exists with the given e-mail address.
        """
        email = self.cleaned_data["email"]
        self.users_cache = User.objects.filter(
                                email__iexact=email,
                                is_active=True
                            )
        if len(self.users_cache) == 0:
            raise forms.ValidationError(_("That e-mail address doesn't have an associated user account. Are you sure you've registered?"))
        return email

    def save(self, domain_override=None, email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator, request=None):
        """
        Generates a one-use only link for resetting password and sends to the user
        """
        # from django.core.mail import send_mail
        for user in self.users_cache:
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            t = loader.get_template(email_template_name)
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': use_https and 'https' or 'http',
            }
            # send_mail(_("Password reset on %s") % site_name,
            #     t.render(Context(c)), None, [user.email])
            utils.send_mail([user.email], 
                            _("Password reset on %s") % site_name,
                            t.render(Context(c)))


class FollowForm(forms.ModelForm):
    class Meta:
        model = Follow


class BookOwnForm(forms.ModelForm):
    class Meta:
        model = BookOwnership
        exclude = ('visible')
