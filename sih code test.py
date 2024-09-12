import librosa
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import time
from scipy.io.wavfile import write
import random

# Function to extract pitch values
def extract_pitch(y, sr, fmin=85.0, fmax=400.0):
    pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr, fmin=fmin, fmax=fmax)
    pitch_values = []
    
    for t in range(pitches.shape[1]):
        index = magnitudes[:, t].argmax()  # Find the index with the highest energy
        pitch = pitches[index, t]  # Get the corresponding pitch
        if fmin <= pitch <= fmax:  # Only consider valid pitch values within a human speech range
            pitch_values.append(pitch)
        else:
            pitch_values.append(0)  # If invalid pitch, set to 0 (silence or noise)
    
    return np.array(pitch_values)

# Function to smooth pitch values using a moving average
def smooth_pitch(pitch_values, window_size=10):
    return np.convolve(pitch_values, np.ones(window_size)/window_size, mode='valid')

# Function to classify the intonation as statement, question, or exclamation
def classify_intonation(pitch_values):
    if len(pitch_values) < 50:
        return "Insufficient data to classify intonation."

    last_pitch_section = pitch_values[-50:]
    
    start_avg_pitch = np.mean(last_pitch_section[:25])
    end_avg_pitch = np.mean(last_pitch_section[25:])
    
    pitch_diff = end_avg_pitch - start_avg_pitch

    if 1 < pitch_diff <= 15:
        return "question"
    elif pitch_diff > 15:
        return "exclamation"
    elif pitch_diff < -5:
        return "statement"
    else:
        return "statement"

# Function to visualize pitch contour (intonation)
def plot_pitch_contour(pitch_values, smoothed_pitch_values):
    plt.figure(figsize=(12, 6))
    
    # Plot original pitch values
    plt.plot(pitch_values, label="Original Pitch Contour", color='blue', alpha=0.6)
    
    # Plot smoothed pitch values
    plt.plot(smoothed_pitch_values, label="Smoothed Pitch Contour", color='red')
    
    plt.title('Pitch Contour (Intonation Analysis)')
    plt.xlabel('Time Frames')
    plt.ylabel('Pitch (Hz)')
    plt.legend()
    plt.show()

# Function to record audio in real-time using sounddevice
def record_audio(duration, sr=48000, device_id=3):  # Set a supported sample rate (e.g., 48000 Hz)
    print(f"Recording for {duration} seconds using device ID {device_id}...")
    recording = sd.rec(int(duration * sr), samplerate=sr, channels=1, device=device_id)
    sd.wait()  # Wait until the recording is finished
    write('test_audio.wav', sr, recording)  # Save the recording as a WAV file
    return 'test_audio.wav'


# Test function to prompt the user, record audio, and give feedback
def intonation_test(prompt_sentence, expected_intonation):
    print(f"Please say the following sentence as a {expected_intonation}:")
    print(f'"{prompt_sentence}"')
    
    # Give the user time to prepare
    time.sleep(2)
    
    # Record the user's speech
    audio_file = record_audio(5)  # Record for 5 seconds
    
    # Load the recorded audio
    y, sr = librosa.load(audio_file, sr=44100)  # Adjust sample rate based on the device
    
    # Step 1: Extract pitch values from the audio
    pitch_values = extract_pitch(y, sr)
    
    # Step 2: Smooth the pitch values to remove noise
    smoothed_pitch_values = smooth_pitch(pitch_values)
    
    # Step 3: Classify the intonation
    classified_intonation = classify_intonation(smoothed_pitch_values)
    
    # Step 4: Provide feedback
    if classified_intonation == expected_intonation:
        print(f"Correct! You said it as a {expected_intonation}.")
    else:
        print(f"Incorrect. You said it as a {classified_intonation}, not a {expected_intonation}.")
    
    # Step 5: Plot the pitch contour (optional)
    plot_pitch_contour(pitch_values, smoothed_pitch_values)

# Prompts for the user to say with different intonations
prompts = [
    {"sentence": "Are you coming to the party?", "intonation": "question"},
    {"sentence": "It's a sunny day outside.", "intonation": "statement"},
    {"sentence": "Wow! That's amazing!", "intonation": "exclamation"},
    {"sentence": "Do you like ice cream?", "intonation": "question"},
    {"sentence": "This is the best day ever!", "intonation": "exclamation"},
    {"sentence": "The meeting starts at 9 AM.", "intonation": "statement"},
    {"sentence": "Can you help me with this?", "intonation": "question"},
    {"sentence": "I can't believe it!", "intonation": "exclamation"},
    {"sentence": "She walks to the store every day.", "intonation": "statement"}
]

# Randomly choose a prompt for the user to say
chosen_prompt = random.choice(prompts)

# Run the intonation test
intonation_test(chosen_prompt["sentence"], chosen_prompt["intonation"])

