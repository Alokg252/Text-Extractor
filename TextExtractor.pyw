import tkinter as tk
import subprocess
from copyScrText import notify
COLORS = {
    "primary": "#ca5cdd",
    "secondary": "#110",
}
PYTHON_EXECUTABLE = "pythonw"  # Or the full path to your Python executable
SCRIPT_PATH = r"copyScrText.py"  # Replace with the full path to your script
IMAGE_CROP_SCRIPT = r"ImageCropText.py"  # Path to image crop script


class FloatingIcon:
    def __init__(self):
        """
        Initializes the FloatingIcon class.

        Sets up a floating icon with the following properties:

        - Removes the title bar
        - Sets the size of the floating icon to 44x44
        - Keeps the window on top
        - Keeps the window on top with 20% opacity
        - Sets the background color of the window to #ca5cdd
        - Adds an icon with the text " Tx " and the color #110
        - Binds mouse events for dragging
        - Binds left-click to execute the program
        - Exits the app when pressing the Escape key

        :return: None
        """
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Removes the title bar
        self.root.geometry("44x44+1855+350")  # Set the size of the floating icon
        self.root.attributes("-topmost", True)  # Keeps the window on top
        self.root.attributes("-alpha", 0.2)  # Keeps the window on top
        self.root.configure(bg=COLORS["primary"])  # Background color

        # Add an icon or label

        self.icon = tk.Label(self.root, text=" Tx ", bg=COLORS["secondary"], fg=COLORS["primary"], font='calibri 20 bold', height=1, width=2)

        self.icon.pack(expand=True, ipadx=4, ipady=1)

        # Bind mouse events for dragging
        self.icon.bind("<Button-1>", self.start_drag)
        self.icon.bind("<B1-Motion>", self.drag)
        self.icon.bind("<Enter>", lambda e:self.root.attributes('-alpha',1))
        self.icon.bind("<Leave>", lambda e:self.root.attributes('-alpha',0.2))

        # Bind left-click to execute the program
        self.icon.bind("<Button-3>", self.show_menu)

        # Exit the app when pressing the Escape key
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def start_drag(self, event):
        """Records the starting position of the drag."""
        self.start_x = event.x
        self.start_y = event.y

    def drag(self, event):
        """Moves the floating icon."""
        x = self.root.winfo_x() + (event.x - self.start_x)
        y = self.root.winfo_y() + (event.y - self.start_y)
        self.root.geometry(f"+{x}+{y}")

    def show_menu(self, event):
        """Show a context menu with options."""
        menu = tk.Menu(self.root, tearoff=0, bg=COLORS["secondary"], fg=COLORS["primary"], activebackground=COLORS["primary"], 
                      activeforeground=COLORS["secondary"], font=('helvetica', 13,))
        menu.add_command(label="capture", command=self.execute_capture_screen)
        menu.add_command(label="upload", command=self.execute_image_crop)
        
        # Display the menu at the mouse position
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def execute_capture_screen(self):
        """Executes the screen capture program."""
        try:
            # Run the script and wait for it to complete
            subprocess.run([PYTHON_EXECUTABLE, SCRIPT_PATH], check=True)
            
        except subprocess.CalledProcessError as e:
            notify(title="Error executing program",message=f"Error executing program: {e}")
        except Exception as e:
            notify(title="Unexpected error",message=f"Unexpected error: {e}")

    def execute_image_crop(self):
        """Executes the image crop and text extraction program."""
        try:
            # Run the script and wait for it to complete
            subprocess.run([PYTHON_EXECUTABLE, IMAGE_CROP_SCRIPT], check=True)
            
        except subprocess.CalledProcessError as e:
            notify(title="Error executing program",message=f"Error executing program: {e}")
        except Exception as e:
            notify(title="Unexpected error",message=f"Unexpected error: {e}")

    def run(self):
        """Runs the floating icon app."""
        self.root.mainloop()

if __name__ == "__main__":
    app = FloatingIcon()
    app.run()