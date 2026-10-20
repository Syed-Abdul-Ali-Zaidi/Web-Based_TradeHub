from django import forms
from .models import Category, TradePost, Negotiation, Offer

class TradePostForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="Select Post Category"
    )
    class Meta:
        model = TradePost
        fields = ['title', 'description', 'image', 'category']

class NegotiationCreateForm(forms.ModelForm):
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
        widgets = {
            'offered_post': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['offered_post'].queryset = TradePost.objects.filter(
                owner=user, 
                status="O"
            )


class CounterOfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['offered_item_details']
        widgets = {
            'offered_item_details': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Write your reply or counter-offer...',
                'class': 'form-control'
            })
        }
        labels = {
            'offered_item_details': 'Message / Counter-Offer'
        }