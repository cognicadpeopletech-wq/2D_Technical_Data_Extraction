import requests
import os

try:
    # Use a real image file from the workspace
    # Need to target the absolute path carefully
    
    # Path relative to where we run the script (backend dir)
    # The find_by_name returned: drawing-ai\data\raw_drawings\d573320e-3269-476c-8186-cd4139b362d1.png (relative to desktop root)
    # We are in backend dir: ...\drawing-ai\backend
    
    # Let's use the absolute path constructed dynamically or hardcoded for this environment
    image_path = r"c:\Users\DhupatiDeepak\OneDrive - Ramp Group Technologies\Desktop\2D_Drawing\drawing-ai\data\raw_drawings\d573320e-3269-476c-8186-cd4139b362d1.png"
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        exit(1)

    url = "http://localhost:8000/extract/"
    files = {'file': ('test_image.png', open(image_path, 'rb'), 'image/png')}
    
    print(f"Testing POST {url} with image {image_path}...")
    response = requests.post(url, files=files)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success! Backend processed the image.")
        # print(response.json()) # Optional: Print output to see dimensions
    else:
        print(f"Failed: {response.text}")

except Exception as e:
    print(f"Error: {e}")
