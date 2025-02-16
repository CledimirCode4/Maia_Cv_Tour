import json
import logging
import paypalrestsdk
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from stripe_payment.models import Payment


# Configuração do logger
logger = logging.getLogger(__name__)

# Configuração do PayPal
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # "sandbox" ou "live"
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})

# 1️⃣ CRIAÇÃO DA SESSÃO DE PAGAMENTO
@csrf_exempt
def create_paypal_payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            amount_cve = int(data.get("preco", 5000))  # Valor enviado ou padrão 5000 CVE
            exchange_rate = 0.010  # Taxa de conversão estimada CVE para USD
            amount_usd = round(amount_cve * exchange_rate, 2)  # Converter para dólares
            currency = 'USD'

            # Criar pagamento PayPal
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "redirect_urls": {
                    "return_url": request.build_absolute_uri('/paypal_payment/success/'),
                    "cancel_url": request.build_absolute_uri('/paypal_payment/cancel/'),
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": data.get("service", "Tour"),
                            "sku": "001",
                            "price": str(amount_usd),
                            "currency": currency,
                            "quantity": 1
                        }]
                    },
                    "amount": {"total": str(amount_usd), "currency": currency},
                    "description": f"Pagamento pelo serviço: {data.get('service', 'Tour')}"
                }]
            })

            if payment.create():
                # Salvar pagamento no banco de dados
                payment_obj = Payment.objects.create(
                    session_id=payment.id,
                    amount=amount_cve,
                    currency="CVE",
                    place=data.get("place", "Cabo Verde"),
                    time=data.get("time", "1 hour"),
                    service=data.get("service", "Tour"),
                    distance=data.get("distance", "10 km"),
                    status="pending"
                )

                # Pegar o link de redirecionamento para o PayPal
                for link in payment.links:
                    if link.rel == "approval_url":
                        return JsonResponse({"redirect_url": link.href})

            else:
                return JsonResponse({"error": "Erro ao criar pagamento PayPal"}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido enviado"}, status=400)
        except Exception as e:
            logger.error(f"Erro ao criar pagamento PayPal: {e}")
            return JsonResponse({"error": str(e)}, status=500)

# 2️⃣ REDIRECIONAMENTO APÓS O PAGAMENTO
def paypal_success(request):
    payment_id = request.GET.get("paymentId")
    payer_id = request.GET.get("PayerID")

    if not payment_id or not payer_id:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        try:
            payment_obj = Payment.objects.get(session_id=payment_id)
            payment_obj.status = "completed"
            payment_obj.save()
            logger.info(f"Pagamento {payment_id} concluído com sucesso")
        except Payment.DoesNotExist:
            logger.error(f"Pagamento {payment_id} não encontrado no banco de dados")

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def paypal_cancel(request):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# 3️⃣ WEBHOOK PARA ATUALIZAR STATUS DO PAGAMENTO
@csrf_exempt
def paypal_webhook(request):
    payload = json.loads(request.body.decode('utf-8'))
    event_type = payload.get("event_type")

    logger.info(f"Recebendo webhook do PayPal: {payload}")

    if event_type == "PAYMENT.SALE.COMPLETED":
        sale_id = payload["resource"]["id"]
        try:
            payment = Payment.objects.get(session_id=sale_id)
            payment.status = "completed"
            payment.save()
            logger.info(f"Pagamento {sale_id} atualizado para 'completed'")
        except Payment.DoesNotExist:
            logger.error(f"Pagamento {sale_id} não encontrado no banco de dados")

    return HttpResponse(status=200)
