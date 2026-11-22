import os
import fitz

pdf_path = r"D:\Paper-orchestrate\projects\turbulence_suppression_hilift\output\AeroGuard_Net_CVPR2025.pdf"

if not os.path.exists(pdf_path):
    print(f"Error: {pdf_path} does not exist.")
    exit(1)

doc = fitz.open(pdf_path)
print(f"Checking {pdf_path}")
print(f"Total Pages: {len(doc)}")

total_overlaps = 0

for page_num in range(len(doc)):
    page = doc[page_num]
    print(f"\n--- PAGE {page_num + 1} ---")
    
    # Extract images and their bboxes
    images = page.get_image_info()
    img_bboxes = [fitz.Rect(img['bbox']) for img in images]
    print(f"Images count: {len(img_bboxes)}")
    for idx, ib in enumerate(img_bboxes):
        print(f"  Img {idx+1}: {ib}")

    # Extract text blocks
    blocks = page.get_text("blocks")
    for b in blocks:
        text_rect = fitz.Rect(b[:4])
        text_content = b[4].strip().replace("\n", " ")
        snip = (text_content[:60] + "...") if len(text_content) > 60 else text_content
        
        for idx, ib in enumerate(img_bboxes):
            inter = text_rect.intersect(ib)
            # If intersection area is non-trivial (> 2 sq points)
            if not inter.is_empty and inter.get_area() > 2.0:
                total_overlaps += 1
                print(f"  [OVERLAP DETECTED] with Image {idx+1}!")
                print(f"    Image Box: {ib}")
                print(f"    Text Box:  {text_rect}")
                print(f"    Overlap Area: {inter.get_area():.2f}")
                print(f"    Text: \"{snip}\"")

if total_overlaps == 0:
    print("\nSUCCESS: ZERO text-image overlaps detected across all pages!")
else:
    print(f"\nWARNING: Found {total_overlaps} text-image overlaps!")
