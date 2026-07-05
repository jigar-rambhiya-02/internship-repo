import os
import time
from groq import Groq
from dotenv import load_dotenv
from typing import List, Dict, Any
from config.logger_config import setup_logger

load_dotenv('/Users/jigar/Documents/jigar/Tasks/.env')

logger = setup_logger("groq_client")

class GroqGenerator:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.critical("Initialization aborted: GROQ_API_KEY environment variable is blank.")
            raise ValueError("Missing GROQ_API_KEY value.")
        self.client = Groq(api_key=self.api_key)
        self.model_name = "llama-3.3-70b-versatile"

    def generate_grounded_answer(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Assembles retrieved context text, passes payloads to Groq LPU systems,
        and ensures strict adherence to tracking metrics.
        """
        # Assemble context block with character boundaries handled explicitly
        context_payload = ""
        retrieved_ids = []
        for idx, chunk in enumerate(context_chunks):
            retrieved_ids.append(chunk["chunk_id"])
            context_payload += f"\n[Document Fragment #{idx+1} | Source: {chunk.get('source_doc', 'Unknown')}]\nID: {chunk['chunk_id']}\nContent: {chunk['text']}\n"
            
        system_prompt = (
            "You are an expert corporate legal advisor and operational auditor.\n"
            "Synthesize a clear, direct, technical response answering the user's inquiry.\n"
            "Your response must be entirely grounded in the provided Document Fragments below.\n"
            "If the information is not present, state that you cannot answer based on context.\n"
            "Do not extrapolate or assume outside facts.\n\n"
            f"=== GROUNDING CONTEXT ==={context_payload}=========================="
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        logger.info(f"Dispatching Groq API request. Model: {self.model_name} | Context Chunks: {retrieved_ids}")
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.0, # Zero variance preferred for factual auditing
                max_tokens=800
            )
            latency_ms = int((time.time() - start_time) * 1000)
            answer = response.choices[0].message.content
            
            token_usage = getattr(response, 'usage', None)
            usage_msg = f"Prompt Tokens: {token_usage.prompt_tokens} | Completion Tokens: {token_usage.completion_tokens}" if token_usage else "Usage stats unavailable"
            
            logger.info(f"Groq API Response received successfully. Latency: {latency_ms}ms | {usage_msg}")
            logger.info(f"Response preview: {answer[:120].strip()}...")
            
            return answer
            
        except Exception as e:
            logger.error(f"Groq API connection crash encountered during generation loop: {str(e)}", exc_info=True)
            raise e

