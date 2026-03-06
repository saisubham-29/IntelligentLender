"""Web portal for credit officers"""
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import pandas as pd
from credit_engine.feature_engineering import FeatureEngineering
from credit_engine.ml_model import CreditDecisionModel
from credit_engine.cam_generator import CAMGenerator
from credit_engine.data_validator import DataValidator
from credit_engine.secondary_research import SecondaryResearch
from credit_engine.primary_insights import PrimaryInsights
from credit_engine.document_parser import DocumentParser

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls', 'csv'}

os.makedirs('uploads', exist_ok=True)

# Initialize components
feature_eng = FeatureEngineering()
ml_model = CreditDecisionModel()
cam_gen = CAMGenerator()
validator = DataValidator()
research = SecondaryResearch()
primary_insights = PrimaryInsights()
doc_parser = DocumentParser()

# Train model with dummy data on startup
X_train = pd.DataFrame([{'f'+str(i): 0.5 for i in range(12)} for _ in range(100)])
ml_model.train(X_train, pd.Series([1]*60 + [0]*40), pd.Series([5000000]*100), pd.Series([0.05]*100))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process_with_files', methods=['POST'])
def process_with_files():
    """Process application with file uploads"""
    try:
        # Get form data
        applicant_id = request.form.get('applicant_id')
        company_name = request.form.get('company_name')
        loan_amount = float(request.form.get('loan_amount', 0))
        loan_purpose = request.form.get('loan_purpose', '')
        tenure_months = int(request.form.get('tenure_months', 60))
        
        # Handle file uploads
        uploaded_files = {}
        parsed_data = {}
        
        if 'financial_statement' in request.files:
            file = request.files['financial_statement']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_files['financial_statement'] = filepath
                
                # Parse financial statement
                if filename.endswith('.pdf'):
                    parsed_data['financial'] = doc_parser.parse_annual_report(filepath)
        
        if 'bank_statement' in request.files:
            file = request.files['bank_statement']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_files['bank_statement'] = filepath
                
                if filename.endswith('.pdf'):
                    parsed_data['bank'] = doc_parser.parse_bank_statement(filepath)
        
        if 'gst_return' in request.files:
            file = request.files['gst_return']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_files['gst_return'] = filepath
                
                if filename.endswith('.pdf'):
                    parsed_data['gst'] = doc_parser.parse_gst_returns(filepath)
        
        # Extract data from parsed documents or use form data
        revenue = float(request.form.get('revenue', 0))
        net_profit = float(request.form.get('net_profit', 0))
        total_assets = float(request.form.get('total_assets', 0))
        net_worth = float(request.form.get('net_worth', 0))
        total_debt = float(request.form.get('total_debt', 0))
        
        # Override with parsed data if available
        if 'financial' in parsed_data:
            revenue = parsed_data['financial'].get('revenue', revenue)
            net_profit = parsed_data['financial'].get('profit', net_profit)
            total_debt = parsed_data['financial'].get('debt', total_debt)
        
        # Build applicant data
        applicant = {
            'applicant_id': applicant_id,
            'name': company_name,
            'cin': request.form.get('cin', ''),
            'gstin': request.form.get('gstin', ''),
            'industry': request.form.get('industry', ''),
            'annual_income': revenue,
            'collateral_value': float(request.form.get('collateral_value', 0)),
            'loan_amount_requested': loan_amount,
            'loan_purpose': loan_purpose,
            'tenure_months': tenure_months
        }
        
        financial = pd.DataFrame([{
            'revenue': revenue,
            'net_profit': net_profit,
            'total_assets': total_assets,
            'net_worth': net_worth,
            'total_debt': total_debt,
            'current_assets': revenue * 0.3,
            'current_liabilities': total_debt * 0.4,
            'ebitda': net_profit * 1.5,
            'dscr': 1.5,
            'interest_coverage': 2.5,
            'tangible_net_worth': net_worth * 0.9,
            'total_income': revenue
        }])
        
        credit = pd.DataFrame([{
            'credit_score': int(request.form.get('credit_score', 700)),
            'balance': total_debt * 0.5,
            'credit_limit': total_debt,
            'delinquent': 0
        }])
        
        # Fraud detection if both GST and Bank data available
        validation_results = {}
        if 'gst' in parsed_data and 'bank' in parsed_data:
            validation_results['gst_bank'] = validator.cross_verify_gst_bank(
                parsed_data['gst'], 
                parsed_data['bank']
            )
            validation_results['circular_trading'] = validator.detect_circular_trading(
                parsed_data['bank']
            )
        
        # Feature engineering
        features = feature_eng.engineer_features(applicant, financial, credit, {})
        
        # ML decision
        decision = ml_model.predict(features)
        
        # Adjust credit limit based on requested amount
        if decision['decision'] == 'APPROVE':
            # Cap at requested amount or model recommendation, whichever is lower
            decision['credit_limit'] = min(decision['credit_limit'], loan_amount)
            
            # Calculate LTV if collateral provided
            collateral = applicant.get('collateral_value', 0)
            if collateral > 0:
                ltv = (decision['credit_limit'] / collateral) * 100
                decision['ltv_ratio'] = ltv
                
                # Adjust if LTV too high
                if ltv > 75:
                    decision['credit_limit'] = collateral * 0.75
                    decision['ltv_adjusted'] = True
        
        # Generate CAM
        research_summary = "Document-based assessment"
        if validation_results:
            research_summary += f"\n\nValidation performed on uploaded documents"
        
        cam = cam_gen.generate_memo(
            applicant, financial, credit,
            research_summary, decision, ml_model.get_feature_importance(),
            validation_results, None
        )
        
        # Save CAM
        cam_file = f"uploads/CAM_{applicant_id}.txt"
        with open(cam_file, 'w', encoding='utf-8') as f:
            f.write(cam)
        
        return jsonify({
            'success': True,
            'decision': decision['decision'],
            'credit_limit': decision['credit_limit'],
            'requested_amount': loan_amount,
            'risk_premium': decision['risk_premium_bps'],
            'approval_probability': decision['approval_probability'] * 100,
            'default_probability': decision['default_probability'] * 100,
            'ltv_ratio': decision.get('ltv_ratio', 0),
            'files_processed': len(uploaded_files),
            'validation_performed': len(validation_results) > 0,
            'validation_results': validation_results,
            'cam_file': cam_file
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/quick_decision', methods=['POST'])
def quick_decision():
    """Quick decision with form data"""
    data = request.json
    
    # Create mock data from form
    applicant = {
        'applicant_id': data['applicant_id'],
        'name': data['company_name'],
        'cin': data.get('cin', ''),
        'gstin': data.get('gstin', ''),
        'industry': data.get('industry', ''),
        'annual_income': float(data.get('revenue', 0)),
        'collateral_value': float(data.get('collateral_value', 0))
    }
    
    financial = pd.DataFrame([{
        'revenue': float(data.get('revenue', 0)),
        'net_profit': float(data.get('net_profit', 0)),
        'total_assets': float(data.get('total_assets', 0)),
        'net_worth': float(data.get('net_worth', 0)),
        'total_debt': float(data.get('total_debt', 0)),
        'current_assets': float(data.get('revenue', 0)) * 0.3,
        'current_liabilities': float(data.get('total_debt', 0)) * 0.4,
        'ebitda': float(data.get('net_profit', 0)) * 1.5,
        'dscr': 1.5,
        'interest_coverage': 2.5,
        'tangible_net_worth': float(data.get('net_worth', 0)) * 0.9,
        'total_income': float(data.get('revenue', 0))
    }])
    
    credit = pd.DataFrame([{
        'credit_score': int(data.get('credit_score', 700)),
        'balance': float(data.get('total_debt', 0)) * 0.5,
        'credit_limit': float(data.get('total_debt', 0)),
        'delinquent': 0
    }])
    
    # Feature engineering
    features = feature_eng.engineer_features(applicant, financial, credit, {})
    
    # ML decision
    decision = ml_model.predict(features)
    
    # Generate CAM
    cam = cam_gen.generate_memo(
        applicant, financial, credit,
        "Quick assessment - no secondary research performed",
        decision, ml_model.get_feature_importance()
    )
    
    # Save CAM
    cam_file = f"uploads/CAM_{applicant['applicant_id']}.txt"
    with open(cam_file, 'w', encoding='utf-8') as f:
        f.write(cam)
    
    return jsonify({
        'success': True,
        'decision': decision['decision'],
        'credit_limit': decision['credit_limit'],
        'risk_premium': decision['risk_premium_bps'],
        'approval_probability': decision['approval_probability'] * 100,
        'default_probability': decision['default_probability'] * 100,
        'cam_file': cam_file
    })

@app.route('/api/add_site_visit', methods=['POST'])
def add_site_visit():
    """Add site visit notes"""
    data = request.json
    
    primary_insights.add_site_visit_notes({
        'capacity_utilization_pct': int(data['capacity_utilization']),
        'machinery_condition': data['machinery_condition'],
        'observations': data['observations']
    })
    
    score = primary_insights.calculate_qualitative_score()
    
    return jsonify({
        'success': True,
        'adjustment': score['total_adjustment'],
        'message': f"Site visit recorded. Score adjustment: {score['total_adjustment']}"
    })

@app.route('/api/add_interview', methods=['POST'])
def add_interview():
    """Add management interview"""
    data = request.json
    
    primary_insights.add_management_interview({
        'quality_rating': int(data['quality_rating']),
        'red_flags': data.get('red_flags', '').split(',') if data.get('red_flags') else [],
        'notes': data['notes']
    })
    
    score = primary_insights.calculate_qualitative_score()
    
    return jsonify({
        'success': True,
        'adjustment': score['total_adjustment'],
        'message': f"Interview recorded. Score adjustment: {score['total_adjustment']}"
    })

@app.route('/api/download_cam/<applicant_id>')
def download_cam(applicant_id):
    """Download CAM document"""
    cam_file = f"uploads/CAM_{applicant_id}.txt"
    if os.path.exists(cam_file):
        return send_file(cam_file, as_attachment=True)
    return jsonify({'error': 'CAM not found'}), 404

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Intelli-Credit Web Portal Starting...")
    print("="*60)
    print("\n📊 Open in browser: http://localhost:5000")
    print("\n✓ ML Model trained and ready")
    print("✓ Upload folder created")
    print("✓ File upload enabled (PDF, Excel, CSV)")
    print("\n" + "="*60 + "\n")
    app.run(debug=True, port=5000, host='0.0.0.0')
