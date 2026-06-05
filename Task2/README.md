# 🔒 Enigma Cryptographic Suite

Enigma is a premium, desktop-native cryptographic application written in Python. Built for **DecodeLabs Project 2 (Basic Encryption & Decryption)**, it serves as an educational and interactive tool demonstrating the transition from classical mathematical shifts to modern block ciphers.

The suite is designed with a sleek cyber-dark user interface that integrates natively with Windows immersive dark mode styling and features real-time visualizations of cryptographic transformations.

---

## 🚀 Key Features

### 1. Classical Cryptography: Caesar Cipher Engine
- **IPO (Input-Process-Output) Cycle:** Real-time data processing as you type plaintext, computing ciphertext, and outputting results instantly.
- **Symmetric Shift Key Control:** A custom canvas-drawn slider allows selection of a shift key from $1$ to $25$.
- **Live Math Tracer:** A vertical flowchart showing the exact step-by-step mathematical transformation for the last character typed:
  $$\text{ASCII} \to \text{Subtract Base} \to \text{Add Shift} \to \text{Modulo 26} \to \text{Add Base} \to \text{Cipher Character}$$
- **Decryption Enclave & Verification:** Instantly decries the output back to plaintext using the reverse shift, checking if $D_n(E_n(P)) == P$, and displays a green `[VALIDATED]` badge.
- **Edge Case Handling:** Safely passes numbers, spaces, and punctuation through without altering them, maintaining casing for letters.

### 2. Modern Cryptography: 128-bit Shield Engine
- **128-bit Keys:** Generates and processes cryptographically secure 128-bit symmetric keys (16 characters / 16 bytes).
- **Two Encryption Modes:**
  - **Simple XOR:** A standard repeating-key bitwise XOR cipher. Demonstrates how stream-like XOR ciphers lack **Diffusion** (changing 1 bit in plaintext changes exactly 1 bit in ciphertext).
  - **SPN Block Cipher:** A Substitution-Permutation Network block cipher (padded to 16 bytes) incorporating a non-linear S-box (Confusion) and byte-row transposition (Diffusion).
- **Bitwise Alignment Display:** Shows a byte-by-byte alignment of Plaintext, Key, and Ciphertext in binary (`01100101`) for the first 8 bytes.
- **Avalanche Effect & Diffusion Tester:** Real-time analysis of bit diffusion (Hamming distance percentage) when mutating one character, showing the difference in security between simple XOR and multi-round SPN ciphers.
- **Entropy Metrics:** Displays Shannon entropy values for both Plaintext and Ciphertext to demonstrate message scrambling effectiveness.

---

## 📁 Project Structure

- `main.py`: The core Python source code containing all cryptographic algorithms (Caesar, Simple XOR, SPN), custom Tkinter styles, and canvas UI components.
- `README.md`: This documentation.

---

## 🛠️ Requirements & Setup

### Prerequisites
- **Python 3.8+**
- **Tkinter:** Standard GUI library, pre-bundled with Python on Windows.
- **Pillow:** Installed during setup (used for UI visualizations/testing).

### Installation & Run

1. Navigate to the project directory:
   ```powershell
   cd "c:\Users\Varun\OneDrive\Desktop\Decode Labs\T2"
   ```
2. Run the application:
   ```powershell
   python main.py
   ```

---

## 📐 Cryptographic Math Reference

### Caesar Cipher
- **Encryption:**
  $$E_n(x) = (x + n) \pmod{26}$$
- **Decryption:**
  $$D_n(x) = (x - n) \pmod{26}$$

### Substitution-Permutation Network (SPN)
To achieve secure **Confusion & Diffusion** (as detailed in Shannon's papers and implemented in AES), the SPN engine performs:
1. **Key Addition:** $B_1 = P \oplus K$
2. **Substitution:** $B_2 = S\_Box(B_1)$ (Non-linear byte substitution)
3. **Permutation:** $B_3 = \text{Rotate/Shuffle}(B_2)$ (Permutes byte indices to diffuse influence)
4. **Key Addition (Round 2):** $C = B_3 \oplus K_{\text{shifted}}$
