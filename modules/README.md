# Modules Directory Documentation

This directory contains various Python scripts responsible for data scraping, processing, and analysis across multiple platforms and services. Each module leverages specific APIs and Apify actors to perform its tasks efficiently.

## Apify Actors

# Apify Actors and Their Platforms

| Apify Actor | Platform |
|-------------|----------|
| junglee/amazon-reviews-scraper | Amazon |
| voyager/booking-reviews-scraper | Booking.com |
| apify/facebook-pages-scraper | Facebook |
| apify/facebook-posts-scraper | Facebook |
| web.harvester/flickr-scraper | Flickr |
| lhotanova/google-news-scraper | Google News |
| google-reviews-scraper (implementation pending) | Google Reviews |
| apify/instagram-profile-scraper | Instagram |
| apify/instagram-scraper | Instagram |
| maxcopell/tripadvisor-reviews | TripAdvisor |
| 2s3kSMq7tpuC3bI6M | Twitter |

## Table of Contents
- [amazon_reviews.py](#amazon_reviewspy)
- [analytics.py](#analyticspy)
- [booking.py](#bookingpy)
- [dashboard.py](#dashboardpy)
- [facebook.py](#facebookpy)
- [flickr.py](#flickrpy)
- [google_news.py](#google_newspy)
- [google_reviews.py](#google_reviewspy)
- [instagram.py](#instagrampy)
- [parse.py](#parsepy)
- [scrape.py](#scrapepy)
- [themes.py](#themespy)
- [tripadvisor.py](#tripadvisorpy)
- [twitter.py](#twitterpy)
- [youtube.py](#youtubepy)

## Module Descriptions

### amazon_reviews.py
**Description:** Handles scraping and processing of Amazon product reviews.

**APIs & Services Used:**
- Apify Actor: junglee/amazon-reviews-scraper
- MongoDB: Stores scraped review data

**Functionality:** Connects to specified Amazon product URLs, retrieves reviews using the designated Apify actor, and stores the processed data in MongoDB for further analysis.

### analytics.py
**Description:** Performs comparative analytics on themes and corpora.

**APIs & Services Used:**
- OpenAI API: Utilized for advanced analytics and language processing

**Functionality:** Fetches theme and corpus data from MongoDB, conducts comparative analysis using OpenAI's language models, and presents the results through a web interface.

### booking.py
**Description:** Manages scraping and processing of Booking.com reviews.

**APIs & Services Used:**
- Apify Actor: voyager/booking-reviews-scraper
- MongoDB: Stores scraped review data

**Functionality:** Connects to Booking.com property URLs, retrieves reviews using the specified Apify actor, and stores the cleaned data in MongoDB for analysis.

### dashboard.py
**Description:** Provides a Streamlit-based dashboard for user interaction and data visualization.

**APIs & Services Used:**
- MongoDB: Retrieves user information and output files
- GridFS: Manages file storage within MongoDB

**Functionality:** Displays user details, manages API keys, and visualizes data such as output files, corpora, and themes associated with the user through an interactive dashboard.

### facebook.py
**Description:** Handles scraping and processing of Facebook posts and profiles.

**APIs & Services Used:**
- Apify Actor: apify/facebook-pages-scraper, apify/facebook-posts-scraper
- MongoDB: Stores scraped Facebook data

**Functionality:** Connects to Facebook URLs, retrieves posts and profile information using the designated Apify actor, and stores the structured data in MongoDB for further analysis.

### flickr.py
**Description:** Manages scraping and processing of Flickr media content.

**APIs & Services Used:**
- Apify Actor: web.harvester/flickr-scraper
- Google Gemini API: Processes image captions
- MongoDB: Stores scraped Flickr data

**Functionality:** Fetches media content based on search queries using the specified Apify actor, processes image captions with Google Gemini API, and stores the resulting data in MongoDB.

### google_news.py
**Description:** Handles scraping and processing of Google News articles.

**APIs & Services Used:**
- Apify Actor: lhotanova/google-news-scraper
- MongoDB: Stores scraped news articles

**Functionality:** Retrieves news articles based on user queries through the designated Apify actor and stores the structured data in MongoDB for analysis.

### google_reviews.py
**Description:** Manages scraping and processing of Google Reviews.

**APIs & Services Used:**
- Apify Actor: google-reviews-scraper (implementation pending)
- MongoDB: Stores scraped review data

**Functionality:** Connects to specified locations or businesses, retrieves reviews using the designated Apify actor, and stores the processed data in MongoDB for further analysis.

### instagram.py
**Description:** Handles scraping and processing of Instagram posts and profiles.

**APIs & Services Used:**
- Apify Actor: apify/instagram-profile-scraper, apify/instagram-scraper
- Google Gemini API: Processes image captions
- MongoDB: Stores scraped Instagram data

**Functionality:** Fetches Instagram posts and profile information using the specified Apify actor, processes captions with Google Gemini API, and stores the structured data in MongoDB.

### parse.py
**Description:** Handles parsing and structuring of unstructured text data using Generative AI.

**APIs & Services Used:**
- Google Gemini API: Utilizes for content parsing
- MongoDB: Stores parsed data

**Functionality:** Extracts specific information from unstructured text based on user descriptions and stores the structured data in MongoDB for analysis.

### scrape.py
**Description:** General-purpose scraping utilities and functions.

**APIs & Services Used:**
- Apify Actors: Various actors for different scraping tasks

**Functionality:** Offers helper functions to support scraping operations across different modules, facilitating data retrieval from multiple platforms and services.

### themes.py
**Description:** Handles theme generation and corpus management using AI models.

**APIs & Services Used:**
- OpenAI API: Utilized for structuring and generating themes
- MongoDB: Stores themes, corpora, and vector data

**Functionality:** Generates themes from uploaded documents, manages corpora by uploading and vectorizing data, and implements vector-based search for theme analytics.

### tripadvisor.py
**Description:** Manages scraping and processing of TripAdvisor hotel reviews.

**APIs & Services Used:**
- Apify Actor: maxcopell/tripadvisor-reviews
- MongoDB: Stores scraped TripAdvisor reviews

**Functionality:** Connects to TripAdvisor hotel URLs, retrieves reviews using the designated Apify actor, and stores the structured data in MongoDB for analysis.

### twitter.py
**Description:** Handles scraping and processing of Twitter data, including tweets and user information.

**APIs & Services Used:**
- Apify Actor: 2s3kSMq7tpuC3bI6M
- Google Gemini API: Processes tweet captions
- MongoDB: Stores scraped Twitter data

**Functionality:** Fetches tweets based on search queries and user accounts using the specified Apify actor, processes captions with Google Gemini API, and stores the structured data in MongoDB.

### youtube.py
**Description:** Manages scraping and processing of YouTube videos, comments, and transcripts.

**APIs & Services Used:**
- YouTube Data API: Retrieves video details and comments
- Apify Actor: youtube-scraper
- Google Gemini API: Processes video thumbnails and captions
- MongoDB: Stores scraped YouTube data

**Functionality:** Fetches video details, comments, and transcripts using YouTube Data API and the designated Apify actor, processes thumbnails and captions with Google Gemini API, and stores the data in MongoDB.

## Dependencies
- Python 3.12
- MongoDB
- Apify actors
- OpenAI API
- Perplexity API
- Google Gemini API
- YouTube Data API
- Streamlit (for dashboard)
- GridFS