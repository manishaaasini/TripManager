import json
import re

def extract_structured_data(text_file, output_json="structured_yatra_package.json"):
    with open(text_file, "r", encoding="utf-8") as file:
        raw_text = file.read()

    # Extract Name
    name_match = re.search(r"^(.*?)\nSeller", raw_text, re.MULTILINE)
    name = name_match.group(1).strip() if name_match else None

    # Extract Price
    price_match = re.search(r"Starting From\s*Rs\.([\d,]+)", raw_text)
    price = float(price_match.group(1).replace(",", "")) if price_match else None

    # Extract Duration
    duration_match = re.search(r"(\d+) Nights", raw_text)
    duration = int(duration_match.group(1)) if duration_match else None

    # Extract Activities
    activities_match = re.findall(r"Themes\s+(.*?)\n", raw_text)
    activities = activities_match[0].split("\n") if activities_match else None

    # Extract Locations (Convert to lowercase and remove duplicates)
    location_match = re.findall(r"(Mussoorie|Rishikesh|Haridwar|Nainital|Uttarakhand|Delhi|Jaipur|Goa)", raw_text, re.IGNORECASE)
    location = list(set(loc.lower().capitalize() for loc in location_match)) if location_match else None  # Normalize to capitalized form

    # Extract Rating (Default to 4.0 if not found)
    rating_match = re.search(r"(\d\.\d)\s*stars", raw_text, re.IGNORECASE)
    rating = float(rating_match.group(1)) if rating_match else 4.0  # Default rating is 4.0

    # Extract Available Dates
    available_dates_match = re.findall(r"(March|April|May|June|July|August|September|October|November|December|January|February) \d{4}", raw_text)
    available_dates = list(set(available_dates_match)) if available_dates_match else None

    # Extract Meal Plan (Ignore invalid values like "Sightseeing")
    meal_plan_match = re.search(r"Meals\s*[:\-]?\s*(.*?)\n", raw_text, re.IGNORECASE)
    meal_plan = meal_plan_match.group(1).strip() if meal_plan_match else None
    if meal_plan and ("Sightseeing" in meal_plan or "Departure Dates" in meal_plan):
        meal_plan = None  # Remove incorrect values

    # Extract Transport Type (Ensure it's correct)
    transport_match = re.search(r"Transport\s+(.*?)\n", raw_text)
    transport_type = transport_match.group(1).strip() if transport_match else None
    if transport_type and transport_type in ["Departure Dates"]:  # Remove incorrect values
        transport_type = None

    # Extract Inclusions
    inclusions_match = re.search(r"Inclusions\s+(.*?)\nLess", raw_text, re.DOTALL)
    inclusions = [item.strip() for item in inclusions_match.group(1).split("\n") if item.strip()] if inclusions_match else None

    # Extract Exclusions
    exclusions_match = re.search(r"Exclusions\s+(.*?)\nLess", raw_text, re.DOTALL)
    exclusions = [item.strip() for item in exclusions_match.group(1).split("\n") if item.strip()] if exclusions_match else None

    # Extract Itinerary
    itinerary_match = re.findall(r"Day (\d+) - (.*?)\n(.*?)\n", raw_text)
    itinerary = {f"Day {day}": f"{title} - {desc}" for day, title, desc in itinerary_match} if itinerary_match else None

    # Extract Payment Policy
    payment_policy_match = re.findall(r"(\d+ or more days before departure): (.*?)\n", raw_text)
    payment_policy = {match[0]: match[1] for match in payment_policy_match} if payment_policy_match else None

    # Extract Cancellation Policy
    cancellation_policy_match = re.findall(r"(\d+ or more days before departure): (.*?)\n", raw_text)
    cancellation_policy = {match[0]: match[1] for match in cancellation_policy_match} if cancellation_policy_match else None

    # Extract Seller Information
    seller_match = re.search(r"Seller : (.*?)\s", raw_text)
    seller = seller_match.group(1).strip() if seller_match else None

    # Extract Package Link
    package_link_match = re.search(r"https://packages.yatra.com/holidays/details.htm\?packageId=.*", raw_text)
    package_link = package_link_match.group(0).strip() if package_link_match else None

    # Extract Difficulty Level
    difficulty_match = re.search(r"Difficulty Level\s+(.*?)\n", raw_text)
    difficulty_level = difficulty_match.group(1).strip() if difficulty_match else None

    # Extract Language Support
    language_match = re.findall(r"Language Support\s+(.*?)\n", raw_text)
    language_support = language_match if language_match else None

    # Extract Maximum Group Size
    max_group_size_match = re.search(r"Max Group Size\s+(\d+)", raw_text)
    max_group_size = int(max_group_size_match.group(1)) if max_group_size_match else None

    # Extract Terms & Conditions
    terms_conditions_match = re.search(r"Terms & Conditions\s+(.*?)\nLess", raw_text, re.DOTALL)
    terms_conditions = [item.strip() for item in terms_conditions_match.group(1).split("\n") if item.strip()] if terms_conditions_match else None

    structured_data = {
        "name": name,
        "location": location,  # ✅ Now removes duplicates & normalizes case
        "price": price,
        "duration": duration,
        "season": None,  # Not explicitly mentioned in text
        "activities": activities,
        "accommodation_type": ">= 3 stars",  # Assuming from previous logic
        "rating": rating,  # ✅ Now correctly extracted, defaults to 4.0 if missing
        "available_dates": available_dates,
        "meal_plan": meal_plan,  # ✅ Now correctly extracted
        "transport_type": transport_type,  # ✅ Now correctly extracted
        "difficulty_level": difficulty_level,
        "language_support": language_support,
        "max_group_size": max_group_size,
        "seller": seller,
        "seller_address": "6th Floor, Tower D, Unitech Cyberpark, Sec 39, Gurgaon, Haryana 122002",
        "package_link": package_link,
        "includes": inclusions,
        "excludes": exclusions,
        "itinerary": itinerary,
        "payment_policy": payment_policy,
        "cancellation_policy": cancellation_policy,
        "terms_conditions": terms_conditions
    }

    # Remove any None values
    structured_data = {k: v for k, v in structured_data.items() if v is not None}

    # Save structured data as JSON
    with open(output_json, "w", encoding="utf-8") as file:
        json.dump(structured_data, file, indent=4)

    print(f"Data successfully structured and saved as {output_json}")

# Example usage
extract_structured_data("thrillophilia_package_details.txt")
