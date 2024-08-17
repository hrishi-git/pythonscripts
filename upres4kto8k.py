from PIL import Image, ImageFilter
import os

def upres_image(input_path, output_path, scale_factor=2, apply_sharpen=False, sharpen_factor=2.0):
    # Open the input image
    img = Image.open(input_path)
    
    # Calculate the new size
    new_width = img.width * scale_factor
    new_height = img.height * scale_factor
    
    # Resize the image
    upres_img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Apply sharpening if requested
    if apply_sharpen:
        upres_img = upres_img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
    
    # Save the upresed image to the output path
    upres_img.save(output_path)
    print(f"Image saved to {output_path}")

def process_directory(input_dir, output_dir, scale_factor=2, apply_sharpen=False, sharpen_factor=2.0):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process each image in the directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            upres_image(input_path, output_path, scale_factor, apply_sharpen, sharpen_factor)
            print(f"Processed {filename}")

if __name__ == "__main__":
    input_directory = "F:/temp/4kimages"
    output_directory = "F:/temp/8kimages"
    
    # Modify these parameters as needed
    scale_factor = 2  # 4K to 8K
    apply_sharpen = True  # Apply sharpening
    sharpen_factor = 2.0  # Sharpening intensity (adjust as needed)

    process_directory(input_directory, output_directory, scale_factor, apply_sharpen, sharpen_factor)
