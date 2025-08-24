# 🚀 Career Copilot Agent - Hackathon Demo

**AI-Powered Career Assistant Built with Portia SDK**

Transform your job search with intelligent automation, ATS-optimized resume analysis, and personalized interview preparation using Portia AI's powerful tool registry.

## ✨ Features

### 📧 **Gmail Job Scanner**

- Automatically scans Gmail for job opportunities and recruiter messages
- Extracts company names, positions, deadlines, and application links
- Prioritizes emails by relevance and urgency
- Uses Portia's Gmail tool with secure OAuth authentication

### 📄 **AI Resume Optimizer**

- Upload PDF, DOCX, or paste text resumes
- AI-powered ATS compatibility scoring (0-100)
- Intelligent keyword matching with job descriptions
- Personalized improvement suggestions
- Tailored professional summary generation

### 🎤 **Comprehensive Interview Prep**

- Generates 10-12 role-specific questions
- Covers behavioral, technical, and system design questions
- STAR method guidance for behavioral responses
- Sample answers with key talking points
- Personalized based on your profile and target role

### 📊 **Automated Job Tracker**

- Google Sheets integration for application tracking
- Automatic spreadsheet creation and updates
- Track application status, deadlines, and follow-ups
- Export and sync across devices

## 🏗️ Architecture

### **Portia SDK Integration**

This project leverages Portia AI's powerful SDK for:

- **Cloud Tool Registry**: Access to Gmail, Google Sheets, Calendar, and more
- **AI Orchestration**: Intelligent plan generation and execution
- **Secure Authentication**: Just-in-time OAuth for all integrations
- **Stateful Execution**: Trackable plan runs with cloud storage

### **Project Structure**

```
Career Copilot Agent/
├── app.py                  # Main Streamlit application
├── cli.py                  # Command-line interface
├── app/
│   └── orchestrator.py     # Portia SDK orchestrator
├── tools/                  # Custom tools implementation
├── config.py               # Configuration management
├── run_demo.ps1            # Demo script for PowerShell
├── run_demo.bat            # Demo script for Windows Command Prompt
├── requirements.txt        # Dependencies
├── .env                    # Environment variables
└── README.md               # This file
```

## 🚀 Quick Start

### 💯 **Hackathon Demo Mode**

For the hackathon demonstration, we've created simplified scripts that run the Gmail scanning functionality without requiring full Google Sheets setup:

**Windows PowerShell:**

```powershell
.\run_demo.ps1
```

**Windows Command Prompt:**

```
run_demo.bat
```

This will demonstrate the email extraction capabilities while skipping the sheet writing portion.

### 1. **Setup Portia Account**

1. Visit [Portia Dashboard](https://app.portialabs.ai/dashboard)
2. Create an account and get your API key
3. Enable Gmail and Google Sheets tools in the tool registry

### 2. **Configure Environment**

Create a `.env` file:

```bash
PORTIA_API_KEY=your_portia_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
SHEET_ID=your_google_sheet_id_here  # Optional, can be passed via CLI
```

### 3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

### 4. **Running the Application**

**Web Interface:**

```bash
streamlit run app.py
```

**CLI Interface:**

```bash
# Standard mode - tries to write to Google Sheets
python cli.py gmail-to-sheets --sheet-id "YOUR_SHEET_ID"

# Demo mode - extracts email data only, doesn't require Google Sheets API setup
python cli.py gmail-to-sheets --sheet-id "YOUR_SHEET_ID" --demo
```

### 5. **Access the Web App**

Open your browser to `http://localhost:8501`

## 🔧 Configuration

### **Portia Tool Registry Setup**

1. **Gmail Tool**: Enable in Portia dashboard for email scanning
2. **Google Sheets Tool**: Enable for job application tracking
3. **OpenAI Integration**: Configure for AI-powered analysis

### **User Profile Setup**

Complete your profile in the sidebar:

- Full name and contact information
- Years of experience
- Current role and target positions
- Core skills and technologies

## 🎯 Usage Guide

### **Gmail Job Scanning**

1. Click "Scan Gmail" in the Job Email Scanner tab
2. Authorize Gmail access (first time only)
3. View structured job data extracted from your emails
4. Optionally export to Google Sheets (requires additional setup)

### **Resume Optimization**

1. Upload your resume or paste the text
2. Enter the job description
3. Get your ATS score and personalized improvements
4. Apply suggested changes to improve compatibility

### **Interview Preparation**

1. Enter the job description
2. Review generated questions and sample answers
3. Practice using the provided guidance
4. Customize responses to match your experience

## 👨‍💻 Development Notes

### **For Hackathon Submission**

- The core functionality of scanning Gmail and extracting structured job data is fully functional
- The Google Sheets integration requires additional OAuth setup that may not be available in all environments
- Use the `--demo` flag with the CLI or run the demo script for a simplified demonstration

### **Known Limitations**

- Google Sheets integration may require additional OAuth setup beyond the hackathon environment
- The Job Application Tracker feature has been temporarily disabled for the hackathon submission due to API limitations
- The LLM can occasionally format JSON incorrectly - error handling is in place

### **Future Enhancements**

- Direct Google Sheets integration without requiring Portia's Google Sheets tool
- Enhanced ATS scoring with industry-specific benchmarks
- Interview recording and feedback analysis
- Automated follow-up email generation

## 🛠️ Troubleshooting

### **OAuth Authentication Issues**

If you encounter OAuth errors:

1. Ensure your Portia API key is valid
2. Check that Gmail and Google Sheets tools are enabled in Portia
3. Follow the terminal prompts to complete authentication

### **Missing Dependencies**

```bash
pip install --upgrade -r requirements.txt
```

### **Sheet Writing Issues**

If data is extracted but not written to Google Sheets:

1. Try the `--demo` mode to verify extraction is working
2. Check your Google Sheet permissions
3. Ensure the sheet ID is correct

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Portia SDK](https://docs.portialabs.ai/)
- Uses [Streamlit](https://streamlit.io/) for the web interface
