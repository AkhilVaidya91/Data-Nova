---
title: Digital Nova
emoji: 📊
colorFrom: green
colorTo: indigo
sdk: streamlit
sdk_version: 1.39.0
app_file: app.py
pinned: false
license: mit
---

# 📊 Digital Nova
## Your GenAI-based Research Companion

Digital Nova is a comprehensive AI-powered research platform that enables data collection, theme generation, data structuring, and advanced analytics. Built with Streamlit and powered by multiple AI models, it provides researchers with a complete toolkit for gathering insights from various online sources.

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.39.0-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Key Features

### 🔍 Multi-Platform Data Collection
- **Social Media**: Instagram, YouTube, Twitter, Flickr, Facebook
- **e-WOM (Electronic Word of Mouth)**: Amazon reviews, Google Reviews, TripAdvisor, Booking.com
- **News Sources**: Google News articles
- **Website Scraping**: AI-powered website content extraction

### 🤖 AI-Powered Analysis
- **Theme Generation**: Generate structured themes using Perplexity API
- **Document Processing**: Extract insights from PDFs and Excel files
- **TCCM-ADO Framework**: Theory, Context, Concept, Methodology - Antecedents, Decisions, Outcomes analysis
- **Literature Synthesis**: Automated research paper analysis and clustering

### 📊 Advanced Analytics
- **RAG-Based Analytics**: Retrieval-Augmented Generation for intelligent data analysis
- **Sentiment Analysis**: Emotion and subjectivity scoring
- **Readability Analysis**: SMOG index calculation
- **Narcissism Detection**: Behavioral pattern analysis
- **Comparative Analysis**: Cross-corpus and cross-theme comparisons

### 🎯 Multiple AI Model Support
- **Language Models**: OpenAI GPT-4, Google Gemini, Llama, Mistral, DeepSeek R1
- **Embedding Models**: OpenAI embeddings, Google Gemini, Universal Sentence Encoder, MiniLM-distilBERT

## 🏗️ Architecture

```
Digital Nova
├── app.py                 # Main Streamlit application
├── modules/
│   ├── models.py         # AI model interfaces and utilities
│   ├── theme_upload.py   # Theme generation and management
│   ├── corpus_upload.py  # Document corpus processing
│   ├── analytics.py      # RAG-based analytics engine
│   ├── dashboard.py      # User dashboard and data visualization
│   └── utils.py          # Utility functions
├── utils/                # Data collection modules
│   ├── instagram_page.py
│   ├── youtube_page.py
│   ├── amazon_page.py
│   └── ... (other scrapers)
├── requirements.txt      # Python dependencies
├── Dockerfile           # Container configuration
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- MongoDB Atlas account
- API keys for various services (see Configuration section)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/AkhilVaidya91/Data-Nova.git
cd digital-nova
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
export MONGO_URI="your_mongodb_connection_string"
export OP_PATH="output"  # Optional: output directory for scraped files
```

4. **Run the application**
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## 🔧 Configuration

### Required API Keys

Digital Nova integrates with multiple services. Obtain API keys from:

