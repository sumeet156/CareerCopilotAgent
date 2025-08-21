import os
import json
from dotenv import load_dotenv
from portia import Portia
from config import config
from portia.cli import CLIExecutionHooks
from portia import Config, StorageClass, LogLevel, LLMProvider

# Try to import a cloud DefaultToolRegistry; fall back to open-source registry if unavailable
DefaultToolRegistry = None  # type: ignore
for modpath, name in (
    ("portia.tools", "DefaultToolRegistry"),
    ("portia.cloud_tools.registry", "DefaultToolRegistry"),
    ("portia.cloud_tools.registry", "PortiaToolRegistry"),
):
    try:
        module = __import__(modpath, fromlist=[name])
        DefaultToolRegistry = getattr(module, name)
        break
    except Exception:
        continue

load_dotenv()

# Build Portia using centralized config (OpenAI first, Gemini fallback)
cfg = config.portia_config

# Use DefaultToolRegistry for better tool loading; fall back to open-source registry or empty
try:
    if DefaultToolRegistry is None:
        raise ImportError("DefaultToolRegistry not available; falling back to open_source_tool_registry")
    # Some versions accept config, some do not
    try:
        tools = DefaultToolRegistry()
    except TypeError:
        try:
            tools = DefaultToolRegistry(config=cfg)
        except TypeError:
            tools = DefaultToolRegistry(cfg)
    print("DefaultToolRegistry created successfully")
except Exception as e:
    print(f"Error creating DefaultToolRegistry: {e}")
    # Prefer letting Portia manage cloud tools from your account by not passing a registry
    tools = None
    print("Falling back to Portia-managed cloud tools (tools=None). Ensure tools are enabled in your Portia dashboard.")

# Optionally, add your own Python helpers as tools too:
try:
    from tools.ats_scoring import ats_score
    from tools.jd_parser import normalize_jd
    from tools.resume_parser import extract_resume_text
    if tools is not None and hasattr(tools, "add_tool"):
        tools.add_tool(ats_score)
        tools.add_tool(normalize_jd)
        tools.add_tool(extract_resume_text)
        print("Custom tools added successfully via add_tool")
    else:
        # When tools=None, Portia cloud tools are used; skip local additions
        print("Custom tools skipped (using cloud tools or unsupported registry API)")
except Exception as e:
    print(f"Error adding custom tools: {e}")

portia = Portia(config=cfg, tools=tools, execution_hooks=CLIExecutionHooks())


