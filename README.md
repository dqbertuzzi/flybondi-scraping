# Flybondi Flight Data Scraper

This personal project consists of a web scraper developed to collect information about specific flights from the airline Flybondi for 3 different round-trip dates to Argentina.

The collected data is subsequently sent to a dashboard on the Render platform.

Data is updated every 6 hours through Windows Task Scheduler.

`scraping.py` gathers flight price data from the Flybondi website, stores it in a CSV file, fetches additional flight data from Google Sheets, combines the datasets, and then updates a file in Google Drive with the resulting data.

`flybondi-dash-monitor.py` sets up a web application using Dash, a Python web application framework for creating interactive, web-based data dashboards. The application allows users to monitor flight prices for a specific route (São Paulo to Buenos Aires) by fetching data from a Google Sheets document and presenting it in an interactive graph.

## Technologies Used
Python: Programming language used to develop the scraper.

Requests, Beautiful Soup: Libraries used to automate navigation on the Flybondi website, parsing and extracting the collected data.

Plotly, Dash: Graphic library and framework for building data apps in Python.

Render: Platform used to host and display the dashboard with the collected data.

## Dashboard
The dashboard can be visualized [here](https://flybondi-monitor.onrender.com/).
