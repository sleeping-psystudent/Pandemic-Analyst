# Pandemic Analyst

[Live App](https://pandemic-analyst-map.streamlit.app/)

## Overview

Pandemic Analyst Map is an interactive web application designed to visualize global disease risks in an intuitive and user-friendly way. The app leverages a ScatterplotLayer on an interactive map to display real-time data on disease outbreaks, categorized by their risk levels. Users can explore detailed summaries, filter results, and adjust parameters for better insights into global health concerns.

## Features

- **Interactive Map Visualization**: Displays disease risks using color-coded markers based on severity.
- **Customizable Filters**:
  - Date range selection to focus on recent or historical data.
  - Disease type filtering to display specific diseases.
  - Risk level filtering to highlight areas of interest.
- **Detailed Summaries**:
  - Hover over map markers to view detailed information, including summaries, publication dates, and risk assessments.
- **Responsive Design**: Optimized for both desktop and mobile platforms.

## Technologies Used

- **Frontend**:
  - Streamlit for UI design and hosting.
  - Pydeck for map visualization.
  - Custom HTML and CSS for tooltips and styling.
- **Backend**:
  - SQLite for data storage.
  - Pandas for data manipulation.
- **Data Visualization**:
  - Mapbox API integration for map rendering.

## Deployment

The app is deployed on Streamlit Cloud. The live version is accessible at: [https://pandemic-analyst-map.streamlit.app/](https://pandemic-analyst-map.streamlit.app/)

## How to Use

1. **Explore the Map**:
   - Hover over any marker to view details about a specific disease occurrence.
   - Use the zoom and pan features to navigate different regions.
2. **Customize Your View**:
   - Adjust the **Date Range** slider to display data within a specific time frame.
   - Use the dropdown menus to filter by disease type and risk levels.
3. **Sidebar Information**:
   - Review the risk level legends and their respective icons to understand the markers on the map.


