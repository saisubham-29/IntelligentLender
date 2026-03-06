"""Example usage of Credit Decisioning Engine - Hackathon Demo"""
from credit_engine import CreditDecisioningEngine

def main():
    # Initialize engine
    engine = CreditDecisioningEngine()
    
    # Example: Process application with documents and primary insights
    applicant_id = "APP-12345"
    
    # Documents to parse
    documents = {
        'annual_report': 'path/to/annual_report.pdf',
        'gst_returns': 'path/to/gstr3b.pdf',
        'bank_statement': 'path/to/bank_statement.pdf',
        'mca_filing': 'path/to/mca_filing.pdf'
    }
    
    # Primary insights from due diligence
    primary_inputs = {
        'site_visit': {
            'capacity_utilization_pct': 40,  # Factory at 40% capacity
            'machinery_condition': 'Good',
            'inventory_levels': 'Normal',
            'employee_count': 150,
            'observations': 'Factory found operating at 40% capacity due to seasonal demand'
        },
        'management_interview': {
            'quality_rating': 4,  # 1-5 scale
            'business_understanding': 'Strong',
            'succession_plan': 'Yes',
            'red_flags': [],
            'notes': 'Management demonstrated strong understanding of business and market'
        },
        'reference_check': {
            'type': 'customer',
            'payment_behavior': 'excellent',
            'relationship_years': 5,
            'feedback': 'Always pays on time, reliable supplier'
        }
    }
    
    # Process application
    result = engine.process_application(
        applicant_id=applicant_id,
        documents=documents,
        primary_inputs=primary_inputs
    )
    
    # Print results
    print("="*80)
    print("CREDIT DECISION SUMMARY")
    print("="*80)
    print(f"Decision: {result['decision']['decision']}")
    print(f"Credit Limit: ₹{result['decision']['credit_limit']:,.2f}")
    print(f"Risk Premium: {result['decision']['risk_premium_bps']} bps")
    print(f"Approval Probability: {result['decision']['approval_probability']*100:.1f}%")
    print(f"Default Probability: {result['decision']['default_probability']*100:.2f}%")
    
    print("\n" + "="*80)
    print("VALIDATION RESULTS")
    print("="*80)
    if result['validation_results']:
        gst_bank = result['validation_results'].get('gst_bank_verification', {})
        if gst_bank:
            print(f"GST-Bank Variance: {gst_bank.get('variance_pct', 0):.2f}%")
            print(f"Suspicious: {'Yes' if gst_bank.get('is_suspicious') else 'No'}")
    
    print("\n" + "="*80)
    print("QUALITATIVE ADJUSTMENT")
    print("="*80)
    qual = result['qualitative_adjustment']
    print(f"Total Score Adjustment: {qual['total_adjustment']}")
    print(f"Insights Recorded: {qual['insights_count']}")
    
    print("\n" + "="*80)
    print("EXPLAINABILITY")
    print("="*80)
    print("\nTop Risk Factors:")
    for feature, importance in sorted(
        result['explainability']['feature_importance'].items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:5]:
        print(f"  • {feature.replace('_', ' ').title()}: {importance:.3f}")
    
    print("\n" + "="*80)
    print("FULL CAM DOCUMENT")
    print("="*80)
    print(result['cam_document'])
    
    # Save CAM to file
    with open(f"CAM_{applicant_id}.txt", "w", encoding='utf-8') as f:
        f.write(result['cam_document'])
    
    print(f"\n✓ CAM saved to CAM_{applicant_id}.txt")

def demo_primary_insights():
    """Demo: Adding primary insights during due diligence"""
    engine = CreditDecisioningEngine()
    
    # Credit officer adds site visit notes
    engine.add_primary_insight('site_visit', {
        'capacity_utilization_pct': 40,
        'machinery_condition': 'Good',
        'observations': 'Factory operating at 40% capacity'
    })
    
    # Add management interview
    engine.add_primary_insight('management_interview', {
        'quality_rating': 3,
        'red_flags': ['Vague about future plans'],
        'notes': 'Management seemed unprepared'
    })
    
    print("✓ Primary insights added successfully")

if __name__ == "__main__":
    main()
    # demo_primary_insights()
