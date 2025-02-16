from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_paypal_payment, name="create_paypal_payment"),
    path("success/", views.paypal_success, name="paypal_success"),
    path("cancel/", views.paypal_cancel, name="paypal_cancel"),
    path("webhook/", views.paypal_webhook, name="paypal_webhook"),
]
