import requests
from urllib.parse import quote

prompt = "girl dancing"
image_path = "girl.png"

# Public Pollinations URL – no key needed, and you can add parameters
url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=1024&height=1024&nologo=true"

print("Generating image...")
response = requests.get(url, timeout=60)  # wait up to 60 seconds

if response.status_code == 200:
    with open(image_path, "wb") as f:
        f.write(response.content)
    print(f"✅ Image saved as {image_path}")
else:
    print(f"❌ Error {response.status_code}")