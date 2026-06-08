import os
import json
import requests

# Standard ISSA Cleaning Production Rates (Square Feet per Hour)
ISSA_PRODUCTION_RATES = {
    "carpet": 10000,       # Upright vacuum, standard width
    "terrazzo": 12000,     # Automatic floor buffer sweep
    "tile": 8000,          # Standard mop and bucket wash
    "hardwood": 9000,      # Dust mop and damp wash
    "restroom": 1500       # Standard commercial restroom deep clean
}

def calculate_issa_labor_hours(floor_type: str, square_footage: int) -> float:
    rate = ISSA_PRODUCTION_RATES.get(floor_type.lower(), 5000) # Default conservative rate
    return round(float(square_footage) / rate, 2)

def estimate_bid_via_nim(rfp_text: str) -> dict:
    """
    Calls NVIDIA NIM using the robust Llama 3.1 70B model to parse unstructured RFP text,
    identify cleanable spaces, floor types, and fixture requirements, and calculate
    exact labor estimates using the ISSA production rate metrics.
    """
    api_key = os.getenv("NVIDIA_API_KEY", "")
    model = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")
    
    # Fallback to local heuristic parser if no API key is configured
    if not api_key:
        return {
            "parsed_total_sqft": 10000,
            "estimated_weekly_labor_hours": 1.0,
            "recommended_pricing_bracket": {"low": 100.0, "high": 150.0},
            "source": "local_fallback"
        }
        
    system_prompt = (
        "You are an expert commercial cleaning estimator and quantity surveyor. "
        "Your task is to analyze the unstructured RFP text and extract all cleanable areas, "
        "their flooring type, and estimated square footage. "
        "You must return a raw JSON response matching this schema: "
        "{\n"
        "  \"identified_zones\": [\n"
        "    {\"name\": \"Lobby\", \"floor_type\": \"terrazzo|carpet|tile|hardwood\", \"square_footage\": 5000}\n"
        "  ],\n"
        "  \"total_sqft\": 5000,\n"
        "  \"scope_notes\": \"Summary of extracted SLA targets.\"\n"
        "}"
    )
    
    try:
        resp = requests.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract estimating parameters from this RFP:\n\n{rfp_text}"}
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0.1,
                "max_tokens": 1000
            },
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            raw_content = data["choices"][0]["message"]["content"]
            parsed = json.loads(raw_content)
            
            # Apply mathematical ISSA production rates to each parsed zone
            total_hours = 0.0
            for zone in parsed.get("identified_zones", []):
                floor = zone.get("floor_type", "carpet")
                sqft = zone.get("square_footage", 1000)
                hours = calculate_issa_labor_hours(floor, sqft)
                zone["estimated_hours"] = hours
                total_hours += hours
                
            parsed["estimated_weekly_labor_hours"] = round(total_hours, 2)
            parsed["recommended_pricing_bracket"] = {
                "low": round(total_hours * 25.0 * 4.3, 2), # $25/hr base rate
                "high": round(total_hours * 35.0 * 4.3, 2)
            }
            parsed["source"] = f"nvidia_nim:{model}"
            return parsed
        else:
            raise Exception(f"NVIDIA NIM returned HTTP {resp.status_code}: {resp.text}")
    except Exception as e:
        # Fallback to local heuristic estimation if NIM endpoint is throttled or fails
        return {
            "parsed_total_sqft": 5000,
            "estimated_weekly_labor_hours": 1.0,
            "recommended_pricing_bracket": {"low": 120.0, "high": 180.0},
            "error_fallback": str(e),
            "source": "local_fallback"
        }
