import json

class TourPackage:
    def __init__(self, data):
        """Initialize a TourPackage object with default values for missing attributes."""
        self.name = data.get("name", "Unknown")
        self.location = data.get("location", "Unknown")
        self.price = data.get("price", 0.0)
        self.duration = data.get("duration", 0)
        self.season = data.get("season", "Year-round")
        self.activities = data.get("activities", [])
        self.accommodation_type = data.get("accommodation_type", "Not specified")
        self.rating = data.get("rating", 0.0)
        self.available_dates = data.get("available_dates", [])
        self.meal_plan = data.get("meal_plan", "Not specified")
        self.transport_type = data.get("transport_type", "Not specified")
        self.difficulty_level = data.get("difficulty_level", "Not specified")
        self.language_support = data.get("language_support", [])
        self.max_group_size = data.get("max_group_size", 0)
        self.seller = data.get("seller", "Unknown")
        self.seller_address = data.get("seller_address", "Not available")
        self.package_link = data.get("package_link", "")
        self.includes = data.get("includes", [])
        self.excludes = data.get("excludes", [])
        self.itinerary = data.get("itinerary", {})
        self.payment_policy = data.get("payment_policy", {})
        self.cancellation_policy = data.get("cancellation_policy", {})
        self.terms_conditions = data.get("terms_conditions", [])

class TourismRecommender:
    def __init__(self, json_file):
        """Load JSON file and initialize tour packages."""
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            self.tour_packages = [TourPackage(pkg) for pkg in data["tour_packages"]]

    def search_packages(self, location, preferences):
        """Search and filter tour packages based on user preferences."""
        # Normalize location to a string for cases where it's a list
        location_query = location.lower()

        filtered_packages = []
        for pkg in self.tour_packages:
            # Ensure `pkg.location` is always treated as a string
            package_locations = pkg.location if isinstance(pkg.location, list) else [pkg.location]
            package_locations_str = ", ".join(package_locations).lower()

            # Check if any location in the package matches the query
            if location_query in package_locations_str:
                filtered_packages.append(pkg)

        # Apply additional filters
        results = [
            pkg for pkg in filtered_packages
            if pkg.price <= preferences.get("max_price", float("inf")) and
            pkg.duration >= preferences.get("preferred_duration", 0) and
            (not preferences.get("preferred_activities") or any(act in pkg.activities for act in preferences["preferred_activities"])) and
            (not preferences.get("accommodation_type") or pkg.accommodation_type == preferences["accommodation_type"]) and
            (not preferences.get("meal_plan") or pkg.meal_plan == preferences["meal_plan"]) and
            (not preferences.get("transport_type") or pkg.transport_type == preferences["transport_type"]) and
            (not preferences.get("difficulty_level") or pkg.difficulty_level == preferences["difficulty_level"]) and
            (not preferences.get("required_languages") or any(lang in pkg.language_support for lang in preferences["required_languages"])) and
            pkg.max_group_size <= preferences.get("max_group_size", float("inf")) and
            pkg.rating >= preferences.get("min_rating", 0)
        ]

        return results

    def get_unique_values(self):
        """Extract unique values from tour packages for filtering."""
        unique_values = {
            "activities": set(),
            "accommodation_types": set(),
            "meal_plans": set(),
            "transport_types": set(),
            "difficulty_levels": set(),
            "languages": set(),
        }
        for pkg in self.tour_packages:
            unique_values["activities"].update(pkg.activities)
            unique_values["accommodation_types"].add(pkg.accommodation_type)
            unique_values["meal_plans"].add(pkg.meal_plan)
            unique_values["transport_types"].add(pkg.transport_type)
            unique_values["difficulty_levels"].add(pkg.difficulty_level)
            unique_values["languages"].update(pkg.language_support)

        return {key: sorted(list(value)) for key, value in unique_values.items()}
