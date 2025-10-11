from django import forms
from .css import EMAIL_FIELD_CSS
from . import services


class EmailForm(forms.Form):

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "id": "email-login-input",
                "class": EMAIL_FIELD_CSS,
                "placeholder": "Твоя почта для логина",
            }
        )
    )

    # class Meta:
    #    model = Email
    #    fields = ["email"]
    def clean_email(self):
        email = self.cleaned_data.get("email")
        verified = services.verify_email(email)
        qs = services.Email.objects.filter(email=email, active=False)
        if qs.exists():
            raise forms.ValidationError("Неверная почта! Попробуй ещё раз!")
        return email
