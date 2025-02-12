import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
import numpy as np
import os
import struct  # Used to pack/unpack integers (data length)

class SteganoTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Steganography Tool")
        self.root.geometry("800x600")
        # Initialize attributes before creating tabs
        self.image = None          # Original image for embedding
        self.stego_image = None    # Image loaded for extraction
        self.selected_encryption = tk.StringVar(value="Fernet")
        self.custom_key = tk.StringVar()
        self.create_tabs()

    def create_tabs(self):
        notebook = ttk.Notebook(self.root)
        self.embed_tab = ttk.Frame(notebook)
        self.extract_tab = ttk.Frame(notebook)
        notebook.add(self.embed_tab, text="Embed Message")
        notebook.add(self.extract_tab, text="Extract Message")
        notebook.pack(expand=1, fill='both')
        self.setup_embed_tab()
        self.setup_extract_tab()

    def setup_embed_tab(self):
        # Label and button to select an image
        self.embed_img_label = tk.Label(self.embed_tab, text="No image selected")
        self.embed_img_label.pack(pady=10)
        tk.Button(self.embed_tab, text="Select Image", command=self.select_image).pack(pady=5)
        
        # Text widget for secret message input
        tk.Label(self.embed_tab, text="Secret Message:").pack()
        self.message_text = tk.Text(self.embed_tab, height=10, width=60)
        self.message_text.pack(pady=5)
        
        # Dropdown to select encryption method
        tk.Label(self.embed_tab, text="Encryption Method:").pack()
        self.encryption_method_cb = ttk.Combobox(
            self.embed_tab, 
            textvariable=self.selected_encryption,
            values=["Fernet", "None"], 
            state="readonly"
        )
        self.encryption_method_cb.pack(pady=5)
        
        # Entry for encryption key (if using Fernet)
        tk.Label(self.embed_tab, text="Encryption Key (if using Fernet, leave blank to auto-generate):").pack()
        self.key_entry = tk.Entry(self.embed_tab, textvariable=self.custom_key, width=50)
        self.key_entry.pack(pady=5)
        
        # Button to embed the message
        tk.Button(self.embed_tab, text="Embed Message", command=self.embed_message).pack(pady=10)
        self.embed_status_label = tk.Label(self.embed_tab, text="")
        self.embed_status_label.pack(pady=5)

    def setup_extract_tab(self):
        # Label and button to select the stego image
        self.extract_img_label = tk.Label(self.extract_tab, text="No image selected")
        self.extract_img_label.pack(pady=10)
        tk.Button(self.extract_tab, text="Select Stego Image", command=self.select_stego_image).pack(pady=5)
        
        # Entry for decryption key (if used)
        tk.Label(self.extract_tab, text="Encryption Key (if used):").pack()
        self.extract_key_entry = tk.Entry(self.extract_tab, width=50)
        self.extract_key_entry.pack(pady=5)
        
        # Button to extract the hidden message
        tk.Button(self.extract_tab, text="Extract Message", command=self.extract_message).pack(pady=10)
        tk.Label(self.extract_tab, text="Extracted Message:").pack()
        self.extracted_message_text = tk.Text(self.extract_tab, height=10, width=60)
        self.extracted_message_text.pack(pady=5)
        self.extract_status_label = tk.Label(self.extract_tab, text="")
        self.extract_status_label.pack(pady=5)

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png"),
                                                           ("BMP Files", "*.bmp"),
                                                           ("JPEG Files", "*.jpg;*.jpeg")])
        if file_path:
            self.image = Image.open(file_path)
            self.embed_img_label.config(text=os.path.basename(file_path))
        else:
            messagebox.showerror("Error", "No image selected!")

    def select_stego_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png"),
                                                           ("BMP Files", "*.bmp"),
                                                           ("JPEG Files", "*.jpg;*.jpeg")])
        if file_path:
            self.stego_image = Image.open(file_path)
            self.extract_img_label.config(text=os.path.basename(file_path))
        else:
            messagebox.showerror("Error", "No image selected!")

    def embed_message(self):
        if self.image is None:
            messagebox.showerror("Error", "Please select an image first.")
            return
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showerror("Error", "Please enter a secret message.")
            return
        encryption_method = self.selected_encryption.get()
        key = self.custom_key.get().strip()
        if encryption_method == "Fernet":
            if not key:
                key = Fernet.generate_key().decode()
                self.custom_key.set(key)
            else:
                if len(key) != 44:
                    messagebox.showerror("Error", "Invalid key length for Fernet. It should be 44 characters.")
                    return
            fernet = Fernet(key.encode())
            encrypted_message = fernet.encrypt(message.encode())
        else:
            encrypted_message = message.encode()
        try:
            stego_img = self.embed_data_into_image(self.image, encrypted_message)
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
            if save_path:
                stego_img.save(save_path)
                self.embed_status_label.config(text="Message embedded and image saved successfully!")
            else:
                self.embed_status_label.config(text="Embedding cancelled.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to embed message: {e}")

    def extract_message(self):
        if self.stego_image is None:
            messagebox.showerror("Error", "Please select a stego image first.")
            return
        key = self.extract_key_entry.get().strip()
        try:
            extracted_bytes = self.extract_data_from_image(self.stego_image)
            if len(extracted_bytes) < 4:
                messagebox.showerror("Error", "No hidden message found!")
                return
            length_bytes = extracted_bytes[:4]
            message_length = struct.unpack("I", length_bytes)[0]
            encrypted_message = extracted_bytes[4:4+message_length]
            if key:
                if len(key) != 44:
                    messagebox.showerror("Error", "Invalid key length for Fernet. It should be 44 characters.")
                    return
                fernet = Fernet(key.encode())
                decrypted_message = fernet.decrypt(encrypted_message).decode()
            else:
                decrypted_message = encrypted_message.decode()
            self.extracted_message_text.delete("1.0", tk.END)
            self.extracted_message_text.insert(tk.END, decrypted_message)
            self.extract_status_label.config(text="Message extracted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract message: {e}")

    def embed_data_into_image(self, image, data_bytes):
        data_length = len(data_bytes)
        length_bytes = struct.pack("I", data_length)
        full_data = length_bytes + data_bytes
        binary_data = ''.join(format(byte, '08b') for byte in full_data)
        img = image.convert("RGB")
        np_img = np.array(img)
        total_pixels = np_img.size // 3
        if len(binary_data) > total_pixels * 3:
            raise ValueError("Data is too large to embed in the selected image.")
        data_index = 0
        for row in range(np_img.shape[0]):
            for col in range(np_img.shape[1]):
                pixel = list(np_img[row, col])
                for channel in range(3):
                    if data_index < len(binary_data):
                        pixel[channel] = (pixel[channel] & ~1) | int(binary_data[data_index])
                        data_index += 1
                np_img[row, col] = pixel
                if data_index >= len(binary_data):
                    break
            if data_index >= len(binary_data):
                break
        stego_image = Image.fromarray(np_img)
        return stego_image

    def extract_data_from_image(self, image):
        img = image.convert("RGB")
        np_img = np.array(img)
        binary_data = ""
        for row in range(np_img.shape[0]):
            for col in range(np_img.shape[1]):
                pixel = np_img[row, col]
                for channel in range(3):
                    binary_data += str(pixel[channel] & 1)
        all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
        data_bytes = bytearray()
        for byte in all_bytes:
            data_bytes.append(int(byte, 2))
        return bytes(data_bytes)

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganoTool(root)
    root.mainloop()
