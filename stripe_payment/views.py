import stripe
import json
import logging
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from .models import Payment  # Importando o modelo

# Configuração do logger
logger = logging.getLogger(__name__)

# Chave secreta do Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def create_checkout_session(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Capturar dados enviados pelo frontend
            amount_cve = int(data.get("preco", 5000))  # Valor enviado ou padrão 5000 CVE
            exchange_rate = 0.010  # Taxa de conversão estimada de CVE para USD
            amount_usd = round(amount_cve * exchange_rate * 100)  # Converter para centavos
            currency = 'usd'

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency,
                        'product_data': {'name': data.get("service", "Tour")},
                        'unit_amount': amount_usd,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/stripe_payment/success/'),
                cancel_url=request.build_absolute_uri('/stripe_payment/cancel/'),
            )

            # Salvar pagamento no banco de dados
            Payment.objects.create(
                session_id=session.id,
                amount=amount_cve,  # Salvar o valor original em CVE
                currency='CVE',
                place=data.get("place", "Cabo Verde"),
                time=data.get("time", "1 hour"),
                service=data.get("service", "Tour"),
                distance=data.get("distance", "10 km"),
                status='pending'
            )

            return JsonResponse({'id': session.id})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido enviado'}, status=400)
        except Exception as e:
            logger.error(f"Erro ao criar sessão de checkout: {e}")
            return JsonResponse({'error': str(e)}, status=500)


def success(request):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def cancel(request):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        logger.warning("Webhook inválido recebido.")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        logger.warning("Falha na verificação da assinatura do webhook.")
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        session_id = session.get("id")

        try:
            payment = Payment.objects.get(session_id=session_id)
            payment.status = "completed"
            payment.save()
            logger.info(f"Pagamento {session_id} atualizado para 'completed'")
        except Payment.DoesNotExist:
            logger.error(f"Pagamento {session_id} não encontrado no banco de dados!")

    return HttpResponse(status=200)