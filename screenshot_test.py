import pyautogui
from PIL import Image, ImageDraw
import time

time.sleep(1)

# Find image location
image_location = pyautogui.locateOnScreen("wheat.png", grayscale=True, confidence=.90)

if image_location != None:
    # Get the coordinates of the image location
    left, top, width, height = image_location

    # Take a screenshot
    screenshot = pyautogui.screenshot()

    # Convert the screenshot to PIL Image
    screenshot_image = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

    # Draw a rectangle on the image
    draw = ImageDraw.Draw(screenshot_image)
    draw.rectangle([(left, top), (left + width, top + height)], outline='red', width=2)

    # Display the image with the drawn rectangle
    screenshot_image.show()
else:
    print("Image not found.")


