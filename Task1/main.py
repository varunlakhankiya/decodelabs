import string
import tkinter as tk
from tkinter import ttk
import ctypes
import os

def make_title_bar_dark(window):
    if os.name == 'nt':
        try:
            window.update()
            hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
            DWMWA_USE_IMMERSIVE_DARK_MODE = 20
            rendering = ctypes.c_int(1)
            result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                ctypes.byref(rendering), ctypes.sizeof(rendering)
            )
            if result != 0:
                DWMWA_USE_IMMERSIVE_DARK_MODE = 19
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                    ctypes.byref(rendering), ctypes.sizeof(rendering)
                )
        except Exception:
            pass

def estimate_crack_time(password: str) -> str:
    if not password:
        return "Instant"
        
    length = len(password)
    pool = 0
    if any(c.islower() for c in password): pool += 26
    if any(c.isupper() for c in password): pool += 26
    if any(c.isdigit() for c in password): pool += 10
    if any(c in string.punctuation for c in password): pool += 32
    
    if pool == 0:
        pool = 10
        
    combinations = pool ** length
    guesses_per_second = 1e10
    seconds = combinations / guesses_per_second
    
    if seconds < 1e-3:
        return "Instant"
    elif seconds < 1:
        return "Under a second"
    elif seconds < 60:
        return f"~{int(seconds)} second" + ("s" if int(seconds) != 1 else "")
    
    minutes = seconds / 60
    if minutes < 60:
        return f"~{int(minutes)} minute" + ("s" if int(minutes) != 1 else "")
        
    hours = minutes / 60
    if hours < 24:
        return f"~{int(hours)} hour" + ("s" if int(hours) != 1 else "")
        
    days = hours / 24
    if days < 365:
        return f"~{int(days)} day" + ("s" if int(days) != 1 else "")
        
    years = days / 365
    if years < 1000:
        return f"~{int(years):,} year" + ("s" if int(years) != 1 else "")
    elif years < 1e6:
        return f"~{int(years/1000):,} thousand years"
    elif years < 1e9:
        return f"~{int(years/1e6):,} million years"
    elif years < 1e12:
        return f"~{int(years/1e9):,} billion years"
    else:
        return f"~{int(years/1e12):,} trillion years"

def check_password_strength(password: str) -> dict:
    if not password:
        return {
            "strength": "None",
            "score": 0,
            "crack_time": "Instant",
            "feedback": ["Please enter a password."],
            "criteria": {
                "length": False,
                "uppercase": False,
                "lowercase": False,
                "number": False,
                "symbol": False
            }
        }

    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_symbol = any(char in string.punctuation for char in password)
    length = len(password)

    score = 0
    feedback = []

    if length >= 12:
        score += 3
        feedback.append("Excellent length (12+ characters).")
    elif length >= 8:
        score += 2
        feedback.append("Good length (8+ characters).")
    else:
        score += 1
        feedback.append("Password is too short (less than 8 characters).")

    if has_upper:
        score += 1
    else:
        feedback.append("Missing uppercase letters.")

    if has_lower:
        score += 1
    else:
        feedback.append("Missing lowercase letters.")

    if has_digit:
        score += 1
    else:
        feedback.append("Missing numbers.")

    if has_symbol:
        score += 1
    else:
        feedback.append("Missing special symbols.")

    if score <= 3 or length < 8:
        strength = "Weak"
    elif score <= 5:
        strength = "Medium"
    else:
        strength = "Strong"

    return {
        "strength": strength,
        "score": score,
        "crack_time": estimate_crack_time(password),
        "feedback": feedback,
        "criteria": {
            "length": length >= 8,
            "uppercase": has_upper,
            "lowercase": has_lower,
            "number": has_digit,
            "symbol": has_symbol
        }
    }