| Service | Purpose | Documentation |
|---------|---------|---------------|
| **Apify** | Web scraping | [Apify Console](https://console.apify.com/account/integrations) |
| **OpenAI** | Language models & embeddings | [OpenAI API Keys](https://platform.openai.com/account/api-keys) |
| **Google Gemini** | Language models & embeddings | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| **Perplexity** | Research and theme generation | [Perplexity Docs](https://docs.perplexity.ai/guides/getting-started) |
| **YouTube Data API** | YouTube content scraping | [Google Cloud Console](https://console.cloud.google.com/apis/credentials) |

### MongoDB Setup

1. Create a MongoDB Atlas cluster
2. Create a database named `digital_nova`
3. Set up the following collections:
   - `users` - User accounts and API keys
   - `corpus` - Document corpus metadata
   - `themes` - Generated themes and reference vectors
   - `analytics` - Analysis results
   - `synthesis` - Literature synthesis results
   - `chat_logs` - Theme generation chat history
   - `corpus_file_content` - Processed document content

## 📖 Usage Guide

### 1. User Registration and Login

1. **Sign Up**: Create an account with your credentials and API keys
2. **Login**: Access your personalized dashboard
3. **API Management**: Update your API keys in the dashboard settings

### 2. Data Collection

Navigate to **Corpus Management > Data Collection**:

#### Social Media Scraping
```python
# Example: Instagram data collection
- Select "Social Media" > "Instagram"
- Enter target username or hashtag
- Configure scraping parameters
- Download structured CSV output
```

#### Product Reviews
```python
# Example: Amazon reviews
- Select "e-WOM" > "Amazon Product Reviews"
- Enter product URL or ASIN
- Set review count limit
- Export analysis-ready dataset
```

### 3. Theme Generation

Navigate to **Deductive Coding**:

#### Chat-based Theme Generation
```python
# Generate themes using Perplexity API
theme_name = "Sustainable Development Goals"
topic = "Climate change initiatives in developing countries"
# System generates structured theme with evidence
```

#### Document Theme Extraction
```python
# Upload PDF documents for theme extraction
# System uses TCCM-ADO framework for analysis
# Output: Structured themes with evidence mapping
```

### 4. Corpus Management

Navigate to **Corpus Management > Corpus Management**:

#### PDF Corpus Upload
```python
# Upload multiple research papers
# System processes and vectorizes content
# Creates searchable knowledge base
```

#### Excel Integration
```python
# Import structured data from Excel
# Supports custom column mapping
# Automatic vectorization for RAG analytics
```

### 5. Analytics

Navigate to **Analytics**:

#### RAG-Based Analysis
```python
# Select theme and corpus
# Configure analysis parameters
# Generate comparative insights with evidence
```

#### Literature Synthesis
```python
# Automated research paper clustering
# TCCM-ADO framework application
# Generate synthesis reports
```

## 🧩 Module Documentation

### Core Modules

#### `models.py` - AI Model Interface
```python
class LLMModelInterface:
    """Unified interface for multiple AI models"""
    
    @staticmethod
    def call_openai_gpt4_mini(prompt: str, api_key: str) -> str
    def call_gemini(prompt: str, api_key: str) -> str
    def call_llama(prompt: str, api_key: str) -> str
    def embed_openai(text: str, api_key: str) -> List[float]
    def embed_gemini(text: str, api_key: str) -> List[float]
```

#### `theme_upload.py` - Theme Management
- Perplexity-based theme generation
- Document theme extraction using TCCM-ADO
- Vector storage for RAG analytics
- Chat history management

#### `corpus_upload.py` - Document Processing
- PDF text extraction and chunking
- Excel data import and processing
- Vector embedding generation
- Literature synthesis framework

#### `analytics.py` - Analysis Engine
- Theme-corpus correlation analysis
- Sentiment and readability scoring
- Evidence-based SDG alignment
- Custom inference generation

### Data Collection Modules

| Module | Platform | Features |
|--------|----------|----------|
| `instagram_page.py` | Instagram | Profile scraping, hashtag analysis, post content extraction |
| `youtube_page.py` | YouTube | Video metadata, comments, transcripts, channel analysis |
| `amazon_page.py` | Amazon | Product reviews, ratings, sentiment analysis |
| `google_news_page.py` | Google News | Article scraping, content summarization |
| `twitter_page.py` | Twitter | Tweet collection, user analysis, trend tracking |

## 🔬 Advanced Features

### TCCM-ADO Framework

Digital Nova implements the TCCM-ADO framework for research paper analysis:

- **T**heory: Theoretical frameworks and models
- **C**ontext: Research settings and environments
- **C**oncept: Core variables and constructs
- **M**ethodology: Research methods and approaches
- **A**ntecedents: Precursors and conditions
- **D**ecisions: Actions and interventions
- **O**utcomes: Results and consequences

### Sentiment Analysis

Built-in sentiment analyzer using sentence transformers:
```python
analyzer = SentimentAnalyzer()
results = analyzer.analyze(sentences)
# Returns: {"average_sentiment": float, "average_subjectivity": float}
```

### Readability Analysis

SMOG Index calculation for document complexity:
```python
smog_score = smog_index(sentences)
# Returns readability grade level
```

## 🐳 Docker Deployment

### Using Docker Compose

```yaml
version: '3.8'
services:
  digital-nova:
    build: .
    ports:
      - "8501:8501"
    environment:
      - MONGO_URI=your_mongodb_uri
      - OP_PATH=/app/output
    volumes:
      - ./output:/app/output
```

### Manual Docker Build

```bash
# Build the image
docker build -t digital-nova .

# Run the container
docker run -p 8501:8501 \
  -e MONGO_URI="your_mongodb_uri" \
  digital-nova
```

## 📊 Sample Outputs

### Theme Generation Output
```json
{
  "theme_name": "UN SDGs",
  "structured_df": [
    {
      "Goal": "No Poverty",
      "Description": "End poverty in all its forms everywhere",
      "Keywords": "poverty reduction, social protection, economic inclusion",
      "Examples": "Microfinance programs, universal basic income",
      "Reference Links": "https://sdgs.un.org/goals/goal1"
    }
  ]
}
```

### Analytics Output
| File Name   | SDG-1 Presence | SDG-1 Evidence                        | Sentiment Score | SMOG Index |
|-------------|----------------|---------------------------------------|-----------------|------------|
| report1.pdf | Yes            | implemented poverty reduction programs | 0.75            | 12.3       |
| report2.pdf | No             |                                       | 0.45            | 14.1       |

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


**Digital Nova** - Empowering Research with AI 🚀
