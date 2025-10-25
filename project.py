"""
Name:       Bella Levy
CS230:      4
Data:       New York Housing Market
URL:        Link to your web application on Streamlit Cloud (if posted)

Description:   This program looks at assisting someone who is looking to see what housing options are available in New York . It includes tools for the filtering property listings
               based on certain criteria such as price, number of beds, size of the property, and
               The program looks to answer three key questions:
               1) How can I filter the data to match my exact criteria in housing
                     - Which properties meet my criteria of min <BEDS>, max <PRICE> and min <PROPERTYSQFT>
               2) How does the cost of the available housing vary in each neighborhood
                     - What is the average price of each <TYPE> of listings in a specific <SUBLOCALITY>
               3) Which neighborhood/part of the city should I look in if I am looking for a specific type of housing?
                     - In which <SUBLOCALITY> are there the most <TYPE> listings for sale?
"""
#PS C:\Users\Bella\PythonProject> python -m streamlit run C:\Users\Bella\PythonProject\FinalProject\project.py
# python -m streamlit run C:\Users\Bella\PythonProject\FinalProject\project.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pydeck as pdk
import folium
import numpy as np

color = st.color_picker("Pick a theme color") #[ST4]
def horizontal_line(color=color): #[ST4]
   st.markdown(f'<hr style="border: 2px solid {color};">', unsafe_allow_html=True) #[ST4]

horizontal_line()

st.title("New York Hosuing Market")

