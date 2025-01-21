import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Image Processor")
        self.root.geometry("1000x1000")

        
        self.input_dir = ""
        self.logo_path = "logo.png"
        self.output_format = tk.StringVar(value="WEBP")
        self.current_image_index = 0
        self.images = []
        self.current_image = None
        self.logo = None
        self.modified_images = {}

        self.create_widgets()

    def create_widgets(self):
        
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=5)
        ttk.Label(input_frame, text="Input Directory:").pack(side=tk.LEFT, padx=5)
        self.input_entry = tk.Entry(input_frame, width=50)
        self.input_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_input).pack(side=tk.LEFT, padx=5)

        
        logo_frame = ttk.Frame(self.root)
        logo_frame.pack(pady=5)
        ttk.Label(logo_frame, text="Logo File Path:").pack(side=tk.LEFT, padx=5)
        self.logo_entry = tk.Entry(logo_frame, width=50)
        self.logo_entry.pack(side=tk.LEFT, padx=5)
        self.logo_entry.insert(tk.END, self.logo_path)
        ttk.Button(logo_frame, text="Browse", command=self.browse_logo).pack(side=tk.LEFT, padx=5)

        
        format_frame = ttk.Frame(self.root)
        format_frame.pack(pady=5)
        ttk.Label(format_frame, text="Output Format:").pack(side=tk.LEFT, padx=5)
        format_menu = ttk.Combobox(format_frame, textvariable=self.output_format, values=["WEBP", "JPEG"])
        format_menu.pack(side=tk.LEFT, padx=5)

        
        process_frame = ttk.Frame(self.root)
        process_frame.pack(pady=10)
        ttk.Button(process_frame, text="Load Images", command=self.start_processing).pack()

        
        self.canvas = tk.Canvas(self.root, width=800, height=800, bg="gray")
        self.canvas.pack(pady=10)

        
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(pady=10)
        ttk.Button(nav_frame, text="Previous", command=self.previous_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Rotate Right", command=lambda: self.rotate_image(90)).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="Rotate Left", command=lambda: self.rotate_image(-90)).pack(side=tk.LEFT, padx=5)
        tk.Button(nav_frame, text="Next", command=self.next_image).pack(side=tk.LEFT, padx=5)

    def browse_input(self):
        directory = filedialog.askdirectory()
        if directory:
            self.input_dir = directory
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(tk.END, directory)

    def browse_logo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
        if file_path:
            self.logo_path = file_path
            self.logo_entry.delete(0, tk.END)
            self.logo_entry.insert(tk.END, file_path)
            self.logo = Image.open(file_path).convert("RGBA")

    def start_processing(self):
        self.images = [os.path.join(self.input_dir, f) for f in os.listdir(self.input_dir)
                       if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp'))]
        self.current_image_index = 0
        self.modified_images = {}   

        if os.path.exists(self.logo_path):
            self.logo = Image.open(self.logo_path).convert("RGBA")
        else:
            self.logo = None

        if self.images:
            self.show_image()
        else:
            messagebox.showinfo("Info", "No images found in the directory.")

    def show_image(self):
        image_path = self.images[self.current_image_index]
        
        if image_path in self.modified_images:
            self.current_image = self.modified_images[image_path]
        else:
            self.current_image = Image.open(image_path).convert("RGBA")
        self.display_current_image()

    def display_current_image(self):
        if self.current_image is not None:
            img = self.current_image.copy()
            img.thumbnail((800, 800), Image.LANCZOS)
            self.photo = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

    def finalize_process(self):
        input_folder_name = os.path.basename(self.input_dir)
        output_dir = os.path.join(self.input_dir, "processed")

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for idx, image_path in enumerate(self.images):
            try:
                img = self.modified_images.get(image_path, Image.open(image_path).convert("RGBA"))
                img = img.resize((1000, 1000), Image.LANCZOS)

                if self.logo:
                    img.paste(self.logo, (0, 0), self.logo)

                output_filename = f"weddkala_{input_folder_name}_{idx + 1}.{self.output_format.get().lower()}"
                output_path = os.path.join(output_dir, output_filename)
                self.save_image_with_size(img, output_path)

            except Exception as e:
                print(f"Error processing {image_path}: {e}")

        
        self.canvas.pack_forget()
        messagebox.showinfo("Info", "All images processed and saved.")

        
        self.reset_application_state()

    def rotate_image(self, angle):
        if self.current_image:
            self.current_image = self.current_image.rotate(angle, expand=True)
            self.modified_images[self.images[self.current_image_index]] = self.current_image
            self.display_current_image()

    def previous_image(self):
        if self.images:
            self.current_image_index = (self.current_image_index - 1) % len(self.images)
            self.show_image()

    def next_image(self):
        if self.images:
            if self.current_image_index == len(self.images) - 1:
                
                self.finalize_process()
                return
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.show_image()

    def save_image_with_size(self, image, output_path):
        quality = 85
        while True:
            image.save(output_path, format=self.output_format.get(), quality=quality)
            if os.path.getsize(output_path) <= 100 * 1024 or quality <= 10:
                break
            quality -= 5

    def reset_application_state(self):
        """Reset application state for new image processing."""
        self.input_dir = ""
        self.current_image_index = 0
        self.images = []
        self.modified_images = {}
        self.output_format.set("WEBP")
        self.logo = None 

        
        self.input_entry.delete(0, tk.END)
        self.logo_entry.delete(0, tk.END)
        self.logo_entry.insert(tk.END, self.logo_path)  
        self.canvas.pack()  


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()
