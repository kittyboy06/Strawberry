import os
from PIL import Image

src_path = r"e:\Projects\Works\Strawberry\Strawberry Admin Dashboard Overview.png"
out_dir = r"e:\Projects\Works\Strawberry\strawberry-admin\src\assets"

os.makedirs(out_dir, exist_ok=True)

img = Image.open(src_path)
width, height = img.size
print(f"Original image size: {width}x{height}")

# 1. Logo strawberry (top-left)
# In 1728x972: roughly x: 45 to 110, y: 25 to 105
logo_box = (int(width * 0.024), int(height * 0.025), int(width * 0.065), int(height * 0.11))
logo_img = img.crop(logo_box)
logo_img.save(os.path.join(out_dir, "strawberry-logo.png"))
print("Saved strawberry-logo.png")

# 2. Top-right vine illustration
# roughly x: 68% to 100%, y: 0% to 32%
vine_box = (int(width * 0.68), int(height * 0.08), int(width * 1.0), int(height * 0.30))
vine_img = img.crop(vine_box)
vine_img.save(os.path.join(out_dir, "strawberry-branch.png"))
print("Saved strawberry-branch.png")

# 3. Bottom-left sidebar strawberry illustration
# roughly x: 0% to 16%, y: 78% to 100%
bottom_box = (int(width * 0.005), int(height * 0.79), int(width * 0.17), int(height * 1.0))
bottom_img = img.crop(bottom_box)
bottom_img.save(os.path.join(out_dir, "strawberry-bottom.png"))
print("Saved strawberry-bottom.png")
