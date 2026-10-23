from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list_view, name='post_list_view'),
    path('<int:post_id>/create_offer/', views.negotiation_create_view, name='negotiation_create_view'),
    path('<int:negotiation_id>/delete_offer/', views.negotiation_delete_view, name='negotiation_delete_view'),
    path('<int:negotiation_id>/details_offer/', views.negotiation_detail_view, name='negotiation_detail_view'),
]

# Add urls in sequence as Views