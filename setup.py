import subprocess, os

# Install required python dependencies
def install_requirements():
    subprocess.check_call(['pip', 'install', '-r', 'requirements.txt'])

# Build config file for easy importation
def build_config():
    subprocess.check_call(['python3', 'project.py', 'list'])

# Store API Key
def openai_key():
    key_path = "openai.key"
    if not os.path.exists(key_path):
        api_key = input("Enter OpenAI API key: ")
        with open(key_path, 'w') as key_file:
            key_file.write(api_key)

if __name__ == '__main__':
    install_requirements()
    openai_key()
    # build_config()