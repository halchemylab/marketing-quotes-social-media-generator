import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
import csv
import os
import random
from datetime import datetime

class QuoteCardGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Quote Card Generator")
        self.root.geometry("600x600")
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

        # Load quotes from CSV
        self.quotes = []
        self.eras = ["Random"]
        self.load_quotes()

        # Variables
        self.template_color = tk.StringVar(value="lime")
        self.author = tk.StringVar()
        self.era = tk.StringVar(value="Random")
        
        self.create_widgets()

    def load_quotes(self):
        """Load quotes from quotes.csv"""
        try:
            if not os.path.exists("quotes.csv"):
                messagebox.showerror("Error", "quotes.csv not found!")
                return

            with open("quotes.csv", mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.quotes.append(row)
                    if row['era'] not in self.eras:
                        self.eras.append(row['era'])
            
            # Sort eras (excluding "Random")
            temp_eras = sorted([e for e in self.eras if e != "Random"])
            self.eras = ["Random"] + temp_eras
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load quotes: {e}")
        
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

        # Era
        tk.Label(quote_frame, text="Era:", bg="#f5f5f5").grid(row=2, column=0, sticky=tk.W, pady=5)
        era_dropdown = ttk.Combobox(
            quote_frame,
            textvariable=self.era,
            values=self.eras,
            state="readonly",
            width=47
        )
        era_dropdown.grid(row=2, column=1, pady=5, padx=5)
        
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
                bbox = draw.textbbox((0, 0), test_line, font=font)
                width = bbox[2] - bbox[0]
                if width <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

        return lines
    
    def generate_quote(self):
        """Generate a quote from the local CSV based on selected era"""
        if not self.quotes:
            messagebox.showerror("Error", "No quotes loaded from quotes.csv")
            return

        self.status_var.set("Selecting quote...")
        self.root.update()

        try:
            selected_era = self.era.get()
            if selected_era == "Random":
                chosen_quote = random.choice(self.quotes)
            else:
                filtered_quotes = [q for q in self.quotes if q['era'] == selected_era]
                if not filtered_quotes:
                    messagebox.showwarning("Warning", f"No quotes found for era: {selected_era}")
                    return
                chosen_quote = random.choice(filtered_quotes)

            quote_text = chosen_quote['quote']
            author_text = chosen_quote['author']

            self.quote_textarea.delete("1.0", tk.END)
            self.quote_textarea.insert(tk.END, quote_text)
            self.author.set(author_text)
            self.status_var.set(f"Selected a quote from {chosen_quote['era']} era")
        except Exception as e:
            self.status_var.set("Error")
            messagebox.showerror("Error", f"Error selecting quote: {e}")
    
    def generate_random_card(self):
        """Pick a random quote, author, and color from local data and save the card"""
        if not self.quotes:
            messagebox.showerror("Error", "No quotes loaded from quotes.csv")
            return

        self.status_var.set("Generating random quote card...")
        self.root.update()

        try:
            # Choose a random quote from the entire list
            chosen_quote = random.choice(self.quotes)
            
            quote_text = chosen_quote['quote']
            author_text = chosen_quote['author']
            random_color = random.choice(self.colors)

            # Update UI
            self.quote_textarea.delete("1.0", tk.END)
            self.quote_textarea.insert(tk.END, quote_text)
            self.author.set(author_text)
            self.era.set(chosen_quote['era'])
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
                bbox = draw.textbbox((0, 0), line, font=font_quote)
                line_width = bbox[2] - bbox[0]
                line_height = bbox[3] - bbox[1]
                x = (img.width - line_width) // 2
                draw.text((x, y), line, font=font_quote, fill="black")
                y += line_height + line_spacing

            # Draw author below the quote - keeping original spacing
            y += 40
            bbox = draw.textbbox((0, 0), author_text, font=font_author)
            line_width = bbox[2] - bbox[0]
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