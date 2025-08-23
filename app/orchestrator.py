import os
import json
from dotenv import load_dotenv
from portia import Portia, DefaultToolRegistry
from config import config
from portia.cli import CLIExecutionHooks
from portia import Config, StorageClass, LogLevel, LLMProvider

load_dotenv()

# Build Portia using centralized config (OpenAI first, Gemini fallback)
cfg = config.portia_config

# Use DefaultToolRegistry with config as recommended
tools = DefaultToolRegistry(config=cfg)

# Optionally, add your own Python helpers as tools too:
try:
    from tools.ats_scoring import ats_score
    from tools.jd_parser import normalize_jd
    from tools.resume_parser import extract_resume_text
    if hasattr(tools, "add_tool"):
        tools.add_tool(ats_score)
        tools.add_tool(normalize_jd)
        tools.add_tool(extract_resume_text)
        print("Custom tools added successfully via add_tool")
except Exception as e:
    print(f"Error adding custom tools: {e}")

portia = Portia(config=cfg, tools=tools, execution_hooks=CLIExecutionHooks())

class CareerCopilotOrchestrator:
    def _serialize_if_needed(self, value):
        """Serialize dict or list to JSON string; pass through strings and other types."""
        if isinstance(value, (dict, list)):
            try:
                return json.dumps(value, ensure_ascii=False)
            except Exception:
                return str(value)
        return value
    def __init__(self):
        self.portia = portia
        self.tools = tools

    def get_available_tools(self):
        """Get list of available tools"""
        try:
            # Try list_tools()
            if hasattr(self.tools, "list_tools"):
                try:
                    result = self.tools.list_tools()
                    tools_list = []
                    if isinstance(result, dict) and "tools" in result:
                        raw = result.get("tools", [])
                    else:
                        raw = result if isinstance(result, list) else []
                    for t in raw:
                        if isinstance(t, dict):
                            tools_list.append({
                                "id": t.get("id") or t.get("name") or str(t),
                                "name": t.get("name") or t.get("id") or str(t),
                            })
                        else:
                            tools_list.append({"id": str(t), "name": str(t)})
                    if tools_list:
                        return tools_list
                except Exception:
                    pass
            # Try .tools attribute (list or dict)
            if hasattr(self.tools, "tools"):
                raw = getattr(self.tools, "tools")
                tools_list = []
                if isinstance(raw, dict):
                    for k, v in raw.items():
                        tools_list.append({
                            "id": getattr(v, "id", k) or k,
                            "name": getattr(v, "name", k) or k,
                        })
                elif isinstance(raw, list):
                    for v in raw:
                        name = getattr(v, "name", None) or getattr(v, "tool_name", None) or v.__class__.__name__
                        tid = getattr(v, "id", None) or name
                        tools_list.append({"id": tid, "name": name})
                if tools_list:
                    return tools_list
            return []
        except Exception as e:
            print(f"Error getting tools: {e}")
            return []
            
    def execute_task(self, task_description):
        """Execute a career-related task"""
        try:
            full_task = f"{CAREER_TASK}\n\nUser request: {self._serialize_if_needed(task_description)}"
            plan = self.portia.run(full_task)
            # Execute the plan so tools run and OAuth prompts appear in terminal if needed
            result = plan.run()
            return self._serialize_if_needed(result)
        except Exception as e:
            if _is_openai_quota_error(e):
                return self._retry_with_gemini(full_task)
            print(f"Error executing task: {e}")
            return f"Error: {str(e)}"

    def gmail_to_sheets(self, sheet_id: str, sheet_tab: str = "Applications"):
        """End-to-end: scan Gmail for job leads and write structured rows to Google Sheet.

        This triggers Portia's OAuth flows in the terminal when permissions are needed.
        """
        prompt = f"""
        You are the Career Copilot Orchestrator.
        Task: Scan Gmail for job or recruiter emails in the last 30 days. For each relevant email, extract:
        [date, company, role, source, url, deadline?].
        Then append or upsert rows into Google Sheet with id '{sheet_id}' and tab '{sheet_tab}'.
        Use Gmail and Google Sheets tools. If OAuth is needed, initiate it.
        Be idempotent: avoid duplicate entries by checking date+company+role.
        Return a concise summary: total scanned, matched, and rows written.
        """
        try:
            plan = self.portia.run(self._serialize_if_needed(prompt))
            result = plan.run()
            return self._serialize_if_needed(result)
        except Exception as e:
            if _is_openai_quota_error(e):
                return self._retry_with_gemini(self._serialize_if_needed(prompt))
            raise

    def analyze_resume_and_job(self, resume_text: str, job_description: str, user_profile: dict | None = None) -> dict:
        """Simple, error-free resume optimization: ATS score + suggestions only."""
        result = {}
        try:
            # 1. ATS score
            prompt_ats = f"Rate the following resume for the given job description on a scale of 0 to 100.\nResume:\n{resume_text}\nJob Description:\n{job_description}\nReturn only the score as a number."
            out_ats = self.portia.run(self._serialize_if_needed(prompt_ats))
            ats_score = self._extract_simple_output(out_ats)
            result['ats_score'] = int(ats_score) if str(ats_score).isdigit() else ats_score

            # 2. Suggestions
            prompt_suggestions = f"Suggest 5-10 improvements to the resume to better match the job description.\nResume:\n{resume_text}\nJob Description:\n{job_description}\nReturn a numbered list."
            out_suggestions = self.portia.run(self._serialize_if_needed(prompt_suggestions))
            suggestions = self._extract_simple_output(out_suggestions)
            result['suggestions'] = suggestions

            return result
        except Exception as e:
            return {"error": str(e)}

    def _extract_simple_output(self, out):
        """Helper to extract string output from Portia tool result."""
        if hasattr(out, 'output'):
            out = out.output
        out = self._serialize_if_needed(out)
        if isinstance(out, dict):
            val = out.get("value", out)
            if isinstance(val, str):
                return val.strip()
            return str(val)
        if isinstance(out, str):
            return out.strip()
        return str(out)

    def generate_interview_questions(self, job_description: str, user_profile: dict | None = None) -> dict:
        """Generate 10-12 interview Q&A tailored to the role and profile. Always return a valid JSON array."""
        profile = self._serialize_if_needed(user_profile or {})
        prompt = f"""
        You are an expert interview coach. Create 10-12 interview questions and sample answers based on the provided user profile and job description.

        USER PROFILE: {profile}
        JOB DESCRIPTION:
        {job_description}

        Your response MUST be a single, valid JSON object containing a single key "interview_prep", which is an array of question objects. Do not include any other text, greetings, or explanations before or after the JSON.
        Each object in the "interview_prep" array must have the following keys: "category", "question", "sample_answer", "key_points", "interviewer_focus".

        Example format:
        {{"interview_prep": [{{"category": "technical", "question": "...", "sample_answer": "...", "key_points": [], "interviewer_focus": "..."}}]}}
        """
        try:
            raw_output = self.portia.run(prompt)
            output_data = self._extract_simple_output(raw_output)

            if isinstance(output_data, str):
                json_start_index = output_data.find('{')
                if json_start_index == -1:
                    return {"error": "Agent returned a non-JSON response.", "raw": output_data}
                
                json_end_index = output_data.rfind('}') + 1
                if json_end_index == 0:
                     return {"error": "Agent returned an incomplete JSON response.", "raw": output_data}

                clean_json_str = output_data[json_start_index:json_end_index]
                
                try:
                    data = json.loads(clean_json_str)
                except json.JSONDecodeError:
                    return {"error": "Agent returned a malformed JSON string after cleaning.", "raw": clean_json_str}
            elif isinstance(output_data, dict):
                data = output_data
            else:
                 return {"error": "Agent returned an unexpected data type.", "raw": str(output_data)}

            if isinstance(data, dict) and "interview_prep" in data and isinstance(data["interview_prep"], list):
                return {"interview_prep": data["interview_prep"]}
            else:
                return {"error": "Agent did not return a valid 'interview_prep' array inside a JSON object.", "raw": data}

        except Exception as e:
            return {"error": str(e)}

    def update_job_tracker(self, job_data: dict, sheet_id: str | None = None, sheet_tab: str | None = None) -> dict:
        """Append one application row to Google Sheets via Portia Sheets tool. Always serialize row as JSON string and force output to be a JSON string."""
        sid = sheet_id or os.getenv("SHEET_ID", "")
        stab = sheet_tab or os.getenv("SHEET_TAB", "Applications")
        if not sid:
            return {"error": "Missing SHEET_ID (env or argument)."}
        # Convert job_data to a flat list of values for Sheets tool
        row_values = [job_data.get(k, "") for k in [
            "date_applied", "company", "position", "status", "source", "contact_person", "next_action", "application_link", "notes"
        ]]
        import json
        row_json = json.dumps(row_values, ensure_ascii=False)
        prompt = f"""
        Using the Google Sheets tool, append this job application row to spreadsheet id '{sid}', tab '{stab}'.
        Ensure headers exist; create if needed. Avoid duplicates based on (date_applied, company, position).
        Row: {row_json}
        Return ONLY a valid JSON string with keys: success (bool), row_count_appended (int), message (str). Do not return any other text or explanation.
        """
        try:
            out = self.portia.run(self._serialize_if_needed(prompt))
            if hasattr(out, 'output'):
                out = out.output
            out = self._serialize_if_needed(out)
            # Always parse output as JSON string
            if isinstance(out, str):
                try:
                    return json.loads(out)
                except Exception:
                    return {"raw": out}
            if isinstance(out, dict):
                val = out.get("value", out)
                if isinstance(val, str):
                    try:
                        return json.loads(val)
                    except Exception:
                        return {"raw": val}
                return val
            return {"raw": out}
        except Exception as e:
            return {"error": str(e)}
# ...existing code...
def _is_openai_quota_error(err: Exception) -> bool:
    msg = str(err).lower()
    return (
        "rate limit" in msg
        or "insufficient_quota" in msg
        or "error code: 429" in msg
        or "you exceeded your current quota" in msg
    )


CAREER_TASK = """
You are the Career Copilot Orchestrator. Capabilities:
1) Gmail → parse job/recruiter mails → JSON rows: [date, company, role, source, url, deadline?].
2) Append/update to Google Sheet 'Career Copilot Tracker' tab 'Applications'.
3) Tailor resume to a JD: extract resume skills, parse JD keywords, compute ATS score, propose 5–10 edits + a targeted summary.
4) Interview prep: generate 8–12 Q&A grounded in the user's bio/skills + the JD.

IMPORTANT: For every step in a multi-step plan, before passing any output to a tool, always serialize dicts/lists to a JSON string. Never pass a Python dict or object directly; always convert to a string. This applies to all intermediate outputs, not just the initial input.

Pause and ask clarifications when anything is missing (OAuth, Sheet not found, user profile).
"""


def run_orchestrator(prompt: str):
    plan = portia.run(prompt or CAREER_TASK)
    return plan.run()