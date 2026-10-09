"""
Budget Estimation Service for Sri Lankan Travel.
Calculates itemized expenditure across Accommodation, Transportation,
Food & Dining, Activities/Tickets, and Contingency buffers.
"""

# Current standard exchange rate approximation
LKR_PER_USD = 310.0

ACCOMMODATION_RATES_PER_ROOM = {
    "budget": 4000.0,      # Homestays / Guest houses / Hostels
    "mid_range": 12000.0,  # 3-star boutique hotels / Airbnbs
    "luxury": 35000.0      # 5-star beachfront & colonial tea bungalows
}

DAILY_FOOD_RATES_PER_PERSON = {
    "budget": 2500.0,      # Local rice & curry, rotis, hopper stalls
    "mid_range": 6000.0,   # Cafes, tourist restaurants, fresh seafood
    "luxury": 15000.0      # Fine dining, hotel buffets, wine
}

TRANSPORT_BASE_DAILY_RATES = {
    "public_transit": 1500.0,   # Scenic trains (1st/2nd class) & intercity buses
    "tuktuk": 4500.0,           # Daily local tuk-tuk runs
    "car_with_driver": 18000.0  # Private AC car/van with English speaking driver + fuel
}


def estimate_trip_budget(
    duration_days: int,
    num_travelers: int,
    destination_avg_costs: list[float] = None,
    travel_style: str = "mid_range",
    transport_mode: str = "car_with_driver",
    user_budget_lkr: float = 0.0
) -> dict:
    days = max(1, duration_days)
    travelers = max(1, num_travelers)
    # Rooms needed assuming 2 persons per room
    rooms_needed = (travelers + 1) // 2

    # 1. Accommodation
    night_rate = ACCOMMODATION_RATES_PER_ROOM.get(travel_style, ACCOMMODATION_RATES_PER_ROOM["mid_range"])
    total_accommodation = night_rate * rooms_needed * days

    # 2. Food & Dining
    food_rate = DAILY_FOOD_RATES_PER_PERSON.get(travel_style, DAILY_FOOD_RATES_PER_PERSON["mid_range"])
    total_food = food_rate * travelers * days

    # 3. Transportation
    daily_transport = TRANSPORT_BASE_DAILY_RATES.get(transport_mode, TRANSPORT_BASE_DAILY_RATES["car_with_driver"])
    total_transport = daily_transport * days

    # 4. Activities & Entrance Fees
    if destination_avg_costs:
        # Estimate tickets/activities based on destinations visited
        total_activities = sum(destination_avg_costs) * 0.45 * travelers
    else:
        # Default average activity rate per day per person
        total_activities = 3500.0 * travelers * days

    # 5. Contingency buffer (8% for unexpected tips, local crafts, water)
    subtotal = total_accommodation + total_food + total_transport + total_activities
    contingency = subtotal * 0.08

    total_estimated_lkr = round(subtotal + contingency, 2)
    total_estimated_usd = round(total_estimated_lkr / LKR_PER_USD, 2)

    cost_per_person_lkr = round(total_estimated_lkr / travelers, 2)
    cost_per_person_usd = round(total_estimated_usd / travelers, 2)

    # Budget comparison
    budget_status = "Not specified"
    variance_lkr = 0.0
    if user_budget_lkr > 0:
        variance_lkr = round(user_budget_lkr - total_estimated_lkr, 2)
        if variance_lkr >= 0:
            budget_status = f"Within budget (Save Rs. {int(variance_lkr):,})"
        else:
            budget_status = f"Exceeds budget by Rs. {int(abs(variance_lkr)):,}"

    return {
        "duration_days": days,
        "num_travelers": travelers,
        "travel_style": travel_style,
        "transport_mode": transport_mode,
        "breakdown": {
            "accommodation": {
                "amount_lkr": round(total_accommodation, 2),
                "amount_usd": round(total_accommodation / LKR_PER_USD, 2),
                "percentage": round((total_accommodation / total_estimated_lkr) * 100, 1),
                "description": f"{rooms_needed} room(s) for {days} nights ({travel_style})"
            },
            "transportation": {
                "amount_lkr": round(total_transport, 2),
                "amount_usd": round(total_transport / LKR_PER_USD, 2),
                "percentage": round((total_transport / total_estimated_lkr) * 100, 1),
                "description": f"{days} days of {transport_mode.replace('_', ' ')}"
            },
            "food_and_dining": {
                "amount_lkr": round(total_food, 2),
                "amount_usd": round(total_food / LKR_PER_USD, 2),
                "percentage": round((total_food / total_estimated_lkr) * 100, 1),
                "description": f"Breakfast, lunch & dinner for {travelers} travelers"
            },
            "activities_and_tickets": {
                "amount_lkr": round(total_activities, 2),
                "amount_usd": round(total_activities / LKR_PER_USD, 2),
                "percentage": round((total_activities / total_estimated_lkr) * 100, 1),
                "description": "Sanctuary permits, heritage site passes, safari jeeps & gear"
            },
            "contingency_buffer": {
                "amount_lkr": round(contingency, 2),
                "amount_usd": round(contingency / LKR_PER_USD, 2),
                "percentage": round((contingency / total_estimated_lkr) * 100, 1),
                "description": "8% buffer for unforeseen expenses, tipping, and souvenirs"
            }
        },
        "total_estimated_lkr": total_estimated_lkr,
        "total_estimated_usd": total_estimated_usd,
        "cost_per_person_lkr": cost_per_person_lkr,
        "cost_per_person_usd": cost_per_person_usd,
        "user_budget_lkr": user_budget_lkr,
        "variance_lkr": variance_lkr,
        "budget_status": budget_status
    }
