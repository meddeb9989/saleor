from ...checkout import models


def resolve_checkout_lines(info, query):
    queryset = models.CheckoutLine.objects.all()
    return queryset


def resolve_checkouts(info, query):
    queryset = models.Checkout.objects.all()
    return queryset


def resolve_checkout(info, token):
    checkout = models.Checkout.objects.filter(token=token).first()
    return checkout
