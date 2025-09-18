from django import forms
from .models import Usuario

class UsuarioAdminForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Usuario
        fields = '__all__'

    def save(self, commit=True):
        usuario = super().save(commit=False)
        if self.cleaned_data['password']:
            usuario.set_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
        return usuario