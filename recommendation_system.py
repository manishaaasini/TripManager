import streamlit as st
from tourism_recommendation import TourismRecommender

def main():
    st.title("🌍 Tourism Package Recommender")
    st.write("Find your perfect vacation package!")

    try:
        # Initialize recommender
        recommender = TourismRecommender("tour_packages.json")

        # Search bar for location
        location_query = st.text_input("🔍 Search for a location (e.g., Munnar, Kerala)", "").strip()

        # Sidebar filters
        st.sidebar.header("🛠️ Filters")

        # Price filter
        st.sidebar.subheader("💰 Price Limit")
        max_price = st.sidebar.number_input("Enter Maximum Price (₹)", min_value=5000, max_value=50000, value=20000, step=1000)

        # Duration filter
        preferred_duration = st.sidebar.slider("🕒 Preferred Duration (days)", 3, 15, 7)

        # Activities
        unique_activities = recommender.get_unique_values()["activities"]
        preferred_activities = st.sidebar.multiselect("🎯 Preferred Activities", unique_activities)

        # Accommodation Type
        unique_accommodations = recommender.get_unique_values()["accommodation_types"]
        accommodation_type = st.sidebar.selectbox("🏨 Accommodation Type", ["Any"] + unique_accommodations)

        # Advanced Filters
        with st.sidebar.expander("⚙️ Advanced Filters"):
            unique_meal_plans = recommender.get_unique_values()["meal_plans"]
            meal_plan = st.selectbox("🍽️ Meal Plan", ["Any"] + unique_meal_plans)

            unique_transport_types = recommender.get_unique_values()["transport_types"]
            transport_type = st.selectbox("🚗 Transport Type", ["Any"] + unique_transport_types)

            unique_difficulty_levels = recommender.get_unique_values()["difficulty_levels"]
            difficulty_level = st.selectbox("🔧 Difficulty Level", ["Any"] + unique_difficulty_levels)

            unique_languages = recommender.get_unique_values()["languages"]
            required_languages = st.multiselect("🗣️ Required Languages", unique_languages, default=["English"])

            max_group_size = st.number_input("👥 Maximum Group Size", 1, 100, 20)
            min_rating = st.slider("⭐ Minimum Rating", 1.0, 5.0, 4.0, 0.1)

        # Build preferences dictionary
        preferences = {
            "max_price": max_price,
            "preferred_activities": preferred_activities,
            "accommodation_type": accommodation_type if accommodation_type != "Any" else None,
            "preferred_duration": preferred_duration,
            "meal_plan": meal_plan if meal_plan != "Any" else None,
            "transport_type": transport_type if transport_type != "Any" else None,
            "difficulty_level": difficulty_level if difficulty_level != "Any" else None,
            "required_languages": required_languages,
            "max_group_size": max_group_size,
            "min_rating": min_rating
        }

        # Search results
        if location_query:
            results = recommender.search_packages(location_query, preferences)

            if not results:
                st.warning("⚠️ No results found. Try adjusting your filters.")
            else:
                st.success(f"✅ Found {len(results)} matching packages!")

                for package in results:
                    with st.expander(f"📍 {package.name} - ₹{package.price:.2f}"):
                        st.write(f"**📍 Location:** {package.location}")
                        st.write(f"**🕒 Duration:** {package.duration} Days")
                        st.write(f"**⭐ Rating:** {package.rating} / 5.0")
                        st.write(f"**🏨 Accommodation:** {package.accommodation_type}")
                        st.write(f"**🍽️ Meal Plan:** {package.meal_plan}")
                        st.write(f"**🚗 Transport:** {package.transport_type}")
                        st.write(f"**🔧 Difficulty:** {package.difficulty_level}")
                        st.write(f"**👥 Max Group Size:** {package.max_group_size}")
                        st.write(f"**🏷️ Seller:** {package.seller}")
                        st.write(f"**📍 Seller Address:** {package.seller_address}")

                        if package.package_link:
                            st.markdown(f"🔗 **[Book Now]({package.package_link})**", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
