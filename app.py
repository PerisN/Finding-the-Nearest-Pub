import streamlit as st
import pandas as pd
from geopy.distance import distance
import folium
from streamlit_folium import folium_static
from scipy.spatial.distance import cdist

# Load the dataset
df = pd.read_csv("Data\data.csv")

# Define function to calculate Euclidean distance
def euclidean_distance(lat1, lon1, lat2, lon2):
    return distance((lat1, lon1), (lat2, lon2)).km

# Define function to filter pubs by postcode or local authority
def filter_pubs(df, column, keyword):
    return df[df[column].str.contains(keyword, case=False)]

# Define function to find the nearest pubs
def find_nearest_pubs(df, user_lat, user_lon, n):
    df["distance"] = df.apply(lambda row: euclidean_distance(user_lat, user_lon, row["latitude"], row["longitude"]), axis=1)
    nearest_pubs = df.sort_values(by="distance").head(n)
    return nearest_pubs

# Define function to display a folium map in Streamlit
def folium_map_to_html(m):
    folium_static(m, width=800, height=500)
    return None

# Define the pages
pages = {
    "Home Page": st.sidebar,
    "Pub Locations": st.sidebar,
    "Find the nearest Pub": st.sidebar
}

# Define the content for each page
page_content = {
    "Home Page": {
        "title": "Welcome to the Pubs Finder",
        "content": [
            f"Number of Pubs: {len(df)}",
            f"Number of Unique Postcodes: {len(df['postcode'].unique())}",
            f"Top 5 Local Authorities with most Pubs:\n{df['local_authority'].value_counts().head()}"
            ],
        "map": df[["latitude", "longitude"]]
    },
    "Pub Locations": {
        "title": "Find Pubs by Postal Code or Local Authority",
        "subtitle": "Enter the Postal Code or Local Authority to display all the pubs in the area:",
        "content": []
    },

    "Find the nearest Pub": {
        "title": "Find the nearest Pubs",
        "subtitle": "Enter your Latitude and Longitude to display the nearest 5 pubs on the map:",
        "content": []
    }
}

# Display the selected page
selected_page = st.sidebar.selectbox("Select a Page", list(pages.keys()))
pages[selected_page].title(page_content[selected_page]["title"])

# Home Page
if selected_page == "Home Page":
    st.header(page_content[selected_page]["title"])
    for item in page_content[selected_page]["content"]:
        st.write(item)
    st.map(df[["latitude", "longitude"]])
    st.write("Note: Map may take a while to load all the pubs.")  

# Pub Locations
elif selected_page == "Pub Locations":
    location_type = pages[selected_page].selectbox("Select Location Type", ["Postal Code", "Local Authority"])
    if location_type == "Postal Code":
        keyword = pages[selected_page].selectbox("Enter Postal Code", df["postcode"].unique())
        filtered_df = filter_pubs(df, "postcode", keyword)
    else:
        keyword = pages[selected_page].selectbox("Enter Local Authority", df["local_authority"].unique())
        filtered_df = filter_pubs(df, "local_authority", keyword)
    if len(filtered_df) == 0:
        st.write(f"No pubs found for {keyword}")
    else:
        page_content[selected_page]["content"] = [
            f"{len(filtered_df)} Pubs found for {keyword}:",
            filtered_df[["name", "address", "postcode"]].to_html(index=False)
        ]
        st.write(page_content[selected_page]["content"][0])
        st.write(page_content[selected_page]["content"][1], unsafe_allow_html=True)
        st.map(filtered_df[["latitude", "longitude"]])

# Find the nearest Pub
elif selected_page == "Find the nearest Pub":
    user_lat = st.number_input("Enter your Latitude:", min_value=-90.0, max_value=90.0, value=0.0)
    user_lon = st.number_input("Enter your Longitude:", min_value=-180.0, max_value=180.0, value=0.0)
    max_distance = st.number_input("Enter the maximum distance to search for pubs (in km):", min_value=0.0, value=5.0)

    # create a new dataframe with only the necessary columns
    pubs_df = df[['name', 'latitude', 'longitude']]

    # calculate the Euclidean distance between the user's location and each pub location
    dist = cdist([[user_lat, user_lon]], pubs_df[['latitude', 'longitude']])
    pubs_df['distance'] = dist[0]

    # select the nearest pubs within the maximum distance
    nearest_pubs = pubs_df[pubs_df['distance'] <= max_distance].sort_values(by=['distance'])

    # Create a folium map centered on the user's location
    map = folium.Map(location=[user_lat, user_lon], zoom_start=12, tiles='cartodbpositron', attr='Map tiles by Carto, under CC BY 3.0. Data by OpenStreetMap, under ODbL.')

    # Add markers for the nearest pubs to the map
    for pub in nearest_pubs.itertuples():
        folium.Marker(location=[pub.latitude, pub.longitude], tooltip=pub.name).add_to(map)

    # Render the map using Streamlit
    st.markdown(f"### Nearest Pubs to ({user_lat:.3f}, {user_lon:.3f})")
    st.markdown(f"Showing the {len(nearest_pubs)} nearest pubs within {max_distance:.2f} km radius")
    st.markdown(folium_map_to_html(map), unsafe_allow_html=True)




