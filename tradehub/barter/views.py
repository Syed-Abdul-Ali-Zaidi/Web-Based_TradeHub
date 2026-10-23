from django.shortcuts import render
from .models import TradePost, Negotiation, Offer
from .forms import NegotiationForm, CounterOfferForm, TradePostForm, UserRegistrationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login

# 1. post_list_view(request)
# 2. my_post_list_view(request, user_id)
# 3. post_create_view(request)
# 4. post_delete_view(request, post_id)

# 5. negotiation_list_view(request, post_id) changed to post_detail_view(request, post_id) {Shows all negotiations for a post if user is owner, else shows only their own negotiation for that post}
# 6. negotiation_create_view(request, post_id)
# 7. negotiation_delete_view(request, negotiation_id)
# 8. negotiation_detail_view(request, negotiation_id) {Will be used for creating Counter offers}
# 9. my_offers_list_view(request, user_id) {Gives Posts on which user has made offer}

# 10. register_view(request)

# Create your views here.
def index(request):
    posts = TradePost.objects.filter(status='O')

    return render(request, 'index.html', {'posts': posts})

#1
def post_list_view(request):
    """Displays a list of all trade posts."""
    posts = TradePost.objects.order_by('-date_created')  # will show all posts
    return render(request, 'post_list.html', {'posts': posts})

#2
@login_required
def my_post_list_view(request, user_id):
    """Displays a list of trade posts created by the logged-in user."""
    if request.user.pk != user_id:
        return redirect('post_list_view')  # Redirect to the main feed if the user is not the owner

    posts = TradePost.objects.filter(owner=request.user).order_by('-date_created')
    return render(request, 'my_post_list.html', {'posts': posts})

#3 
@login_required
def post_create_view(request):
    """Allows an authenticated user to list a new item for trade."""
    if request.method == "POST":
        form = TradePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.owner = request.user  # Assign the logged-in user as the owner
            post.status = 'O'  # Set the status to OPEN
            post.save()
            return redirect('post_list_view')  # Redirect back to the feed/list view
    else:
        form = TradePostForm()
        
    return render(request, 'post_create.html', {'form': form})

#4
@login_required
def post_delete_view(request, post_id):
    """Allows the owner of a trade post to delete it."""
    post = get_object_or_404(TradePost, pk=post_id, owner=request.user)

    if request.method == "POST":
        post.delete()
        return redirect('my_post_list_view', user_id=request.user.pk)

    return render(request, 'post_confirm_delete.html', {'post': post})


#5
def post_detail_view(request, post_id):
    """Displays negotiations for a specific trade post (All for owner, own offer for proposer)."""
    post = get_object_or_404(TradePost, pk=post_id)

    # 1. If the user is the owner, they see all negotiations for this post
    if post.owner == request.user:
        negotiations = Negotiation.objects.filter(requested_post=post).order_by('-date_created')
        
    else:
        # 2. If the user is not the owner, filter to only show their own negotiations for this post
        negotiations = Negotiation.objects.filter(requested_post=post, proposer=request.user).order_by('-date_created')
        
        # If they aren't the owner AND haven't made any negotiation here, kick them out
        if not negotiations.exists():
            return redirect('post_list_view')

    return render(request, 'negotiation_list.html', {'negotiations': negotiations, 'post': post})

# 6
@login_required
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
@login_required
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
@login_required
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

# 10
def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.changed_data['password1'])
            user.save()
            login(request, user)
            return redirect('post_list_view')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})