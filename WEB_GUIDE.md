# 🌐 Web Frontend Guide

## Start the Web Portal

```bash
# Option 1: Direct
python web_portal.py

# Option 2: Using script
./start_web.sh
```

Then open: **http://localhost:5000**

## Features

### 1. Quick Credit Decision
- Enter company details (CIN, GSTIN, financials)
- Get instant APPROVE/REJECT decision
- View credit limit, risk premium, probabilities
- Download full CAM report

### 2. Site Visit Recording
- Record factory capacity utilization
- Document machinery condition
- Add qualitative observations
- Auto-adjusts credit score

### 3. Management Interview
- Rate management quality (1-5)
- Flag red flags
- Document interview notes
- Impacts final decision

## Screenshots

### Main Dashboard
- Clean, modern UI with gradient background
- Three tabs: Quick Decision, Site Visit, Interview
- Real-time processing with loading spinner

### Decision Result
- ✅ Green for APPROVE
- ❌ Red for REJECT
- Shows credit limit, risk premium, probabilities
- Download button for full CAM

## API Endpoints

```
POST /api/quick_decision
  - Input: Company financials
  - Output: Decision + CAM file

POST /api/add_site_visit
  - Input: Site visit notes
  - Output: Score adjustment

POST /api/add_interview
  - Input: Interview notes
  - Output: Score adjustment

GET /api/download_cam/<applicant_id>
  - Downloads CAM report as .txt file
```

## Sample Workflow

1. **Enter Application**
   - Application ID: APP-12345
   - Company: ABC Manufacturing
   - Revenue: ₹5,00,00,000
   - Net Profit: ₹40,00,000
   - Total Debt: ₹2,00,00,000

2. **Click "Generate Credit Decision"**
   - Processing takes 2-3 seconds
   - ML model analyzes data
   - Generates decision + CAM

3. **View Result**
   - Decision: APPROVE
   - Credit Limit: ₹5,23,45,678
   - Risk Premium: 650 bps
   - Approval Probability: 78.5%

4. **Add Site Visit** (Optional)
   - Switch to "Site Visit" tab
   - Enter capacity: 75%
   - Condition: Good
   - Observations: "Well-maintained facility"
   - Score adjusts by +10 points

5. **Download CAM**
   - Click "Download Full CAM Report"
   - Gets comprehensive memo with Five Cs analysis

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript
- **ML**: scikit-learn (Gradient Boosting, Random Forest)
- **Styling**: Modern gradient UI with animations

## Customization

### Change Colors
Edit `templates/index.html`, line 9:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Add Fields
Edit form in `templates/index.html` and update API in `web_portal.py`

### Change Port
Edit `web_portal.py`, last line:
```python
app.run(debug=True, port=5000)  # Change 5000 to your port
```

## Production Deployment

```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 web_portal:app
```

## Troubleshooting

**Issue**: Port 5000 already in use
```bash
# Use different port
python web_portal.py --port 8000
```

**Issue**: Can't access from other devices
- Change `host='0.0.0.0'` in `web_portal.py`
- Access via: http://YOUR_IP:5000

**Issue**: Form not submitting
- Check browser console (F12)
- Verify Flask server is running
- Check network tab for API errors

## Mobile Responsive

The UI is fully responsive and works on:
- ✓ Desktop (1920x1080+)
- ✓ Tablet (768px+)
- ✓ Mobile (375px+)

---

**Ready to use!** Just run `python web_portal.py` and open http://localhost:5000
