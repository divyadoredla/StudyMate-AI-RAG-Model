import os
import sys
import subprocess

def kill_python_processes():
    print("Attempting to kill all python/streamlit processes...")
    current_pid = os.getpid()
    
    # Try using taskkill with absolute path
    try:
        # We target all python.exe processes except this one if possible, but taskkill /F /IM python.exe will kill everything including this script.
        # That is actually fine since we want to clear everything anyway!
        print("Running taskkill via absolute path...")
        subprocess.run(["C:\\Windows\\System32\\taskkill.exe", "/F", "/IM", "python.exe"], capture_output=True)
        print("Taskkill command sent.")
    except Exception as e:
        print(f"Taskkill failed: {e}")

    # Try PowerShell Stop-Process
    try:
        print("Running PowerShell Stop-Process...")
        subprocess.run(["powershell", "-Command", "Stop-Process -Name python -Force"], capture_output=True)
    except Exception as e:
        print(f"PowerShell Stop-Process failed: {e}")

    # Try WMIC as fallback
    try:
        print("Running WMIC process delete...")
        subprocess.run(["C:\\Windows\\System32\\wbem\\wmic.exe", "process", "where", "name='python.exe'", "delete"], capture_output=True)
    except Exception as e:
        print(f"WMIC failed: {e}")

if __name__ == "__main__":
    kill_python_processes()
