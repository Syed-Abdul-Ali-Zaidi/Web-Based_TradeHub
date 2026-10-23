from django import forms
from .models import Category, TradePost, Negotiation, Offer
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class TradePostForm(forms.ModelForm):
    class Meta:
        model = TradePost
        fields = ['title', 'description', 'image', 'category']
        # Just Adding label to category, Category will be populated by .all() by default
        labels = {
            'category': 'Select Post Category',
        }

class NegotiationForm(forms.ModelForm):
    message = forms.CharField(
        required=False,
        max_length=400,
        widget=forms.Textarea(attrs={
            "rows": 3,
            "placeholder": "Write an initial proposal message (optional)...",
            "class": "form-control"
        }),
        label="Initial Message"
    )

    class Meta:
        model = Negotiation
        fields = ['offered_post']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['offered_post'].queryset = TradePost.objects.filter(
                owner=user,
                status="O"
            )
            self.fields['offered_post'].label = "Select your Post to Offer"

    def clean(self):
        cleaned_data = super().clean()

        message = cleaned_data.get('message')
        offered_post = cleaned_data.get('offered_post')

        if not message and not offered_post:
            raise forms.ValidationError(
                "Please Select a Post to offer or Provide Text."
            )

        return cleaned_data
            
class CounterOfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['offered_item_details']
        widgets = {
            'offered_item_details': forms.Textarea(attrs={
                'placeholder': 'Write your reply or counter-offer...'
            })
        }
        labels = {
            'offered_item_details': 'Message / Counter-Offer'
        }

class UserRegistrationForm(UserCreationForm):
    emial = forms.EmailField()
    class Meta:
        model = User
        fields = ('username', 'emial', 'password1', 'password2')