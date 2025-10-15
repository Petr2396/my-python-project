import uuid
import json
import requests
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
from orders.models import Order


def create_payment(request, order):
    # В тестовом режиме просто имитируем успешную оплату
    if settings.DEBUG:
        order.is_paid = True
        order.payment_id = f"test_payment_{order.id}_{uuid.uuid4().hex[:8]}"
        order.save()
        messages.success(request, f"Заказ №{order.id} успешно оплачен (тестовый режим)!")
        return redirect("orders:my_orders")

    # Продакшен
    url = "https://api.yookassa.ru/v3/payments"
    headers = {
        "Content-Type": "application/json",
        "Idempotence-Key": str(uuid.uuid4()),
    }
    auth = (settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_API_KEY)

    data = {
        "amount": {"value": str(order.get_total_cost()), "currency": "RUB"},
        "confirmation": {
            "type": "redirect",
            "return_url": request.build_absolute_uri(
                reverse("payments:success")  # возвращаемся сюда
            ),
        },
        "capture": True,
        "description": f"Заказ №{order.id}",
        "metadata": {"order_id": order.id},
    }

    response = requests.post(url, json=data, headers=headers, auth=auth)
    payment = response.json()

    if response.status_code == 200:
        confirmation = payment.get("confirmation")
        if confirmation and confirmation.get("confirmation_url"):
            order.payment_id = payment.get("id")
            order.save()
            return redirect(confirmation["confirmation_url"])

    messages.error(request, "Ошибка создания платежа")
    return redirect("orders:my_orders")


def payment_success(request):
    print("Параметры запроса:", dict(request.GET))  # отладка
    payment_id = request.GET.get("payment")  # ЮKassa возвращает именно ?payment=...

    if not payment_id:
        messages.error(request, "Нет ID платежа")
        return redirect("orders:my_orders")

    url = f"https://api.yookassa.ru/v3/payments/{payment_id}"
    auth = (settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_API_KEY)
    response = requests.get(url, auth=auth)
    payment = response.json()

    if payment.get("status") == "succeeded":
        order_id = payment.get("metadata", {}).get("order_id")
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.is_paid = True
                order.save()
                messages.success(request, f"Заказ №{order.id} успешно оплачен!")
            except Order.DoesNotExist:
                messages.error(request, "Заказ не найден")
    else:
        messages.warning(request, "Платёж не завершён")

    return redirect("orders:my_orders")


@csrf_exempt
def payment_webhook(request):
    if request.method == "POST":
        event_json = json.loads(request.body.decode("utf-8"))
        if event_json.get("event") == "payment.succeeded":
            payment_data = event_json.get("object", {})
            order_id = payment_data.get("metadata", {}).get("order_id")
            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                    order.is_paid = True
                    order.save()
                    print(f"Заказ {order_id} оплачен через webhook")
                except Order.DoesNotExist:
                    pass
        return HttpResponse(status=200)
    return HttpResponse(status=405)
