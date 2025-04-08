import os
from PIL import Image


def convert_images(input_dir, output_dir, format, max_width, quality, progress_callback=None):
    image_extensions = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff")
    all_files = []

    for root_dir, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(image_extensions):
                full_path = os.path.join(root_dir, file)
                all_files.append(full_path)

    total = len(all_files)

    for index, input_path in enumerate(all_files):
        try:
            relative_path = os.path.relpath(input_path, input_dir)
            relative_path = os.path.splitext(relative_path)[0] + f".{format.lower()}"
            output_path = os.path.join(output_dir, relative_path)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with Image.open(input_path) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                width_percent = max_width / float(img.width)
                height_size = int((float(img.height) * float(width_percent)))
                img = img.resize((max_width, height_size), resample=Image.Resampling.LANCZOS)

                img.save(output_path, format=format.upper(), quality=quality, optimize=True)
        except Exception as e:
            print(f"Error processing {input_path}: {e}")

        if progress_callback:
            progress = int((index + 1) / total * 100)
            progress_callback(progress)
