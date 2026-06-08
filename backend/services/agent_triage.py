import os
import json
import requests
import subprocess

def triage_field_anomaly(raw_text: str) -> dict:
    """
    Invokes the 'Concierge' Agent using Llama 3.1 70B on NVIDIA NIM to analyze a raw
    field report, determine situational severity, assign it to a specialized agent from AGENTS.md,
    and formulate a real-world ticket payload.
    """
    api_key = os.getenv("NVIDIA_API_KEY", "")
    model = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")

    if not api_key:
        return {
            "issue": raw_text,
            "severity": "medium",
            "assigned_agent": "Concierge",
            "reasoning": "API key missing. Default fallback triage.",
            "immediate_action": "Review manually",
            "github_issue_created": False
        }

    system_prompt = (
        "You are 'The Concierge', the client intake and front-line support agent for the Atlas Pre-Construction & Maintenance Agency. "
        "Your task is to analyze raw, unstructured field anomalies sent by on-site workers (sometimes in Spanish or broken English). "
        "You must:\n"
        "1. Identify the core physical/operational issue.\n"
        "2. Assess operational severity: 'low' (cosmetic), 'medium' (needs attention within 24h), 'high' (halts operations/SLA breach risks).\n"
        "3. Delegate to the correct internal department from AGENTS.md:\n"
        "   - 'Tech Lead' (for hardware failure, machinery breakdowns, plumbing, or structural repairs)\n"
        "   - 'Concierge' (for standard janitorial refills, sanitation alerts, access issues, scheduling errors)\n"
        "4. Write a concise, professional reasoning statement explaining why you triaged it this way.\n"
        "5. Formulate a short, descriptive title for a GitHub maintenance issue.\n\n"
        "You must respond ONLY with a raw JSON object matching this schema:\n"
        "{\n"
        "  \"detected_issue\": \"Brief description in English\",\n"
        "  \"severity\": \"low|medium|high\",\n"
        "  \"assigned_agent\": \"Tech Lead|Concierge\",\n"
        "  \"reasoning\": \"One-sentence explanation of your triage logic\",\n"
        "  \"github_issue_title\": \"[MAINTENANCE] Title description\"\n"
        "}"
    )

    try:
        resp = requests.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Field Message: \"{raw_text}\""}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.1,
                "max_tokens": 500
            },
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=15
        )

        if resp.status_code == 200:
            data = resp.json()
            raw_content = data["choices"][0]["message"]["content"]
            parsed = json.loads(raw_content)
            
            # If severity is high, let's programmatically trigger a real GitHub issue creation!
            issue_created = False
            issue_url = None
            if parsed.get("severity") == "high":
                issue_title = parsed.get("github_issue_title", f"[MAINTENANCE] Field Anomaly: {parsed.get('detected_issue')}")
                issue_body = (
                    f"### 🚨 High Severity Field Anomaly Triaged by The Concierge Agent\n\n"
                    f"- **Worker Report:** \"{raw_text}\"\n"
                    f"- **Detected Issue:** {parsed.get('detected_issue')}\n"
                    f"- **Assigned Department:** {parsed.get('assigned_agent')}\n"
                    f"- **Triage Reasoning:** {parsed.get('reasoning')}\n\n"
                    f"Please inspect the WSL server database and schedule physical crew response immediately."
                )
                
                try:
                    # Execute gh issue create command using local terminal context
                    cmd = ["gh", "issue", "create", "--repo", "kyzltrade-cpu/terra", "--title", issue_title, "--body", issue_body]
                    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    # Extract the issue URL from stdout
                    out_lines = proc.stdout.splitlines()
                    if out_lines:
                        issue_url = out_lines[-1].strip()
                        issue_created = True
                except Exception as gh_err:
                    print(f"Failed to create GitHub issue: {gh_err}")

            parsed["github_issue_created"] = issue_created
            parsed["github_issue_url"] = issue_url
            return parsed
        else:
            raise Exception(f"NVIDIA NIM HTTP {resp.status_code}")
    except Exception as e:
        return {
            "detected_issue": raw_text,
            "severity": "medium",
            "assigned_agent": "Concierge",
            "reasoning": f"NVIDIA NIM parsing fallback due to: {str(e)}",
            "github_issue_title": f"[MAINTENANCE] {raw_text}",
            "github_issue_created": False
        }
