## Theme
- This project helps UOP students find proper housing near UOP stockton campus by good rent price and distance from campus

## Dataset columns
- All columns: dict_keys(['id', 'formattedAddress', 'addressLine1', 'addressLine2', 'city', 'state', 'stateFips', 'zipCode', 'county', 'countyFips', 'latitude', 'longitude', 'propertyType', 'bedrooms', 'bathrooms', 'squareFootage', 'status', 'price', 'listingType', 'listedDate', 'removedDate', 'createdDate', 'lastSeenDate', 'daysOnMarket', 'history'])

- Columns used: name, address, city, state, zip, rent, bedrooms, bathrooms, sqft, property_type, latitude, longitude, distance_from_uop_miles, listing_url

## Workflow
1. Data Collection
    - Data is from the Rentcast API
2. Data Processing
    - The API response is converted into a DataFrame, where each listing becomes a row and each key becomes a column
    - Missing values are handled by selecting the first available non-null value
3. Filtering / Ranking
    - Listings are filtered and ranked based on price range and distance
4. Visualization / Dashboard
    - The processed data is visualized using charts and maps using Streamlit

## Setup
Create a `.env` file in the project folder

```bash
.env file should look like this.

RENTCAST_API_KEY=your_api_key_here
```

## Install requirements.txt and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

- if it doesn't work, try:
```bash
python -m streamlit run app.py
```
