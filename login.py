import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import requests
import subprocess
import base64

#verify
hwid = str(subprocess.check_output(
    'wmic bios get serialnumber')).split('\\r\\n')[1].strip('\\r').strip()

def getdburl():
    url = 'https://raw.githubusercontent.com/y9b/simple_login/refs/heads/main/db.txt' #change to your url
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.splitlines()
    else:
        print("Failed to get database.")
        return []

def getdate():
    try:
        response = requests.get('http://worldtimeapi.org/api/ip')
        if response.status_code == 200:
            data = response.json()
            current_date_str = data['datetime'].split('T')[0]
            return datetime.strptime(current_date_str, '%Y-%m-%d')
        else:
            return None
    except requests.RequestException:
        return None

#base64 decode encode
def encode(data):
    return base64.b64encode(data.encode()).decode()

def decode(data):
    return base64.b64decode(data.encode()).decode()

#login process
def check_login(username, password, hwid):
    try:
        current_hwid = hwid
        current_date = getdate()

        if not current_date:
            return False, "Failed to retrieve the current date from the API."

        database = getdburl()

        for line in database:
            parts = line.strip().split(':')

            enc_username, enc_password, db_hwid, db_expiration = parts

            db_username = decode(enc_username)
            db_password = decode(enc_password)

            if username == db_username and password == db_password and current_hwid == db_hwid:
                expiration_date = datetime.strptime(db_expiration, '%Y-%m-%d')

                if current_date <= expiration_date:
                    days_left = (expiration_date - current_date).days
                    return True, f"Login successful! Subscription expires in {days_left} day(s)."
                else:
                    return False, "Subscription expired."
        return False, "Invalid username, password, or HWID."
    except Exception as e:
        return False, f"An error occurred: {e}"

def login():
    username = entry_username.get()
    password = entry_password.get()
    
    success, message = check_login(username, password, hwid)
    
    if success:
        messagebox.showinfo("Success", message)
    else:
        messagebox.showerror("Error", message)


#GUI
window = tk.Tk()
window.title("Secure Login")
window.geometry("300x300")

label_username = tk.Label(window, text="username")
label_username.pack(pady=10)
entry_username = tk.Entry(window)
entry_username.pack()

label_password = tk.Label(window, text="password")
label_password.pack(pady=10)
entry_password = tk.Entry(window, show="*")
entry_password.pack()

login_button = tk.Button(window, text="Login", command=login)
login_button.pack(pady=20)

window.mainloop()
