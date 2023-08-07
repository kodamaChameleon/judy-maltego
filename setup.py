import subprocess, os

# Install required python dependencies
def install_requirements():
    subprocess.check_call(['pip', 'install', '-r', 'requirements.txt'])

# Build config file for easy importation
def build_config():
    subprocess.check_call(['python3', 'project.py', 'list'])

# Store Twilio API creds
def store_account_credentials():

    if os.path.exists(".key"):
        answer = ""
        while answer not in ['y','n']:
            answer = input(".key already exist. Overwrite (y/n)? ").lower() 

        if answer == 'n':
            return

    account_sid = input("Please enter your Twilio Account SID: ")
    auth_token = input("Please enter your Twilio Auth Token: ")

    try:
        with open(".key", "w") as file:
            file.write(f"ACCOUNT_SID={account_sid}\n")
            file.write(f"AUTH_TOKEN={auth_token}\n")
        print("Account credentials have been successfully stored in .key.")
    except Exception as e:
        print(f"An error occurred while storing the credentials: {e}")

if __name__ == '__main__':
    install_requirements()
    store_account_credentials()
    build_config()