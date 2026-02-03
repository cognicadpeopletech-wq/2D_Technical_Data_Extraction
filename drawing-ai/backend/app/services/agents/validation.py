import logging

class ValidationAgent:
    """
    Sanity checks the extracted data.
    """
    @staticmethod
    def process(context):
        logging.info("[ValidationAgent] Validating results...")
        
        dims = context["features"]["dimensions"]
        valid_dims = []
        
        for d in dims:
            # 1. Check for valid value
            if not any(char.isdigit() for char in d["value"]):
                continue
                
            # 2. Check Logic
            try:
                clean = "".join([c for c in d["value"] if c.isdigit() or c == "."])
                if clean and float(clean) == 0:
                    continue
            except: pass
            
            valid_dims.append(d)
            
        context["features"]["dimensions"] = valid_dims
        return context
