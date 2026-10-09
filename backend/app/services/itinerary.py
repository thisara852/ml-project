"""
Trip Planning and Day-by-Day Itinerary Generation Engine.
Sequences tourist destinations by geographical proximity and time constraints
into realistic morning, afternoon, and evening travel schedules.
"""

from typing import List, Dict


def generate_itinerary(
    destinations: List[Dict],
    duration_days: int = 3,
    starting_location: str = "Colombo",
    interests: List[str] = None
) -> Dict:
    """
    Generate an optimized day-by-day itinerary given recommended destinations.
    """
    days_count = max(1, min(duration_days, 14))
    
    if not destinations:
        return {"error": "No destinations provided to plan itinerary"}

    # Sort destinations to form coherent travel corridors
    # (e.g. Western -> Southern -> Uva/Hill Country -> Central -> North Central)
    region_priority = {
        "Western": 1,
        "Southern": 2,
        "Sabaragamuwa": 3,
        "Uva": 4,
        "Central": 5,
        "Eastern": 6,
        "North Central": 7,
        "North Western": 8,
        "Northern": 9
    }

    sorted_dests = sorted(
        destinations,
        key=lambda d: (region_priority.get(d.get("province", ""), 5), -d.get("rating", 4.5))
    )

    days_plan = []
    dest_idx = 0
    num_dests = len(sorted_dests)

    for day in range(1, days_count + 1):
        # Pick 1-2 primary destinations for the day
        day_dest = sorted_dests[dest_idx % num_dests]
        dest_idx += 1
        
        secondary_dest = None
        if num_dests > days_count and (dest_idx < num_dests):
            candidate = sorted_dests[dest_idx % num_dests]
            # Pair if in same or adjacent province
            if candidate.get("province") == day_dest.get("province"):
                secondary_dest = candidate
                dest_idx += 1

        day_title = f"Day {day}: Exploring {day_dest.get('name')}"
        if secondary_dest:
            day_title += f" & {secondary_dest.get('name')}"

        activities_list = [act.strip() for act in str(day_dest.get("activities", "")).split(",") if act.strip()]
        primary_activity = activities_list[0] if activities_list else "Sightseeing"
        secondary_activity = activities_list[1] if len(activities_list) > 1 else "Photography"

        morning = {
            "time": "08:00 AM - 11:30 AM",
            "destination": day_dest.get("name"),
            "activity": f"Morning exploration: {primary_activity}",
            "description": f"Begin your day visiting {day_dest.get('name')}. Enjoy pleasant morning temperatures and pristine lighting for photography.",
            "tip": f"Ideal for {day_dest.get('category')}. Bring water and camera gear."
        }

        if secondary_dest:
            sec_activities = [act.strip() for act in str(secondary_dest.get("activities", "")).split(",") if act.strip()]
            sec_act = sec_activities[0] if sec_activities else "Cultural Walk"
            afternoon = {
                "time": "01:30 PM - 04:30 PM",
                "destination": secondary_dest.get("name"),
                "activity": f"Afternoon session: {sec_act}",
                "description": f"Transit short distance to {secondary_dest.get('name')}. {secondary_dest.get('description')[:120]}...",
                "tip": f"Best visited around {secondary_dest.get('best_season', 'Year-round')}."
            }
        else:
            afternoon = {
                "time": "01:00 PM - 04:30 PM",
                "destination": day_dest.get("name"),
                "activity": f"Afternoon deep-dive: {secondary_activity}",
                "description": f"Continue relaxing or engaging in secondary activities around {day_dest.get('district')} district.",
                "tip": "Sample local Ceylon tea or king coconut from roadside stalls."
            }

        evening = {
            "time": "05:30 PM - 08:30 PM",
            "destination": f"{day_dest.get('district')} Scenic Environs",
            "activity": "Golden Hour Sunset & Traditional Dinner",
            "description": f"Catch scenic dusk views in {day_dest.get('province')} province followed by an authentic Sri Lankan dinner (curries, hoppers, or coastal seafood).",
            "tip": "Book dinner or seaside tables in advance during peak season."
        }

        days_plan.append({
            "day": day,
            "title": day_title,
            "province": day_dest.get("province"),
            "district": day_dest.get("district"),
            "primary_destination_id": day_dest.get("id"),
            "primary_destination_name": day_dest.get("name"),
            "image_url": day_dest.get("image_url"),
            "schedule": {
                "morning": morning,
                "afternoon": afternoon,
                "evening": evening
            },
            "estimated_transit_hours": 1.5 if day > 1 else 2.5,
            "recommended_overnight_stay": f"Boutique hotel or scenic eco-lodge in {day_dest.get('district')}"
        })

    return {
        "trip_name": f"{days_count}-Day Sri Lanka Explorer from {starting_location}",
        "starting_location": starting_location,
        "duration_days": days_count,
        "total_stops": len(days_plan),
        "days": days_plan
    }
