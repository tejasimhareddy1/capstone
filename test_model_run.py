import subprocess

# Replace 'your_script.py' with the actual filename of your Python script
script_path = 'test_model.py'

# Run the script as a subprocess
process = subprocess.Popen(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Wait for the subprocess to finish and capture the output
stdout, stderr = process.communicate()

# Get the exit code of the subprocess
exit_code = process.returncode

# Print the results
print(f"Exit Code: {exit_code}")
print(f"Standard Output:\n{stdout.decode()}")
# print(f"Standard Error:\n{stderr.decode()}")
