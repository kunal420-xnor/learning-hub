import ollama
import json
import re

def qualify_lead(lead):
    prompt = f"""
You are a real estate lead qualification assistant.

Analyze this lead and respond ONLY with a JSON object like this:
{{"status": "HOT/WARM/COLD", "score": 1-10, "reason": "one sentence explanation", "next_action": "what the agent should do next"}}

Lead details:
- Name: {lead['name']}
- Budget: ₹{lead['budget']:,}
- Location interest: {lead['location']}
- Intent: {lead['intent']}
- Timeline: {lead['timeline']}

Respond with JSON only. No extra text.
"""
    response = ollama.chat(
        model="gemma3:1b",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response["message"]["content"]

    # extract JSON even if model adds extra text
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    return {"error": "could not parse response", "raw": raw}

leads = [
    {"name": "Rahul Sharma", "budget": 8000000, "location": "Delhi", "intent": "buy", "timeline": "within 1 month"},
    {"name": "Priya Mehta", "budget": 1500000, "location": "Jaipur", "intent": "rent", "timeline": "no rush"},
    {"name": "Amit Verma", "budget": 4000000, "location": "Mumbai", "intent": "invest", "timeline": "3 months"},
]

print("\n====== LEAD QUALIFICATION REPORT ======")
for lead in leads:
    result = qualify_lead(lead)
    status = result.get("status", "N/A")
    score = result.get("score", "N/A")
    reason = result.get("reason", "N/A")
    action = result.get("next_action", "N/A")

    print(f"""
Name:        {lead['name']}
Status:      {status}
Score:       {score}/10
Reason:      {reason}
Next Action: {action}
{"─"*40}""")
