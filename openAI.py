import logging
import requests
import time

logger = logging.getLogger(__name__)

OLLAMA_URL = 'http://localhost:11434/api/generate'
MAX_PROMPT_LENGTH = 1000  # Limit prompt length
REQUEST_TIMEOUT = 30  # seconds


def getChatGPTanswer(text):
    """
    Get AI response from Ollama for chatgpt queries.
    Processes the input text and calls the local Ollama API.
    """
    try:
        if not text or not isinstance(text, str):
            logger.warning("Invalid input to getChatGPTanswer")
            return "Invalid query format."
        
        # Process the text input - remove "chatgpt" prefix
        words = text.split()
        if len(words) > 0 and words[0].lower() == "chatgpt":
            words.pop(0)
        
        prompt = " ".join(words).strip()
        
        if not prompt:
            return "Please provide a question after 'chatgpt'."
        
        # Limit prompt length
        if len(prompt) > MAX_PROMPT_LENGTH:
            prompt = prompt[:MAX_PROMPT_LENGTH] + "..."
            logger.info(f"Prompt truncated to {MAX_PROMPT_LENGTH} characters")
        
        logger.info(f"Sending prompt to Ollama: {prompt[:50]}...")
        
        # Call Ollama API with timeout
        start_time = time.time()
        response = requests.post(
            OLLAMA_URL,
            json={
                'model': 'llama2',
                'prompt': prompt,
                'stream': False
            },
            timeout=REQUEST_TIMEOUT
        )
        
        response_time = time.time() - start_time
        logger.info(f"Ollama response time: {response_time:.2f}s")
        
        if response.status_code == 200:
            try:
                data = response.json()
                ai_response = data.get('response', '').strip()
                if not ai_response:
                    logger.warning("Empty response from Ollama")
                    return "AI returned an empty response."
                
                # Limit response length
                if len(ai_response) > 2000:
                    ai_response = ai_response[:2000] + "..."
                
                return ai_response
                
            except ValueError as e:
                logger.error(f"Invalid JSON response from Ollama: {e}")
                return "Error parsing AI response."
        
        else:
            logger.error(f"Ollama API error: {response.status_code} - {response.text}")
            if response.status_code == 404:
                return "AI model not found. Please ensure Ollama is running and llama2 is installed."
            elif response.status_code >= 500:
                return "AI service is temporarily unavailable."
            else:
                return f"AI request failed (status {response.status_code})."
    
    except requests.exceptions.Timeout:
        logger.error("Timeout connecting to Ollama")
        return "AI request timed out. Please try again."
    
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama - service may not be running")
        return "Cannot connect to AI service. Please ensure Ollama is running."
    
    except Exception as e:
        logger.error(f"Unexpected error in getChatGPTanswer: {e}")
        return "An unexpected error occurred with the AI service."
