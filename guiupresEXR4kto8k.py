import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageFilter
import OpenEXR
import Imath
import numpy as np
import os

# Run the following commands to install the dependencies
# pip install OpenEXR numpy Pillow
# written by Hrishikesh Andurlekar 2024
# upreses all images by scale fact. Originally written to upres 4k EXR renders to 8k. SHould work on all images


def upres_image(input_path, output_path, scale_factor=2, apply_sharpen=False, sharpen_factor=2.0):
    # Check if the file is an EXR file
    if input_path.lower().endswith('.exr'):
        # Open the EXR file
        exr_file = OpenEXR.InputFile(input_path)
        
        # Get the image size and channels
        dw = exr_file.header()['dataWindow']
        size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
        
        # Define the channel type for the EXR file (float32)
        pixel_type = Imath.PixelType(Imath.PixelType.FLOAT)
        
        # Read the image data as numpy arrays
        channel_data = {
            c: np.frombuffer(exr_file.channel(c, pixel_type), dtype=np.float32).reshape(size[::-1])
            for c in ('R', 'G', 'B')
        }
        
        # Resize the image channels
        resized_channels = {
            c: np.array(Image.fromarray(channel_data[c]).resize(
                (int(size[0] * scale_factor), int(size[1] * scale_factor)), Image.LANCZOS)
            )
            for c in channel_data
        }
        
        # Combine the channels back into an EXR image
        exr_header = OpenEXR.Header(resized_channels['R'].shape[1], resized_channels['R'].shape[0])
        exr_out = OpenEXR.OutputFile(output_path, exr_header)
        exr_out.writePixels({
            'R': resized_channels['R'].astype(np.float32).tobytes(),
            'G': resized_channels['G'].astype(np.float32).tobytes(),
            'B': resized_channels['B'].astype(np.float32).tobytes()
        })
        
        exr_out.close()
    else:
        # Handle non-EXR files with Pillow
        img = Image.open(input_path)
        new_width = int(img.width * scale_factor)
        new_height = int(img.height * scale_factor)
        upres_img = img.resize((new_width, new_height), Image.LANCZOS)
        if apply_sharpen:
            upres_img = upres_img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        upres_img.save(output_path)

def process_directory(input_dir, output_dir, scale_factor=2, apply_sharpen=False, sharpen_factor=2.0, progress_callback=None):
    os.makedirs(output_dir, exist_ok=True)
    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.exr'))]
    total_images = len(image_files)
    
    for index, filename in enumerate(image_files):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        upres_image(input_path, output_path, scale_factor, apply_sharpen, sharpen_factor)
        
        # Update progress bar if callback is provided
        if progress_callback:
            progress_callback(index + 1, total_images)
        print(f"Processed {filename}")

class UpscaleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Upscaler")
        
        # Input directory
        self.input_dir_label = tk.Label(root, text="Input Directory:")
        self.input_dir_label.grid(row=0, column=0, padx=10, pady=10)
        self.input_dir_entry = tk.Entry(root, width=50)
        self.input_dir_entry.grid(row=0, column=1, padx=10, pady=10)
        self.browse_input_button = tk.Button(root, text="Browse", command=self.browse_input_dir)
        self.browse_input_button.grid(row=0, column=2, padx=10, pady=10)
        
        # Output directory
        self.output_dir_label = tk.Label(root, text="Output Directory:")
        self.output_dir_label.grid(row=1, column=0, padx=10, pady=10)
        self.output_dir_entry = tk.Entry(root, width=50)
        self.output_dir_entry.grid(row=1, column=1, padx=10, pady=10)
        self.browse_output_button = tk.Button(root, text="Browse", command=self.browse_output_dir)
        self.browse_output_button.grid(row=1, column=2, padx=10, pady=10)
        
        # Scale factor
        self.scale_label = tk.Label(root, text="Scale Factor:")
        self.scale_label.grid(row=2, column=0, padx=10, pady=10)
        self.scale_entry = tk.Entry(root)
        self.scale_entry.grid(row=2, column=1, padx=10, pady=10)
        self.scale_entry.insert(0, "2")  # Default to 2 (4K to 8K)
        
        # Sharpening option
        self.sharpen_var = tk.BooleanVar()
        self.sharpen_check = tk.Checkbutton(root, text="Apply Sharpening", variable=self.sharpen_var)
        self.sharpen_check.grid(row=3, column=0, padx=10, pady=10)
        
        # Sharpening factor
        self.sharpen_factor_label = tk.Label(root, text="Sharpening Intensity:")
        self.sharpen_factor_label.grid(row=4, column=0, padx=10, pady=10)
        self.sharpen_factor_entry = tk.Entry(root)
        self.sharpen_factor_entry.grid(row=4, column=1, padx=10, pady=10)
        self.sharpen_factor_entry.insert(0, "2.0")  # Default sharpening factor
        
        # Progress bar
        self.progress_label = tk.Label(root, text="Progress:")
        self.progress_label.grid(row=5, column=0, padx=10, pady=10)
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.grid(row=5, column=1, padx=10, pady=10)
        
        # Process button
        self.process_button = tk.Button(root, text="Start Processing", command=self.start_processing)
        self.process_button.grid(row=6, column=1, padx=10, pady=10)
    
    def browse_input_dir(self):
        input_dir = filedialog.askdirectory()
        if input_dir:
            self.input_dir_entry.delete(0, tk.END)
            self.input_dir_entry.insert(0, input_dir)
    
    def browse_output_dir(self):
        output_dir = filedialog.askdirectory()
        if output_dir:
            self.output_dir_entry.delete(0, tk.END)
            self.output_dir_entry.insert(0, output_dir)
    
    def start_processing(self):
        input_dir = self.input_dir_entry.get()
        output_dir = self.output_dir_entry.get()
        scale_factor = float(self.scale_entry.get())
        apply_sharpen = self.sharpen_var.get()
        sharpen_factor = float(self.sharpen_factor_entry.get())
        
        if not input_dir or not output_dir:
            messagebox.showerror("Error", "Please select both input and output directories.")
            return
        
        try:
            image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.exr'))]
            self.progress_bar["value"] = 0
            self.progress_bar["maximum"] = len(image_files)
            process_directory(input_dir, output_dir, scale_factor, apply_sharpen, sharpen_factor, self.update_progress)
            messagebox.showinfo("Success", "Processing completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    
    def update_progress(self, current, total):
        self.progress_bar["value"] = current
        self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = UpscaleApp(root)
    root.mainloop()