st.markdown(
    """
    <style>
    iframe {
        background-color: black
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True
) #[ST4]

# How can I filter the data to match my exact criteria
# Which properties meet my criteria of min <BEDS>, max <PRICE> and min <PROPERTYSQFT>

def read_data():
  file = 'NY-House-Dataset.csv'
   df = pd.read_csv(file)
   df = df.dropna(subset=["PRICE", "LATITUDE", "LONGITUDE"])  #[DA1], #[DA7]
   df["PRICE"] = pd.to_numeric(df["PRICE"]) #[DA1], #[DA7], #[DA9]
   return df

def get_price_bounds(df): #[PY2]
   return int(df["PRICE"].min()), int(df["PRICE"].max()) #[PY2]

st.sidebar.header("Filter Listings") #[ST4]

df = read_data()
print(df)
all_neighborhoods = sorted(df["SUBLOCALITY"].dropna().unique())
if "selected_neighborhoods" not in st.session_state:
    st.session_state.selected_neighborhoods = ["Manhattan", "Brooklyn"]

selected_neighborhoods = st.sidebar.multiselect("Choose Neighborhoods", all_neighborhoods, default=st.session_state.selected_neighborhoods) #[ST1]

select_all_neighborhoods = st.sidebar.checkbox("Select All Neighborhoods", value=False) #[ST2]

if select_all_neighborhoods:
    selected_neighborhoods = all_neighborhoods
    st.session_state.selected_neighborhoods = all_neighborhoods

min_price, max_price = get_price_bounds(df)
price_range = st.sidebar.slider("Select Price Range", min_price, max_price, (min_price, max_price))  # [ST3]

min_beds = st.sidebar.number_input("Minimum Bedrooms", min_value=0, max_value=10, value=2)  # [ST3]
min_sqft = st.sidebar.number_input("Minimum Square Footage", min_value=0, value=500)

listing_types = [
    "Condo for sale", "House for sale", "Townhouse for sale", "Co-op for sale",
    "Multi-family home for sale", "Contingent", "Land for sale", "Foreclosure",
    "Coming Soon", "Pending", "For sale"
]

available_types = sorted(df["TYPE"].dropna().unique())
valid_types = [t for t in listing_types if t in available_types] #[PY4]

if "selected_types" not in st.session_state:
    st.session_state.selected_types = valid_types

selected_types = st.sidebar.multiselect(
    "Listing Type", valid_types, default=st.session_state.selected_types
) #[ST1]

select_all_types = st.sidebar.checkbox("Select All Listing Types", value=False) #[ST2]

if select_all_types:
    selected_types = valid_types
    st.session_state.selected_types = valid_types
else:
    st.session_state.selected_types = selected_types

filtered_df = df[
    (df["SUBLOCALITY"].isin(selected_neighborhoods)) &
    (df["TYPE"].isin(selected_types)) &
    (df["PRICE"] >= price_range[0]) &
    (df["PRICE"] <= price_range[1]) &
    (df["BEDS"] >= min_beds) &
    (df["PROPERTYSQFT"] >= min_sqft)
] #[DA1], #[DA5]

columns_to_display = ["TYPE", "PRICE", "BEDS", "BATH", "ADDRESS", "PROPERTYSQFT", "SUBLOCALITY", "BROKERTITLE"]
renamed_columns = {
    "TYPE": "Type",
    "PRICE": "Price",
    "BEDS": "Beds",
    "BATH": "Bath",
    "ADDRESS": "Address",
    "PROPERTYSQFT": "SqFt",
    "SUBLOCALITY": "Neighborhood",
    "BROKERTITLE": "Broker"
} #[PY5], #[DA7]
filtered_df = filtered_df.round({'BATH': 1}) #[DA1], #[DA9]

horizontal_line()
st.header("Filtered Housing Data")
st.caption("*** Use sidebar to make filter selections ***")
st.write(f"Showing {len(filtered_df)} results")

#TABS (https://docs.streamlit.io/develop/api-reference/layout/st.tabs)
tab1, tab2 = st.tabs(["Filtered Listings", "Maps of Filtered Listings"]) #[ST4]
with tab1: #[ST4]
   st.subheader("Filtered Data")
   st.dataframe(filtered_df[columns_to_display].rename(columns=renamed_columns)) #[PY5]

with tab2: #[ST4]
   st.subheader("Maps Showing Filtered Listings")
   filtered_df = filtered_df.dropna(subset=["LATITUDE", "LONGITUDE", "PRICE"])
   filtered_df = filtered_df.rename(columns={"LATITUDE": "lat", "LONGITUDE": "lon"}) #[DA7]

   layer = pdk.Layer(
      "ScatterplotLayer",
      data=filtered_df,
      get_position='[lon, lat]',
      get_radius=200,
      get_fill_color='[400, 0, 0, 160]',
      pickable=True,
   )
   view_state = pdk.ViewState(
      latitude=filtered_df["lat"].mean(),
      longitude=filtered_df["lon"].mean(),
      zoom=10,
      pitch=0,
   )
   tooltip = {
      "html": "<b>Price:</b> ${PRICE}<br/><b>Type:</b> {TYPE}<br/><b>Beds:</b> {BEDS}",
      "style": {"backgroundColor": "steelblue", "color": "white"}
   } #[PY5]

   st.pydeck_chart(pdk.Deck(
      map_style="mapbox://styles/mapbox/light-v9",
      initial_view_state=view_state,
      layers=[layer],
      tooltip=tooltip
   ))

   from streamlit_folium import st_folium
   #Reference: https://python-visualization.github.io/folium/latest/getting_started.html
   map = folium.Map(location=[filtered_df["lat"].mean(), filtered_df["lon"].mean()], zoom_start=11)  #[FOLIUM1]

   def create_marker(row):
      details = {
         "Price": f"${row['PRICE']:,}",
         "Type": row["TYPE"],
         "Beds": row["BEDS"],
         "Address": row["ADDRESS"]
      }

      popup_html = "<br>".join(f"<b>{key}:</b> {value}" for key, value in details.items())
      popup = folium.Popup(popup_html, max_width=300)

      return folium.Marker(
         location=(row["lat"], row["lon"]),
         popup=popup,
         icon=folium.Icon(color=color, icon="home", prefix="fa")
      ).add_to(map)

   filtered_df.apply(create_marker, axis=1)
   st_folium(map, width=1000, height=500)


# How does the cost of the available housing vary in each neighborhood
# What is the average price of each <TYPE> of listings in a specific <SUBLOCALITY>
horizontal_line()
st.header("Pricing vs Neighborhoods")

# Resource: https://docs.streamlit.io/develop/api-reference/layout/st.tabs
tab1, tab2 = st.tabs(["Average Price of All Neighborhoods", "Pricing in a Select Neighboorhod"]) #[ST4]
with tab1: #[ST4]
   import matplotlib.ticker as ticker
   st.subheader("Average Price of All Neighborhoods")  # [SEA1]
   avg_price = df.groupby("SUBLOCALITY")["PRICE"].mean().sort_values(ascending=False)  # [DA2], [DA7]
   #Resource: https://seaborn.pydata.org/generated/seaborn.set_theme.html
   sns.set_theme(style="white")
   fig2, ax2 = plt.subplots(figsize=(12, 6))
   sns.barplot(x=avg_price.values, y=avg_price.index, ax=ax2, color=color)
   ax2.set_title("Neighborhoods by Average Price")
   ax2.set_xlabel("Average Price")
   ax2.set_ylabel("Neighborhood")
   ax2.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
   st.pyplot(fig2)
with tab2: #[ST4]
   st.subheader("Average Price by Listing Type in a Selected Neighborhood")
   selected_sublocality = st.selectbox("Choose a Neighborhood", all_neighborhoods)
   subset_df = df[(df["SUBLOCALITY"] == selected_sublocality) & (df["TYPE"])] #[DA4]
   try: #[PY3]
      avg_prices = subset_df.groupby("TYPE")["PRICE"].mean() #[DA7]
      avg_price_by_type = pd.Series(avg_prices, index=listing_types).sort_values(ascending=False) #[DA2]
      fig4, ax4 = plt.subplots(figsize=(10, 5))
      avg_price_by_type.plot(kind="bar", color=color, ax=ax4)
      ax4.set_title(f"Average Price by Listing Type in {selected_sublocality}")
      ax4.set_ylabel("Average Price")
      ax4.set_xlabel("Type of Listing")
      ax4.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
      st.pyplot(fig4)
   except: #[PY3]
      st.warning("Unable to display data. This neighborhood may not have listings for the selected types.")


# Which neighborhood/part of the city should I look in if I am looking for a specific type of housing?
# In which <SUBLOCALITY> are there the most <TYPE> listings for sale?
horizontal_line()
st.header("Locations of the Listings")
type_choice = st.selectbox("Choose a Listing Type:", valid_types)

type_filtered_df = df[df["TYPE"] == type_choice] #[DA4]
listing_counts = type_filtered_df["SUBLOCALITY"].value_counts().sort_values(ascending=False) #[DA2]

tab1, tab2 = st.tabs([f"Neighborhoods with the highest {type_choice} listings", f"Map of the {type_choice} listings"]) #[ST4]
with tab1: #[ST4]
   st.subheader(f"Neighborhoods with the highest {type_choice} listings")
   listing_table = listing_counts.reset_index()
   listing_table.columns = ["Neighborhood", "Number of Listings"] #[DA7]
   st.dataframe(listing_table)
with tab2: #[ST4]
   st.subheader(f"Map of the {type_choice} listings")

   type_filtered_df = type_filtered_df.dropna(subset=["LATITUDE", "LONGITUDE"])
   type_filtered_df = type_filtered_df.rename(columns={"LATITUDE": "lat", "LONGITUDE": "lon"})

   layer = pdk.Layer(
      "ScatterplotLayer",
      data=type_filtered_df,
      get_position='[lon, lat]',
      get_radius=200,
      get_fill_color='[255, 100, 100, 160]',
      pickable=True,
   )
   view_state = pdk.ViewState(
      latitude=type_filtered_df["lat"].mean(),
      longitude=type_filtered_df["lon"].mean(),
      zoom=10,
      pitch=0,
   )
   tooltip = {
      "html": "<b>Price:</b> ${PRICE}<br/><b>Beds:</b> {BEDS}<br/><b>Neighborhood:</b> {SUBLOCALITY}",
      "style": {"backgroundColor": "steelblue", "color": "white"}
   } #[PY5]
   st.pydeck_chart(pdk.Deck(
      map_style="mapbox://styles/mapbox/light-v9",
      initial_view_state=view_state,
      layers=[layer],
      tooltip=tooltip
   )) #[MAP]

horizontal_line()

if st.button("Click for a suprise"):
   st.balloons()


