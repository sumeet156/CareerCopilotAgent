# 🚀 Career Copilot Agent

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
├── app.py                 # Main Streamlit application
├── orchestrator.py        # Portia SDK orchestrator
├── config.py             # Configuration management
├── requirements.txt      # Dependencies
├── .env                  # Environment variables
└── README.md            # This file
```

## 🚀 Quick Start

### 1. **Setup Portia Account**
1. Visit [Portia Dashboard](https://app.portialabs.ai/dashboard)
2. Create an account and get your API key
3. Enable Gmail and Google Sheets tools in the tool registry

### 2. **Configure Environment**
Create a `.env` file:
```bash
PORTIA_API_KEY=your_portia_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Run the Application**
```bash
streamlit run app.py
```

### 5. **Access the App**
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
3. Review discovered job opportunities
4. Add relevant emails directly to your job tracker

### **Resume Optimization**
1. Upload your resume (PDF/DOCX) or paste text
2. Paste the target job description
3. Click "Optimize Resume"
4. Review ATS score and implement suggestions

### **Interview Preparation**
1. Paste the job description or role summary
2. Click "Generate Interview Prep"
3. Review questions by category
4. Practice with provided sample answers

### **Job Application Tracking**
1. Add applications manually or from email scanner
2. Track status changes and follow-up actions
3. Access your Google Sheets tracker for detailed management

## 🔐 Security & Privacy

- **OAuth Authentication**: Secure, user-controlled access to Gmail and Google Sheets
- **No Data Storage**: Your personal data stays in your own Google account
- **API Key Protection**: Environment variables keep credentials secure
- **Portia Cloud**: Optional cloud storage for plan runs and history

## 🛠️ Development

### **Extending Functionality**
The Portia SDK makes it easy to add new features:

```python
# Add new tools from Portia's registry
from portia import PortiaToolRegistry

# Access LinkedIn, Slack, Calendar, and more
tool_registry = PortiaToolRegistry(config)
```

### **Custom Tools**
Create custom tools for specific needs:

```python
from portia import Tool

class CustomCareerTool(Tool):
    def execute(self, **kwargs):
        # Your custom logic here
        pass
```

## 📊 Technical Specifications

### **Dependencies**
- **Portia SDK**: AI orchestration and tool registry
- **Streamlit**: Modern web interface
- **Python 3.8+**: Core runtime
- **OAuth2**: Secure API authentication

### **API Integrations**
- **Gmail API**: Email scanning and analysis
- **Google Sheets API**: Job tracking automation
- **OpenAI API**: Resume analysis and interview prep
- **Portia Cloud**: Plan execution and storage

## 🎉 Key Benefits

### **For Job Seekers**
- ⚡ **Save Time**: Automate email scanning and application tracking
- 🎯 **Improve Success**: ATS-optimized resumes and targeted prep
- 📈 **Stay Organized**: Centralized job search management
- 🤖 **AI-Powered**: Intelligent insights and recommendations

### **For Developers**
- 🔧 **Portia SDK**: Leverage powerful AI orchestration
- 🚀 **Cloud Tools**: Ready-made integrations
- 📊 **Scalable**: Enterprise-ready architecture
- 🔐 **Secure**: Built-in authentication and privacy

## 🏆 Competition Ready

This project demonstrates:
- ✅ **Full Portia SDK Integration**: Uses cloud tool registry
- ✅ **Professional UI**: Streamlit-based web application
- ✅ **Real-world Value**: Solves actual career management problems
- ✅ **Extensible Architecture**: Easy to add new features
- ✅ **Secure Implementation**: Best practices for API management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests and documentation
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Portia Documentation**: [docs.portialabs.ai](https://docs.portialabs.ai/)
- **Discord Community**: [Portia Discord](https://discord.gg/DvAJz9ffaR)
- **Issues**: GitHub Issues tab for bug reports and feature requests

---

**Built with ❤️ using Portia AI SDK**

*Revolutionizing career management through intelligent automation and AI-powered insights.*
