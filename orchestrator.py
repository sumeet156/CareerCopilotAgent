"""
Career Copilot Agent - Main Orchestrator
Uses official Portia SDK patterns with DefaultToolRegistry for cloud tools
"""
from dotenv import load_dotenv
from portia import Portia, Config, DefaultToolRegistry, LLMProvider
from portia.config import StorageClass, LogLevel
import logging
import os

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CareerCopilotOrchestrator:
    """Main orchestrator for Career Copilot using DefaultToolRegistry for cloud tools"""
    
    def __init__(self):
        self.config = self._create_config()
        # Use DefaultToolRegistry which includes both open source and cloud tools
        try:
            self.tool_registry = DefaultToolRegistry(config=self.config)
            logger.info(f"✅ DefaultToolRegistry created with config")
        except Exception as e:
            logger.error(f"❌ Failed to create DefaultToolRegistry: {e}")
            # Fallback to no tools
            self.tool_registry = []
            
        self.portia = Portia(
            config=self.config,
            tools=self.tool_registry
        )
        logger.info("✅ Career Copilot Orchestrator initialized with DefaultToolRegistry + Google Gemini")
    
    def _create_config(self):
        """Create Portia config following official documentation with Google Gemini"""
        # Use official Config.from_default() method with Google Gemini
        config = Config.from_default(
            # Use Google Gemini instead of OpenAI (quota exceeded)
            llm_provider=LLMProvider.GOOGLE,
            default_model="google/gemini-1.5-flash",
            # Use cloud storage if Portia API key is available
            storage_class=StorageClass.CLOUD if os.getenv('PORTIA_API_KEY') else StorageClass.MEMORY,
            # Debug logging for detailed output
            default_log_level=LogLevel.DEBUG if os.getenv('PORTIA_API_KEY') else LogLevel.INFO
        )
        
        return config
    
    def get_available_tools(self):
        """List all available tools from the registry"""
        try:
            if hasattr(self.tool_registry, 'tools'):
                tools = list(self.tool_registry.tools)
            elif hasattr(self.tool_registry, '__iter__'):
                tools = list(self.tool_registry)
            else:
                tools = []
                
            tool_info = []
            for tool in tools:
                try:
                    tool_info.append({
                        'id': getattr(tool, 'id', str(tool)),
                        'name': getattr(tool, 'name', str(tool)),
                        'description': getattr(tool, 'description', 'No description')[:100] + '...' if len(getattr(tool, 'description', '')) > 100 else getattr(tool, 'description', 'No description')
                    })
                except Exception as e:
                    logger.error(f"Error processing tool {tool}: {e}")
                    
            logger.info(f"Found {len(tool_info)} tools")
            return tool_info
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return []
    
    def analyze_resume_and_job(self, resume_text: str, job_description: str, user_profile: dict = None) -> dict:
        """
        Analyze resume against job description and provide tailoring suggestions
        """
        prompt = f"""
        You are an expert ATS resume optimizer and career advisor. 

        USER PROFILE: {user_profile or 'Not provided'}
        
        RESUME TEXT:
        {resume_text}
        
        JOB DESCRIPTION:
        {job_description}
        
        Please perform the following analysis:
        1. Extract key skills and technologies from the resume
        2. Identify important keywords and requirements from the job description
        3. Calculate an ATS compatibility score (0-100)
        4. Provide 8-10 specific bullet point improvements for the resume
        5. Suggest a tailored professional summary (3-4 lines)
        6. Highlight any gaps that need to be addressed
        
        Return your response in this JSON format:
        {{
            "ats_score": <number>,
            "resume_skills": [<list of skills>],
            "job_keywords": [<list of keywords>],
            "improvements": [<list of specific bullet point suggestions>],
            "tailored_summary": "<professional summary>",
            "skill_gaps": [<list of missing skills>],
            "recommendations": [<list of action items>]
        }}
        """
        
        try:
            result = self.portia.run(prompt)
            return result.run()
        except Exception as e:
            logger.error(f"Resume analysis failed: {e}")
            return {"error": str(e)}
    
    def generate_interview_questions(self, job_description: str, user_profile: dict = None) -> dict:
        """
        Generate comprehensive interview Q&A for the role
        """
        prompt = f"""
        You are an expert interview coach and hiring manager.
        
        USER PROFILE: {user_profile or 'Not provided'}
        
        JOB DESCRIPTION:
        {job_description}
        
        Generate 10-12 comprehensive interview questions with detailed answers:
        
        Include:
        - 3-4 behavioral questions (STAR method answers)
        - 3-4 technical questions (specific to the role)
        - 2-3 system design or problem-solving questions
        - 2 situational questions
        
        For each question, provide:
        - The question
        - A detailed sample answer
        - Key points to cover
        - What the interviewer is looking for
        
        Return in this JSON format:
        {{
            "interview_prep": [
                {{
                    "category": "<behavioral/technical/system_design/situational>",
                    "question": "<question>",
                    "sample_answer": "<detailed answer>",
                    "key_points": [<list of key points>],
                    "interviewer_focus": "<what they're evaluating>"
                }}
            ]
        }}
        """
        
        try:
            result = self.portia.run(prompt)
            return result.run()
        except Exception as e:
            logger.error(f"Interview prep generation failed: {e}")
            return {"error": str(e)}
    
    def fetch_job_emails(self) -> dict:
        """
        Use Portia's Gmail tool to fetch job-related emails
        """
        prompt = """
        Use the Gmail tool to search for recent emails related to job opportunities, recruiters, and career-related messages.
        
        Search criteria:
        - Look for emails from the last 30 days
        - Keywords: job, opportunity, interview, hiring, recruiter, position, career, application
        - From domains commonly used by recruiters (linkedin.com, indeed.com, etc.)
        
        For each relevant email, extract:
        - Sender name and email
        - Subject line
        - Date received
        - Company name (if mentioned)
        - Job title/position (if mentioned)
        - Any links to job postings
        - Application deadlines (if mentioned)
        
        Return in this JSON format:
        {{
            "job_emails": [
                {{
                    "sender": "<name and email>",
                    "subject": "<subject>",
                    "date": "<date>",
                    "company": "<company name>",
                    "position": "<job title>",
                    "links": [<job posting links>],
                    "deadline": "<application deadline>",
                    "priority": "<high/medium/low>"
                }}
            ],
            "summary": {{
                "total_emails": <count>,
                "high_priority": <count>,
                "companies": [<unique companies>]
            }}
        }}
        """
        
        try:
            result = self.portia.run(prompt)
            return result.run()
        except Exception as e:
            logger.error(f"Gmail fetch failed: {e}")
            return {"error": str(e)}
    
    def update_job_tracker(self, job_data: dict) -> dict:
        """
        Use Portia's Google Sheets tool to update job application tracker
        """
        prompt = f"""
        Use the Google Sheets tool to update a job application tracker spreadsheet.
        
        Spreadsheet details:
        - Name: "Career Copilot Job Tracker"
        - Sheet: "Applications"
        
        If the spreadsheet doesn't exist, create it with these columns:
        - Date Applied
        - Company
        - Position
        - Status
        - Source
        - Contact Person
        - Next Action
        - Application Link
        - Notes
        
        Add or update this job application:
        {job_data}
        
        Return confirmation of the update including the row number and spreadsheet link.
        """
        
        try:
            result = self.portia.run(prompt)
            return result.run()
        except Exception as e:
            logger.error(f"Google Sheets update failed: {e}")
            return {"error": str(e)}

# Global orchestrator instance
orchestrator = CareerCopilotOrchestrator()