class ModernProgressBar(tk.Canvas):
    def __init__(self, parent, bg_color='#0f0f13', track_color='#1e1e24', thickness=12, **kwargs):
        canvas_height = thickness + 4
        super().__init__(parent, height=canvas_height, bg=bg_color, bd=0, highlightthickness=0, **kwargs)
        self.track_color = track_color
        self.thickness = thickness
        self.current_progress = 0.0
        self.target_progress = 0.0
        self.current_color = '#64748b'
        self.target_color = '#64748b'
        self.animating = False
        self.scan_pos = -0.2
        self.scan_active = False
        self.bind("<Configure>", lambda e: self.draw())

    def set_progress(self, val, color):
        self.target_progress = min(max(val, 0.0), 1.0)
        self.target_color = color
        
        if self.target_progress != self.current_progress:
            self.scan_active = True
            if self.scan_pos > 1.0 or self.scan_pos < 0.0:
                self.scan_pos = -0.2
                
        if not self.animating:
            self.animate_loop()

    def animate_loop(self):
        self.animating = True
        
        p_diff = self.target_progress - self.current_progress
        if abs(p_diff) > 0.001:
            self.current_progress += p_diff * 0.12
        else:
            self.current_progress = self.target_progress
            
        self.current_color = self.interpolate_hex(self.current_color, self.target_color, 0.15)
        
        if self.scan_active:
            self.scan_pos += 0.04
            if self.scan_pos > 1.2:
                self.scan_pos = -0.2
                self.scan_active = False
                
        self.draw()
        
        p_done = abs(self.target_progress - self.current_progress) <= 0.001
        c_done = self.current_color.lower() == self.target_color.lower()
        
        if not (p_done and c_done and not self.scan_active):
            self.after(16, self.animate_loop)
        else:
            self.current_progress = self.target_progress
            self.current_color = self.target_color
            self.draw()
            self.animating = False

    def interpolate_hex(self, color1, color2, factor):
        try:
            r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
            r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
            r = int(r1 + (r2 - r1) * factor)
            g = int(g1 + (g2 - g1) * factor)
            b = int(b1 + (b2 - b1) * factor)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return color2

    def draw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        r = self.thickness / 2
        cy = h / 2

        if w > self.thickness:
            self.create_line(r, cy, w - r, cy, width=self.thickness, fill=self.track_color, capstyle=tk.ROUND)
            
            if self.current_progress > 0:
                fill_w = r + (w - self.thickness) * self.current_progress
                if fill_w > r:
                    self.create_line(r, cy, fill_w, cy, width=self.thickness, fill=self.current_color, capstyle=tk.ROUND)
                    
            if self.scan_active and self.current_progress > 0:
                sweep_center = r + (w - self.thickness) * self.scan_pos
                if r <= sweep_center <= fill_w:
                    laser_len = 35
                    lx1 = max(r, sweep_center - laser_len/2)
                    lx2 = min(fill_w, sweep_center + laser_len/2)
                    if lx2 > lx1:
                        self.create_line(lx1, cy, lx2, cy, width=self.thickness, fill='#ffffff', capstyle=tk.ROUND)

