# 🔒 Password Shield

Password Shield is a modern, desktop-native cryptographic strength analyzer and password rating tool written in Python. Built using the standard library's `tkinter` and custom graphical canvas elements, it delivers a sleek, high-fidelity dark-themed user experience that goes beyond standard system-native GUI designs.

---

## 🚀 Key Features

*   **Real-time Cryptographic Analysis:** Evaluates passwords as you type against key entropy criteria.
*   **Time-to-Crack Estimation:** Calculates mathematical permutations based on character pool sizes (lowercase, uppercase, digits, symbols) and password length, assuming a default rate of 10 billion guesses per second ($10^{10}$ GS/s).
*   **Custom UI Elements (No Generic Tkinter Widgets):**
    *   `ModernProgressBar`: A custom canvas progress bar utilizing smooth linear interpolation transitions, dynamic color shifting, and a white sweeping laser animation on update.
    *   `CriteriaCheckbox`: A custom circular canvas checkbox that dynamically draws its checkmark icon via vector path animation when its condition is met.
*   **Aesthetic Styling & Polish:**
    *   Integrated immersive Windows dark mode theme (`DWMWA_USE_IMMERSIVE_DARK_MODE` via `ctypes` on NT systems).
    *   Dynamic badge pulsing transitions that highlight rating shifts.
    *   Responsive checklist indicating exactly which criteria are missing/met.
    *   Handy **SHOW/HIDE** password visibility toggle.

---

## 📁 Project Structure

*   `main.py`: The core application source file containing all helper functions (`estimate_crack_time`, `check_password_strength`), custom widgets, layout configuration, and the GUI event loop.
*   `.venv/`: Python virtual environment (ignored).

---

## 🛠️ Requirements & Setup

### Prerequisites
*   **Python 3.8+**
*   **Tkinter:** Usually bundled with standard Python installers on Windows and macOS. 
    *   *Linux users* may need to install it manually:
        ```bash
        sudo apt-get install python3-tk
        ```

### Installation & Run

1.  Clone this repository or navigate to the project directory:
    ```powershell
    cd "c:\Users\Varun\OneDrive\Desktop\Decode Labs\T1"
    ```
2.  Run the application directly using the Python interpreter:
    ```powershell
    python main.py
    ```

---

## 🔒 Strength Criteria Breakdown

The analyzer awards scores up to a maximum rating based on these checkpoints:

| Criteria | Description | Score Points |
| :--- | :--- | :---: |
| **Length** | $\ge$ 12 characters (Excellent) or $\ge$ 8 characters (Good) | Up to +3 |
| **Uppercase** | Contains at least one uppercase letter (`A-Z`) | +1 |
| **Lowercase** | Contains at least one lowercase letter (`a-z`) | +1 |
| **Numbers** | Contains at least one numeric digit (`0-9`) | +1 |
| **Symbols** | Contains at least one special character/punctuation | +1 |

### Rating Ranges
*   **Weak:** Score $\le 3$ or length $< 8$
*   **Medium:** Score $4$ or $5$
*   **Strong:** Score $\ge 6$ with length $\ge 8$
