import stripe

from config import API_SECRET_KEY

stripe.api_key = API_SECRET_KEY


def create_stripe_product(name, description):
    """Создает продукт в Stripe."""
    return stripe.Product.create(name=name, description=description)


def create_stripe_price(product_id, unit_amount, currency="rub"):
    """Создает цену в Stripe."""
    return stripe.Price.create(
        product=product_id, unit_amount=unit_amount, currency=currency
    )


def create_stripe_session(
    price_id,
    quantity=1,
    success_url="https://example.com/success",
    cancel_url="https://yourwebsite.com/cancel",
):
    """Создает сессию в Stripe."""
    return stripe.checkout.Session.create(
        line_items=[
            {
                "price": price_id,
                "quantity": quantity,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