class CriteriaCheckbox(tk.Canvas):
    def __init__(self, parent, bg_color='#181820', active_color='#10b981', inactive_color='#2d2d3a', **kwargs):
        super().__init__(parent, width=20, height=20, bg=bg_color, bd=0, highlightthickness=0, **kwargs)
        self.bg_color = bg_color
        self.active_color = active_color
        self.inactive_color = inactive_color
        
        self.is_checked = False
        self.progress = 0.0
        self.animating = False
        
        self.draw()

    def set_checked(self, checked):
        if self.is_checked == checked:
            return
        self.is_checked = checked
        self.animate()

    def animate(self):
        if self.animating:
            return
        self.animate_loop()

    def animate_loop(self):
        self.animating = True
        step = 0.15
        if self.is_checked:
            self.progress = min(self.progress + step, 1.0)
        else:
            self.progress = max(self.progress - step, 0.0)
            
        self.draw()
        
        if (self.is_checked and self.progress < 1.0) or (not self.is_checked and self.progress > 0.0):
            self.after(16, self.animate_loop)
        else:
            self.animating = False

    def draw(self):
        self.delete("all")
        r = 8
        cx, cy = 10, 10
        
        color = self.interpolate_hex(self.inactive_color, self.active_color, self.progress)
        self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color, outline="", width=0)
        
        if self.progress > 0:
            x1, y1 = 6.5, 10.0
            x2_mid, y2_mid = 9.5, 13.0
            x3, y3 = 14.5, 7.0
            
            p1 = min(self.progress / 0.4, 1.0)
            curr_x = x1 + (x2_mid - x1) * p1
            curr_y = y1 + (y2_mid - y1) * p1
            self.create_line(x1, y1, curr_x, curr_y, fill="#ffffff", width=2, capstyle=tk.ROUND)
            
            if self.progress > 0.4:
                p2 = (self.progress - 0.4) / 0.6
                curr_x2 = x2_mid + (x3 - x2_mid) * p2
                curr_y2 = y2_mid + (y3 - y2_mid) * p2
                self.create_line(x2_mid, y2_mid, curr_x2, curr_y2, fill="#ffffff", width=2, capstyle=tk.ROUND)

    def interpolate_hex(self, color1, color2, factor):
        try:
            r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
            r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
            r = int(r1 + (r2 - r1) * factor)
            g = int(g1 + (g2 - g1) * factor)
            b = int(b1 + (b2 - b1) * factor)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return color2

class PasswordCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Shield")
        self.root.geometry("460x460")
        self.root.resizable(True, True)
        self.root.minsize(460, 460)
        
        make_title_bar_dark(self.root)
        self.root.configure(bg='#0f0f13')
        
        bg_color = '#0f0f13'
        card_color = '#181820'
        text_primary = '#ffffff'
        text_secondary = '#94a3b8'
        border_color = '#2d2d3a'
        accent_color = '#6366f1'
        
        self.border_target_color = border_color
        self.border_animating = False
        
        self.badge_pulsing = False
        self.last_strength = None
        
        self.main_frame = tk.Frame(self.root, bg=bg_color, padx=24, pady=24)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_frame = tk.Frame(self.main_frame, bg=bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_lbl = tk.Label(title_frame, text="🔒 Password Shield", font=('Segoe UI', 16, 'bold'), fg='#ffffff', bg=bg_color)
        title_lbl.pack(anchor=tk.W)
        
        subtitle_lbl = tk.Label(title_frame, text="Advanced real-time cryptographic strength analyzer.", font=('Segoe UI', 9), fg='#64748b', bg=bg_color)
        subtitle_lbl.pack(anchor=tk.W, pady=(2, 0))
        
        input_frame = tk.Frame(self.main_frame, bg=bg_color)
        input_frame.pack(fill=tk.X, pady=(0, 16))
        
        lbl = tk.Label(input_frame, text="ENTER PASSWORD", font=('Segoe UI', 8, 'bold'), fg='#64748b', bg=bg_color)
        lbl.pack(anchor=tk.W, pady=(0, 6))
        
        self.entry_container = tk.Frame(input_frame, bg=card_color, bd=0, highlightthickness=1, highlightbackground=border_color)
        self.entry_container.pack(fill=tk.X)
        
        self.password_var = tk.StringVar()
        self.password_var.trace_add("write", self.on_password_change)
        
        self.entry = tk.Entry(self.entry_container, textvariable=self.password_var, show="*", font=('Segoe UI', 11),
                              bg=card_color, fg=text_primary, bd=0, relief=tk.FLAT,
                              insertbackground='#ffffff', selectbackground=accent_color)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(12, 6), pady=10)
        
        self.entry.bind("<FocusIn>", lambda e: self.set_border_target(accent_color))
        self.entry.bind("<FocusOut>", lambda e: self.set_border_target(border_color))
        
        self.toggle_btn = tk.Label(self.entry_container, text="SHOW", font=('Segoe UI', 8, 'bold'), fg=accent_color, bg=card_color, cursor='hand2')
        self.toggle_btn.pack(side=tk.RIGHT, padx=(6, 12), pady=10)
        self.toggle_btn.bind("<Button-1>", lambda e: self.toggle_password())
        
        self.progress = ModernProgressBar(self.main_frame, bg_color=bg_color, track_color='#1e1e26', thickness=10)
        self.progress.pack(fill=tk.X, pady=(0, 16))
        
        self.badge_frame = tk.Frame(self.main_frame, bg=card_color, bd=0, highlightthickness=1, highlightbackground=border_color)
        self.badge_frame.pack(fill=tk.X, pady=(0, 20), ipady=8)
        
        self.badge_frame.columnconfigure(0, weight=1)
        self.badge_frame.columnconfigure(1, weight=1)
        
        left_panel = tk.Frame(self.badge_frame, bg=card_color)
        left_panel.grid(row=0, column=0, padx=12, pady=6, sticky=tk.W)
        
        self.status_title = tk.Label(left_panel, text="RATING", font=('Segoe UI', 8, 'bold'), fg='#64748b', bg=card_color)
        self.status_title.pack(side=tk.LEFT)
        
        self.status_badge = tk.Label(left_panel, text="NONE", font=('Segoe UI', 9, 'bold'), fg='#ffffff', bg='#1e1e24', padx=8, pady=2)
        self.status_badge.pack(side=tk.LEFT, padx=(8, 0))
        
        right_panel = tk.Frame(self.badge_frame, bg=card_color)
        right_panel.grid(row=0, column=1, padx=12, pady=6, sticky=tk.E)
        
        self.time_title = tk.Label(right_panel, text="TIME TO CRACK", font=('Segoe UI', 8, 'bold'), fg='#64748b', bg=card_color)
        self.time_title.pack(side=tk.LEFT)
        
        self.time_badge = tk.Label(right_panel, text="INSTANT", font=('Segoe UI', 9, 'bold'), fg='#ffffff', bg='#1e1e24', padx=8, pady=2)
        self.time_badge.pack(side=tk.LEFT, padx=(8, 0))
        
        self.strength_desc = tk.Label(self.badge_frame, text="Ready.", font=('Segoe UI', 9), fg='#64748b', bg=card_color)
        self.strength_desc.grid(row=1, column=0, columnspan=2, pady=(2, 2))
        
        feedback_header = tk.Label(self.main_frame, text="CRITERIA CHECKLIST", font=('Segoe UI', 8, 'bold'), fg='#64748b', bg=bg_color)
        feedback_header.pack(anchor=tk.W, pady=(0, 6))
        
        self.checklist_frame = tk.Frame(self.main_frame, bg=card_color, bd=0, highlightthickness=1, highlightbackground=border_color)
        self.checklist_frame.pack(fill=tk.BOTH, expand=True, ipady=4)
        
        self.criteria = {}
        criteria_list = [
            ("length", "At least 8 characters long"),
            ("uppercase", "Contains uppercase letter (A-Z)"),
            ("lowercase", "Contains lowercase letter (a-z)"),
            ("number", "Contains numeric digit (0-9)"),
            ("symbol", "Contains special symbol (e.g., !@#$)")
        ]
        
        for key, text in criteria_list:
            row = tk.Frame(self.checklist_frame, bg=card_color)
            row.pack(fill=tk.X, padx=16, pady=4)
            
            checkbox = CriteriaCheckbox(row, bg_color=card_color, inactive_color=border_color, active_color='#10b981')
            checkbox.pack(side=tk.LEFT)
            
            lbl = tk.Label(row, text=text, font=('Segoe UI', 9), fg='#64748b', bg=card_color)
            lbl.pack(side=tk.LEFT, padx=(10, 0))
            
            self.criteria[key] = (checkbox, lbl)
            
        self.on_password_change()

    def toggle_password(self):
        if self.entry.cget("show") == "*":
            self.entry.config(show="")
            self.toggle_btn.config(text="HIDE", fg='#94a3b8')
        else:
            self.entry.config(show="*")
            self.toggle_btn.config(text="SHOW", fg='#6366f1')

    def set_border_target(self, color):
        self.border_target_color = color
        if not self.border_animating:
            self.animate_border_loop()

    def animate_border_loop(self):
        self.border_animating = True
        curr = self.entry_container.cget("highlightbackground")
        targ = self.border_target_color
        new_hex = self.interpolate_hex(curr, targ, 0.22)
        self.entry_container.configure(highlightbackground=new_hex)
        if new_hex.lower() != targ.lower():
            self.root.after(16, self.animate_border_loop)
        else:
            self.border_animating = False

    def trigger_badge_pulse(self, base_color, flash_color, base_bg, flash_bg):
        self.badge_pulse_factor = 1.0
        self.badge_base_color = base_color
        self.badge_flash_color = flash_color
        self.badge_base_bg = base_bg
        self.badge_flash_bg = flash_bg
        if not self.badge_pulsing:
            self.badge_pulse_loop()

    def badge_pulse_loop(self):
        self.badge_pulsing = True
        self.badge_pulse_factor -= 0.12
        if self.badge_pulse_factor > 0:
            bg = self.interpolate_hex(self.badge_base_bg, self.badge_flash_bg, self.badge_pulse_factor)
            fg = self.interpolate_hex(self.badge_base_color, self.badge_flash_color, self.badge_pulse_factor)
            self.status_badge.config(fg=fg, bg=bg)
            self.time_badge.config(fg=fg, bg=bg)
            self.root.after(18, self.badge_pulse_loop)
        else:
            self.status_badge.config(fg=self.badge_base_color, bg=self.badge_base_bg)
            self.time_badge.config(fg=self.badge_base_color, bg=self.badge_base_bg)
            self.badge_pulsing = False

    def interpolate_hex(self, color1, color2, factor):
        try:
            r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
            r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
            r = int(r1 + (r2 - r1) * factor)
            g = int(g1 + (g2 - g1) * factor)
            b = int(b1 + (b2 - b1) * factor)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return color2

    def on_password_change(self, *args):
        password = self.password_var.get()
        result = check_password_strength(password)
        
        strength = result['strength']
        score = result['score']
        crack_time = result['crack_time']
        
        if strength == "Strong":
            color = "#10b981"
            flash_color = "#6ee7b7"
            bg_pill = "#064e3b"
            flash_bg = "#0f766e"
            desc = "Highly secure password. Excellent!"
        elif strength == "Medium":
            color = "#f59e0b"
            flash_color = "#fde047"
            bg_pill = "#451a03"
            flash_bg = "#78350f"
            desc = "Good, but could be stronger."
        elif strength == "Weak":
            color = "#ef4444"
            flash_color = "#fca5a5"
            bg_pill = "#4c0519"
            flash_bg = "#991b1b"
            desc = "Weak. Vulnerable to attacks."
        else:
            color = "#64748b"
            flash_color = "#cbd5e1"
            bg_pill = "#27273a"
            flash_bg = "#475569"
            desc = "Enter a password to begin analysis."
            
        self.progress.set_progress(score / 7.0, color)
        
        if strength != self.last_strength:
            self.last_strength = strength
            self.trigger_badge_pulse(color, flash_color, bg_pill, flash_bg)
        else:
            if not self.badge_pulsing:
                self.status_badge.config(text=strength.upper(), fg=color, bg=bg_pill)
                self.time_badge.config(text=crack_time.upper(), fg=color, bg=bg_pill)
                
        self.status_badge.config(text=strength.upper())
        self.time_badge.config(text=crack_time.upper())
        self.strength_desc.config(text=desc)
        
        for key, satisfied in result['criteria'].items():
            checkbox, lbl = self.criteria[key]
            checkbox.set_checked(satisfied)
            if satisfied:
                lbl.config(fg='#ffffff')
            else:
                lbl.config(fg='#64748b')

def main():
    root = tk.Tk()
    app = PasswordCheckerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()