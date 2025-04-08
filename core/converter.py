import os
from PIL import Image
import concurrent.futures
import time
from utils.logger import logger

def process_single_image(input_path, output_path, max_width, quality, format):
    try:
        with Image.open(input_path) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            width_percent = max_width / float(img.width)
            height_size = int((float(img.height) * float(width_percent)))
            img = img.resize((max_width, height_size), resample=Image.Resampling.LANCZOS)

            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, format=format.upper(), quality=quality, optimize=True)
            return True, input_path
    except Exception as e:
        logger.error(f"Error processing {input_path}: {e}")
        return False, input_path

def convert_images(input_dir, output_dir, format, max_width, quality, progress_callback=None):
    image_extensions = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff")
    all_files = []
    start_time = time.time()

    logger.info(f"Starting conversion process with parameters:")
    logger.info(f"Input directory: {input_dir}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Format: {format}, Max width: {max_width}, Quality: {quality}")

    for root_dir, _, files in os.walk(input_dir):
        for file in files:
            if file.lower().endswith(image_extensions):
                full_path = os.path.join(root_dir, file)
                all_files.append(full_path)

    total = len(all_files)
    if total == 0:
        logger.warning("No image files found in the input directory")
        return

    logger.info(f"Found {total} images to process")
    processed = 0
    successful = 0
    failed = 0

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for input_path in all_files:
            relative_path = os.path.relpath(input_path, input_dir)
            relative_path = os.path.splitext(relative_path)[0] + f".{format.lower()}"
            output_path = os.path.join(output_dir, relative_path)
            
            futures.append(
                executor.submit(
                    process_single_image,
                    input_path,
                    output_path,
                    max_width,
                    quality,
                    format
                )
            )

        for future in concurrent.futures.as_completed(futures):
            processed += 1
            success, file_path = future.result()
            
            if success:
                successful += 1
                logger.info(f"Successfully processed: {file_path}")
            else:
                failed += 1
                logger.error(f"Failed to process: {file_path}")

            if progress_callback:
                progress = int((processed / total) * 100)
                elapsed_time = time.time() - start_time
                if processed > 0:
                    avg_time_per_file = elapsed_time / processed
                    remaining_files = total - processed
                    estimated_remaining = avg_time_per_file * remaining_files
                else:
                    estimated_remaining = 0
                
                progress_callback(progress, estimated_remaining)

    end_time = time.time()
    total_time = end_time - start_time
    logger.info(f"Conversion completed in {total_time:.2f} seconds")
    logger.info(f"Total files: {total}, Successful: {successful}, Failed: {failed}")
