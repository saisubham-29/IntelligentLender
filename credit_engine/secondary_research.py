"""Secondary research using web scraping and RAG with Groq"""
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import os
from groq import Groq
from ddgs import DDGS

class SecondaryResearch:
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        self.client = Groq(api_key=api_key) if api_key else None
        self.model = "llama-3.3-70b-versatile"
    
    def research_entity(self, entity_name: str, cin: str = None, gstin: str = None) -> Dict:
        """Perform web research with scraping and RAG analysis"""
        if not self.client:
            return {"summary": "Web research unavailable - set GROQ_API_KEY", "articles": []}
        
        print(f"🔍 Searching web for: {entity_name}")
        
        # Search and scrape articles
        articles = self._search_and_scrape(entity_name)
        
        if not articles:
            return {
                "entity": entity_name,
                "articles": [],
                "summary": f"No significant web findings for {entity_name}",
                "risk_flags": []
            }
        
        # Use RAG to analyze scraped content
        analysis = self._rag_analysis(entity_name, articles)
        
        return {
            "entity": entity_name,
            "articles": articles,
            "summary": analysis.get("summary", ""),
            "risk_flags": analysis.get("risk_flags", []),
            "key_insights": analysis.get("insights", [])
        }
    
    def _search_and_scrape(self, entity: str) -> List[Dict]:
        """Search and scrape articles from web"""
        articles = []
        
        # Search queries focused on credit risk
        queries = [
            f"{entity} fraud scam investigation India",
            f"{entity} default NPA legal case",
            f"{entity} financial news India",
            f"{entity} SEBI RBI regulatory action"
        ]
        
        try:
            with DDGS() as ddgs:
                for query in queries:
                    results = list(ddgs.text(query, max_results=3))
                    
                    for result in results:
                        article = {
                            "title": result.get("title", ""),
                            "url": result.get("href", ""),
                            "snippet": result.get("body", ""),
                            "content": ""
                        }
                        
                        # Try to scrape full content
                        try:
                            content = self._scrape_article(article["url"])
                            article["content"] = content[:2000]  # Limit content
                        except:
                            article["content"] = article["snippet"]
                        
                        articles.append(article)
                        
                        if len(articles) >= 8:  # Limit total articles
                            break
                    
                    if len(articles) >= 8:
                        break
        except Exception as e:
            print(f"Search error: {e}")
        
        return articles
    
    def _scrape_article(self, url: str) -> str:
        """Scrape article content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text from article body
            article_body = soup.find('article') or soup.find('main') or soup.body
            if article_body:
                text = article_body.get_text(separator=' ', strip=True)
                return text[:2000]  # Limit to 2000 chars
            
            return ""
        except:
            return ""
    
    def _rag_analysis(self, entity: str, articles: List[Dict]) -> Dict:
        """Use Groq RAG to analyze scraped articles"""
        
        # Prepare context from articles
        context = f"Entity: {entity}\n\n"
        context += "ARTICLES FOUND:\n\n"
        
        for i, article in enumerate(articles, 1):
            context += f"[{i}] {article['title']}\n"
            context += f"Source: {article['url']}\n"
            content = article.get('content') or article.get('snippet', '')
            context += f"Content: {content[:500]}...\n\n"
        
        # RAG prompt for credit risk analysis
        prompt = f"""You are a credit risk analyst. Analyze these web articles about "{entity}" and provide:

1. SUMMARY: 2-3 sentence summary focusing on credit risks, fraud, defaults, legal issues, or regulatory actions
2. RISK_FLAGS: List any risk flags found (fraud, default, legal, investigation, regulatory, insolvency)
3. KEY_INSIGHTS: 3-4 bullet points of important findings

Context:
{context}

Respond in JSON format:
{{
  "summary": "...",
  "risk_flags": ["flag1", "flag2"],
  "insights": ["insight1", "insight2", "insight3"]
}}

If no significant risks found, say "No significant adverse findings" in summary."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            import json
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            result = json.loads(content)
            
            # Convert risk flags to emoji format
            flag_map = {
                'fraud': '🚨 Fraud allegations',
                'scam': '🚨 Scam involvement',
                'default': '⚠️ Payment defaults',
                'npa': '⚠️ NPA classification',
                'legal': '⚠️ Legal proceedings',
                'investigation': '🚨 Under investigation',
                'regulatory': '⚠️ Regulatory action',
                'insolvency': '🚨 Insolvency proceedings'
            }
            
            formatted_flags = []
            for flag in result.get('risk_flags', []):
                flag_lower = flag.lower()
                for key, emoji_flag in flag_map.items():
                    if key in flag_lower:
                        formatted_flags.append(emoji_flag)
                        break
            
            result['risk_flags'] = formatted_flags
            return result
            
        except Exception as e:
            print(f"RAG analysis error: {e}")
            return {
                "summary": "Analysis unavailable",
                "risk_flags": [],
                "insights": []
            }
