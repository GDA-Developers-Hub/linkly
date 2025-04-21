from .models import PlatformCredentials

class PlatformCredentialsForm(forms.ModelForm):
    """Form for clients to add their OAuth credentials"""
    
    class Meta:
        model = PlatformCredentials
        fields = ['platform', 'client_id', 'client_secret', 'redirect_uri']
        widgets = {
            'client_secret': forms.PasswordInput(render_value=True),
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['platform'].widget = forms.Select(choices=PlatformCredentials._meta.get_field('platform').choices)
        self.fields['redirect_uri'].help_text = "The redirect URI you registered in the platform's developer portal."
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance 