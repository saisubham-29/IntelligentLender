"""External intelligence gathering from MCA, e-Courts, and news"""
import os
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
from groq import Groq
from duckduckgo_search import DDGS

class ExternalIntelligence:
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        self.client = Groq(api_key=api_key) if api_key else None
        self.model = "llama-3.3-70b-versatile"
    
    def gather_intelligence(self, company_name: str, cin: str = None, pan: str = None) -> Dict:
        """Gather all external intelligence"""
        
        results = {
            "mca_filings": self.search_mca_filings(company_name, cin),
            "legal_cases": self.search_ecourts(company_name, cin),
            "sector_news": self.search_sector_trends(company_name),
            "company_news": self.search_company_news(company_name)
        }
        
        # Synthesize with RAG
        if self.client:
            results["intelligence_summary"] = self._synthesize_intelligence(company_name, results)
        
        return results
    
    def search_mca_filings(self, company_name: str, cin: str = None) -> Dict:
        """Search MCA portal for company filings"""
        articles = []
        
        queries = [
            f"{company_name} MCA filing director change",
            f"{company_name} MCA charge modification",
            f"{cin} MCA annual return" if cin else f"{company_name} MCA compliance"
        ]
        
        try:
            with DDGS() as ddgs:
                for query in queries:
                    results = list(ddgs.text(f"site:mca.gov.in {query}", max_results=2))
                    for result in results:
                        articles.append({
                            "title": result.get("title", ""),
                            "url": result.get("href", ""),
                            "snippet": result.get("body", ""),
                            "source": "MCA"
                        })
        except Exception as e:
            print(f"MCA search error: {e}")
        
        return {
            "filings_found": len(articles),
            "articles": articles,
            "summary": self._analyze_mca_data(articles) if articles else "No MCA filings found"
        }
    
    def search_ecourts(self, company_name: str, cin: str = None) -> Dict:
        """Search e-Courts portal for legal cases"""
        articles = []
        
        queries = [
            f"{company_name} court case legal dispute",
            f"{company_name} NCLT insolvency",
            f"{company_name} arbitration litigation"
        ]
        
        try:
            with DDGS() as ddgs:
                for query in queries:
                    results = list(ddgs.text(f"site:ecourts.gov.in OR site:nclt.gov.in {query}", max_results=2))
                    for result in results:
                        articles.append({
                            "title": result.get("title", ""),
                            "url": result.get("href", ""),
                            "snippet": result.get("body", ""),
                            "source": "e-Courts"
                        })
        except Exception as e:
            print(f"e-Courts search error: {e}")
        
        return {
            "cases_found": len(articles),
            "articles": articles,
            "summary": self._analyze_legal_data(articles) if articles else "No legal cases found"
        }
    
    def search_sector_trends(self, company_name: str) -> Dict:
        """Search for sector-specific trends and news"""
        articles = []
        
        # Extract sector from company name or use generic
        queries = [
            f"India sector trends {company_name} industry",
            f"regulatory changes {company_name} sector",
            f"market outlook {company_name} industry India"
        ]
        
        try:
            with DDGS() as ddgs:
                for query in queries:
                    results = list(ddgs.text(query, max_results=2))
                    for result in results:
                        articles.append({
                            "title": result.get("title", ""),
                            "url": result.get("href", ""),
                            "snippet": result.get("body", ""),
                            "source": "News"
                        })
        except Exception as e:
            print(f"Sector search error: {e}")
        
        return {
            "articles_found": len(articles),
            "articles": articles,
            "summary": self._analyze_sector_data(articles) if articles else "No sector trends found"
        }
    
    def search_company_news(self, company_name: str) -> Dict:
        """Search for company-specific news"""
        articles = []
        
        queries = [
            f"{company_name} India news",
            f"{company_name} financial performance",
            f"{company_name} expansion plans investment"
        ]
        
        try:
            with DDGS() as ddgs:
                for query in queries:
                    results = list(ddgs.text(query, max_results=3))
                    for result in results:
                        articles.append({
                            "title": result.get("title", ""),
                            "url": result.get("href", ""),
                            "snippet": result.get("body", ""),
                            "source": "News"
                        })
        except Exception as e:
            print(f"News search error: {e}")
        
        return {
            "articles_found": len(articles),
            "articles": articles
        }
    
    def _analyze_mca_data(self, articles: List[Dict]) -> str:
        """Analyze MCA filings with Groq"""
        if not self.client or not articles:
            return "No analysis available"
        
        context = "\n".join([f"{a['title']}: {a['snippet']}" for a in articles])
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": f"Analyze these MCA filings for credit risk concerns:\n{context}\n\nProvide 2-3 sentence summary."
                }],
                temperature=0,
                max_tokens=200
            )
            return response.choices[0].message.content
        except:
            return "Analysis unavailable"
    
    def _analyze_legal_data(self, articles: List[Dict]) -> str:
        """Analyze legal cases with Groq"""
        if not self.client or not articles:
            return "No analysis available"
        
        context = "\n".join([f"{a['title']}: {a['snippet']}" for a in articles])
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": f"Analyze these legal cases for credit risk:\n{context}\n\nProvide 2-3 sentence summary."
                }],
                temperature=0,
                max_tokens=200
            )
            return response.choices[0].message.content
        except:
            return "Analysis unavailable"
    
    def _analyze_sector_data(self, articles: List[Dict]) -> str:
        """Analyze sector trends with Groq"""
        if not self.client or not articles:
            return "No analysis available"
        
        context = "\n".join([f"{a['title']}: {a['snippet']}" for a in articles])
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": f"Analyze these sector trends for credit implications:\n{context}\n\nProvide 2-3 sentence summary."
                }],
                temperature=0,
                max_tokens=200
            )
            return response.choices[0].message.content
        except:
            return "Analysis unavailable"
    
    def _synthesize_intelligence(self, company_name: str, results: Dict) -> str:
        """Synthesize all intelligence with RAG"""
        if not self.client:
            return "Synthesis unavailable"
        
        context = f"""Company: {company_name}

MCA Filings: {results['mca_filings']['summary']}
Legal Cases: {results['legal_cases']['summary']}
Sector Trends: {results['sector_news']['summary']}
News Articles: {len(results['company_news']['articles'])} articles found
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": f"Synthesize this external intelligence for credit appraisal:\n{context}\n\nProvide comprehensive 4-5 sentence summary highlighting key risks and opportunities."
                }],
                temperature=0,
                max_tokens=400
            )
            return response.choices[0].message.content
        except:
            return "Synthesis unavailable"
