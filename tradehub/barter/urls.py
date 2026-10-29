from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list_view, name='post_list_view'),
    path('user/<int:user_id>/posts/', views.my_post_list_view, name='my_post_list_view'),
    path('posts/new/', views.post_create_view, name='post_create_view'),
    path('posts/<int:post_id>/delete/', views.post_delete_view, name='post_delete_view'),
    path('posts/<int:post_id>/', views.post_detail_view, name='post_detail_view'),    
    path('<int:post_id>/create_offer/', views.negotiation_create_view, name='negotiation_create_view'),
    path('<int:negotiation_id>/decline_offer/', views.negotiation_decline_view, name='negotiation_decline_view'),
    path('<int:negotiation_id>/withdraw_offer/', views.negotiation_withdraw_view, name='negotiation_withdraw_view'),
    path('<int:negotiation_id>/accept_offer/', views.negotiation_accept_view, name='negotiation_accept_view'),
    path('<int:negotiation_id>/details_offer/', views.negotiation_detail_view, name='negotiation_detail_view'),
    path('<int:user_id>/my_offers/', views.my_offers_list_view, name='my_offers_list_view'),
    path('register/', views.register_view, name='register_view'),
    path('about_us/', views.about_us_view, name='about_us_view'),

]

# Add urls in sequence as Views 
