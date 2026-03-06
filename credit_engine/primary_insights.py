"""Primary insights portal for qualitative inputs"""
from typing import Dict, List
from datetime import datetime

class PrimaryInsights:
    def __init__(self):
        self.insights = []
    
    def add_site_visit_notes(self, notes: Dict) -> None:
        """Add factory/site visit observations"""
        insight = {
            'type': 'site_visit',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'capacity_utilization': notes.get('capacity_utilization_pct'),
                'machinery_condition': notes.get('machinery_condition'),
                'inventory_levels': notes.get('inventory_levels'),
                'employee_count': notes.get('employee_count'),
                'safety_compliance': notes.get('safety_compliance'),
                'observations': notes.get('observations', '')
            }
        }
        self.insights.append(insight)
    
    def add_management_interview(self, interview: Dict) -> None:
        """Add management interview notes"""
        insight = {
            'type': 'management_interview',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'management_quality': interview.get('quality_rating'),  # 1-5
                'business_understanding': interview.get('business_understanding'),
                'succession_plan': interview.get('succession_plan'),
                'red_flags': interview.get('red_flags', []),
                'notes': interview.get('notes', '')
            }
        }
        self.insights.append(insight)
    
    def add_customer_supplier_feedback(self, feedback: Dict) -> None:
        """Add customer/supplier reference checks"""
        insight = {
            'type': 'reference_check',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'entity_type': feedback.get('type'),  # customer/supplier
                'payment_behavior': feedback.get('payment_behavior'),
                'relationship_duration': feedback.get('relationship_years'),
                'feedback': feedback.get('feedback', '')
            }
        }
        self.insights.append(insight)
    
    def add_custom_observation(self, observation: Dict) -> None:
        """Add any custom qualitative observation"""
        insight = {
            'type': 'custom',
            'timestamp': datetime.now().isoformat(),
            'data': observation
        }
        self.insights.append(insight)
    
    def calculate_qualitative_score(self) -> Dict:
        """Calculate risk adjustment based on qualitative insights"""
        score_adjustments = {
            'capacity_utilization': 0,
            'management_quality': 0,
            'reference_checks': 0,
            'red_flags': 0
        }
        
        for insight in self.insights:
            if insight['type'] == 'site_visit':
                capacity = insight['data'].get('capacity_utilization')
                if capacity and capacity < 50:
                    score_adjustments['capacity_utilization'] -= 15  # -15 points
                elif capacity and capacity > 80:
                    score_adjustments['capacity_utilization'] += 10  # +10 points
            
            elif insight['type'] == 'management_interview':
                quality = insight['data'].get('management_quality')
                if quality:
                    score_adjustments['management_quality'] = (quality - 3) * 5  # -10 to +10
                
                red_flags = insight['data'].get('red_flags', [])
                score_adjustments['red_flags'] -= len(red_flags) * 10
            
            elif insight['type'] == 'reference_check':
                payment = insight['data'].get('payment_behavior')
                if payment == 'poor':
                    score_adjustments['reference_checks'] -= 20
                elif payment == 'excellent':
                    score_adjustments['reference_checks'] += 10
        
        total_adjustment = sum(score_adjustments.values())
        
        return {
            'total_adjustment': total_adjustment,
            'breakdown': score_adjustments,
            'insights_count': len(self.insights)
        }
    
    def get_summary(self) -> str:
        """Get narrative summary of primary insights"""
        if not self.insights:
            return "No primary insights recorded"
        
        summary = []
        
        site_visits = [i for i in self.insights if i['type'] == 'site_visit']
        if site_visits:
            latest = site_visits[-1]
            capacity = latest['data'].get('capacity_utilization')
            if capacity:
                summary.append(f"Factory operating at {capacity}% capacity")
        
        interviews = [i for i in self.insights if i['type'] == 'management_interview']
        if interviews:
            latest = interviews[-1]
            red_flags = latest['data'].get('red_flags', [])
            if red_flags:
                summary.append(f"Management interview revealed {len(red_flags)} red flags")
        
        return ". ".join(summary) if summary else "Primary due diligence completed"
