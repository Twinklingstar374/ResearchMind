"""
Source Scorer — Evaluates and ranks search results based on
recency, relevance, and domain credibility.
"""

from datetime import datetime, timezone
from urllib.parse import urlparse


# Domain credibility tiers
TIER_1_DOMAINS = {
    "arxiv.org": 95,
    "nature.com": 95,
    "science.org": 95,
    "ieee.org": 92,
    "acm.org": 92,
    "scholar.google.com": 90,
    "pubmed.ncbi.nlm.nih.gov": 93,
    "nih.gov": 92,
}

TIER_2_DOMAINS = {
    "reuters.com": 88,
    "bbc.com": 87,
    "bbc.co.uk": 87,
    "nytimes.com": 86,
    "theguardian.com": 85,
    "washingtonpost.com": 85,
    "apnews.com": 88,
    "bloomberg.com": 87,
    "economist.com": 86,
    "ft.com": 86,
}

TIER_3_DOMAINS = {
    "techcrunch.com": 80,
    "wired.com": 80,
    "arstechnica.com": 79,
    "theverge.com": 78,
    "technologyreview.com": 82,
    "venturebeat.com": 76,
    "zdnet.com": 75,
    "cnet.com": 74,
    "engadget.com": 73,
    "towardsdatascience.com": 72,
    "medium.com": 55,
    "forbes.com": 74,
    "cnbc.com": 76,
}

TIER_4_DOMAINS = {
    "github.com": 70,
    "stackoverflow.com": 68,
    "wikipedia.org": 72,
    "huggingface.co": 75,
    "openai.com": 80,
    "anthropic.com": 80,
    "google.ai": 80,
    "deepmind.google": 82,
    "microsoft.com": 75,
    "aws.amazon.com": 73,
}

# Merge all tiers
ALL_KNOWN_DOMAINS = {}
ALL_KNOWN_DOMAINS.update(TIER_1_DOMAINS)
ALL_KNOWN_DOMAINS.update(TIER_2_DOMAINS)
ALL_KNOWN_DOMAINS.update(TIER_3_DOMAINS)
ALL_KNOWN_DOMAINS.update(TIER_4_DOMAINS)


def _get_domain_score(url: str) -> int:
    """Score a URL based on its domain credibility."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        
        # Direct match
        if domain in ALL_KNOWN_DOMAINS:
            return ALL_KNOWN_DOMAINS[domain]
        
        # Check if it's a subdomain of a known domain
        for known_domain, score in ALL_KNOWN_DOMAINS.items():
            if domain.endswith("." + known_domain):
                return max(score - 5, 40)
        
        # Check for .edu and .gov domains
        if domain.endswith(".edu"):
            return 85
        if domain.endswith(".gov"):
            return 88
        if domain.endswith(".org"):
            return 60
        
        # Unknown domain gets a baseline score
        return 40
    except Exception:
        return 35


def _get_recency_score(published_date: str) -> int:
    """Score based on how recent the source is."""
    if not published_date:
        return 50  # Unknown date gets neutral score
    
    try:
        # Try multiple date formats
        date_formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
        ]
        
        pub_date = None
        for fmt in date_formats:
            try:
                pub_date = datetime.strptime(published_date.strip(), fmt)
                break
            except ValueError:
                continue
        
        if pub_date is None:
            return 50
        
        now = datetime.now()
        days_old = (now - pub_date).days
        
        if days_old < 0:
            days_old = 0
        
        if days_old <= 7:
            return 100
        elif days_old <= 30:
            return 90
        elif days_old <= 90:
            return 80
        elif days_old <= 180:
            return 70
        elif days_old <= 365:
            return 60
        elif days_old <= 730:
            return 45
        else:
            return 30
            
    except Exception:
        return 50


def _get_relevance_score(tavily_score: float) -> int:
    """Convert Tavily's relevance score (0-1) to 0-100 scale."""
    if tavily_score is None:
        return 50
    
    try:
        score = float(tavily_score)
        # Tavily scores are typically 0-1
        if 0 <= score <= 1:
            return int(score * 100)
        elif 0 <= score <= 100:
            return int(score)
        else:
            return 50
    except (ValueError, TypeError):
        return 50


def score_sources(sources: list[dict], weights: dict = None) -> list[dict]:
    """
    Score and rank search result sources.
    
    Args:
        sources: List of source dicts from Tavily search results.
                 Each should have: title, url, content, published_date, score
        weights: Optional custom weights for scoring dimensions.
                 Defaults to: recency=0.25, relevance=0.40, domain=0.35
    
    Returns:
        Top 5 sources sorted by credibility score, filtered to score >= 40.
        Each source dict gets additional fields:
        - recency_score, relevance_score, domain_score, credibility_score
    """
    if weights is None:
        weights = {
            "recency": 0.25,
            "relevance": 0.40,
            "domain": 0.35
        }
    
    scored = []
    
    for source in sources:
        recency = _get_recency_score(source.get("published_date", ""))
        relevance = _get_relevance_score(source.get("score"))
        domain = _get_domain_score(source.get("url", ""))
        
        credibility = (
            weights["recency"] * recency +
            weights["relevance"] * relevance +
            weights["domain"] * domain
        )
        
        scored_source = {
            **source,
            "recency_score": recency,
            "relevance_score": relevance,
            "domain_score": domain,
            "credibility_score": round(credibility, 1)
        }
        scored.append(scored_source)
    
    # Filter below threshold 40
    filtered = [s for s in scored if s["credibility_score"] >= 40]
    
    # Sort by credibility descending
    filtered.sort(key=lambda x: x["credibility_score"], reverse=True)
    
    # Return top 5
    return filtered[:5]
