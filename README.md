
# AI Operations Copilot

An AI-powered subscription analytics and business operations application combining MySQL, Python, Streamlit, and locally hosted AI.

## Project Overview

AI Operations Copilot demonstrates how data engineering, business analytics, rule-based automation, and generative AI can support subscription management and customer operations.

The application uses a synthetic MySQL dataset containing 176,003 records across 16 tables.

## Key Features

### Business Analytics
- Revenue and payment analysis
- Monthly payment trends
- Subscription status monitoring
- Service provider performance dashboards
- Cancellation analysis

### AI Business Assistant
- Answers predefined business questions using verified SQL queries
- Generates business interpretations using a local Ollama model
- Separates SQL-calculated metrics from AI explanations

### Operations Alert Center
- Identifies subscriptions requiring review
- Detects upcoming and past billing dates
- Monitors pending subscriptions
- Provides filtering, visualizations, and CSV exports

### AI Customer Support
- Generates suggested support actions
- Drafts customer communications
- Recommends internal follow-up steps
- Requires human review before any customer action

## Technology Stack

- Python
- MySQL
- SQL
- Streamlit
- Pandas
- Ollama
- Qwen 2.5 (3B)
- Git and GitHub

## Architecture

MySQL Database
    |
    v
Python Data Access Layer
    |
    +--> SQL Analytics
    |
    +--> Operations Alert Rules
    |
    +--> Verified Business Queries
                |
                v
           Ollama AI
                |
                v
       Streamlit Application

## Project Results

- 176,003 synthetic database records
- 16 relational database tables
- 75,007 payment records analyzed
- 15,007 subscriptions monitored
- 974 operational alerts identified in the demonstrated run
- Four supported SQL business questions
- Three AI customer support scenarios

## Local Installation

1. Clone the repository.
2. Install dependencies:

    pip install -r requirements.txt

3. Create a `.env` file based on `.env.example`.
4. Configure a local MySQL database named `subscription_portfolio` and import the synthetic dataset separately.
5. Install Ollama and run:

    ollama pull qwen2.5:3b

6. Launch Streamlit:

    streamlit run app.py

## Important Notes

- The database contains fictional data.
- MySQL and Ollama must be running locally.
- Database contents are not included in this application repository.
- AI-generated recommendations require human review.
- No customer emails or payments are processed by this application.

## Project Purpose

This project demonstrates practical skills relevant to data engineering, analytics engineering, AI analytics, business operations automation, and solutions engineering.
