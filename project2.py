import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

# === Image Processing Functions ===
def light_denoise(img):
    return cv2.fastNlMeansDenoisingColored(img, None, 3, 3, 5, 15)

def white_balance(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=1.3, tileGridSize=(8, 8))
    l = clahe.apply(l)
    return cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)

def gentle_sharpen(img):
    blur = cv2.GaussianBlur(img, (0, 0), 1.2)
    return cv2.addWeighted(img, 1.15, blur, -0.15, 0)

def upscale(img, scale=1.5):
    h, w = img.shape[:2]
    return cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)

def stylize_filter(img):
    b, g, r = cv2.split(img)
    r = cv2.add(r, 10)
    g = cv2.add(g, 5)
    return cv2.merge((b, g, r))

def final_polish(pil_img, mode):
    if mode == "Natural":
        pil_img = ImageEnhance.Sharpness(pil_img).enhance(1.05)
        pil_img = ImageEnhance.Brightness(pil_img).enhance(1.02)
        pil_img = ImageEnhance.Contrast(pil_img).enhance(1.08)
    elif mode == "Stylized":
        pil_img = ImageEnhance.Sharpness(pil_img).enhance(1.15)
        pil_img = ImageEnhance.Brightness(pil_img).enhance(1.08)
        pil_img = ImageEnhance.Color(pil_img).enhance(1.15)
        pil_img = ImageEnhance.Contrast(pil_img).enhance(1.1)
    return pil_img

def save_comparison(original, edited, output_path):
    orig_pil = Image.fromarray(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    edited_pil = Image.fromarray(cv2.cvtColor(edited, cv2.COLOR_BGR2RGB))
    max_height = max(orig_pil.height, edited_pil.height)
    total_width = orig_pil.width + edited_pil.width
    combined = Image.new('RGB', (total_width, max_height))
    combined.paste(orig_pil, (0, 0))
    combined.paste(edited_pil, (orig_pil.width, 0))
    combined.save(output_path)

# === GUI Application ===
def process_image(file_path, mode):
    try:
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError("Could not read image.")

        edited = light_denoise(img)
        edited = white_balance(edited)
        edited = gentle_sharpen(edited)
        edited = upscale(edited, scale=1.5)

        if mode == "Stylized":
            edited = stylize_filter(edited)

        pil_img = Image.fromarray(cv2.cvtColor(edited, cv2.COLOR_BGR2RGB))
        polished = final_polish(pil_img, mode)

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        edited_path = os.path.join(os.getcwd(), f"{base_name}_{mode}.jpg")
        polished.save(edited_path)

        comparison_path = os.path.join(os.getcwd(), f"{base_name}_compare.jpg")
        save_comparison(img, edited, comparison_path)

        result_label.config(text=f"✅ Done!\nSaved: {base_name}_{mode}.jpg and _compare.jpg", foreground="green")
    except Exception as e:
        result_label.config(text=f"❌ Error: {str(e)}", foreground="red")


def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
    if not file_path:
        return
    selected_mode = mode_var.get()
    result_label.config(text="Processing...", foreground="blue")
    root.after(100, lambda: process_image(file_path, selected_mode))

# === Build GUI ===
root = tk.Tk()
root.title("Image Enhancer (iPhone 16 Pro Max Style)")
root.geometry("600x600")
root.configure(bg="#1e1e1e")
root.resizable(False, False)

style = ttk.Style()
style.theme_use("clam")
style.configure("TFrame", background="#1e1e1e")
style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Segoe UI", 14))
style.configure("TButton", font=("Segoe UI", 12), padding=10)
style.map("TButton",
          background=[("active", "#3a86ff"), ("!active", "#5e60ce")],
          foreground=[("active", "white"), ("!active", "white")])

frame = ttk.Frame(root, padding=40)
frame.pack(fill='both', expand=True)

title = ttk.Label(frame, text="Choose Editing Style")
title.pack(pady=(0, 10))

mode_var = tk.StringVar(value="Natural")
style_selector = ttk.Combobox(frame, textvariable=mode_var, state="readonly", font=("Segoe UI", 12))
style_selector['values'] = ["Natural", "Stylized"]
style_selector.pack(pady=(0, 20))

upload_btn = ttk.Button(frame, text="📂 Select Image", command=open_file)
upload_btn.pack(pady=10)

result_label = ttk.Label(frame, text="", font=("Segoe UI", 12))
result_label.pack(pady=20)

root.mainloop()
