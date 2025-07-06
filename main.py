import subprocess

# Run jarvis bot
jarvis_process = subprocess.Popen(['python3', 'Jarvis/main.py'])

# Run friday bot
friday_process = subprocess.Popen(['python3', 'Friday/main.py'])

# Wait for both to finish (optional)
jarvis_process.wait()
friday_process.wait()
