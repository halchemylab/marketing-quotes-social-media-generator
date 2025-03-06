import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
from openai import OpenAI
import os
import random
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=API_KEY)

class QuoteCardGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Quote Card Generator")
        self.root.geometry("600x550")  # Increased height for new button
        self.root.configure(bg="#f5f5f5")
        
        # Template paths
        self.template_paths = {
            "lime": "lime.jpg",
            "orange": "orange.jpg",
            "pink": "pink.jpg",
            "purple": "purple.jpg",
            "yellow": "yellow.jpg",
        }
        
        # List of colors for random selection
        self.colors = list(self.template_paths.keys())
        
        # Variables
        self.template_color = tk.StringVar(value="lime")
        self.author = tk.StringVar()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg="#f5f5f5", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Quote Card Generator", 
            font=("Arial", 16, "bold"),
            bg="#f5f5f5"
        )
        title_label.pack(pady=10)
        
        # Quote section
        quote_frame = tk.LabelFrame(main_frame, text="Quote Content", padx=10, pady=10, bg="#f5f5f5")
        quote_frame.pack(fill=tk.X, pady=10)
        
        # Quote text
        tk.Label(quote_frame, text="Quote:", bg="#f5f5f5").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.quote_textarea = tk.Text(quote_frame, height=4, width=50, wrap=tk.WORD)
        self.quote_textarea.grid(row=0, column=1, pady=5, padx=5)
        
        # Author
        tk.Label(quote_frame, text="Author:", bg="#f5f5f5").grid(row=1, column=0, sticky=tk.W, pady=5)
        author_entry = tk.Entry(quote_frame, textvariable=self.author, width=50)
        author_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Template selection
        template_frame = tk.LabelFrame(main_frame, text="Template Settings", padx=10, pady=10, bg="#f5f5f5")
        template_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(template_frame, text="Template Color:", bg="#f5f5f5").grid(row=0, column=0, sticky=tk.W, pady=5)
        color_dropdown = ttk.Combobox(
            template_frame, 
            textvariable=self.template_color, 
            values=list(self.template_paths.keys()), 
            state="readonly",
            width=47
        )
        color_dropdown.grid(row=0, column=1, pady=5, padx=5)
        
        # Preview will be added in a future version
        # tk.Label(template_frame, text="Preview:", bg="#f5f5f5").grid(row=1, column=0, sticky=tk.W, pady=5)
        # preview_label = tk.Label(template_frame, text="[Preview will be shown here]", bg="white", width=47, height=5)
        # preview_label.grid(row=1, column=1, pady=5, padx=5)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg="#f5f5f5")
        button_frame.pack(pady=10)
        
        generate_button = tk.Button(
            button_frame, 
            text="Generate Quote", 
            command=self.generate_quote,
            bg="#4CAF50",
            fg="white",
            padx=10,
            pady=5
        )
        generate_button.grid(row=0, column=0, padx=10)
        
        save_button = tk.Button(
            button_frame, 
            text="Save Quote Card", 
            command=self.save_quote_card,
            bg="#2196F3",
            fg="white",
            padx=10,
            pady=5
        )
        save_button.grid(row=0, column=1, padx=10)
        
        random_button = tk.Button(
            button_frame, 
            text="Just generate it for me", 
            command=self.generate_random_card,
            bg="#9C27B0",
            fg="white",
            padx=10,
            pady=5
        )
        random_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        # Status bar
        self.status_var = tk.StringVar()
        status_bar = tk.Label(
            self.root, 
            textvariable=self.status_var, 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_var.set("Ready")
        
        # Check API key on startup
        if not API_KEY:
            messagebox.showwarning(
                "API Key Missing", 
                "OpenAI API key not found in .env file. Please add OPENAI_API_KEY=your_key to a .env file in the same directory."
            )
    
    def load_template(self, color):
        """Load the selected template image"""
        template_path = self.template_paths[color]
        return Image.open(template_path).convert("RGBA")
    
    def wrap_text_with_newlines(self, text, font, max_width, draw):
        """Wrap text manually and respect newlines"""
        lines = []
        for line in text.split("\n"):  # Split by newline to preserve manual line breaks
            words = line.split()
            current_line = ""

            for word in words:
                test_line = f"{current_line} {word}".strip()
                width, _ = draw.textsize(test_line, font=font)
                if width <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

        return lines
    
    def generate_quote(self):
        """Generate a quote using OpenAI API"""
        if not API_KEY:
            messagebox.showerror(
                "Error", 
                "API Key missing. Please add OPENAI_API_KEY=your_key to a .env file in the same directory."
            )
            return
        
        self.status_var.set("Generating quote...")
        self.root.update()
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a quote generator."},
                    {"role": "user", "content": "Generate an inspiring quote (max 50 characters) and its author:"}
                ],
                max_tokens=50,
                temperature=0.7,
            )
            text = response.choices[0].message.content.strip()
            
            # Split into quote and author
            parts = text.split('-')
            if len(parts) > 1:
                quote_text = parts[0].strip()
                author_text = parts[1].strip()
            else:
                quote_text = text
                author_text = "Unknown"
            
            self.quote_textarea.delete("1.0", tk.END)
            self.quote_textarea.insert(tk.END, quote_text)
            self.author.set(author_text)
            self.status_var.set("Quote generated successfully")
        except Exception as e:
            self.status_var.set("Error")
            messagebox.showerror("Error", f"OpenAI API Error: {e}")
    
    def generate_random_card(self):
        """Generate a random quote, author, and color and save the card"""
        if not API_KEY:
            messagebox.showerror(
                "Error", 
                "API Key missing. Please add OPENAI_API_KEY=your_key to a .env file in the same directory."
            )
            return
            
        self.status_var.set("Generating random quote card...")
        self.root.update()
        
        try:
            # Generate random quote
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a quote generator."},
                    {"role": "user", "content": "Generate an inspiring quote (max 50 characters) and its author:"}
                ],
                max_tokens=50,
                temperature=0.7,
            )
            text = response.choices[0].message.content.strip()
            
            # Split into quote and author
            parts = text.split('-')
            if len(parts) > 1:
                quote_text = parts[0].strip()
                author_text = parts[1].strip()
            else:
                quote_text = text
                author_text = "Unknown"
                
            # Choose random color
            random_color = random.choice(self.colors)
            
            # Update UI
            self.quote_textarea.delete("1.0", tk.END)
            self.quote_textarea.insert(tk.END, quote_text)
            self.author.set(author_text)
            self.template_color.set(random_color)
            
            # Save the card
            self.save_quote_card()
            
        except Exception as e:
            self.status_var.set("Error generating random card")
            messagebox.showerror("Error", f"Error generating random card: {e}")
    
    def save_quote_card(self):
        """Create and save the final quote card"""
        try:
            self.status_var.set("Creating quote card...")
            self.root.update()
            
            color = self.template_color.get()
            img = self.load_template(color)
            draw = ImageDraw.Draw(img)

            # Load fonts - keeping the original settings
            font_quote = ImageFont.truetype("arial.ttf", 50)
            font_author = ImageFont.truetype("arial.ttf", 50)

            # Retrieve quote with manual line breaks
            quote_text = self.quote_textarea.get("1.0", tk.END).strip()
            author_text = f"- by {self.author.get()}"

            # Wrap text for quote - keeping original width
            max_width = img.width - 150
            quote_lines = self.wrap_text_with_newlines(quote_text, font_quote, max_width, draw)

            # Keep original position settings
            y_start_quote = 470  # Original coordinate
            line_spacing = 10

            # Draw quote lines
            y = y_start_quote
            for line in quote_lines:
                line_width, line_height = draw.textsize(line, font=font_quote)
                x = (img.width - line_width) // 2
                draw.text((x, y), line, font=font_quote, fill="black")
                y += line_height + line_spacing

            # Draw author below the quote - keeping original spacing
            y += 40
            line_width, line_height = draw.textsize(author_text, font=font_author)
            x = (img.width - line_width) // 2
            draw.text((x, y), author_text, font=font_author, fill="black")

            # Save the output
            if not os.path.exists("output"):
                os.makedirs("output")
            
            today_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output_path = os.path.join("output", f"{color}_{today_date}.png")
            img.save(output_path)
            
            self.status_var.set(f"Quote card saved: {output_path}")
            messagebox.showinfo("Success", f"Quote card saved to {output_path}")
        except Exception as e:
            self.status_var.set("Error saving quote card")
            messagebox.showerror("Error", f"Error saving the quote card: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteCardGenerator(root)
    root.mainloop()