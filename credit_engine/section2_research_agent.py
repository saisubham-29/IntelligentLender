"""
SECTION 2: RESEARCH AGENT (The "Digital Credit Manager")
Automated secondary research and primary insight integration
"""
import os
from typing import Dict, List
from groq import Groq
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup

class ResearchAgent:
    """
    Digital Credit Manager - Automated research with human insight integration
    """
    
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        self.client = Groq(api_key=api_key) if api_key else None
        self.model = "llama-3.3-70b-versatile"
        self.primary_insights = {}
    
    # ============================================================
    # SECONDARY RESEARCH
    # ============================================================
    
    def conduct_secondary_research(self, company_name: str, promoters: List[str], 
                                   sector: str, cin: str = None) -> Dict:
        """
        Comprehensive secondary research covering:
        - Promoter background and reputation
        - Sector-specific headwinds/tailwinds
        - Litigation history
        - Regulatory actions
        """
        
        research_results = {
            'promoter_research': self._research_promoters(promoters),
            'sector_research': self._research_sector(sector),
            'litigation_research': self._research_litigation(company_name, cin),
            'regulatory_research': self._research_regulatory(company_name, sector),
            'mca_research': self._research_mca(company_name, cin),
            'news_sentiment': self._analyze_news_sentiment(company_name)
        }
        
        # Synthesize all research with RAG
        synthesis = self._synthesize_research(company_name, research_results)
        
        return {
            **research_results,
            'synthesis': synthesis,
            'risk_score': self._calculate_research_risk_score(research_results),
            'key_findings': self._extract_key_findings(research_results)
        }
    
    def _research_promoters(self, promoters: List[str]) -> Dict:
        """Research promoter background and reputation"""
        
        if not promoters:
            return {'findings': [], 'risk_level': 'UNKNOWN'}
        
        findings = []
        articles = []
        
        for promoter in promoters[:3]:  # Limit to top 3 promoters
            queries = [
                f"{promoter} fraud scam investigation India",
                f"{promoter} wilful defaulter RBI",
                f"{promoter} SEBI action penalty"
            ]
            
            for query in queries:
                try:
                    with DDGS() as ddgs:
                        results = list(ddgs.text(query, max_results=2))
                        for result in results:
                            articles.append({
                                'promoter': promoter,
                                'title': result.get('title', ''),
                                'url': result.get('href', ''),
                                'snippet': result.get('body', '')
                            })
                            findings.append(f"{promoter}: {result.get('title', '')}")
                except:
                    pass
        
        # Analyze findings
        risk_keywords = ['fraud', 'scam', 'defaulter', 'investigation', 'penalty', 'action']
        risk_count = sum(1 for f in findings if any(k in f.lower() for k in risk_keywords))
        
        return {
            'promoters_checked': promoters,
            'findings': findings,
            'articles': articles,
            'risk_level': 'HIGH' if risk_count > 2 else 'MEDIUM' if risk_count > 0 else 'LOW',
            'summary': self._summarize_with_rag(f"Promoter research for {', '.join(promoters)}", findings)
        }
    
    def _research_sector(self, sector: str) -> Dict:
        """Research sector-specific headwinds and tailwinds"""
        
        queries = [
            f"{sector} India sector outlook 2024",
            f"RBI regulations {sector} new rules",
            f"{sector} industry challenges India",
            f"{sector} growth opportunities India"
        ]
        
        articles = []
        for query in queries:
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=2))
                    for result in results:
                        articles.append({
                            'title': result.get('title', ''),
                            'url': result.get('href', ''),
                            'snippet': result.get('body', '')
                        })
            except:
                pass
        
        return {
            'sector': sector,
            'articles': articles,
            'headwinds': self._extract_headwinds(articles),
            'tailwinds': self._extract_tailwinds(articles),
            'regulatory_changes': self._extract_regulatory_changes(articles),
            'summary': self._summarize_with_rag(f"Sector research for {sector}", [a['snippet'] for a in articles])
        }
    
    def _research_litigation(self, company_name: str, cin: str) -> Dict:
        """Research litigation history"""
        
        queries = [
            f"{company_name} court case legal dispute India",
            f"{company_name} NCLT insolvency",
            f"{cin} litigation" if cin else f"{company_name} lawsuit"
        ]
        
        articles = []
        for query in queries:
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(f"site:ecourts.gov.in OR site:nclt.gov.in {query}", max_results=2))
                    for result in results:
                        articles.append({
                            'title': result.get('title', ''),
                            'url': result.get('href', ''),
                            'snippet': result.get('body', '')
                        })
            except:
                pass
        
        return {
            'cases_found': len(articles),
            'articles': articles,
            'risk_level': 'HIGH' if len(articles) > 3 else 'MEDIUM' if len(articles) > 0 else 'LOW',
            'summary': self._summarize_with_rag(f"Litigation research for {company_name}", [a['snippet'] for a in articles])
        }
    
    def _research_regulatory(self, company_name: str, sector: str) -> Dict:
        """Research regulatory actions"""
        
        queries = [
            f"{company_name} RBI action penalty",
            f"{company_name} SEBI order",
            f"{sector} regulatory compliance India"
        ]
        
        articles = []
        for query in queries:
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(f"site:rbi.org.in OR site:sebi.gov.in {query}", max_results=2))
                    for result in results:
                        articles.append({
                            'title': result.get('title', ''),
                            'url': result.get('href', ''),
                            'snippet': result.get('body', '')
                        })
            except:
                pass
        
        return {
            'actions_found': len(articles),
            'articles': articles,
            'risk_level': 'HIGH' if len(articles) > 2 else 'MEDIUM' if len(articles) > 0 else 'LOW'
        }
    
    def _research_mca(self, company_name: str, cin: str) -> Dict:
        """Research MCA filings"""
        
        queries = [
            f"{company_name} MCA director change",
            f"{cin} MCA filing" if cin else f"{company_name} MCA compliance"
        ]
        
        articles = []
        for query in queries:
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(f"site:mca.gov.in {query}", max_results=2))
                    for result in results:
                        articles.append({
                            'title': result.get('title', ''),
                            'url': result.get('href', ''),
                            'snippet': result.get('body', '')
                        })
            except:
                pass
        
        return {
            'filings_found': len(articles),
            'articles': articles
        }
    
    def _analyze_news_sentiment(self, company_name: str) -> Dict:
        """Analyze overall news sentiment"""
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(f"{company_name} India news", max_results=5))
                
                if not results:
                    return {'sentiment': 'NEUTRAL', 'confidence': 0}
                
                # Analyze sentiment with RAG
                snippets = [r.get('body', '') for r in results]
                sentiment_analysis = self._analyze_sentiment_with_rag(company_name, snippets)
                
                return {
                    'sentiment': sentiment_analysis.get('sentiment', 'NEUTRAL'),
                    'confidence': sentiment_analysis.get('confidence', 0),
                    'articles_analyzed': len(results)
                }
        except:
            return {'sentiment': 'NEUTRAL', 'confidence': 0}
    
    # ============================================================
    # PRIMARY INSIGHT INTEGRATION
    # ============================================================
    
    def add_primary_insight(self, insight_type: str, data: Dict):
        """
        Add qualitative insights from Credit Officer
        Types: site_visit, management_interview, market_intelligence
        """
        
        if insight_type not in self.primary_insights:
            self.primary_insights[insight_type] = []
        
        self.primary_insights[insight_type].append(data)
        
        # Calculate impact on risk score
        impact = self._calculate_insight_impact(insight_type, data)
        
        return {
            'insight_recorded': True,
            'type': insight_type,
            'impact_on_score': impact,
            'total_insights': len(self.primary_insights.get(insight_type, []))
        }
    
    def _calculate_insight_impact(self, insight_type: str, data: Dict) -> Dict:
        """Calculate how primary insights affect risk score"""
        
        score_adjustment = 0
        explanation = []
        
        if insight_type == 'site_visit':
            capacity = data.get('capacity_utilization_pct', 100)
            if capacity < 50:
                score_adjustment -= 15
                explanation.append(f"Low capacity utilization ({capacity}%) indicates operational stress")
            elif capacity > 80:
                score_adjustment += 10
                explanation.append(f"High capacity utilization ({capacity}%) shows strong demand")
            
            machinery = data.get('machinery_condition', 'Good')
            if machinery == 'Poor':
                score_adjustment -= 10
                explanation.append("Poor machinery condition raises operational risk")
        
        elif insight_type == 'management_interview':
            quality = data.get('quality_rating', 5)
            if quality <= 3:
                score_adjustment -= 10
                explanation.append(f"Management quality rated {quality}/10 - concerns about capability")
            elif quality >= 8:
                score_adjustment += 5
                explanation.append(f"Strong management team (rated {quality}/10)")
            
            red_flags = data.get('red_flags', [])
            if red_flags:
                score_adjustment -= len(red_flags) * 5
                explanation.append(f"{len(red_flags)} red flags identified in interview")
        
        return {
            'score_adjustment': score_adjustment,
            'explanation': explanation,
            'severity': 'HIGH' if abs(score_adjustment) > 15 else 'MEDIUM' if abs(score_adjustment) > 5 else 'LOW'
        }
    
    def get_integrated_assessment(self) -> Dict:
        """Get combined assessment from secondary research and primary insights"""
        
        total_adjustment = 0
        all_explanations = []
        
        for insight_type, insights in self.primary_insights.items():
            for insight in insights:
                impact = self._calculate_insight_impact(insight_type, insight)
                total_adjustment += impact['score_adjustment']
                all_explanations.extend(impact['explanation'])
        
        return {
            'primary_insights_count': sum(len(v) for v in self.primary_insights.values()),
            'total_score_adjustment': total_adjustment,
            'explanations': all_explanations,
            'insights_summary': self._summarize_primary_insights()
        }
    
    def _summarize_primary_insights(self) -> str:
        """Summarize all primary insights"""
        
        if not self.primary_insights:
            return "No primary insights recorded"
        
        summary = []
        for insight_type, insights in self.primary_insights.items():
            summary.append(f"{insight_type.replace('_', ' ').title()}: {len(insights)} observation(s)")
        
        return "; ".join(summary)
    
    # ============================================================
    # RAG ANALYSIS HELPERS
    # ============================================================
    
    def _summarize_with_rag(self, topic: str, content: List[str]) -> str:
        """Summarize content using Groq RAG"""
        
        if not self.client or not content:
            return "No analysis available"
        
        combined = "\n".join([c for c in content if c])[:3000]  # Limit context
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": f"Summarize this {topic} for credit risk assessment (2-3 sentences):\n\n{combined}"
                }],
                temperature=0,
                max_tokens=200
            )
            return response.choices[0].message.content
        except:
            return "Analysis unavailable"
    
    def _extract_headwinds(self, articles: List[Dict]) -> List[str]:
        """Extract sector headwinds from articles"""
        headwind_keywords = ['challenge', 'risk', 'decline', 'slowdown', 'regulation', 'restriction']
        headwinds = []
        for article in articles:
            snippet = article.get('snippet', '').lower()
            if any(k in snippet for k in headwind_keywords):
                headwinds.append(article.get('title', ''))
        return headwinds[:3]
    
    def _extract_tailwinds(self, articles: List[Dict]) -> List[str]:
        """Extract sector tailwinds from articles"""
        tailwind_keywords = ['growth', 'opportunity', 'expansion', 'demand', 'positive', 'boost']
        tailwinds = []
        for article in articles:
            snippet = article.get('snippet', '').lower()
            if any(k in snippet for k in tailwind_keywords):
                tailwinds.append(article.get('title', ''))
        return tailwinds[:3]
    
    def _extract_regulatory_changes(self, articles: List[Dict]) -> List[str]:
        """Extract regulatory changes"""
        reg_keywords = ['rbi', 'sebi', 'regulation', 'policy', 'guideline', 'circular']
        changes = []
        for article in articles:
            snippet = article.get('snippet', '').lower()
            if any(k in snippet for k in reg_keywords):
                changes.append(article.get('title', ''))
        return changes[:3]
    
    def _analyze_sentiment_with_rag(self, company: str, snippets: List[str]) -> Dict:
        """Analyze sentiment using RAG"""
        
        if not self.client:
            return {'sentiment': 'NEUTRAL', 'confidence': 0}
        
        combined = "\n".join(snippets)[:2000]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": f"Analyze news sentiment for {company}. Return JSON: {{\"sentiment\": \"POSITIVE/NEUTRAL/NEGATIVE\", \"confidence\": 0-100}}\n\n{combined}"
                }],
                temperature=0,
                max_tokens=100
            )
            
            import json
            content = response.choices[0].message.content
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            return json.loads(content)
        except:
            return {'sentiment': 'NEUTRAL', 'confidence': 0}
    
    def _synthesize_research(self, company: str, results: Dict) -> str:
        """Synthesize all research findings"""
        
        if not self.client:
            return "Synthesis unavailable"
        
        context = f"""Company: {company}
Promoter Risk: {results['promoter_research']['risk_level']}
Sector Outlook: {results['sector_research'].get('summary', 'N/A')}
Litigation: {results['litigation_research']['risk_level']} ({results['litigation_research']['cases_found']} cases)
Regulatory: {results['regulatory_research']['risk_level']} ({results['regulatory_research']['actions_found']} actions)
News Sentiment: {results['news_sentiment']['sentiment']}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": f"Synthesize this research for credit decision (3-4 sentences, focus on key risks):\n\n{context}"
                }],
                temperature=0,
                max_tokens=300
            )
            return response.choices[0].message.content
        except:
            return "Synthesis unavailable"
    
    def _calculate_research_risk_score(self, results: Dict) -> int:
        """Calculate overall risk score from research (0-100, higher = riskier)"""
        
        score = 50  # Start neutral
        
        # Promoter risk
        if results['promoter_research']['risk_level'] == 'HIGH':
            score += 20
        elif results['promoter_research']['risk_level'] == 'MEDIUM':
            score += 10
        
        # Litigation
        if results['litigation_research']['risk_level'] == 'HIGH':
            score += 15
        elif results['litigation_research']['risk_level'] == 'MEDIUM':
            score += 7
        
        # Regulatory
        if results['regulatory_research']['risk_level'] == 'HIGH':
            score += 15
        elif results['regulatory_research']['risk_level'] == 'MEDIUM':
            score += 7
        
        # Sentiment
        sentiment = results['news_sentiment']['sentiment']
        if sentiment == 'NEGATIVE':
            score += 10
        elif sentiment == 'POSITIVE':
            score -= 10
        
        return min(max(score, 0), 100)  # Clamp between 0-100
    
    def _extract_key_findings(self, results: Dict) -> List[str]:
        """Extract key findings from all research"""
        
        findings = []
        
        if results['promoter_research']['risk_level'] != 'LOW':
            findings.append(f"Promoter Risk: {results['promoter_research']['risk_level']}")
        
        if results['litigation_research']['cases_found'] > 0:
            findings.append(f"{results['litigation_research']['cases_found']} litigation case(s) found")
        
        if results['regulatory_research']['actions_found'] > 0:
            findings.append(f"{results['regulatory_research']['actions_found']} regulatory action(s) found")
        
        if results['sector_research'].get('headwinds'):
            findings.append(f"Sector headwinds: {len(results['sector_research']['headwinds'])} identified")
        
        if results['news_sentiment']['sentiment'] == 'NEGATIVE':
            findings.append("Negative news sentiment detected")
        
        return findings
