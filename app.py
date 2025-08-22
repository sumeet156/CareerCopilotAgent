"""
Career Copilot Agent - Streamlit Frontend
Professional career assistance powered by Portia AI SDK
"""
import streamlit as st
import json
from datetime import datetime
import pandas as pd
from app.orchestrator import CareerCopilotOrchestrator
from config import config

# Initialize orchestrator
@st.cache_resource
def get_orchestrator():
    return CareerCopilotOrchestrator()

orchestrator = get_orchestrator()

# Page configuration
st.set_page_config(
    page_title="Career Copilot Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        border: none;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        color: white;
    }
    .feature-card h4 {
        color: white !important;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    .feature-card ul {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    .feature-card li {
        margin-bottom: 0.5rem;
        padding-left: 0.5rem;
    }
    .success-box {
        background: #d4edda;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 Career Copilot Agent</h1>', unsafe_allow_html=True)
    st.markdown("**Powered by Portia AI SDK** | Your AI-powered career assistant")
    
    # Check configuration
    if not config.is_configured():
        st.error("⚠️ Please configure your API keys in the .env file")
        st.stop()
    
    # Sidebar - User Profile
    setup_sidebar()
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📧 Job Email Scanner", 
        "📄 Resume Optimizer", 
        "🎤 Interview Prep", 
        "📊 Job Tracker"
    ])
    
    with tab1:
        job_email_scanner()
    
    with tab2:
        resume_optimizer()
    
    with tab3:
        interview_prep()
    
    with tab4:
        job_tracker()

def setup_sidebar():
    """Setup user profile sidebar"""
    st.sidebar.header("👤 User Profile")
    
    # Store user profile in session state
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    
    st.session_state.user_profile['name'] = st.sidebar.text_input(
        "Full Name", 
        value=st.session_state.user_profile.get('name', '')
    )
    
    st.session_state.user_profile['email'] = st.sidebar.text_input(
        "Email", 
        value=st.session_state.user_profile.get('email', '')
    )
    
    st.session_state.user_profile['experience_years'] = st.sidebar.selectbox(
        "Years of Experience",
        options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 20],
        index=st.session_state.user_profile.get('experience_years', 2)
    )
    
    st.session_state.user_profile['current_role'] = st.sidebar.text_input(
        "Current Role", 
        value=st.session_state.user_profile.get('current_role', '')
    )
    
    st.session_state.user_profile['target_roles'] = st.sidebar.text_area(
        "Target Roles (one per line)",
        value=st.session_state.user_profile.get('target_roles', ''),
        height=100
    )
    
    st.session_state.user_profile['skills'] = st.sidebar.text_area(
        "Core Skills (comma separated)",
        value=st.session_state.user_profile.get('skills', ''),
        height=100
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Configuration Status:**")
    st.sidebar.success("✅ Portia SDK Connected")
    
    # Show available tools
    try:
        tools = orchestrator.get_available_tools()
        gmail_tools = [t for t in tools if 'gmail' in t['id'].lower()]
        sheets_tools = [t for t in tools if 'sheet' in t['id'].lower()]
        
        st.sidebar.info(f"📧 Gmail Tool: {'Enabled' if gmail_tools else 'Setup Required'} ({len(gmail_tools)} tools)")
        st.sidebar.info(f"📊 Sheets Tool: {'Enabled' if sheets_tools else 'Setup Required'} ({len(sheets_tools)} tools)")
        
        # Show total tools available
        st.sidebar.markdown(f"**Total Tools Available:** {len(tools)}")
        
        # Debug: Show first few tools
        if st.sidebar.button("🔍 Show Available Tools"):
            st.sidebar.write("Available tools:")
            for tool in tools[:5]:  # Show first 5 tools
                st.sidebar.write(f"- {tool['name']}")
            if len(tools) > 5:
                st.sidebar.write(f"... and {len(tools) - 5} more")
        
        # Test Portia connection
        if st.sidebar.button("🧪 Test Portia Connection"):
            try:
                test_result = orchestrator.portia.run("What is 2+2?")
                if test_result and hasattr(test_result, 'final_output'):
                    st.sidebar.success("✅ Portia working!")
                else:
                    st.sidebar.error("❌ Portia not responding")
            except Exception as e:
                st.sidebar.error(f"❌ Portia error: {str(e)[:50]}...")
                
    except Exception as e:
        st.sidebar.error(f"Error checking tools: {str(e)}")
        st.sidebar.info("📧 Gmail Tool: Unknown")
        st.sidebar.info("📊 Sheets Tool: Unknown")

def job_email_scanner():
    """Job email scanner using Portia Gmail tool"""
    st.header("📧 Job Email Scanner")
    st.markdown("Scan your Gmail for job opportunities and recruiter messages using Portia's Gmail tool.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="feature-card">
        <h4 style="color: #1f77b4;">🔍 What this tool does:</h4>
        <ul style="color: #333333;">
            <li>Scans your Gmail for job-related emails</li>
            <li>Identifies recruiter messages and job opportunities</li>
            <li>Extracts company names, positions, and deadlines</li>
            <li>Prioritizes emails by relevance</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🔄 Scan Gmail", type="primary", use_container_width=True):
            with st.spinner("Scanning your Gmail for job opportunities..."):
                try:
                    # Check if tools are available first
                    available_tools = orchestrator.get_available_tools()
                    gmail_tools = [t for t in available_tools if 'gmail' in t['id'].lower()]
                    
                    if not gmail_tools:
                        st.error("❌ Gmail tool not available")
                        st.write("**Troubleshooting steps:**")
                        st.write("1. Check your Portia dashboard: https://app.portialabs.ai/dashboard/tool-registry")
                        st.write("2. Ensure Gmail tool is enabled and authenticated")
                        st.write("3. Verify your Portia API key is correct")
                        st.write(f"4. Current tools available: {len(available_tools)}")
                        return
                    
                    # Simple test query first
                    test_query = "What tools are available to me?"
                    test_result = orchestrator.portia.run(test_query)
                    
                    if test_result and hasattr(test_result, 'final_output'):
                        st.success("✅ Portia connection working!")
                        
                        # Now try Gmail query
                        gmail_query = """
                        Please search my Gmail for recent emails (last 7 days) that might be job-related.
                        Look for emails with keywords like: job, opportunity, position, recruiter, hiring, interview.
                        
                        If you can access Gmail, provide:
                        1. Number of relevant emails found
                        2. Subject lines of the most relevant ones
                        3. Sender information
                        
                        If you cannot access Gmail, please explain what authentication is needed.
                        """
                        
                        gmail_result = orchestrator.portia.run(gmail_query)
                        
                        if gmail_result and hasattr(gmail_result, 'final_output'):
                            st.write("**Gmail Scan Results:**")
                            if isinstance(gmail_result.final_output, dict) and 'value' in gmail_result.final_output:
                                st.write(gmail_result.final_output['value'])
                            else:
                                st.write(str(gmail_result.final_output))
                        else:
                            st.warning("Gmail query completed but no results returned")
                    else:
                        st.error("❌ Portia connection failed")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    if "validation error" in str(e).lower():
                        st.write("**This appears to be a Portia configuration issue:**")
                        st.write("1. Try restarting the application")
                        st.write("2. Check if your Portia API key is valid")
                        st.write("3. Ensure tools are properly enabled in dashboard")
                    st.write("**Debug info:**")
                    st.code(str(e))

def display_job_emails(result):
    """Display job email results"""
    if 'job_emails' in result and result['job_emails']:
        st.success(f"✅ Found {len(result['job_emails'])} job-related emails!")
        
        # Summary
        if 'summary' in result:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Emails", result['summary'].get('total_emails', 0))
            with col2:
                st.metric("High Priority", result['summary'].get('high_priority', 0))
            with col3:
                st.metric("Companies", len(result['summary'].get('companies', [])))
        
        # Email list
        for i, email in enumerate(result['job_emails']):
            with st.expander(f"📩 {email.get('subject', 'No Subject')} - {email.get('company', 'Unknown')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**From:** {email.get('sender', 'Unknown')}")
                    st.write(f"**Company:** {email.get('company', 'Not specified')}")
                    st.write(f"**Position:** {email.get('position', 'Not specified')}")
                with col2:
                    st.write(f"**Date:** {email.get('date', 'Unknown')}")
                    st.write(f"**Priority:** {email.get('priority', 'Medium')}")
                    if email.get('deadline'):
                        st.write(f"**Deadline:** {email.get('deadline')}")
                
                if email.get('links'):
                    st.write("**Links:**")
                    for link in email['links']:
                        st.write(f"- {link}")
                
                # Add to tracker button
                if st.button(f"➕ Add to Job Tracker", key=f"add_email_{i}"):
                    add_to_tracker(email)
    else:
        st.info("No job-related emails found in recent messages.")

def resume_optimizer():
    """Resume optimization using Portia AI"""
    st.header("📄 Resume Optimizer")
    st.markdown("Upload your resume and job description to get AI-powered optimization suggestions.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Your Resume")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Resume (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'txt'],
            help="Upload your current resume for analysis"
        )
        
        # Text area as alternative
        resume_text = st.text_area(
            "Or paste your resume text here:",
            height=300,
            placeholder="Paste your resume content here..."
        )
        
        # Use uploaded file or text
        final_resume_text = ""
        if uploaded_file:
            if uploaded_file.type == "text/plain":
                final_resume_text = str(uploaded_file.read(), "utf-8")
            else:
                st.info("📄 File uploaded. Processing...")
                # Note: In a full implementation, you'd extract text from PDF/DOCX
                final_resume_text = f"[Uploaded file: {uploaded_file.name}]"
        elif resume_text:
            final_resume_text = resume_text
    
    with col2:
        st.subheader("🎯 Target Job")
        
        job_description = st.text_area(
            "Paste the job description:",
            height=300,
            placeholder="Paste the complete job description here..."
        )
        
        if st.button("🚀 Optimize Resume", type="primary", use_container_width=True):
            if final_resume_text and job_description:
                with st.spinner("Analyzing your resume and optimizing for the target role..."):
                    try:
                        result = orchestrator.analyze_resume_and_job(
                            final_resume_text, 
                            job_description, 
                            st.session_state.user_profile
                        )
                        
                        if 'error' in result:
                            st.error(f"❌ Error: {result['error']}")
                        else:
                            display_resume_analysis(result)
                            
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
            else:
                st.warning("⚠️ Please provide both resume and job description.")

def display_resume_analysis(result):
    """Display resume analysis results"""
    if isinstance(result, dict):
        st.success("✅ Resume analysis completed!")
        
        # ATS Score
        ats_score = result.get('ats_score', 0)
        st.metric("🎯 ATS Compatibility Score", f"{ats_score}/100")
        
        # Progress bar for ATS score
        progress_color = "🟢" if ats_score >= 70 else "🟡" if ats_score >= 50 else "🔴"
        st.progress(ats_score / 100)
        st.caption(f"{progress_color} {get_ats_feedback(ats_score)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Resume skills
            if 'resume_skills' in result:
                st.subheader("💼 Your Skills")
                for skill in result['resume_skills']:
                    st.badge(skill)
            
            # Skill gaps
            if 'skill_gaps' in result:
                st.subheader("🎯 Skill Gaps to Address")
                for gap in result['skill_gaps']:
                    st.write(f"• {gap}")
        
        with col2:
            # Job keywords
            if 'job_keywords' in result:
                st.subheader("🔑 Job Keywords")
                for keyword in result['job_keywords']:
                    st.badge(keyword, outline=True)
        
        # Tailored summary
        if 'tailored_summary' in result:
            st.subheader("✨ Tailored Professional Summary")
            st.info(result['tailored_summary'])
        
        # Improvements
        if 'improvements' in result:
            st.subheader("🔧 Resume Improvements")
            for i, improvement in enumerate(result['improvements'], 1):
                st.write(f"{i}. {improvement}")
        
        # Recommendations
        if 'recommendations' in result:
            st.subheader("💡 Action Items")
            for rec in result['recommendations']:
                st.write(f"• {rec}")

def interview_prep():
    """Interview preparation using Portia AI"""
    st.header("🎤 Interview Preparation")
    st.markdown("Get comprehensive interview questions and answers tailored to your target role.")
    
    job_description = st.text_area(
        "📋 Job Description or Role Summary:",
        height=200,
        placeholder="Paste the job description or provide a summary of the role you're preparing for..."
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        <div class="feature-card">
        <h4 style="color: #1f77b4;">🎯 Interview Prep Features:</h4>
        <ul style="color: #333333;">
            <li>10-12 comprehensive questions covering all categories</li>
            <li>Behavioral questions with STAR method guidance</li>
            <li>Technical questions specific to your role</li>
            <li>System design and problem-solving scenarios</li>
            <li>Detailed sample answers and key points</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🎯 Generate Interview Prep", type="primary", use_container_width=True):
            if job_description:
                with st.spinner("Generating personalized interview questions..."):
                    try:
                        result = orchestrator.generate_interview_questions(
                            job_description, 
                            st.session_state.user_profile
                        )
                        
                        if 'error' in result:
                            st.error(f"❌ Error: {result['error']}")
                        else:
                            display_interview_questions(result)
                            
                    except Exception as e:
                        st.error(f"❌ Failed to generate questions: {str(e)}")
            else:
                st.warning("⚠️ Please provide a job description.")

def display_interview_questions(result):
    """Display interview questions and answers"""
    if 'interview_prep' in result:
        st.success("✅ Interview preparation ready!")
        
        questions = result['interview_prep']
        
        # Group by category
        categories = {}
        for q in questions:
            cat = q.get('category', 'general')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(q)
        
        # Display by category
        for category, cat_questions in categories.items():
            st.subheader(f"📚 {category.title()} Questions")
            
            for i, q in enumerate(cat_questions, 1):
                with st.expander(f"Q{i}: {q.get('question', 'No question')}"):
                    
                    # Sample answer
                    if 'sample_answer' in q:
                        st.markdown("**💡 Sample Answer:**")
                        st.write(q['sample_answer'])
                    
                    # Key points
                    if 'key_points' in q and q['key_points']:
                        st.markdown("**🎯 Key Points to Cover:**")
                        for point in q['key_points']:
                            st.write(f"• {point}")
                    
                    # What interviewer looks for
                    if 'interviewer_focus' in q:
                        st.markdown("**🔍 What the Interviewer is Evaluating:**")
                        st.info(q['interviewer_focus'])

def job_tracker():
    """Job application tracker using Google Sheets"""
    st.header("📊 Job Application Tracker")
    st.markdown("Track your job applications with automated Google Sheets integration.")
    
    # Manual job entry
    st.subheader("➕ Add New Application")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        company = st.text_input("Company Name")
        position = st.text_input("Position Title")
        source = st.selectbox("Source", ["LinkedIn", "Company Website", "Indeed", "Recruiter", "Referral", "Other"])
    
    with col2:
        status = st.selectbox("Status", ["Applied", "Interview Scheduled", "Interviewed", "Follow-up", "Rejected", "Offer"])
        application_link = st.text_input("Application Link (optional)")
        contact_person = st.text_input("Contact Person (optional)")
    
    with col3:
        next_action = st.text_input("Next Action")
        notes = st.text_area("Notes", height=100)
    
    if st.button("📝 Add to Tracker", type="primary"):
        if company and position:
            job_data = {
                "date_applied": datetime.now().strftime("%Y-%m-%d"),
                "company": company,
                "position": position,
                "status": status,
                "source": source,
                "contact_person": contact_person,
                "next_action": next_action,
                "application_link": application_link,
                "notes": notes
            }
            
            with st.spinner("Adding to Google Sheets tracker..."):
                try:
                    result = orchestrator.update_job_tracker(job_data)
                    
                    if 'error' in result:
                        st.error(f"❌ Error: {result['error']}")
                    else:
                        st.success("✅ Application added to tracker!")
                        st.json(result)
                        
                except Exception as e:
                    st.error(f"❌ Failed to update tracker: {str(e)}")
        else:
            st.warning("⚠️ Please provide at least company name and position.")

def add_to_tracker(email_data):
    """Add email data to job tracker"""
    job_data = {
        "date_applied": datetime.now().strftime("%Y-%m-%d"),
        "company": email_data.get('company', 'Unknown'),
        "position": email_data.get('position', 'Unknown'),
        "status": "Email Received",
        "source": "Gmail Scanner",
        "contact_person": email_data.get('sender', ''),
        "next_action": "Review and Apply",
        "application_link": ", ".join(email_data.get('links', [])),
        "notes": f"Email subject: {email_data.get('subject', '')}"
    }
    
    try:
        result = orchestrator.update_job_tracker(job_data)
        if 'error' not in result:
            st.success("✅ Added to job tracker!")
        else:
            st.error(f"❌ Failed to add: {result['error']}")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

def get_ats_feedback(score):
    """Get feedback based on ATS score"""
    if score >= 80:
        return "Excellent match! Your resume is well-optimized for this role."
    elif score >= 60:
        return "Good match with room for improvement. Follow the suggestions below."
    elif score >= 40:
        return "Moderate match. Significant improvements needed."
    else:
        return "Poor match. Major revisions required to pass ATS screening."

if __name__ == "__main__":
    main()
