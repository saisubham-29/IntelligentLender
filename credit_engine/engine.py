"""Main Credit Decisioning Engine orchestrator - Indian context"""
from .data_ingestion import DataIngestion
from .document_parser import DocumentParser
from .data_validator import DataValidator
from .secondary_research import SecondaryResearch
from .primary_insights import PrimaryInsights
from .feature_engineering import FeatureEngineering
from .ml_model import CreditDecisionModel
from .cam_generator import CAMGenerator
from typing import Dict
import pandas as pd

class CreditDecisioningEngine:
    def __init__(self):
        self.data_ingestion = DataIngestion()
        self.doc_parser = DocumentParser()
        self.validator = DataValidator()
        self.research = SecondaryResearch()
        self.primary_insights = PrimaryInsights()
        self.feature_eng = FeatureEngineering()
        self.ml_model = CreditDecisionModel()
        self.cam_generator = CAMGenerator()
    
    def process_application(self, applicant_id: str, documents: Dict = None, 
                          primary_inputs: Dict = None) -> Dict:
        """End-to-end processing of credit application"""
        
        # Step 1: Data Ingestion from Databricks
        self.data_ingestion.connect()
        applicant_data = self.data_ingestion.fetch_applicant_data(applicant_id)
        financial_data = self.data_ingestion.fetch_financial_data(applicant_id)
        credit_history = self.data_ingestion.fetch_credit_history(applicant_id)
        self.data_ingestion.close()
        
        # Step 2: Document Parsing (if documents provided)
        parsed_docs = {}
        if documents:
            if 'annual_report' in documents:
                parsed_docs['annual_report'] = self.doc_parser.parse_annual_report(documents['annual_report'])
            if 'gst_returns' in documents:
                parsed_docs['gst_returns'] = self.doc_parser.parse_gst_returns(documents['gst_returns'])
            if 'bank_statement' in documents:
                parsed_docs['bank_statement'] = self.doc_parser.parse_bank_statement(documents['bank_statement'])
            if 'mca_filing' in documents:
                parsed_docs['mca_filing'] = self.doc_parser.parse_mca_filing(documents['mca_filing'])
            if 'legal_notice' in documents:
                parsed_docs['legal_notice'] = self.doc_parser.parse_legal_notice(documents['legal_notice'])
        
        # Step 3: Data Validation & Fraud Detection
        validation_results = {}
        if parsed_docs.get('gst_returns') and parsed_docs.get('bank_statement'):
            validation_results['gst_bank_verification'] = self.validator.cross_verify_gst_bank(
                parsed_docs['gst_returns'], 
                parsed_docs['bank_statement']
            )
            validation_results['circular_trading'] = self.validator.detect_circular_trading(
                parsed_docs['bank_statement']
            )
        
        # Step 4: Secondary Research
        entity_name = applicant_data.get('name', '') or applicant_data.get('company_name', '')
        cin = applicant_data.get('cin') or parsed_docs.get('mca_filing', {}).get('cin')
        promoters = applicant_data.get('promoters', [])
        
        research_data = self.research.research_entity(entity_name, cin, promoters)
        research_summary = self.research.synthesize_findings(research_data)
        
        # Step 5: Primary Insights Integration
        if primary_inputs:
            if 'site_visit' in primary_inputs:
                self.primary_insights.add_site_visit_notes(primary_inputs['site_visit'])
            if 'management_interview' in primary_inputs:
                self.primary_insights.add_management_interview(primary_inputs['management_interview'])
            if 'reference_check' in primary_inputs:
                self.primary_insights.add_customer_supplier_feedback(primary_inputs['reference_check'])
        
        qualitative_score = self.primary_insights.calculate_qualitative_score()
        primary_summary = self.primary_insights.get_summary()
        
        # Step 6: Feature Engineering
        features = self.feature_eng.engineer_features(
            applicant_data, financial_data, credit_history, research_data
        )
        
        # Step 7: ML Decision (with qualitative adjustment)
        ml_decision = self.ml_model.predict(features)
        
        # Adjust decision based on qualitative insights
        ml_decision['approval_probability'] += (qualitative_score['total_adjustment'] / 100)
        ml_decision['approval_probability'] = max(0, min(1, ml_decision['approval_probability']))
        
        # Re-evaluate decision after adjustment
        from .config import ML_MODEL_CONFIG
        should_approve = ml_decision['approval_probability'] >= ML_MODEL_CONFIG['risk_threshold']
        ml_decision['decision'] = "APPROVE" if should_approve else "REJECT"
        
        feature_importance = self.ml_model.get_feature_importance()
        
        # Step 8: Generate CAM
        cam_document = self.cam_generator.generate_memo(
            applicant_data, financial_data, credit_history,
            research_summary, ml_decision, feature_importance,
            validation_results, primary_summary
        )
        
        return {
            "applicant_id": applicant_id,
            "decision": ml_decision,
            "validation_results": validation_results,
            "qualitative_adjustment": qualitative_score,
            "cam_document": cam_document,
            "explainability": {
                "feature_importance": feature_importance,
                "validation_flags": validation_results,
                "research_findings": research_summary,
                "primary_insights": primary_summary
            }
        }
    
    def train_model(self, training_data_query: str):
        """Train the ML model on historical data"""
        self.data_ingestion.connect()
        # Fetch training data from Databricks
        # This would be customized based on your data schema
        self.data_ingestion.close()
    
    def add_primary_insight(self, insight_type: str, data: Dict):
        """Add primary insight during due diligence"""
        if insight_type == 'site_visit':
            self.primary_insights.add_site_visit_notes(data)
        elif insight_type == 'management_interview':
            self.primary_insights.add_management_interview(data)
        elif insight_type == 'reference_check':
            self.primary_insights.add_customer_supplier_feedback(data)
        else:
            self.primary_insights.add_custom_observation(data)
