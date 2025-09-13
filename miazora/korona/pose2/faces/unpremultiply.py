from PIL import Image
import os

def unpremultiply_image(image_path, output_path):
    """
    Unpremultiplies the alpha channel of an RGBA or LA image.

    The color channels (RGB) are divided by the alpha channel to revert them
    to their original, non-premultiplied state.

    Args:
        image_path (str): The path to the input image file.
        output_path (str): The path to save the new image file.
    
    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    try:
        # Open the image file
        img = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image {image_path}: {e}")
        return False

    # Check for an alpha channel
    if img.mode not in ('RGBA', 'LA'):
        print(f"Skipping '{os.path.basename(image_path)}': No alpha channel found.")
        return False

    # Convert to RGBA for consistent pixel access
    img = img.convert("RGBA")
    pixels = img.load()
    width, height = img.size

    # Create a new image to store the unpremultiplied data
    new_img = Image.new('RGBA', (width, height))
    new_pixels = new_img.load()

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            
            # Unpremultiply the color channels
            # Avoid division by zero by checking for alpha > 0
            if a > 0:
                # Normalizing the alpha to a float from 0.0 to 1.0
                a_norm = a / 255.0
                
                # Apply the unpremultiply formula: color / alpha_norm
                r_new = min(255, int(r / a_norm))
                g_new = min(255, int(g / a_norm))
                b_new = min(255, int(b / a_norm))
                
                new_pixels[x, y] = (r_new, g_new, b_new, a)
            else:
                # If alpha is zero, the color should be too
                new_pixels[x, y] = (0, 0, 0, 0)
    
    # Save the new unpremultiplied image
    try:
        new_img.save(output_path, "PNG")
        print(f"Successfully processed '{os.path.basename(image_path)}' -> '{os.path.basename(output_path)}'")
        return True
    except Exception as e:
        print(f"Error saving image to {output_path}: {e}")
        return False

def unpremultiply_folder_recursive(folder_path):
    """
    Recursively finds and unpremultiplies all PNG images in a folder.
    
    Args:
        folder_path (str): The starting directory path.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: Directory not found at {folder_path}")
        return

    print(f"Starting recursive unpremultiplication in '{folder_path}'...")
    print("-" * 50)

    png_files_found = False

    # Walk through the directory and all subdirectories
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith('.png'):
                png_files_found = True
                
                # Construct the full file paths
                original_path = os.path.join(root, filename)
                
                # Create the output filename with a suffix
                name, ext = os.path.splitext(filename)
                output_filename = f"unpr_{name}{ext}"
                output_path = os.path.join(root, output_filename)
                
                unpremultiply_image(original_path, output_path)

    if not png_files_found:
        print("No PNG files found in the specified directory or its subdirectories.")

if __name__ == "__main__":
    # Specify the root directory to start the recursive search
    # This will use the directory where the script is located
    root_directory = "."
    
    unpremultiply_folder_recursive(root_directory)
    print("")
    input("Press Enter to continue...")
