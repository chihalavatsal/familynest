from PIL import Image, ImageDraw, ImageFont
def create_icon(size):
    img = Image.new('RGBA', (size, size), color=(146, 97, 74, 255))
    d = ImageDraw.Draw(img)
    # Simple F
    d.text((size/2, size/2), "F", fill=(255,255,255), anchor="mm", font_size=int(size*0.6))
    img.save(f"frontend/public/icons/icon-{size}x{size}.png")

create_icon(192)
create_icon(512)