class CareerCopilotOrchestrator:
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
            full_task = f"{CAREER_TASK}\n\nUser request: {task_description}"
            plan = self.portia.run(full_task)
            # Execute the plan so tools run and OAuth prompts appear in terminal if needed
            return plan.run()
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
            plan = self.portia.run(prompt)
            return plan.run()
        except Exception as e:
            if _is_openai_quota_error(e):
                return self._retry_with_gemini(prompt)
            raise

    def analyze_resume_and_job(self, resume_text: str, job_description: str, user_profile: dict | None = None) -> dict:
        """Analyze resume vs JD and return structured JSON with ATS score and suggestions."""
        profile = json.dumps(user_profile or {}, ensure_ascii=False)
        prompt = f"""
        You are an expert ATS optimizer.
        USER PROFILE: {profile}
        RESUME TEXT:\n{resume_text}
        JOB DESCRIPTION:\n{job_description}

        Perform:
        - Extract resume skills
        - Extract JD keywords
        - ATS score 0-100
        - 8-10 improvements
        - Tailored 3-4 line summary
        - Skill gaps and recommendations

        Return valid JSON only with keys: ats_score, resume_skills, job_keywords, improvements, tailored_summary, skill_gaps, recommendations.
        """
        try:
            out = self.portia.run(prompt).run()
            if isinstance(out, dict):
                # Some Portia tools wrap output in {"value": ...}
                val = out.get("value", out)
                if isinstance(val, str):
                    try:
                        return json.loads(val)
                    except Exception:
                        return {"raw": val}
                return val
            if isinstance(out, str):
                try:
                    return json.loads(out)
                except Exception:
                    return {"raw": out}
            return {"raw": out}
        except Exception as e:
            if _is_openai_quota_error(e):
                try:
                    out = self._retry_with_gemini(prompt)
                    if isinstance(out, dict):
                        val = out.get("value", out)
                        if isinstance(val, str):
                            try:
                                return json.loads(val)
                            except Exception:
                                return {"raw": val}
                        return val
                    if isinstance(out, str):
                        try:
                            return json.loads(out)
                        except Exception:
                            return {"raw": out}
                    return {"raw": out}
                except Exception as ee:
                    return {"error": str(ee)}
            return {"error": str(e)}

    def generate_interview_questions(self, job_description: str, user_profile: dict | None = None) -> dict:
        """Generate 10-12 interview Q&A tailored to the role and profile."""
        profile = json.dumps(user_profile or {}, ensure_ascii=False)
        prompt = f"""
        Create 10-12 interview Q&A tailored to the following role and profile.
        USER PROFILE: {profile}
        JOB DESCRIPTION:\n{job_description}

        Provide a JSON array named interview_prep where each item has:
        - category (behavioral|technical|system design|other)
        - question
        - sample_answer
        - key_points (array)
        - interviewer_focus
        Return JSON only.
        """
        try:
            out = self.portia.run(prompt).run()
            if isinstance(out, dict):
                val = out.get("value", out)
                if isinstance(val, str):
                    try:
                        data = json.loads(val)
                    except Exception:
                        data = {"raw": val}
                else:
                    data = val
            elif isinstance(out, str):
                try:
                    data = json.loads(out)
                except Exception:
                    data = {"raw": out}
            else:
                data = {"raw": out}

            # Normalize to {"interview_prep": [...]}
            if isinstance(data, dict) and "interview_prep" in data:
                return {"interview_prep": data["interview_prep"]}
            if isinstance(data, list):
                return {"interview_prep": data}
            return data
        except Exception as e:
            if _is_openai_quota_error(e):
                try:
                    out = self._retry_with_gemini(prompt)
                    if isinstance(out, dict):
                        val = out.get("value", out)
                        if isinstance(val, str):
                            try:
                                data = json.loads(val)
                            except Exception:
                                data = {"raw": val}
                        else:
                            data = val
                    elif isinstance(out, str):
                        try:
                            data = json.loads(out)
                        except Exception:
                            data = {"raw": out}
                    else:
                        data = {"raw": out}
                    if isinstance(data, dict) and "interview_prep" in data:
                        return {"interview_prep": data["interview_prep"]}
                    if isinstance(data, list):
                        return {"interview_prep": data}
                    return data
                except Exception as ee:
                    return {"error": str(ee)}
            return {"error": str(e)}

    def update_job_tracker(self, job_data: dict, sheet_id: str | None = None, sheet_tab: str | None = None) -> dict:
        """Append one application row to Google Sheets via Portia Sheets tool."""
        sid = sheet_id or os.getenv("SHEET_ID", "")
        stab = sheet_tab or os.getenv("SHEET_TAB", "Applications")
        if not sid:
            return {"error": "Missing SHEET_ID (env or argument)."}
        payload = json.dumps(job_data, ensure_ascii=False)
        prompt = f"""
        Using the Google Sheets tool, append this job application row to spreadsheet id '{sid}', tab '{stab}'.
        Ensure headers exist; create if needed. Avoid duplicates based on (date_applied, company, position).
        Row JSON: {payload}
        Return a summary JSON with keys: success (bool), row_count_appended (int), message (str).
        """
        try:
            out = self.portia.run(prompt).run()
            if isinstance(out, dict):
                return out.get("value", out)
            if isinstance(out, str):
                try:
                    return json.loads(out)
                except Exception:
                    return {"raw": out}
            return {"raw": out}
        except Exception as e:
            if _is_openai_quota_error(e):
                try:
                    out = self._retry_with_gemini(prompt)
                    if isinstance(out, dict):
                        return out.get("value", out)
                    if isinstance(out, str):
                        try:
                            return json.loads(out)
                        except Exception:
                            return {"raw": out}
                    return {"raw": out}
                except Exception as ee:
                    return {"error": str(ee)}
            return {"error": str(e)}

    def _retry_with_gemini(self, prompt: str):
        """Rebuild Portia with Gemini and retry the same prompt; returns plan.run() output."""
        print("OpenAI quota/rate limit encountered. Falling back to Google Gemini and retrying...")
        gemini_cfg = Config.from_default(
            llm_provider=LLMProvider.GOOGLE,
            default_model="google/gemini-1.5-flash",
            storage_class=StorageClass.CLOUD if os.getenv("PORTIA_API_KEY") else StorageClass.MEMORY,
            default_log_level=LogLevel.DEBUG if os.getenv("PORTIA_API_KEY") else LogLevel.INFO,
        )
        self.portia = Portia(config=gemini_cfg, tools=self.tools, execution_hooks=CLIExecutionHooks())
        return self.portia.run(prompt).run()


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
Pause and ask clarifications when anything is missing (OAuth, Sheet not found, user profile).
"""


def run_orchestrator(prompt: str):
    plan = portia.run(prompt or CAREER_TASK)
    return plan.run()