from PIL import Image
import os

def is_premultiplied(image_path):
    """
    Checks if a PNG image has premultiplied alpha.

    Args:
        image_path (str): The path to the image file.

    Returns:
        bool: True if the image appears to have premultiplied alpha, False otherwise.
              Returns None if the image has no alpha channel or is not a PNG.
    """
    try:
        # Open the image file
        img = Image.open(image_path)
    except FileNotFoundError:
        print(f"Error: File not found at {image_path}")
        return None
    except Exception as e:
        print(f"Error opening image {image_path}: {e}")
        return None

    # Check for an alpha channel
    if img.mode not in ('RGBA', 'LA'):
        return None

    # Load the pixel data
    pixels = img.load()
    width, height = img.size

    for y in range(height):
        for x in range(width):
            # Get the pixel data (R, G, B, A)
            if img.mode == 'RGBA':
                r, g, b, a = pixels[x, y]
            elif img.mode == 'LA':
                l, a = pixels[x, y]
                r, g, b = l, l, l # Treat luminance as R, G, B for this check

            # Normalize values from 0-255 to 0-1 for the check
            a_norm = a / 255.0

            # Check for premultiplied alpha condition
            # If any color channel is greater than the alpha, it's not premultiplied
            if (r > a) or (g > a) or (b > a):
                return False

    # If the loop completes without finding a violation, it's likely premultiplied
    return True

def check_folder(folder_path):
    """
    Checks all PNG files in a given folder for premultiplied alpha.

    Args:
        folder_path (str): The path to the folder.
    """
    if not os.path.isdir(folder_path):
        print(f"Error: Directory not found at {folder_path}")
        return

    print(f"Checking PNG files in '{folder_path}'...")
    print("-" * 30)

    png_files_found = False

    # Iterate through all files in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.png'):
            png_files_found = True
            file_path = os.path.join(folder_path, filename)
            result = is_premultiplied(file_path)

            if result is True:
                print(f"'{filename}': Premultiplied Alpha (Likely)")
            elif result is False:
                print(f"'{filename}': Straight Alpha (Definitely)")
            else:
                # result is None
                print(f"'{filename}': No Alpha Channel or an error occurred.")

    if not png_files_found:
        print("No PNG files found in the specified directory.")

if __name__ == "__main__":
    # Specify the folder you want to check
    # You can change this to any path on your system
    folder_to_check = "." # Checks the current directory
    
    # You can also use a specific path, e.g.,
    # folder_to_check = "C:/Users/YourName/Desktop/game_assets"
    
    check_folder(folder_to_check)
    print("")
    input("Press Enter to continue...")
