import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import pytesseract
import pyperclip
from copyScrText import notify

# Set up pytesseract path
pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'


class ImageCropApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Image Crop & Extract Text")
        self.root.geometry("900x700")
        self.root.configure(bg="#f0f0f0")
        
        self.image = None
        self.photo_image = None
        self.canvas = None
        self.start_x = self.start_y = self.end_x = self.end_y = 0
        self.rect_id = None
        self.original_image = None
        self.image_path = None
        
        # Set up UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Title
        title = tk.Label(self.root, text="Upload & Crop Image", font='calibri 16 bold', bg="#f0f0f0")
        title.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=5)
        
        # Upload button
        upload_btn = tk.Button(button_frame, text="📁 Upload Image", command=self.upload_image, 
                              font='calibri 10', bg="#ca5cdd", fg="white", padx=10, pady=5)
        upload_btn.pack(side=tk.LEFT, padx=5)
        
        # Extract button
        extract_btn = tk.Button(button_frame, text="✂️ Extract Text", command=self.extract_text,
                               font='calibri 10', bg="#4CAF50", fg="white", padx=10, pady=5)
        extract_btn.pack(side=tk.LEFT, padx=5)
        
        # Clear button
        clear_btn = tk.Button(button_frame, text="🔄 Clear", command=self.clear_selection,
                             font='calibri 10', bg="#ff9800", fg="white", padx=10, pady=5)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Instructions
        instructions = tk.Label(self.root, 
                               text="1. Upload an image  2. Click and drag to select a region  3. Extract Text",
                               font='calibri 9', bg="#f0f0f0", fg="#666")
        instructions.pack(pady=5)
        
        # Canvas for image
        canvas_frame = tk.Frame(self.root, bg="white", relief=tk.SUNKEN, bd=2)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0, cursor='cross')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind('<ButtonPress-1>', self.on_mouse_down)
        self.canvas.bind('<B1-Motion>', self.on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_mouse_up)
        
        # Status bar
        self.status_label = tk.Label(self.root, text="Ready to upload image", 
                                     font='calibri 9', bg="#f0f0f0", fg="#666")
        self.status_label.pack(pady=5)
    
    def upload_image(self):
        """Upload an image file."""
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.image_path = file_path
                self.original_image = Image.open(file_path)
                self.display_image(self.original_image)
                self.status_label.config(text=f"Loaded: {file_path.split('/')[-1]}")
                self.rect_id = None  # Clear any previous selection
            except Exception as e:
                notify(title="Error", message=f"Error loading image: {e}")
                self.status_label.config(text="Error loading image")
    
    def display_image(self, image):
        """Display the image on the canvas."""
        if not self.canvas:
            return
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 880
        if canvas_height <= 1:
            canvas_height = 550
        
        # Resize image to fit canvas while maintaining aspect ratio
        image.thumbnail((canvas_width, canvas_height), Image.Resampling.LANCZOS)
        
        # Create PhotoImage
        self.photo_image = ImageTk.PhotoImage(image)
        
        # Display on canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.photo_image, anchor='nw')
        
        # Store the displayed image size for coordinate mapping
        self.displayed_width = image.width
        self.displayed_height = image.height
    
    def on_mouse_down(self, event):
        """Start drawing the selection rectangle."""
        if not self.original_image:
            self.status_label.config(text="Please upload an image first")
            return
        
        self.start_x, self.start_y = event.x, event.y
        self.rect_id = None
    
    def on_mouse_drag(self, event):
        """Update the selection rectangle."""
        if not self.original_image:
            return
        
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline="red", width=2
        )
    
    def on_mouse_up(self, event):
        """Finalize the selection."""
        if not self.original_image:
            return
        
        self.end_x, self.end_y = event.x, event.y
    
    def extract_text(self):
        """Extract text from the selected region."""
        if not self.original_image or self.rect_id is None:
            self.status_label.config(text="Please select a region first")
            notify(title="Error", message="Please select a region to extract text from")
            return
        
        # Calculate the bounding box
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)
        
        # Map canvas coordinates to original image coordinates
        scale_x = self.original_image.width / self.displayed_width
        scale_y = self.original_image.height / self.displayed_height
        
        orig_x1 = int(x1 * scale_x)
        orig_y1 = int(y1 * scale_y)
        orig_x2 = int(x2 * scale_x)
        orig_y2 = int(y2 * scale_y)
        
        # Crop the image
        cropped = self.original_image.crop((orig_x1, orig_y1, orig_x2, orig_y2))
        
        # Extract text
        text = ""
        try:
            text = pytesseract.image_to_string(cropped).strip()
        except Exception as e:
            notify(title="Error", message=f"Error extracting text: {e}")
            self.status_label.config(text="Error extracting text")
            return
        
        if text:
            pyperclip.copy(text)
            notify(title="Success", message="Text extracted and copied to clipboard!")
            self.status_label.config(text=f"Extracted: {len(text)} characters")
        else:
            notify(title="No Text Found", message="No text found in the selected region")
            self.status_label.config(text="No text found in selection")
    
    def clear_selection(self):
        """Clear the current selection."""
        if self.canvas and self.photo_image:
            self.rect_id = None
            self.display_image(self.original_image)
            self.status_label.config(text="Selection cleared")
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


if __name__ == "__main__":
    app = ImageCropApp()
    app.run()
