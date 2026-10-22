from django.shortcuts import render
from .models import TradePost, Negotiation, Offer
from .forms import NegotiationForm, CounterOfferForm
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q

# 1. post_list_view(request)
# 2. my_post_list_view(request, user_id)
# 3. post_create_view(request)
# 4. post_delete_view(request, post_id)

# 5. negotiation_list_view(request, post_id)
# 6. negotiation_create_view(request, post_id)
# 7. negotiation_delete_view(request, negotiation_id)
# 8. negotiation_detail_view(request, negotiation_id) {Will be used for creating Counter offers}
# 9. my_offers_list_view(request, user_id) {Gives Posts on which user has made offer}

# 9. register_view(request)

# Create your views here.
def index(request):
    return render(request, 'index.html')

# 6
def negotiation_create_view(request, post_id):
    requested_post = get_object_or_404(TradePost, pk=post_id)

    # Prevent users from negotiating with themselves
    if requested_post.owner == request.user:
        return redirect('negotiation_list_view', post_id=requested_post.pk)
    
    if request.method == "POST":
        form = NegotiationForm(request.POST, user= request.user)
        if form.is_valid():
            negotiation = form.save(commit=False)
            negotiation.requested_post = requested_post
            negotiation.proposer = request.user
            negotiation.save()

            # Create the initial Offer record in the view if message exists
            message = form.cleaned_data['message']
            if message:
                Offer.objects.create(
                    negotiation=negotiation,
                    sender=request.user,
                    offered_item_details=message
                )
            return redirect('negotiation_detail_view', negotiation_id= negotiation.pk)
    else:
        form = NegotiationForm(user= request.user)

    return render(request, 'negotiation_create.html', {'form': form, 'requested_post': requested_post})

# 7
def negotiation_delete_view(request, negotiation_id):
    negotiation = get_object_or_404(
                    Negotiation,
                    Q(proposer=request.user) | Q(requested_post__owner=request.user),   # Two people can delete a Negotiation: PostOwner or OfferOwner
                    pk=negotiation_id
                    )
    
    if request.method == "POST":
        post_id = negotiation.requested_post.pk
        negotiation.delete()
        return redirect('negotiation_list_view', post_id=post_id)
    
    return render(request, 'negotiation_delete.html', {'negotiation': negotiation})

# 8 Making counter offer or Viewing the Chat(Waiting for Response from opposite party)
def negotiation_detail_view(request, negotiation_id):
    negotiation = get_object_or_404(
                    Negotiation,
                    Q(proposer=request.user) | Q(requested_post__owner=request.user),   # Two people can counter Offer a Negotiation: PostOwner or OfferOwner
                    pk=negotiation_id
                    )

    chat_messages = negotiation.offers.all().order_by('date_created') # here "offers" is the related_name(relationship)

    if request.method == "POST":
        form = CounterOfferForm(request.POST)
        if form.is_valid():
            counter_offer = form.save(commit=False)
            counter_offer.negotiation = negotiation
            counter_offer.sender = request.user
            counter_offer.save()
            return redirect('negotiation_detail_view', negotiation_id= negotiation.pk)
    else:
        form = CounterOfferForm()

    return render(request, 'negotiation_detail.html', {'form': form, 'negotiation': negotiation, 'chat_messages': chat_messages})
