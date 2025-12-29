import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np


# ---- Redness detection (tweak these if needed) ----
MIN_R = 80          # minimum red channel
RED_ADVANTAGE = 30  # how much R must exceed G and B
MIN_SAT = 40        # "saturation" proxy: max(R,G,B) - min(R,G,B)


def compute_redness_percent(pil_img: Image.Image) -> float:
    """
    Returns percent of pixels classified as red-ish.
    Uses a fast RGB heuristic + saturation proxy.
    """
    img = pil_img.convert("RGB")

    # Resize for speed (keeps aspect ratio). Increase if you want more accuracy.
    img.thumbnail((800, 800))

    arr = np.asarray(img, dtype=np.uint8)
    r = arr[:, :, 0].astype(np.int16)
    g = arr[:, :, 1].astype(np.int16)
    b = arr[:, :, 2].astype(np.int16)

    maxc = np.maximum(np.maximum(r, g), b)
    minc = np.minimum(np.minimum(r, g), b)
    sat = maxc - minc  # 0..255

    red_mask = (
        (r >= MIN_R) &
        (r >= g + RED_ADVANTAGE) &
        (r >= b + RED_ADVANTAGE) &
        (sat >= MIN_SAT)
    )

    return float(red_mask.mean() * 100.0)


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Redness Meter")

        self.selected_path = tk.StringVar(value="")
        self.result_text = tk.StringVar(value="Select an image to begin.")
        self.photo_ref = None  # keep a reference to avoid image disappearing

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Select Image", command=self.select_image).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Calculate Redness %", command=self.calculate).pack(side="left", padx=6)

        # Path display
        tk.Label(root, textvariable=self.selected_path, wraplength=520, justify="left").pack(pady=6)

        # Image preview
        self.image_label = tk.Label(root)
        self.image_label.pack(pady=8)

        # Result
        tk.Label(root, textvariable=self.result_text, font=("Arial", 14)).pack(pady=10)

        # Hint
        tk.Label(
            root,
            text="Note: This is a visual redness estimate (pixel-based), not a lab measurement of Red 40.",
            fg="gray"
        ).pack(pady=6)

    def select_image(self):
        path = filedialog.askopenfilename(
            title="Select an Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")]
        )
        if not path:
            return

        self.selected_path.set(path)
        self.result_text.set("Image selected. Click 'Calculate Redness %'.")

        # Preview
        try:
            img = Image.open(path)
            preview = img.copy()
            preview.thumbnail((450, 450))
            self.photo_ref = ImageTk.PhotoImage(preview)
            self.image_label.config(image=self.photo_ref)
        except Exception as e:
            self.image_label.config(image="")
            self.photo_ref = None
            messagebox.showerror("Error", f"Could not open image:\n{e}")

    def calculate(self):
        path = self.selected_path.get().strip()
        if not path:
            messagebox.showwarning("No image", "Please select an image first.")
            return

        try:
            img = Image.open(path)
            redness = compute_redness_percent(img)
            self.result_text.set(f"Redness score: {redness:.2f}%")
        except Exception as e:
            messagebox.showerror("Error", f"Could not process image:\n{e}")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
