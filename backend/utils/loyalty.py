from database.models import Client, Promotion
from datetime import datetime

def calculate_loyalty_points(amount):
    """
    Calculate loyalty points based on purchase amount.
    Base rate: 1 point per 10 currency units
    """
    base_points = int(amount / 10)

    # Check for active promotions that might affect point calculation
    active_promotions = Promotion.query.filter(
        Promotion.is_active == True,
        Promotion.end_date >= datetime.utcnow(),
        Promotion.discount_type == 'loyalty_multiplier'
    ).all()

    # Apply any active point multipliers
    multiplier = 1.0
    for promo in active_promotions:
        if promo.discount_value > multiplier:
            multiplier = promo.discount_value

    return int(base_points * multiplier)

def get_client_tier(client):
    """
    Determine client loyalty tier based on total points
    """
    points = client.loyalty_points

    if points >= 1000:
        return 'platinum'
    elif points >= 500:
        return 'gold'
    elif points >= 100:
        return 'silver'
    else:
        return 'bronze'

def get_tier_benefits(tier):
    """
    Get benefits associated with each loyalty tier
    """
    benefits = {
        'platinum': {
            'discount': 0.15,  # 15% discount
            'free_drinks': 2,  # Free drinks per month
            'priority_service': True
        },
        'gold': {
            'discount': 0.10,  # 10% discount
            'free_drinks': 1,  # Free drink per month
            'priority_service': True
        },
        'silver': {
            'discount': 0.05,  # 5% discount
            'free_drinks': 0,
            'priority_service': False
        },
        'bronze': {
            'discount': 0.00,
            'free_drinks': 0,
            'priority_service': False
        }
    }
    return benefits.get(tier, benefits['bronze'])

def apply_loyalty_discount(client, amount):
    """
    Apply loyalty discount to purchase amount
    """
    tier = get_client_tier(client)
    benefits = get_tier_benefits(tier)
    discount = amount * benefits['discount']
    return amount - discount

def check_free_drinks_eligibility(client):
    """
    Check if client is eligible for free drinks based on their tier
    """
    tier = get_client_tier(client)
    benefits = get_tier_benefits(tier)

    if benefits['free_drinks'] > 0:
        # Check if client has used their free drinks this month
        current_month = datetime.utcnow().month
        current_year = datetime.utcnow().year

        # This would need to be implemented in the database
        # For now, we'll assume they haven't used their free drinks
        return benefits['free_drinks']

    return 0