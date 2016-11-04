from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Max
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Item

import logging
# Create your views here.

logger = logging.getLogger(__name__)

def convert_item_to_attachment(item):
    fields = [
        {
            "title": item.name,
            "value": item.description,
            "short": False
        },
        {
            "title": "Price",
            "value": "${}/{}".format(item.price, item.unit),
            "short": True
        },
        {
            "title": "Quantity",
            "value": "{} {}".format(item.quantity, item.unit),
            "short": True
        }
    ]
    fallback = "{} - Price: ${}/{} Quantity: {}".format(item.name, item.price, item.unit, item.quantity)
    return {
        "fallback": fallback,
        "fields": fields
    }

def inventory(request):
    items = Item.objects.all()
    last_updated = items.aggregate(Max('updated_at'))['updated_at__max']
    data = {
        "response_type": "in_channel",
        "text": "Current inventory as of *_{}_*\nPayment methods: cash or <https://cash.me/$punknpoultry>".format(last_updated.date()),
        "attachments": list(map(convert_item_to_attachment, items))
    }
    return JsonResponse(data)

def order(request):
    send_mail(
        "New Order",
        "From: <{}> ({})\nOrder: {}".format(request.POST['user_name'], request.POST['user_id'], request.POST['text']),
        "noreply@punknpoultry.com",
        ["orders@punknpoultry.com"],
        fail_silently=False,
    )
    data = {
        "text": "Hi {}, your order has been sent to orders@punknpoultry.com. :thankyou:".format(request.POST['user_name'])
    }
    return JsonResponse(data)

def help():
    data = {
    "text": "Available commands:",
    "attachments": [
        {
            "fallback": "inventory - Shows current inventory and price list\norder <order text> - Send your order to Punk N Poultry\nExample: /farm order 3 dz duck eggs\nhelp - Displays this message",
            "fields": [
                        {
                            "title": "inventory",
                            "value": "Shows current inventory and price list",
                            "short": False
                        },
                        {
                            "title": "order <order text>",
                            "value": "Send your order to Punk N Poultry\nExample: /farm order 3 dz duck eggs",
                            "short": False
                        },
                        {
                            "title": "help",
                            "value": "Displays this message.",
                            "short": False
                        }
            ]
        }
    ]
}
    return JsonResponse(data)

@csrf_exempt
def farm(request):
    if settings.SLACK_TOKEN != request.POST['token']:
        return HttpResponse(status=403)

    logger.info("Incoming farm request: {}".format(request.POST))
    text = request.POST['text'].strip().lower()
    if text.startswith('inv'):
        return inventory(request)
    elif text.startswith('order'):
        return order(request)
    else:
        return help()

