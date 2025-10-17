from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'company', 'location', 'description', 'contact_email']


class ContactForm(forms.Form):
    """Form for job applications - used on job_detail page"""
    name = forms.CharField(max_length=120, label='Name', required=True)
    email = forms.EmailField(label='Email', required=True)
    message = forms.CharField(widget=forms.Textarea, label='Message', required=True)
