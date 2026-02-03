import logging
import json
import os

class LLMValidatorAgent:
    """
    The REASONING Agent.
    Strictly validates, normalizes, and explains features extracted by CV.
    Does NOT extract new features from images.
    """
    _llm = None
    
    @classmethod
    def load_model(cls):
        if cls._llm is None:
            try:
                from llama_cpp import Llama
                # Look for model in models directory
                # Expecting: drawing-ai/backend/models/llama-3.1-8b-instruct.gguf
                # Or user can set env var
                model_path = os.getenv("LLAMA_MODEL_PATH", "models/llama-3.1-8b-instruct.gguf")
                
                if os.path.exists(model_path):
                    logging.info(f"[LLMValidator] Loading generic LLaMA model from {model_path}...")
                    cls._llm = Llama(
                        model_path=model_path,
                        n_ctx=8192, # Large context for many features
                        n_gpu_layers=-1, # Offload all to GPU if available
                        verbose=False
                    )
                else:
                    logging.warning(f"[LLMValidator] Model not found at {model_path}. Running in MOCK mode.")
            except ImportError:
                logging.warning("[LLMValidator] llama-cpp-python not installed. Running in MOCK mode.")
            except Exception as e:
                logging.warning(f"[LLMValidator] Model load failed: {e}")

    @staticmethod
    def process(context):
        logging.info("[LLMValidator] Starting Layout & Logic Reasoning...")
        LLMValidatorAgent.load_model()
        
        features = context["features"]
        
        # Prepare Payload for LLM
        # We only send what's necessary to save tokens
        candidate_features = []
        for cat in ["dimensions", "bores", "chamfers", "radii"]:
            for f in features.get(cat, []):
                candidate_features.append({
                    "id": f["id"],
                    "type": f["type"],
                    "raw_text": f["value"],
                    "linked_arrows": len(f["linked_arrows"]) > 0
                })
                
        if not candidate_features:
            logging.info("[LLMValidator] No features to validate.")
            return context

        prompt = f"""
You are an engineering validation agent.

Rules:
- Do not invent new features.
- Do not modify geometry.
- Accept, Reject, or Normalize only.
- Output STRICT JSON.

Task:
1. Validate each feature.
2. Normalize text (e.g. "3x Ø10" -> value: "10", type: "bore", count: 3).
3. Reject invalid entries (e.g. random text, title block artifacts).

Input:
{json.dumps(candidate_features, indent=2)}

Response Format (JSON List):
[
  {{
    "id": "1",
    "status": "accepted", 
    "normalized_value": "10.0",
    "normalized_type": "bore",
    "tolerance": "+/-0.1",
    "count": 1,
    "confidence": 0.95
  }},
  {{
    "id": "2",
    "status": "rejected",
    "reason": "Floating text with no arrows"
  }}
]
"""
        
        validated_map = {}
        
        if cls._llm:
            try:
                logging.info("[LLMValidator] Querying LLaMA...")
                output = cls._llm(
                    f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
                    max_tokens=2048,
                    stop=["<|eot_id|>"],
                    temperature=0.0 # Deterministic
                )
                response_text = output["choices"][0]["text"]
                
                # Parse JSON
                # Robust parsing logic
                json_start = response_text.find('[')
                json_end = response_text.rfind(']') + 1
                if json_start != -1 and json_end != -1:
                    json_str = response_text[json_start:json_end]
                    validated_list = json.loads(json_str)
                    
                    for item in validated_list:
                        validated_map[str(item.get("id"))] = item
                else:
                    logging.warning("[LLMValidator] Could not find JSON in response.")
            except Exception as e:
                logging.error(f"[LLMValidator] Inference failed: {e}")
        else:
            # Mock Implementation if no model
            for f in candidate_features:
                validated_map[str(f["id"])] = {
                    "id": f["id"],
                    "status": "accepted",
                    "normalized_value": f["raw_text"],
                    "normalized_type": f["type"],
                    "confidence": 0.8
                }

        # Apply Validations to Context
        # We iterate through original features and update/remove based on LLM decision
        for cat in ["dimensions", "bores", "chamfers", "radii"]:
            valid_list = []
            for f in features.get(cat, []):
                decision = validated_map.get(str(f["id"]))
                
                if decision:
                    if decision.get("status") == "rejected":
                        logging.info(f"[LLMValidator] Rejected {f['value']}: {decision.get('reason')}")
                        continue
                    
                    # Update feature with normalized data
                    f["value"] = decision.get("normalized_value", f["value"])
                    f["valid_type"] = decision.get("normalized_type", f["type"])
                    f["llm_confidence"] = decision.get("confidence", 0.5)
                    f["tolerance"] = decision.get("tolerance", "")
                    # Move to correct category if LLM changed type? 
                    # For POC simplicity, allow type override but keep in original bucket or consolidated bucket?
                    # Let's keep in original bucket but mark it.
                    
                    valid_list.append(f)
                else:
                    # Keep if LLM missed it (conservative) or drop?
                    # Let's keep it but flag low confidence
                    valid_list.append(f)
            
            features[cat] = valid_list

        return context
