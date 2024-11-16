---
title: Data-Nova
emoji: 📊
colorFrom: green
colorTo: indigo
sdk: streamlit
sdk_version: 1.39.0
app_file: app.py
pinned: false
license: mit
---

# Data-Nova: 📊
## Data Mining, Structuring and LLM Analytics

A comprehensive application for data collection, theme generation, data structuring, and RAG-based analytics. This application leverages various APIs and services to scrape data from multiple platforms, process and analyze the data, and provide insightful analytics through an intuitive dashboard.

## Features

- **Data Collection:** Scrape data from various platforms including:
  - Amazon
  - Booking.com
  - Facebook
  - Flickr
  - Google News
  - Instagram
  - TripAdvisor
  - Twitter
  - YouTube
- **Theme Generation:** Utilize AI models to generate and manage themes from collected data
- **Data Structuring:** Organize and structure unstructured data for efficient analysis
- **RAG-based Analytics:** Perform Retrieval-Augmented Generation based analytics on themes and corpora
- **Dashboard:** Interactive Streamlit dashboard for visualization and user interaction
- **Dockerized Deployment:** Easy deployment using Docker and Docker Compose

## Prerequisites

- Docker and Docker Compose
- Python 3.x
- MongoDB
- Required API keys:
  - Apify
  - OpenAI
  - Google Gemini
  - YouTube Data API

## Installation

### Setup

1. Clone the repository
2. Configure environment variables
3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running with Docker

```bash
docker-compose up
```

### Running Locally

```bash
streamlit run app.py
```

## Core Modules

### Data Collection

| Module | Platform | Apify Actor | APIs Used | Description |
|--------|----------|-------------|------------|-------------|
| amazon_reviews.py | Amazon | amazon-reviews-scraper | Apify, MongoDB | Scrapes Amazon product reviews |
| booking.py | Booking.com | booking-reviews-scraper | Apify, MongoDB | Scrapes Booking.com reviews |
| facebook.py | Facebook | facebook-scraper | Apify, MongoDB | Scrapes Facebook posts and profiles |
| flickr.py | Flickr | flickr-scraper | Apify, Google Gemini API, MongoDB | Scrapes Flickr media content |
| google_news.py | Google News | google-news-scraper | Apify, MongoDB | Scrapes Google News articles |
| google_reviews.py | Google Reviews | google-reviews-scraper | Apify, MongoDB | Scrapes Google Reviews |
| instagram.py | Instagram | instagram-scraper | Apify, Google Gemini API, MongoDB | Scrapes Instagram posts |
| tripadvisor.py | TripAdvisor | tripadvisor-scraper | Apify, MongoDB | Scrapes TripAdvisor hotel reviews |
| twitter.py | Twitter | twitter-scraper | Apify, Google Gemini API, MongoDB | Scrapes Twitter data |
| youtube.py | YouTube | youtube-scraper | YouTube Data API, Apify, Google Gemini API, MongoDB | Scrapes YouTube videos, comments, and transcripts |

### Theme Generation

- **Module:** themes.py
- **APIs Used:** OpenAI API, MongoDB
- **Features:**
  - Perplexity-based theme generation
  - Document theme extraction
  - Corpus management
  - Vector-based search for RAG analytics

### Data Structuring & Analytics

- **Module:** analytics.py
- **APIs Used:** OpenAI API, MongoDB
- **Features:**
  - Theme and corpus data fetching
  - Comparative analysis using OpenAI models
  - Web interface visualization
