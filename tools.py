import wikipedia

def wiki_search(query: str) -> str:
    """Searches Wikipedia for company information, research, and general knowledge."""
    try:
        results = wikipedia.search(query, results=2)
        if not results:
            return "No Wikipedia articles found."
        
        summary = wikipedia.summary(results[0], sentences=3)
        return f"Title: {results[0]}\nSummary: {summary}"
    except Exception as e:
        return f"Error searching Wikipedia: {e}"

def patent_search(company_name: str) -> str:
    """Searches the patent database for recent patents filed by a competitor."""
    # Mock data to ensure a flawless demo for the hackathon
    mock_database = {
        "openai": "1. US-Pat-109: 'Method for scalable training of large language models.' (Filed: Jan 2024)\n2. US-Pat-110: 'System for multimodal video generation.' (Filed: Mar 2024)",
        "google": "1. US-Pat-201: 'Efficient attention mechanisms for transformers.' (Filed: Feb 2024)",
        "microsoft": "1. US-Pat-305: 'Integration of generative AI into operating systems.' (Filed: April 2024)"
    }
    
    company = company_name.lower()
    for key, patents in mock_database.items():
        if key in company:
            return f"Recent Patents for {company_name}:\n{patents}"
            
    return f"No recent patents found for '{company_name}' in our tracking database."

# Tool registry
AVAILABLE_TOOLS = {
    "wiki_search": wiki_search,
    "patent_search": patent_search
}
