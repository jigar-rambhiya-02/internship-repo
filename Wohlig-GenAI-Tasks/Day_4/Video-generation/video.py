import requests
import time
from urllib.parse import quote

# Pollinations free image generation endpoint (no API key needed)
prompt = "a cute penguin looking at the night sky, glowing stars, digital art"

# Generate multiple frames and combine them into a video
frames = []
print("⏳ Generating 12 frames (this takes ~30 seconds)...")

for i in range(12):
    # Each frame slightly shifts the prompt for motion effect
    step_prompt = f"{prompt}, frame {i+1}/12, slight motion"
    url = f"https://image.pollinations.ai/prompt/{quote(step_prompt)}?width=512&height=512&nologo=true"
    
    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        frames.append(response.content)
        print(f"  ✅ Frame {i+1}/12 generated")
    else:
        print(f"  ❌ Frame {i+1} failed: {response.status_code}")
    time.sleep(1)  # Rate limiting

# Save frames as a GIF (since we can't make MP4 without extra libraries)
if frames:
    from PIL import Image
    import io
    
    images = []
    for frame_data in frames:
        img = Image.open(io.BytesIO(frame_data))
        images.append(img)
    
    # Save as animated GIF
    images[0].save("penguin_sky.gif", 
                   save_all=True, 
                   append_images=images[1:], 
                   duration=200,  # 0.2 seconds per frame
                   loop=0,
                   optimize=False)
    print("✅ Video saved as 'penguin_sky.gif' (open in browser or preview)")
else:
    print("❌ No frames generated – check your internet connection.")