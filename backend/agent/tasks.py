import json
import re
from browser_use import Agent, ChatGoogle
from browser_use.llm.messages import UserMessage
from backend.agent.prompts import HUNTER_PROMPT, SYNTHESIZER_PROMPT

def get_llm():
    """Returns the browser-use specific wrapper."""
    return ChatGoogle(
        model='gemini-3-flash-preview',
        temperature=0.0  # Forces robotic, strict JSON formatting
    )

def extract_json_from_text(text: str) -> dict:
    """Bulletproof JSON extraction using Regex."""
    text = str(text)
    match = re.search(r'\{.*\}', text, re.DOTALL)
    
    if not match:
        print("[PARSER ERROR] No braces found in text:", text)
        raise ValueError("No JSON object found in the AI's response.")
        
    json_str = match.group(0)
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"[PARSER ERROR] Decode failed: {e}\nRaw String:\n{json_str[:500]}")
        raise ValueError("AI returned malformed JSON.")


def _extract_text_from_agent_history(history) -> tuple[str | None, str | None]:
    """Find the latest non-empty extracted_content across all steps.

    browser-use may append a final step with only ``error`` (e.g. max_steps) and no
    ``extracted_content``; real output often lives on earlier steps.
    Returns (text, first_error_from_end) — error is the first error seen when walking
    backward from the last step, only used when text is None.
    """
    if not history or not getattr(history, "history", None):
        return None, None
    last_error: str | None = None
    for step in reversed(history.history):
        for res in reversed(step.result or []):
            content = (res.extracted_content or "").strip()
            if content:
                return content, None
            if res.error and last_error is None:
                last_error = res.error
    return None, last_error


# ==========================================
# AGENT 1: THE HUNTER (Web Scraping)
# ==========================================
async def extract_raw_data(product_name: str) -> dict:
    print(f"[HUNTER] Initiating web search for: {product_name}...")
    
    prompt = HUNTER_PROMPT.replace("{entity_name}", product_name)

    agent = Agent(
        task=prompt, 
        llm=get_llm(),
    )
    
    # Run the agent
    history = await agent.run()

    # Prefer full-history scan (handles synthetic max_steps tail step); then library helper.
    final_text, tail_error = _extract_text_from_agent_history(history)
    if not final_text:
        fr = history.final_result() if history else None
        final_text = (fr or "").strip() if fr else ""

    if not final_text:
        detail = tail_error or "no extracted_content in any step"
        raise ValueError(f"The Hunter agent returned an empty response. ({detail})")

    print("[HUNTER] Extracted Text from Agent:\n", final_text[:200], "...")

    data = extract_json_from_text(final_text)
    print(f"[HUNTER] Successfully extracted {len(data.get('reviews', []))} raw reviews.")
    return data

# ==========================================
# AGENT 2: THE SYNTHESIZER (Analysis)
# ==========================================
async def synthesize_final_analysis(product_name: str, raw_data_dict: dict) -> dict:
    print(f"[SYNTHESIZER] Analyzing raw data for: {product_name}...")
    
    raw_data_string = json.dumps(raw_data_dict.get("reviews", []), indent=2)
    prompt = SYNTHESIZER_PROMPT.replace("{entity_name}", product_name).replace("{raw_data}", raw_data_string)
    
    llm = get_llm()
    # ChatGoogle expects browser_use BaseMessage models, not ("user", text) tuples (those break model_copy in the serializer).
    response = await llm.ainvoke([UserMessage(content=prompt)])

    text_output = response.completion
    if not isinstance(text_output, str):
        text_output = str(text_output)
    
    if not text_output:
        raise ValueError("The Synthesizer agent returned an empty response.")

    data = extract_json_from_text(text_output)
    print(f"[SYNTHESIZER] Successfully generated Mega-JSON for {product_name}.")
    return data