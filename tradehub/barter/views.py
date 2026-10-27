from django.shortcuts import render
from .models import TradePost, Negotiation, Offer, Category, Advertisement
from .forms import NegotiationForm, CounterOfferForm, TradePostForm, UserRegistrationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.utils import timezone

# 1. post_list_view(request)
# 2. my_post_list_view(request, user_id)
# 3. post_create_view(request)
# 4. post_delete_view(request, post_id)

# 5. negotiation_list_view(request, post_id) changed to post_detail_view(request, post_id) {Shows all negotiations for a post if user is owner, else shows only their own negotiation for that post}
# 6. negotiation_create_view(request, post_id)
# 7. negotiation_decline_view(request, negotiation_id)
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
    search = request.GET.get("q")
    status_id = request.GET.get("status")
    category_id = request.GET.get("category")

    posts = TradePost.objects.order_by('-date_created')  # will show all posts

    if search:
        posts = posts.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    if status_id:
        posts = posts.filter(status=status_id)

    if category_id:
        posts = posts.filter(category=category_id)


    now = timezone.now()
    active_ads = Advertisement.objects.filter(
        is_active=True
    ).filter(
        Q(date_start__isnull=True) | Q(date_start__lte=now),
        Q(date_end__isnull=True) | Q(date_end__gte=now),
    )
        
    return render(request, 'post_list.html', {
        'posts': posts,
        'search': search,
        'status': status_id,
        'category': category_id,
        'status_choices': TradePost.TRADEPOST_STATUS_CHOICES,
        'category_choices': Category.objects.all(),

        # Advertisements
        "header_ad": active_ads.filter(placement="HE").first(),
        "sidebar_ads": active_ads.filter(placement="SB"),
        "feed_ad": active_ads.filter(placement="FS").first(),
    })

#2
@login_required
def my_post_list_view(request, user_id):
    """Displays a list of trade posts created by the logged-in user."""
    if request.user.pk != user_id:
        return redirect('post_list_view')  # Redirect to the main feed if the user is not the owner

    search = request.GET.get("q")
    status_id = request.GET.get("status")
    category_id = request.GET.get("category")

    posts = TradePost.objects.filter(owner=request.user).order_by('-date_created')

    if search:
            posts = posts.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
    
    if status_id:
        posts = posts.filter(status=status_id)

    if category_id:
        posts = posts.filter(category=category_id)
        
    return render(request, 'my_post_list.html', {
        'posts': posts,
        'search': search,
        'status': status_id,
        'category': category_id,
        'status_choices': TradePost.TRADEPOST_STATUS_CHOICES,
        'category_choices': Category.objects.all(),
    })

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

    if request.user.is_authenticated:
        # 1. If the user is the owner, they see all negotiations for this post
        if post.owner == request.user:
            negotiations = Negotiation.objects.filter(requested_post=post).order_by('-date_created')

        # 2. If the user is not the owner, filter to only show their own negotiations for this post        
        elif request.user:
            negotiations = Negotiation.objects.filter(requested_post=post, proposer=request.user).order_by('-date_created')
            
    else:
        negotiations = Negotiation.objects.none()

    # Adding next_responder to each nego for btns logic
    for negotiation in negotiations:
        latest_offer = negotiation.offers.order_by("-date_created", "-pk").first()

        if latest_offer is None:
            # No offer obj yet: post owner's turn
            negotiation.next_responder = negotiation.requested_post.owner

        elif latest_offer.sender_id == negotiation.requested_post.owner_id:
            # Owner countered: proposer's turn
            negotiation.next_responder = negotiation.proposer

        elif latest_offer.sender_id == negotiation.proposer_id:
            # Proposer countered: owner's turn
            negotiation.next_responder = negotiation.requested_post.owner

    return render(request, 'post_details.html', {'negotiations': negotiations, 'post': post})

# 6
@login_required
def negotiation_create_view(request, post_id):
    requested_post = get_object_or_404(TradePost, pk=post_id)

    # Prevent users from negotiating with themselves
    if requested_post.owner == request.user:
        return redirect('post_detail_view', post_id=requested_post.pk)
    
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
def negotiation_decline_view(request, negotiation_id):
    negotiation = get_object_or_404(
                    Negotiation,
                    requested_post__owner=request.user,   # Only Post owner can declined a Nego
                    pk=negotiation_id
                    )
    
    if request.method == "POST":
        post_id = negotiation.requested_post.pk

        if negotiation.status == 'PE':
            negotiation.status = 'DE'
            negotiation.save(update_fields=["status"])

        return redirect('post_detail_view', post_id=post_id)
    
    return render(request, 'negotiation_decline.html', {'negotiation': negotiation})

# 8
@login_required
def negotiation_withdraw_view(request, negotiation_id):
    negotiation = get_object_or_404(
                    Negotiation,
                    proposer=request.user,   # Only NEGO owner can withdraw a Nego
                    pk=negotiation_id
                    )
    
    if request.method == "POST":
        post_id = negotiation.requested_post.pk

        if negotiation.status == 'PE':
            negotiation.status = 'WI'
            negotiation.save(update_fields=["status"])

        return redirect('post_detail_view', post_id=post_id)
    
    return render(request, 'negotiation_withdraw.html', {'negotiation': negotiation})

# 9 Making counter offer or Viewing the Chat(Waiting for Response from opposite party)
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
def negotiation_accept_view(request, negotiation_id):
    ''' mark requested post as traded
        mark all requested post's pending negos as declined except current nego 
        mark offered post as traded
        mark offered post's pending negos as declined
        mark mark all all negos as withdrawn where offered_post is current offered post except current nego
        '''
    negotiation = get_object_or_404(
                    Negotiation,
                    Q(proposer=request.user) | Q(requested_post__owner=request.user),   # Two people can Accept a Negotiation: PostOwner or OfferOwner
                    pk=negotiation_id
                    )

    if request.method == "POST":
        pass

    return render(request, 'negotiation_accept.html', {'negotiation': negotiation})


# 11
@login_required 
def my_offers_list_view(request, user_id):
    '''Simply returns Negotiations, Negotiation already have Requested_post object as well as Offer_post object'''
    if request.user.pk != user_id:
            return redirect('post_list_view')  # Redirect to the main feed if the user is not the owner

    my_negotiations = Negotiation.objects.filter(proposer= request.user
                        ).select_related(   # select_related all fetch specified objects along with Nego obj
                            'requested_post', 
                            'offered_post', 
                            'requested_post__owner'
                        ).order_by('-date_created')

    return render(request, 'my_offers_list.html', {'my_negotiations': my_negotiations})

# 12
def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            login(request, user)
            return redirect('post_list_view')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


