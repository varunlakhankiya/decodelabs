import sys
import os
import random
import string
import math
import tkinter as tk
from tkinter import ttk, messagebox

# Windows-specific immersive dark mode integration
try:
    import ctypes
    # DWM API constants
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_USE_IMMERSIVE_DARK_MODE_OLD = 19
except ImportError:
    ctypes = None

def apply_immersive_dark_mode(window):
    if ctypes is None:
        return
    window.update()
    try:
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        if hwnd == 0:
            hwnd = window.winfo_id()
        
        # Try new Windows 11 build first
        rendering_policy = ctypes.c_int(1)
        res = ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 
            DWMWA_USE_IMMERSIVE_DARK_MODE, 
            ctypes.byref(rendering_policy), 
            ctypes.sizeof(rendering_policy)
        )
        if res != 0:
            # Fallback to older Windows 10 build
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 
                DWMWA_USE_IMMERSIVE_DARK_MODE_OLD, 
                ctypes.byref(rendering_policy), 
                ctypes.sizeof(rendering_policy)
            )
    except Exception as e:
        print("Failed to apply dark mode window borders:", e)

# --- Cryptographic Algorithms ---

def caesar_encrypt_char(char, shift):
    """Encrypts a single character using Caesar cipher logic."""
    o = ord(char)
    if 65 <= o <= 90:  # Uppercase
        return chr((o - 65 + shift) % 26 + 65)
    elif 97 <= o <= 122:  # Lowercase
        return chr((o - 97 + shift) % 26 + 97)
    return char  # Edge case: spaces/punctuation/numbers pass through

def caesar_encrypt(text, shift):
    return "".join(caesar_encrypt_char(c, shift) for c in text)

def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)

def simple_xor_cipher(data_bytes, key_bytes):
    """Simple repeating-key XOR."""
    if not key_bytes:
        return data_bytes
    out = bytearray(len(data_bytes))
    for i in range(len(data_bytes)):
        out[i] = data_bytes[i] ^ key_bytes[i % len(key_bytes)]
    return bytes(out)

# Simple S-Box mapping for confusion (reversible non-linear byte transformation)
S_BOX = [
    (i * 3 + 107) % 256 for i in range(256)
]
INV_S_BOX = [0] * 256
for i, val in enumerate(S_BOX):
    INV_S_BOX[val] = i

def spn_block_cipher_encrypt(data_bytes, key_bytes):
    """
    A simple 128-bit block size SPN (Substitution-Permutation Network) 
    cipher round to demonstrate confusion and diffusion (avalanche effect).
    Padded to 16 bytes (128-bit blocks).
    """
    if not key_bytes:
        return data_bytes
    
    # Pad input to 16-byte blocks
    pad_len = 16 - (len(data_bytes) % 16)
    padded = data_bytes + bytes([pad_len] * pad_len)
    
    # Ensure key is at least 16 bytes
    k = key_bytes
    while len(k) < 16:
        k += key_bytes
    k = k[:16]
    
    out = bytearray()
    for block_idx in range(0, len(padded), 16):
        block = bytearray(padded[block_idx : block_idx + 16])
        
        # Round 1: Key Addition (XOR)
        for i in range(16):
            block[i] ^= k[i]
            
        # Round 2: Substitution (S-box)
        for i in range(16):
            block[i] = S_BOX[block[i]]
            
        # Round 3: Permutation (Diffusion shift / byte shuffle)
        # Shift rows / rotate block
        temp = block[:]
        for i in range(16):
            block[i] = temp[(i * 5 + 3) % 16]
            
        # Round 4: Final Key Addition (XOR with shifted key)
        for i in range(16):
            block[i] ^= k[(i + 7) % 16]
            
        out.extend(block)
    return bytes(out)

def spn_block_cipher_decrypt(data_bytes, key_bytes):
    """Decrypt SPN block cipher (reverse operations)."""
    if not key_bytes or len(data_bytes) % 16 != 0:
        return data_bytes
        
    k = key_bytes
    while len(k) < 16:
        k += key_bytes
    k = k[:16]
    
    out = bytearray()
    for block_idx in range(0, len(data_bytes), 16):
        block = bytearray(data_bytes[block_idx : block_idx + 16])
        
        # Round 4 inverse: Key Addition
        for i in range(16):
            block[i] ^= k[(i + 7) % 16]
            
        # Round 3 inverse: Reverse Permutation
        temp = block[:]
        for i in range(16):
            block[(i * 5 + 3) % 16] = temp[i]
            
        # Round 2 inverse: S-box inverse
        for i in range(16):
            block[i] = INV_S_BOX[block[i]]
            
        # Round 1 inverse: Key Addition
        for i in range(16):
            block[i] ^= k[i]
            
        out.extend(block)
        
    # Remove padding
    if len(out) > 0:
        pad_len = out[-1]
        if 0 < pad_len <= 16:
            # check padding validity
            if all(x == pad_len for x in out[-pad_len:]):
                out = out[:-pad_len]
                
    return bytes(out)

