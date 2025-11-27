#!/usr/bin/env python3
"""
Surfer-H Native DOM Approach
Uses HTML parsing and CSS selectors instead of screenshot coordinates
"""

import time
import json
import re
from openai import OpenAI
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from src.surfer_h_cli.simple_browser import SimpleWebBrowserTools


def get_page_html(browser: SimpleWebBrowserTools) -> str:
    """Extract the HTML content of the current page"""
    assert browser.driver
    return browser.driver.page_source


def parse_json_response(response_text: str) -> dict:
    """Robustly parse JSON response, fixing common formatting issues"""
    response_text = response_text.strip()
    
    # Method 1: Try direct parsing
    try:
        return json.loads(response_text)
    except:
        pass
    
    # Method 2: Fix extra closing braces
    try:
        open_braces = response_text.count('{')
        close_braces = response_text.count('}')
        if close_braces > open_braces:
            response_text = response_text.rstrip('}') + '}'
        return json.loads(response_text)
    except:
        pass
    
    # Method 3: Extract first valid JSON object
    try:
        start = response_text.find('{')
        if start == -1:
            raise ValueError("No JSON object found")
        
        depth = 0
        for i in range(start, len(response_text)):
            if response_text[i] == '{':
                depth += 1
            elif response_text[i] == '}':
                depth -= 1
                if depth == 0:
                    json_str = response_text[start:i+1]
                    return json.loads(json_str)
        raise ValueError("No matching closing brace")
    except:
        pass
    
    # Method 4: Reconstruct from regex
    try:
        action_match = re.search(r'"action"\s*:\s*"([^"]+)"', response_text)
        selector_match = re.search(r'"selector"\s*:\s*"([^"]+)"', response_text)
        content_match = re.search(r'"content"\s*:\s*"([^"]+)"', response_text)
        
        if action_match:
            result = {"action": action_match.group(1)}
            if selector_match:
                result["selector"] = selector_match.group(1)
            if content_match:
                result["content"] = content_match.group(1)
            return result
    except:
        pass
    
    raise ValueError(f"Could not parse JSON: {response_text}")


def create_navigation_prompt(task: str, html: str, history: list) -> str:
    """Create prompt for the navigation model"""
    history_str = "\n".join([f"Step {i}: {h}" for i, h in enumerate(history)])
    
    # Determine what step we're on
    num_completed = len(history)
    
    return f"""You are a web automation agent. You must complete steps IN ORDER.

TASK STEPS:
{task}

COMPLETED STEPS ({num_completed}):
{history_str if history else "None - START WITH STEP 1"}

CURRENT PAGE HTML:
{html[:8000]}

CRITICAL: You have completed {num_completed} steps. Do the NEXT step only.

Return ONLY valid JSON (no extra braces):
{{"action": "fill_field", "selector": "#id", "content": "text"}}
{{"action": "click_element", "selector": ".class"}}
{{"action": "extract_text", "selector": "#id"}}
{{"action": "answer", "content": "done"}}

What is step {num_completed + 1}?"""


def execute_action(action: dict, browser: SimpleWebBrowserTools) -> tuple[bool, str]:
    """Execute an action"""
    assert browser.driver
    
    try:
        if action["action"] == "fill_field":
            selector = action["selector"]
            content = action["content"]
            
            print(f"🔍 Finding: {selector}")
            element = browser.driver.find_element(By.CSS_SELECTOR, selector)
            element.clear()
            element.send_keys(content)
            print(f"✅ Filled with: {content}")
            return True, f"Filled {selector}"
                
        elif action["action"] == "click_element":
            selector = action["selector"]
            print(f"🔍 Finding: {selector}")
            element = browser.driver.find_element(By.CSS_SELECTOR, selector)
            element.click()
            time.sleep(3)  # Wait longer for page to load
            print(f"✅ Clicked")
            return True, f"Clicked {selector}"
            
        elif action["action"] == "extract_text":
            selector = action["selector"]
            print(f"🔍 Finding: {selector}")
            element = browser.driver.find_element(By.CSS_SELECTOR, selector)
            text = element.text.strip()
            print(f"\n{'='*60}")
            print(f"🎯 EXTRACTED: {text}")
            print(f"{'='*60}\n")
            return True, f"Extracted: {text}"
            
        elif action["action"] == "answer":
            print(f"✅ Complete: {action['content']}")
            return True, action["content"]
            
        else:
            return False, "Unknown action"
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, str(e)


def run_agent(task: str, url: str, api_key: str, model_url: str, model_name: str, max_steps: int = 30):
    """Main agent loop"""
    browser = SimpleWebBrowserTools()
    browser.open_browser(headless=False, width=1920, height=1080, action_timeout=10)
    client = OpenAI(api_key=api_key, base_url=model_url)
    
    print(f"🌐 Navigating to: {url}")
    browser.goto(url)
    time.sleep(2)
    
    history = []
    
    for step in range(max_steps):
        print(f"\n{'='*60}")
        print(f"🎉 Step {step}")
        print(f"{'='*60}")
        
        html = get_page_html(browser)
        prompt = create_navigation_prompt(task, html, history)
        
        print(f"🤖 Asking model...")
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        try:
            response_text = response.choices[0].message.content
            action = parse_json_response(response_text)
            print(f"🛠️  Action: {action}")
        except Exception as e:
            print(f"❌ Parse error: {e}")
            print(f"Response: {response_text}")
            continue
        
        if action["action"] == "answer":
            print(f"\n✅ TASK COMPLETE")
            break
        
        success, result = execute_action(action, browser)
        history.append(result)
        
        if not success:
            print(f"⚠️  Failed, retrying...")
        
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"Finished after {step + 1} steps")
    print(f"{'='*60}")
    
    input("\nPress Enter to close...")
    browser.close()


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    with open("instructions-native.txt", "r") as f:
        task = f.read()
    
    run_agent(
        task=task,
        url="file:///home/justine/Documents/surfer-h-cli/automation_forms_filling/login.html",
        api_key=os.getenv("HAI_API_KEY"),
        model_url=os.getenv("HAI_MODEL_URL_NAVIGATION"),
        model_name=os.getenv("HAI_MODEL_NAME_NAVIGATION"),
        max_steps=30
    )
