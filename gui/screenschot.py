from PIL import ImageGrab, ImageFilter, ImageEnhance
from screeninfo import get_monitors
monitor_size = {
    "width": get_monitors()[0].width,
    "height": get_monitors()[0].height
}

print(monitor_size)

# Screenshot
screenshot = ImageGrab.grab((0, 70, monitor_size["width"], monitor_size["height"]))

#screenshot = screenshot.crop((100, 100, 400, 400))

# Apply filter
enhancer = ImageEnhance.Brightness(screenshot).enhance(0.45)
enhancer = enhancer.filter(ImageFilter.GaussianBlur(7))
enhancer.save("screenshot.png")
