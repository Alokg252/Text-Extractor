import tkinter as tk
import pyautogui
import pytesseract
import pyperclip

# Set up pytesseract path (adjust if necessary)
pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'

def notify(title, message):
    from plyer import notification as nf
    nf.notify(
        title=title,
        message=message,
        app_name="Text Extractor",
        app_icon=r"Tesseract-OCR\ak.ico"
    )

class ScreenCaptureApp:
    color = "red"
    def __init__(self):
        self.root = tk.Tk()
        self.start_x = self.start_y = self.end_x = self.end_y = 0
        self.rect_id = None

        # Set up a fullscreen transparent overlay
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)  # Semi-transparent
        self.root.configure(bg='black', cursor='cross')

        # Bind mouse events
        self.root.bind('<ButtonPress-1>', self.on_mouse_down)
        self.root.bind('<B1-Motion>', self.on_mouse_drag)
        self.root.bind('<ButtonRelease-1>', self.on_mouse_up)

    def on_mouse_down(self, event):
        """Start drawing the rectangle."""
        self.start_x, self.start_y = event.x, event.y
        self.rect_id = None

    def on_mouse_drag(self, event):
        """Update the rectangle as the mouse is dragged."""
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(
        self.start_x, self.start_y, event.x, event.y,
        outline=self.color, width=3)

    def on_mouse_up(self, event):
        """Capture the selected area, extract text, and close the app."""
        self.end_x, self.end_y = event.x, event.y

        # Calculate the bounding box
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)


        # Take a screenshot of the selected area
        screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))

        # Extract text using pytesseract
        text = ""
        try:
            text = pytesseract.image_to_string(screenshot).strip()
        except Exception as e:
            notify(title="Error extracting text",message=f"Error extracting text: {e}")
        
        if text:
            pyperclip.copy(text)
            notify(title="Copied", message="Text Copied to Clipboard")
        
        else:
            notify(title="No Text Found", message="No text found in the selected area.")

        # Close the app
        self.root.destroy()

    def start(self):
        """Start the fullscreen app."""

            
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.root.mainloop()


if __name__ == "__main__":
    app = ScreenCaptureApp()
    app.start()
