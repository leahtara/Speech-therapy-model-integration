import os
import sounddevice as sd
import json
import random
import string
from vosk import Model, KaldiRecognizer
from tkinter import messagebox, Tk

# Define the paths to the datasets
severity_datasets = {
    'severe': r"C:/Users/Isaac David/Documents/me/severe.txt",
    'moderate': r"C:/Users/Isaac David/Documents/me/moderate.txt",
    'mild': r"C:/Users/Isaac David/Documents/me/mild.txt"
}

# Path to Vosk model
model_path = r"C:/Users/Isaac David/Documents/me/vosk/vosk-model-small-en-us-0.15"
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model path {model_path} does not exist.")

# Initialize the recognizer with the model
model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

# Function to remove punctuation from text
def remove_punctuation(text):
    return text.translate(str.maketrans('', '', string.punctuation)).lower()

# Function to capture and process audio from the microphone
def capture_and_process_audio(expected_word):
    print("Listening...")

    # Use sounddevice to capture audio
    def callback(indata, frames, time, status):
        if status:
            print(f"Error: {status}")
        # Process audio input
        try:
            audio_data = bytes(indata)
            if recognizer.AcceptWaveform(audio_data):
                result = recognizer.Result()
                result_json = json.loads(result)
                spoken_text = result_json.get("text", "").lower()  # Get recognized text and convert to lowercase
                expected_word_clean = remove_punctuation(expected_word)  # Clean expected text
                spoken_text_clean = remove_punctuation(spoken_text)  # Clean transcribed text

                print(f"Transcribed text: {spoken_text}")
                
                if spoken_text_clean == expected_word_clean:
                    print(f"Correct! The word is '{expected_word}'. ★")
                    show_gold_star()
                else:
                    print(f"Incorrect. You said '{spoken_text}' but expected '{expected_word}'.")
        except Exception as e:
            print(f"Error processing audio: {e}")

    # Open an audio stream and set the callback function
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print(f"Please say the word '{expected_word}'...")
        sd.sleep(5000)  # Listen for 5 seconds

# Function to show a gold star popup
def show_gold_star():
    root = Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Gold Star", "★ Correct! You earned a gold star!")
    root.destroy()

# Function to get random word from the selected severity dataset
def get_random_word(severity_level):
    file_path = severity_datasets.get(severity_level)
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset for {severity_level} not found.")

    with open(file_path, 'r') as file:
        words = file.readlines()
    return random.choice(words).strip()

# Menu-driven system for selecting the testing level
def menu():
    print("Select the level of testing:")
    print("1. Severe")
    print("2. Moderate")
    print("3. Mild")
    
    choice = input("Enter your choice (1/2/3): ")

    if choice == '1':
        return 'severe'
    elif choice == '2':
        return 'moderate'
    elif choice == '3':
        return 'mild'
    else:
        print("Invalid choice. Please try again.")
        return menu()

# Main function
if __name__ == "__main__":
    # Show the menu and get the severity level
    severity_level = menu()

    # Get a random word based on the chosen severity level
    expected_word = get_random_word(severity_level)
    print(f"Expected word: {expected_word}")

    # Process the audio and check if the word matches
    capture_and_process_audio(expected_word)
