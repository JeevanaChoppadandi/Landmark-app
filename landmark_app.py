import tkinter as tk
from tkinter import messagebox, filedialog
import google.generativeai as genai
from googletrans import Translator
import pyttsx3
import requests
import geocoder
from PIL import Image, ImageTk
from io import BytesIO
from geopy.geocoders import Nominatim
import webbrowser
from gtts import gTTS
import os
from reportlab.pdfgen import canvas

# Configure Gemini API
genai.configure(api_key="AIzaSyD-KkgvFy4pLf9uK_Hk-BoKnxEy3EG-SWo")  # Replace with your API key

# Function to get landmark description
def get_description():
    landmark = landmark_entry.get()
    language = lang_entry.get() if lang_entry.get() else "en"

    if not landmark:
        messagebox.showerror("Error", "Please enter a landmark name.")
        return

    try:
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"Describe the landmark: {landmark} and provide 3 fun facts."
        response = model.generate_content(prompt)
        description = response.text if response else "No description available."

        # Translate description
        translator = Translator()
        translated_text = translator.translate(description, dest=language).text

        # Display result
        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, translated_text)
        result_text.config(state=tk.DISABLED)

        # Fetch landmark image
        fetch_image(landmark)

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to fetch landmark image
def fetch_image(landmark):
    try:
        img_url = f"https://source.unsplash.com/400x300/?{landmark.replace(' ', '+')}"
        img_data = requests.get(img_url).content
        img = Image.open(BytesIO(img_data))
        img = img.resize((300, 200), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)

        image_label.config(image=img)
        image_label.image = img
    except Exception:
        image_label.config(text="Image not found")

# Function to detect location and find nearest landmark
def get_nearest_landmark():
    try:
        # Get current location using geocoder
        g = geocoder.ip('me')
        if g.ok:
            lat, lon = g.latlng  # Extract latitude and longitude
            
            # Use geopy to find the nearest landmark
            geolocator = Nominatim(user_agent="geoapiExercises")
            location = geolocator.reverse((lat, lon), exactly_one=True)

            if location and location.address:
                landmark_entry.delete(0, tk.END)
                landmark_entry.insert(0, location.address)
            else:
                messagebox.showerror("Error", "Could not determine the nearest landmark.")
        else:
            messagebox.showerror("Error", "Could not retrieve location data.")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to open Google Maps for AR mode
def open_google_maps():
    landmark = landmark_entry.get()
    if landmark:
        url = f"https://www.google.com/maps/search/{landmark.replace(' ', '+')}"
        webbrowser.open(url)
    else:
        messagebox.showerror("Error", "Please enter a landmark name.")

# Function to save description as PDF
def save_to_pdf():
    landmark = landmark_entry.get()
    description = result_text.get(1.0, tk.END).strip()

    if not landmark or not description:
        messagebox.showerror("Error", "No landmark or description found to save.")
        return

    filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if filename:
        pdf = canvas.Canvas(filename)
        pdf.drawString(100, 750, f"Landmark: {landmark}")
        pdf.drawString(100, 730, "Description:")
        text_lines = description.split("\n")
        y_position = 710
        for line in text_lines:
            pdf.drawString(100, y_position, line)
            y_position -= 20
        pdf.save()
        messagebox.showinfo("Success", f"PDF saved as {filename}")

# Function for text-to-speech (TTS)
def speak_text():
    text = result_text.get(1.0, tk.END).strip()
    if text:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    else:
        messagebox.showerror("Error", "No description available to speak.")

# Function for multilingual text-to-speech
def speak_multilingual():
    text = result_text.get(1.0, tk.END).strip()
    language = lang_entry.get() if lang_entry.get() else "en"

    if text:
        tts = gTTS(text=text, lang=language)
        tts.save("output.mp3")
        os.system("start output.mp3")  # Use "afplay" for Mac, "mpg321 output.mp3" for Linux
    else:
        messagebox.showerror("Error", "No description available to speak.")

# GUI Setup
root = tk.Tk()
root.title("Gemini Landmark Description App")
root.geometry("600x700")

# Labels & Input Fields
tk.Label(root, text="Enter Landmark Name:").pack(pady=5)
landmark_entry = tk.Entry(root, width=40)
landmark_entry.pack(pady=5)

tk.Label(root, text="Enter Language Code (e.g., 'fr' for French, 'es' for Spanish):").pack(pady=5)
lang_entry = tk.Entry(root, width=10)
lang_entry.pack(pady=5)

# Buttons
tk.Button(root, text="Get Description", command=get_description).pack(pady=10)
tk.Button(root, text="🔊 Speak", command=speak_text).pack(pady=5)
tk.Button(root, text="🎤 Speak (Multilingual)", command=speak_multilingual).pack(pady=5)
tk.Button(root, text="📍 Detect Nearest Landmark", command=get_nearest_landmark).pack(pady=5)
tk.Button(root, text="🗺 Open Google Maps (AR Mode)", command=open_google_maps).pack(pady=5)
tk.Button(root, text="💾 Save as PDF", command=save_to_pdf).pack(pady=5)
tk.Button(root, text="❌ Exit", command=root.quit).pack(pady=5)  # Exit Button Added

# Result Display
result_text = tk.Text(root, width=70, height=10, state=tk.DISABLED)
result_text.pack(pady=10)

# Image Display
image_label = tk.Label(root, text="Landmark Image Will Appear Here")
image_label.pack(pady=10)

# Run the GUI
root.mainloop()