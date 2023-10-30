import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageFont

def generate_image():
    # Get the text from the input box
    text = text_input.get()

    # Create an image with the text
    img = Image.new('RGB', (800, 600), color='white')
    d = ImageDraw.Draw(img)
    fnt = ImageFont.load_default()  # You can specify your font

    # Add text to the image
    d.text((30, 30), text, font=fnt, fill='black')
    img.save("output.png")

# Create the main window
root = tk.Tk()
root.title("Text to Image Converter")

# Text input box
text_input = tk.Entry(root)
text_input.pack()

# Generate button
generate_button = ttk.Button(root, text="Generate Image", command=generate_image)
generate_button.pack()

# Start the GUI event loop
root.mainloop()