def get_hamming_distance(bytes_a, bytes_b):
    """Calculates the Hamming distance (number of bit differences) between two byte sequences."""
    min_len = min(len(bytes_a), len(bytes_b))
    max_len = max(len(bytes_a), len(bytes_b))
    dist = (max_len - min_len) * 8
    for i in range(min_len):
        xor = bytes_a[i] ^ bytes_b[i]
        dist += bin(xor).count('1')
    return dist

def get_entropy(data_bytes):
    """Calculates Shannon entropy of byte data."""
    if not data_bytes:
        return 0.0
    freq = {}
    for b in data_bytes:
        freq[b] = freq.get(b, 0) + 1
    entropy = 0.0
    for count in freq.values():
        p = count / len(data_bytes)
        entropy -= p * math.log2(p)
    return entropy

# --- GUI Application ---

class EnigmaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Enigma Cryptographic Suite | DecodeLabs")
        self.geometry("1100x750")
        self.minsize(1000, 680)
        self.configure(bg="#0A0E17")
        
        # Apply dark mode title bars
        apply_immersive_dark_mode(self)
        
        # Style Configuration
        self.setup_styles()
        
        # App Variables
        self.caesar_shift = tk.IntVar(value=3)
        self.xor_key = tk.StringVar(value="DecodeLabs128BitKey")
        self.modern_mode = tk.StringVar(value="SPN")  # SPN or XOR
        self.avalanche_input = tk.StringVar(value="DecodeLabsSecurity")
        self.avalanche_mutated = tk.StringVar(value="DecodeLabsSecur1ty") # 1-character difference
        
        # Layout Setup
        self.create_layout()
        
        # Default bindings
        self.bind_events()
        
        # Trigger initial calculation
        self.on_caesar_input_change()
        self.on_modern_input_change()

    def setup_styles(self):
        # Configure overall ttk styling
        style = ttk.Style()
        style.theme_use("clam")
        
        # Colors:
        # Backgrounds: #0A0E17 (app), #111827 (card/panel), #1F2937 (header/widget)
        # Accents: #00F0FF (electric cyan), #7000FF (neon violet), #00FF66 (neon green)
        # Text: #F3F4F6 (high contrast), #9CA3AF (low contrast)
        
        style.configure(".", bg="#0A0E17", fg="#F3F4F6", font=("Segoe UI", 10))
        
        style.configure("TFrame", background="#0A0E17")
        style.configure("Card.TFrame", background="#111827", relief="flat", borderwidth=0)
        
        # Tabs
        style.configure("TNotebook", background="#0A0E17", borderwidth=0, padding=0)
        style.configure("TNotebook.Tab", background="#111827", foreground="#9CA3AF", padding=(20, 8), font=("Segoe UI", 11, "bold"), borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", "#00F0FF"), ("active", "#1F2937")],
                  foreground=[("selected", "#0A0E17"), ("active", "#F3F4F6")])
        
        # Custom button
        style.configure("Cyber.TButton", background="#7000FF", foreground="#F3F4F6", font=("Segoe UI", 10, "bold"), borderwidth=0, padding=(12, 6))
        style.map("Cyber.TButton",
                  background=[("active", "#00F0FF")],
                  foreground=[("active", "#0A0E17")])
                  
        style.configure("CyberCyan.TButton", background="#00F0FF", foreground="#0A0E17", font=("Segoe UI", 10, "bold"), borderwidth=0, padding=(12, 6))
        style.map("CyberCyan.TButton",
                  background=[("active", "#7000FF")],
                  foreground=[("active", "#F3F4F6")])

    def create_layout(self):
        # Header Banner
        header = tk.Frame(self, bg="#111827", height=70)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        title_lbl = tk.Label(
            header, 
            text="🔒 ENIGMA CRYPTOGRAPHIC SUITE", 
            font=("Segoe UI", 16, "bold"), 
            bg="#111827", 
            fg="#00F0FF"
        )
        title_lbl.pack(side="left", padx=20, pady=15)
        
        sub_lbl = tk.Label(
            header, 
            text="PROJECT 2: CONFIDENTIALITY ENGINE | DECODELABS INTERN SHIELD", 
            font=("Segoe UI", 9, "bold"), 
            bg="#111827", 
            fg="#7000FF"
        )
        sub_lbl.pack(side="right", padx=20, pady=18)
        
        # Main Notebook Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.caesar_tab = ttk.Frame(self.notebook, style="TFrame")
        self.modern_tab = ttk.Frame(self.notebook, style="TFrame")
        
        self.notebook.add(self.caesar_tab, text=" CLASSICAL (CAESAR) ")
        self.notebook.add(self.modern_tab, text=" MODERN (128-BIT SHIELD) ")
        
        # Build Panels
        self.build_caesar_tab()
        self.build_modern_tab()

    # --- Caesar Cipher Layout and Implementation ---
    
    def build_caesar_tab(self):
        # Left Panel (Input / Output Card)
        left_panel = ttk.Frame(self.caesar_tab, style="Card.TFrame")
        left_panel.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        # Inner padding frame
        inner_left = tk.Frame(left_panel, bg="#111827")
        inner_left.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(inner_left, text="IPO CYCLE: CRYPTOGRAPHIC INPUT", font=("Segoe UI", 12, "bold"), bg="#111827", fg="#00F0FF").pack(anchor="w", pady=(0, 10))
        
        # Text Input
        tk.Label(inner_left, text="Plaintext (Raw Data):", font=("Segoe UI", 9), bg="#111827", fg="#9CA3AF").pack(anchor="w")
        self.caesar_input = tk.Text(inner_left, height=8, bg="#1F2937", fg="#F3F4F6", insertbackground="#00F0FF", relief="flat", font=("Consolas", 11), padx=10, pady=10)
        self.caesar_input.insert("1.0", "Hello World! Master the Caesar Cipher logic to build a strong digital shield.")
        self.caesar_input.pack(fill="x", pady=(5, 15))
        
        # Shift Key Control
        shift_frame = tk.Frame(inner_left, bg="#111827")
        shift_frame.pack(fill="x", pady=5)
        
        tk.Label(shift_frame, text="Symmetric Shift Key (1 - 25):", font=("Segoe UI", 9), bg="#111827", fg="#9CA3AF").pack(side="left")
        self.shift_value_lbl = tk.Label(shift_frame, textvariable=self.caesar_shift, font=("Segoe UI", 11, "bold"), bg="#111827", fg="#00FF66")
        self.shift_value_lbl.pack(side="left", padx=10)
        
        # Styled Canvas Slider
        self.slider_canvas = tk.Canvas(inner_left, height=35, bg="#111827", highlightthickness=0)
        self.slider_canvas.pack(fill="x", pady=(0, 15))
        self.slider_canvas.bind("<B1-Motion>", self.on_slider_drag)
        self.slider_canvas.bind("<Button-1>", self.on_slider_click)
        self.slider_canvas.bind("<Configure>", lambda e: self.draw_custom_slider())
        
        # Ciphertext Output
        tk.Label(inner_left, text="Ciphertext (Secured Output):", font=("Segoe UI", 9), bg="#111827", fg="#9CA3AF").pack(anchor="w")
        self.caesar_output = tk.Text(inner_left, height=8, bg="#0A0E17", fg="#00FF66", relief="flat", font=("Consolas", 11), padx=10, pady=10, state="disabled")
        self.caesar_output.pack(fill="x", pady=(5, 10))
        
        # Copy button
        copy_btn = ttk.Button(inner_left, text="Copy Ciphertext", style="CyberCyan.TButton", command=self.copy_caesar_output)
        copy_btn.pack(anchor="e")
        
        # Right Panel (Decryption Enclave / Math Tracer)
        right_panel = ttk.Frame(self.caesar_tab, style="Card.TFrame")
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        inner_right = tk.Frame(right_panel, bg="#111827")
        inner_right.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Verification Enclave
        verif_header = tk.Frame(inner_right, bg="#111827")
        verif_header.pack(fill="x")
        
        tk.Label(verif_header, text="DECRYPTION VALIDATION", font=("Segoe UI", 12, "bold"), bg="#111827", fg="#7000FF").pack(side="left")
        
        self.verif_badge = tk.Canvas(verif_header, width=150, height=26, bg="#111827", highlightthickness=0)
        self.verif_badge.pack(side="right")
        
        tk.Label(inner_right, text="Decrypted Plaintext (D_n(C) Verification):", font=("Segoe UI", 9), bg="#111827", fg="#9CA3AF").pack(anchor="w", pady=(10, 5))
        self.caesar_decrypted = tk.Text(inner_right, height=5, bg="#0A0E17", fg="#F3F4F6", relief="flat", font=("Consolas", 10), padx=8, pady=8, state="disabled")
        self.caesar_decrypted.pack(fill="x", pady=(0, 15))
        
        # Math Tracer Card
        tk.Label(inner_right, text="CRYPTOGRAPHIC ENGINE: LIVE MATH TRACER", font=("Segoe UI", 11, "bold"), bg="#111827", fg="#00F0FF").pack(anchor="w", pady=(5, 5))
        
        self.tracer_canvas = tk.Canvas(inner_right, bg="#0A0E17", highlightthickness=1, highlightbackground="#1F2937", height=240)
        self.tracer_canvas.pack(fill="both", expand=True, pady=5)
        self.tracer_canvas.bind("<Configure>", lambda e: self.draw_math_trace())

    def draw_custom_slider(self):
        canvas = self.slider_canvas
        canvas.delete("all")
        
        w = canvas.winfo_width()
        if w < 10:
            return
            
        h = canvas.winfo_height()
        
        # Draw track
        track_y = h // 2
        canvas.create_line(15, track_y, w - 15, track_y, fill="#1F2937", width=6, capstyle="round")
        
        # Calculate handle position based on shift
        val = self.caesar_shift.get()
        percentage = (val - 1) / 24.0
        handle_x = 15 + percentage * (w - 30)
        
        # Color filled portion
        canvas.create_line(15, track_y, handle_x, track_y, fill="#00F0FF", width=6, capstyle="round")
        
        # Draw ticks/numbers
        for tick in [1, 5, 10, 13, 15, 20, 25]:
            tick_percentage = (tick - 1) / 24.0
            tick_x = 15 + tick_percentage * (w - 30)
            canvas.create_line(tick_x, track_y - 6, tick_x, track_y + 6, fill="#1F2937", width=2)
            canvas.create_text(tick_x, track_y + 14, text=str(tick), fill="#9CA3AF", font=("Segoe UI", 7))
            
        # Draw handle
        canvas.create_oval(handle_x - 10, track_y - 10, handle_x + 10, track_y + 10, fill="#7000FF", outline="#00F0FF", width=2)

    def on_slider_drag(self, event):
        w = self.slider_canvas.winfo_width()
        if w < 30:
            return
        x = event.x
        # Clamp x
        x = max(15, min(x, w - 15))
        percentage = (x - 15) / (w - 30)
        val = int(round(1 + percentage * 24))
        self.caesar_shift.set(val)
        self.draw_custom_slider()
        self.on_caesar_input_change()

    def on_slider_click(self, event):
        w = self.slider_canvas.winfo_width()
        if w < 30:
            return
        x = event.x
        x = max(15, min(x, w - 15))
        percentage = (x - 15) / (w - 30)
        val = int(round(1 + percentage * 24))
        self.caesar_shift.set(val)
        self.draw_custom_slider()
        self.on_caesar_input_change()

    def on_caesar_input_change(self, event=None):
        plaintext = self.caesar_input.get("1.0", "end-1c")
        shift = self.caesar_shift.get()
        
        ciphertext = caesar_encrypt(plaintext, shift)
        decrypted = caesar_decrypt(ciphertext, shift)
        
        # Update UI text outputs
        self.caesar_output.config(state="normal")
        self.caesar_output.delete("1.0", "end")
        self.caesar_output.insert("1.0", ciphertext)
        self.caesar_output.config(state="disabled")
        
        self.caesar_decrypted.config(state="normal")
        self.caesar_decrypted.delete("1.0", "end")
        self.caesar_decrypted.insert("1.0", decrypted)
        self.caesar_decrypted.config(state="disabled")
        
        # Update badge
        self.update_verif_badge(plaintext == decrypted and len(plaintext) > 0)
        
        # Redraw mathematical trace
        self.draw_math_trace()

    def update_verif_badge(self, is_valid):
        self.verif_badge.delete("all")
        w = self.verif_badge.winfo_width()
        h = self.verif_badge.winfo_height()
        if w < 10:
            w, h = 150, 26
            
        if is_valid:
            # Draw green badge
            self.verif_badge.create_rectangle(2, 2, w - 2, h - 2, fill="#052E16", outline="#00FF66", width=1)
            self.verif_badge.create_text(w // 2, h // 2, text="✓ VALIDATED", fill="#00FF66", font=("Segoe UI", 8, "bold"))
        else:
            # Draw warning/empty badge
            self.verif_badge.create_rectangle(2, 2, w - 2, h - 2, fill="#450A0A", outline="#FF0055", width=1)
            self.verif_badge.create_text(w // 2, h // 2, text="✗ EMPTY/ERROR", fill="#FF0055", font=("Segoe UI", 8, "bold"))

    def copy_caesar_output(self):
        self.clipboard_clear()
        self.clipboard_append(self.caesar_output.get("1.0", "end-1c"))
        messagebox.showinfo("Success", "Ciphertext copied to clipboard!")

    def draw_math_trace(self):
        canvas = self.tracer_canvas
        canvas.delete("all")
        
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w < 10:
            return
            
        plaintext = self.caesar_input.get("1.0", "end-1c")
        if not plaintext:
            canvas.create_text(w//2, h//2, text="[ Type plaintext to visualize shift logic ]", fill="#9CA3AF", font=("Segoe UI", 10, "italic"))
            return
            
        # Get the very last character typed/entered
        last_char = plaintext[-1]
        shift = self.caesar_shift.get()
        o = ord(last_char)
        
        is_upper = 65 <= o <= 90
        is_lower = 97 <= o <= 122
        
        steps = []
        if is_upper:
            base = 65
            idx = o - 65
            shifted = idx + shift
            mod = shifted % 26
            final_ascii = mod + 65
            cipher_char = chr(final_ascii)
            
            steps = [
                f"Input Character: '{last_char}'",
                f"ASCII Code: ord('{last_char}') = {o}",
                f"Subtract Base ({base}): {o} - {base} = {idx}",
                f"Add Shift Key (+{shift}): {idx} + {shift} = {shifted}",
                f"Modulo Alphabet Size (% 26): {shifted} % 26 = {mod}",
                f"Add Base ({base}): {mod} + {base} = {final_ascii}",
                f"Cipher Character: chr({final_ascii}) = '{cipher_char}'"
            ]
        elif is_lower:
            base = 97
            idx = o - 97
            shifted = idx + shift
            mod = shifted % 26
            final_ascii = mod + 97
            cipher_char = chr(final_ascii)
            
            steps = [
                f"Input Character: '{last_char}'",
                f"ASCII Code: ord('{last_char}') = {o}",
                f"Subtract Base ({base}): {o} - {base} = {idx}",
                f"Add Shift Key (+{shift}): {idx} + {shift} = {shifted}",
                f"Modulo Alphabet Size (% 26): {shifted} % 26 = {mod}",
                f"Add Base ({base}): {mod} + {base} = {final_ascii}",
                f"Cipher Character: chr({final_ascii}) = '{cipher_char}'"
            ]
        else:
            steps = [
                f"Input Character: '{last_char}'",
                f"ASCII Code: ord('{last_char}') = {o}",
                "Condition Check: Non-alphabetic character detected.",
                "Transformation: Pass through directly without modification.",
                f"Cipher Character: '{last_char}'"
            ]
            
        # Draw steps vertically
        y_start = 25
        y_spacing = 28
        
        for i, step in enumerate(steps):
            is_last = (i == len(steps) - 1)
            is_first = (i == 0)
            
            text_color = "#00FF66" if is_last else ("#00F0FF" if is_first else "#F3F4F6")
            font_style = ("Consolas", 9, "bold") if (is_last or is_first) else ("Consolas", 9)
            
            # Draw connection line
            if i < len(steps) - 1:
                canvas.create_line(50, y_start + i * y_spacing + 10, 50, y_start + (i+1) * y_spacing - 10, fill="#1F2937", arrow="last", arrowshape=(6,8,3))
            
            # Draw Step Dot
            dot_color = "#00FF66" if is_last else ("#00F0FF" if is_first else "#7000FF")
            canvas.create_oval(45, y_start + i * y_spacing - 5, 55, y_start + i * y_spacing + 5, fill=dot_color, outline="")
            
            # Draw Step Text
            canvas.create_text(70, y_start + i * y_spacing, text=step, anchor="w", fill=text_color, font=font_style)

    # --- Modern XOR Layout and Implementation ---
    
    def build_modern_tab(self):
        # Left Panel: Data & Keys Entry
        left_panel = ttk.Frame(self.modern_tab, style="Card.TFrame")
        left_panel.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        inner_left = tk.Frame(left_panel, bg="#111827")
        inner_left.pack(fill="both", expand=True, padx=20, pady=15)
        
        tk.Label(inner_left, text="MODERN CRYPTOGRAPHY ENGINE", font=("Segoe UI", 12, "bold"), bg="#111827", fg="#00F0FF").pack(anchor="w", pady=(0, 5))
        
        # Plaintext Input
        tk.Label(inner_left, text="Plaintext Input:", font=("Segoe UI", 9), bg="#111827", fg="#9CA3AF").pack(anchor="w")
        self.modern_input = tk.Text(inner_left, height=4, bg="#1F2937", fg="#F3F4F6", insertbackground="#00F0FF", relief="flat", font=("Consolas", 10), padx=8, pady=8)
        self.modern_input.insert("1.0", "TopSecretShield")
        self.modern_input.pack(fill="x", pady=(5, 10))
        
        # 128-bit Key Panel
        key_header = tk.Frame(inner_left, bg="#111827")
        key_header.pack(fill="x", pady=(5, 0))
        tk.Label(key_header, text="128-bit Symmetric Key (16 Bytes / Chars):", font=("Segoe UI", 9), bg="#111827", fg="#9CA3AF").pack(side="left")
        
        gen_key_btn = ttk.Button(key_header, text="Gen 128-bit Key", style="Cyber.TButton", command=self.generate_secure_key)
        gen_key_btn.pack(side="right")
        
        self.key_entry = tk.Entry(inner_left, textvariable=self.xor_key, bg="#1F2937", fg="#00FF66", insertbackground="#00F0FF", relief="flat", font=("Consolas", 10), bd=5)
        self.key_entry.pack(fill="x", pady=(5, 10))
        
        # Mode Selection: Simple XOR vs. SPN Block Cipher (Confusion + Diffusion)
        mode_frame = tk.Frame(inner_left, bg="#111827")
        mode_frame.pack(fill="x", pady=(5, 10))
        
        tk.Label(mode_frame, text="Cryptographic Engine Mode:", font=("Segoe UI", 9, "bold"), bg="#111827", fg="#9CA3AF").pack(side="left")
        
        xor_btn = tk.Radiobutton(mode_frame, text="Simple XOR", variable=self.modern_mode, value="XOR", bg="#111827", fg="#F3F4F6", selectcolor="#1F2937", font=("Segoe UI", 9), command=self.on_modern_input_change)
        xor_btn.pack(side="left", padx=10)
        
        spn_btn = tk.Radiobutton(mode_frame, text="SPN (Confusion + Diffusion)", variable=self.modern_mode, value="SPN", bg="#111827", fg="#F3F4F6", selectcolor="#1F2937", font=("Segoe UI", 9), command=self.on_modern_input_change)
        spn_btn.pack(side="left", padx=10)
        
        # Output Text Hex
        tk.Label(inner_left, text="Secure Ciphertext Output (Hexadecimal representation):", font=("Segoe UI", 9), bg="#111827", fg="#9CA3AF").pack(anchor="w")
        self.modern_output_hex = tk.Text(inner_left, height=4, bg="#0A0E17", fg="#00FF66", relief="flat", font=("Consolas", 10), padx=8, pady=8, state="disabled")
        self.modern_output_hex.pack(fill="x", pady=(5, 10))
        
        # Decrypted Plaintext
        tk.Label(inner_left, text="Decrypted Plaintext:", font=("Segoe UI", 9), bg="#111827", fg="#9CA3AF").pack(anchor="w")
        self.modern_decrypted = tk.Text(inner_left, height=4, bg="#0A0E17", fg="#F3F4F6", relief="flat", font=("Consolas", 10), padx=8, pady=8, state="disabled")
        self.modern_decrypted.pack(fill="x", pady=(5, 0))
        
        # Right Panel: Analysis & Diffusion Simulator
        right_panel = ttk.Frame(self.modern_tab, style="Card.TFrame")
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        inner_right = tk.Frame(right_panel, bg="#111827")
        inner_right.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Bitwise alignment visualization
        tk.Label(inner_right, text="BITWISE ENGINE ANALYSIS (First 8 Bytes)", font=("Segoe UI", 11, "bold"), bg="#111827", fg="#00F0FF").pack(anchor="w", pady=(0, 5))
        
        self.bitwise_display = tk.Text(inner_right, height=8, bg="#0A0E17", fg="#9CA3AF", relief="flat", font=("Consolas", 9), padx=8, pady=8, state="disabled")
        self.bitwise_display.pack(fill="x", pady=(0, 15))
        
        # Avalanche & Diffusion simulator
        tk.Label(inner_right, text="AVALANCHE EFFECT & DIFFUSION TESTER", font=("Segoe UI", 11, "bold"), bg="#111827", fg="#7000FF").pack(anchor="w", pady=(5, 5))
        
        diffusion_desc = (
            "To prove mathematical diffusion, modify one character in the input "
            "and observe how many bits shift in the ciphertext."
        )
        tk.Label(inner_right, text=diffusion_desc, font=("Segoe UI", 8, "italic"), bg="#111827", fg="#9CA3AF", wraplength=450, justify="left").pack(anchor="w", pady=(0, 8))
        
        # Diffusion inputs
        diff_inputs_frame = tk.Frame(inner_right, bg="#111827")
        diff_inputs_frame.pack(fill="x", pady=2)
        
        tk.Label(diff_inputs_frame, text="Original Str:", font=("Segoe UI", 9), bg="#111827", fg="#9CA3AF").grid(row=0, column=0, sticky="w", pady=2)
        original_entry = tk.Entry(diff_inputs_frame, textvariable=self.avalanche_input, bg="#1F2937", fg="#F3F4F6", insertbackground="#00F0FF", relief="flat", font=("Consolas", 9), width=35)
        original_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        tk.Label(diff_inputs_frame, text="Mutated Str:", font=("Segoe UI", 9), bg="#111827", fg="#9CA3AF").grid(row=1, column=0, sticky="w", pady=2)
        mutated_entry = tk.Entry(diff_inputs_frame, textvariable=self.avalanche_mutated, bg="#1F2937", fg="#F3F4F6", insertbackground="#00F0FF", relief="flat", font=("Consolas", 9), width=35)
        mutated_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        # Diffusion Output Stats
        self.diffusion_metric_frame = tk.Frame(inner_right, bg="#111827")
        self.diffusion_metric_frame.pack(fill="both", expand=True, pady=10)
        
        self.diffusion_bar_canvas = tk.Canvas(self.diffusion_metric_frame, height=22, bg="#0A0E17", highlightthickness=0)
        self.diffusion_bar_canvas.pack(fill="x", pady=(5, 5))
        
        self.diffusion_lbl = tk.Label(self.diffusion_metric_frame, text="Diffusion Stats: -", font=("Segoe UI", 9, "bold"), bg="#111827", fg="#00FF66")
        self.diffusion_lbl.pack(anchor="w")
        
        self.entropy_lbl = tk.Label(self.diffusion_metric_frame, text="Plaintext Entropy: - | Ciphertext Entropy: -", font=("Segoe UI", 9), bg="#111827", fg="#9CA3AF")
        self.entropy_lbl.pack(anchor="w", pady=2)
        
    def generate_secure_key(self):
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        new_key = "".join(random.choice(chars) for _ in range(16))
        self.xor_key.set(new_key)
        self.on_modern_input_change()
        
    def on_modern_input_change(self, event=None):
        plaintext = self.modern_input.get("1.0", "end-1c")
        key = self.xor_key.get()
        mode = self.modern_mode.get()
        
        data_bytes = plaintext.encode("utf-8")
        key_bytes = key.encode("utf-8")
        
        if mode == "XOR":
            ciphertext_bytes = simple_xor_cipher(data_bytes, key_bytes)
            decrypted_bytes = simple_xor_cipher(ciphertext_bytes, key_bytes)
        else: # SPN
            ciphertext_bytes = spn_block_cipher_encrypt(data_bytes, key_bytes)
            decrypted_bytes = spn_block_cipher_decrypt(ciphertext_bytes, key_bytes)
            
        # Update output Hex
        self.modern_output_hex.config(state="normal")
        self.modern_output_hex.delete("1.0", "end")
        self.modern_output_hex.insert("1.0", ciphertext_bytes.hex())
        self.modern_output_hex.config(state="disabled")
        
        # Update decrypted output
        try:
            decrypted_text = decrypted_bytes.decode("utf-8")
        except UnicodeDecodeError:
            decrypted_text = decrypted_bytes.decode("utf-8", errors="replace")
            
        self.modern_decrypted.config(state="normal")
        self.modern_decrypted.delete("1.0", "end")
        self.modern_decrypted.insert("1.0", decrypted_text)
        self.modern_decrypted.config(state="disabled")
        
        # Draw bitwise visualization (first 8 bytes)
        self.update_bitwise_display(data_bytes, key_bytes, ciphertext_bytes)
        
        # Calculate Diffusion
        self.update_diffusion_metrics()

    def update_bitwise_display(self, data_bytes, key_bytes, ciphertext_bytes):
        self.bitwise_display.config(state="normal")
        self.bitwise_display.delete("1.0", "end")
        
        limit = min(8, len(data_bytes))
        if limit == 0:
            self.bitwise_display.insert("1.0", "[ No input bytes to analyze ]")
            self.bitwise_display.config(state="disabled")
            return
            
        lines = []
        lines.append("Byte Alignment Analysis (XOR Mapping):")
        lines.append("-" * 55)
        
        for idx in range(limit):
            pb = data_bytes[idx]
            kb = key_bytes[idx % len(key_bytes)] if key_bytes else 0
            cb = ciphertext_bytes[idx] if idx < len(ciphertext_bytes) else 0
            
            p_bin = f"{pb:08b}"
            k_bin = f"{kb:08b}"
            c_bin = f"{cb:08b}"
            
            p_char = repr(chr(pb)) if 32 <= pb <= 126 else "\\x{:02x}".format(pb)
            c_hex = f"{cb:02x}"
            
            lines.append(f"Byte {idx}: Plaintext {p_char:<4} ({p_bin})")
            lines.append(f"        Key Byte  {chr(kb) if (32<=kb<=126) else '.':<4} ({k_bin})")
            lines.append(f"        Ciphertext hex {c_hex:<2} ({c_bin})")
            lines.append("-" * 55)
            
        self.bitwise_display.insert("1.0", "\n".join(lines))
        self.bitwise_display.config(state="disabled")

    def update_diffusion_metrics(self):
        orig_str = self.avalanche_input.get()
        mutated_str = self.avalanche_mutated.get()
        key = self.xor_key.get()
        mode = self.modern_mode.get()
        
        if not orig_str or not key:
            self.diffusion_lbl.config(text="Diffusion Stats: Enter input to compute.")
            return
            
        orig_bytes = orig_str.encode("utf-8")
        mut_bytes = mutated_str.encode("utf-8")
        key_bytes = key.encode("utf-8")
        
        # Encrypt original
        if mode == "XOR":
            c_orig = simple_xor_cipher(orig_bytes, key_bytes)
            c_mut = simple_xor_cipher(mut_bytes, key_bytes)
        else: # SPN
            c_orig = spn_block_cipher_encrypt(orig_bytes, key_bytes)
            c_mut = spn_block_cipher_encrypt(mut_bytes, key_bytes)
            
        # Compute Hamming distance
        dist = get_hamming_distance(c_orig, c_mut)
        total_bits = max(len(c_orig), len(c_mut)) * 8
        
        pct = (dist / total_bits * 100) if total_bits > 0 else 0.0
        
        # Calculate Entropy
        ent_plain = get_entropy(orig_bytes)
        ent_cipher = get_entropy(c_orig)
        
        self.diffusion_lbl.config(
            text=f"Bit Changes (Hamming Dist): {dist} / {total_bits} bits ({pct:.2f}% shift)"
        )
        self.entropy_lbl.config(
            text=f"Plaintext Entropy: {ent_plain:.4f} bits/symbol | Ciphertext Entropy: {ent_cipher:.4f} bits/symbol"
        )
        
        # Redraw diffusion progress bar
        canvas = self.diffusion_bar_canvas
        canvas.delete("all")
        w = canvas.winfo_width()
        if w < 10:
            w = 400
        h = canvas.winfo_height()
        
        # Draw background bar
        canvas.create_rectangle(0, 0, w, h, fill="#1F2937", outline="")
        
        # Draw filled bar (percentage)
        fill_w = w * (pct / 100.0)
        
        # Colors: Green for good diffusion (~50% for block cipher), Cyan for stream cipher (low)
        # SPN block cipher usually achieves close to 50% diffusion (avalanche effect).
        # Simple XOR will have very low diffusion percentage if string is long and only 1 char changes.
        bar_color = "#00FF66" if (40 <= pct <= 60) else "#00F0FF"
        canvas.create_rectangle(0, 0, fill_w, h, fill=bar_color, outline="")
        
        # Label indicator
        ideal_text = " (Ideal ~50% Avalanche)" if mode == "SPN" else " (Stream XOR - No Diffusion)"
        canvas.create_text(w//2, h//2, text=f"Diffusion Output: {pct:.1f}%{ideal_text}", fill="#0A0E17" if pct > 40 else "#F3F4F6", font=("Segoe UI", 9, "bold"))

    # --- Bindings & Controls ---

    def bind_events(self):
        # Bind typing inside text fields
        self.caesar_input.bind("<KeyRelease>", self.on_caesar_input_change)
        self.modern_input.bind("<KeyRelease>", self.on_modern_input_change)
        
        self.key_entry.bind("<KeyRelease>", self.on_modern_input_change)
        
        # Avalanche entries
        self.avalanche_input.trace_add("write", lambda *args: self.on_modern_input_change())
        self.avalanche_mutated.trace_add("write", lambda *args: self.on_modern_input_change())
        
        # Window resize binders for redraw
        self.slider_canvas.bind("<Configure>", lambda e: self.draw_custom_slider())
        self.tracer_canvas.bind("<Configure>", lambda e: self.draw_math_trace())
        self.diffusion_bar_canvas.bind("<Configure>", lambda e: self.update_diffusion_metrics())

# --- Self-Test Block (Validation Checks) ---
def run_unit_tests():
    print("Running cryptographic verification checks...")
    
    # 1. Caesar Cipher checks
    p1 = "HelloWorld 123!"
    c1 = caesar_encrypt(p1, 3)
    d1 = caesar_decrypt(c1, 3)
    assert d1 == p1, f"Caesar roundtrip failed: {p1} vs {d1}"
    assert c1 == "KhoorZruog 123!", f"Caesar encryption failed: {c1}"
    print("[OK] Caesar Cipher validation passed.")
    
    # 2. Simple XOR checks
    p2 = b"SecretMessage"
    key2 = b"Key123"
    c2 = simple_xor_cipher(p2, key2)
    d2 = simple_xor_cipher(c2, key2)
    assert d2 == p2, "XOR roundtrip failed."
    print("[OK] Simple XOR validation passed.")
    
    # 3. SPN Block Cipher checks
    p3 = b"AnotherSecretMessage123"
    key3 = b"Key128BitShield!"
    c3 = spn_block_cipher_encrypt(p3, key3)
    d3 = spn_block_cipher_decrypt(c3, key3)
    assert d3 == p3, f"SPN roundtrip failed: {p3} vs {d3}"
    print("[OK] SPN Block Cipher validation passed.")
    
    print("All unit tests passed successfully!")

if __name__ == "__main__":
    # Run tests before launching app
    run_unit_tests()
    
    # Run UI
    app = EnigmaApp()
    app.mainloop()
