from django.urls import path
from .views import create_checkout_session, success, cancel, stripe_webhook

urlpatterns = [
    path('create-checkout-session/', create_checkout_session, name="create_checkout_session"),
    path('success/', success, name="success"),
    path('cancel/', cancel, name="cancel"),
    path('webhook/', stripe_webhook, name="stripe_webhook"),

]
