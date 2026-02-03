import logging
import ollama

class VLMEngine:
    def __init__(self, model_name="llava:v1.6"):
        self.model_name = model_name
        self.valid = True # Assume valid if Ollama is running

    def analyze(self, image_path, prompt="Extract all dimensions and text from this engineering drawing."):
        logging.info(f"Analyzing {image_path} with Ollama {self.model_name}...")
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                        'images': [image_path]
                    }
                ]
            )
            return response['message']['content']
        except Exception as e:
            logging.error(f"Ollama Error: {e}")
            return "Error calling Ollama. Ensure 'ollama serve' is running."
