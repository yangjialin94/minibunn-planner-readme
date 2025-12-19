from typing import Optional

from pydantic import BaseModel, ConfigDict


class StripeCheckout(BaseModel):
    """
    Schema for Stripe Checkout session creation.
    """

    url: str

    model_config = ConfigDict(from_attributes=True)


class SubscriptionStatus(BaseModel):
    """
    Schema for subscription status.
    """

    is_subscribed: bool
    status: Optional[str] = None
    period_end_date: Optional[str] = None
    cancel_at_period_end: Optional[bool] = None
    plan_name: Optional[str] = None
    price_amount: Optional[float] = None
    price_currency: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CheckoutSessionCreate(BaseModel):
    """
    Schema for creating a Stripe Checkout session.
    """

    price_id: str
    mode: str
    success_url: str
    cancel_url: str

    model_config = ConfigDict(from_attributes=True)
