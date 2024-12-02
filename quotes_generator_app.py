import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
import openai
import os
from datetime import datetime

# Function to load the selected template
def load_template(color):
    template_path = template_paths[color]
    return Image.open(template_path).convert("RGBA")

# Function to wrap text manually and respect newlines
def wrap_text_with_newlines(text, font, max_width, draw):
    lines = []
    for line in text.split("\n"):  # Split by newline to preserve manual line breaks
        words = line.split()
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if draw.textsize(test_line, font=font)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

    return lines

# Function to generate the quote using OpenAI
def generate_quote():
    if not api_key.get():
        messagebox.showerror("Error", "API Key missing. Please put your OpenAI key in the field above.")
        return
    try:
        openai.api_key = api_key.get()
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Updated model
            messages=[
                {"role": "system", "content": "You are a quote generator."},
                {"role": "user", "content": "Generate an inspiring quote (max 50 characters) and its author:"}
            ],
            max_tokens=50,
            temperature=0.7,
        )
        text = response['choices'][0]['message']['content'].strip()
        quote_text, author_text = text.split('-')
        quote_textarea.delete("1.0", tk.END)
        quote_textarea.insert(tk.END, quote_text.strip())
        author.set(author_text.strip())
    except Exception as e:
        messagebox.showerror("Error", f"OpenAI API Error: {e}")

# Function to create and save the final quote card
def save_quote_card():
    try:
        color = template_color.get()
        img = load_template(color)
        draw = ImageDraw.Draw(img)

        # Load fonts
        font_quote = ImageFont.truetype("arial.ttf", 50)  # Updated quote font size
        font_author = ImageFont.truetype("arial.ttf", 50)  # Updated author font size

        # Retrieve quote with manual line breaks
        quote_text = quote_textarea.get("1.0", tk.END).strip()
        author_text = f"- by {author.get()}"  # Updated author format

        # Wrap text for quote
        max_width = img.width - 150  # Allow more padding on the sides
        quote_lines = wrap_text_with_newlines(quote_text, font_quote, max_width, draw)

        # Hard-coded starting point for quote
        y_start_quote = 470  # Adjust this value to move the quote up/down
        line_spacing = 10  # Space between lines

        # Draw quote lines
        y = y_start_quote
        for line in quote_lines:
            line_width, line_height = draw.textsize(line, font=font_quote)
            x = (img.width - line_width) // 2
            draw.text((x, y), line, font=font_quote, fill="black")
            y += line_height + line_spacing

        # Draw author below the quote
        y += 40  # Additional space before the author
        line_width, line_height = draw.textsize(author_text, font=font_author)
        x = (img.width - line_width) // 2
        draw.text((x, y), author_text, font=font_author, fill="black")

        # Save the output
        if not os.path.exists("output"):
            os.makedirs("output")
        today_date = datetime.now().strftime("%Y-%m-%d")
        output_path = os.path.join("output", f"{color}_{today_date}.png")
        img.save(output_path)
        messagebox.showinfo("Success", f"Quote card saved to {output_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Error saving the quote card: {e}")

# GUI setup
app = tk.Tk()
app.title("Quote Card Generator")
app.geometry("500x350")  # Adjusted size to fit everything nicely

# Template paths
template_paths = {
    "lime": "lime.jpg",
    "orange": "orange.jpg",
    "pink": "pink.jpg",
    "purple": "purple.jpg",
    "yellow": "yellow.jpg",
}

# Variables
template_color = tk.StringVar(value="lime")
author = tk.StringVar()
api_key = tk.StringVar()

# UI Elements
tk.Label(app, text="API Key:").pack(pady=5)
tk.Entry(app, textvariable=api_key, show="*", width=50).pack(pady=5)

tk.Label(app, text="Quote:").pack()
quote_textarea = tk.Text(app, height=3, width=50)  # Multi-line text area for quote
quote_textarea.pack(pady=5)

tk.Label(app, text="Author:").pack()
tk.Entry(app, textvariable=author, width=50).pack(pady=5)

# Dropdown for template color
tk.Label(app, text="Template Color:").pack(pady=5)
color_dropdown = ttk.Combobox(app, textvariable=template_color, values=list(template_paths.keys()), state="readonly")
color_dropdown.pack(pady=5)

# Buttons
tk.Button(app, text="Generate Quote", command=generate_quote).pack(pady=5)
tk.Button(app, text="Save Quote Card", command=save_quote_card).pack(pady=5)

app.mainloop()
