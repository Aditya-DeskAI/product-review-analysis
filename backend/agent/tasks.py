import json
import re
from browser_use import Agent, ChatGoogle

async def run_browser_agent(product_name: str) -> dict:
    """
    Initializes the browser-use agent to search the web for product reviews
    using the official ChatGoogle wrapper.
    """
    
    # Initialize the model natively (using gemini-1.5-pro as it reasons better for browsing)
    llm = ChatGoogle(model='gemini-pro-latest')

    # Define the exact task for the agent
    task_prompt = f"""
    You are an expert product researcher. 
    1. Go to Google and search for reviews of "{product_name}".
    2. Read reviews from at least 2 different major platforms (e.g., Reddit, Amazon, Trustpilot, Goodreads).
    3. Analyze the overall sentiment, pros, and cons based on what actual users are saying.
    4. Provide your final answer strictly as a JSON object matching this schema exactly:
    {{
        "product_name": "{product_name}",
        "overall_summary": "A 3-4 sentence summary of the general consensus.",
        "average_sentiment_score": 85,
        "pros": ["pro1", "pro2", "pro3"],
        "cons": ["con1", "con2"],
        "platforms_scraped": ["Reddit", "Amazon"]
    }}
    CRITICAL: Do not include any markdown formatting like ```json, just output the raw JSON string.
    """

    # Create agent with the model
    agent = Agent(
        task=task_prompt,
        llm=llm
    )

    # Run the agent
    result = await agent.run()
    
    # Extract the final textual response
    final_text = result.final_result()
    
    # --- ADD THIS SAFETY CHECK ---
    if not final_text:
        raise ValueError("The agent failed to complete the task and returned nothing.")
    # -----------------------------

    # Clean up the output in case Gemini adds markdown
    cleaned_text = re.sub(r'```json\n|\n```|```', '', final_text).strip()
    
    # Parse the text into a Python dictionary
    try:
        data = json.loads(cleaned_text)
        return data
    except json.JSONDecodeError:
        print("Failed to parse agent output as JSON. Raw output:", final_text)
        # Fallback dictionary
        return {
            "product_name": product_name,
            "overall_summary": "Agent successfully browsed but failed to format the output as JSON. Raw text: " + final_text[:200],
            "average_sentiment_score": 50,
            "pros": [],
            "cons": [],
            "platforms_scraped": []
        }