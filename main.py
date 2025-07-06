import subprocess


# Run jarvis bot
jarvis_process = subprocess.Popen(['python3', 'Jarvis/main.py'])

# Run friday bot
friday_process = subprocess.Popen(['python3', 'Friday/main.py'])

# Wait for both to finish (optional)

# Run both bots
jarvis_process = subprocess.Popen(['python3', 'Jarvis/main.py'])
friday_process = subprocess.Popen(['python3', 'Friday/main.py'])

# Wait for both to finish, if not needed then comment out.

jarvis_process.wait()
friday_process.wait()
