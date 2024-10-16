import os
import sys
import time
import subprocess
import openai
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import clear
from playwright.sync_api import sync_playwright
import tiktoken

# Style for the CLI
style = Style.from_dict({
    'prompt': 'bg:#ansiblack #ansigreen bold',
    'command': '#ansigreen',
    'output': '#ansiwhite',
})

# Initialize prompt session
session = PromptSession()

# Set up OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize tokenizer
enc = tiktoken.get_encoding("cl100k_base")

def num_tokens_from_string(string: str) -> int:
    """Returns the number of tokens in a text string."""
    return len(enc.encode(string))

def print_slowly(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())
    return process.poll()

def get_input(prompt_text):
    return session.prompt(HTML(f'<prompt>{prompt_text}</prompt> '), style=style)

def get_ai_assistance(prompt, max_tokens=150):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant helping with the setup and deployment of an Incident Management SaaS application."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            n=1,
            temperature=0.7,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        print(f"Error getting AI assistance: {str(e)}")
        return "Unable to get AI assistance at the moment. Please proceed with the next step."

def setup_vercel():
    print_slowly("Setting up Vercel...")
    email = get_input("Enter your Vercel email:")
    password = get_input("Enter your Vercel password:")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://vercel.com/login")
            page.fill('input[name="email"]', email)
            page.fill('input[name="password"]', password)
            page.click('button[type="submit"]')
            page.wait_for_load_state("networkidle")
            
            if "dashboard" in page.url:
                print_slowly("Successfully logged in to Vercel!")
                token = page.evaluate("() => localStorage.getItem('token')")
                print_slowly(f"Your Vercel token is: {token}")
                return token
            else:
                print_slowly("Failed to log in to Vercel. Please check your credentials.")
                return None
    except Exception as e:
        print(f"Error setting up Vercel: {str(e)}")
        return None

def setup_stripe():
    print_slowly("Setting up Stripe...")
    api_key = get_input("Enter your Stripe API Key:")
    return api_key

def deploy_application(vercel_token):
    print_slowly("Deploying application to Vercel...")
    os.environ['VERCEL_TOKEN'] = vercel_token
    result = run_command("vercel --token $VERCEL_TOKEN --prod")
    if result == 0:
        print_slowly("Application deployed successfully!")
    else:
        print_slowly("Deployment failed. Please check the logs.")

def main():
    clear()
    print_slowly("Welcome to the Incident Management SaaS Setup CLI!")
    print_slowly("This tool will guide you through the setup and deployment process.")
    
    # Get AI assistance for overall process
    setup_info = get_ai_assistance("Provide a brief overview of the setup process for an Incident Management SaaS application, including the need for Vercel and Stripe credentials.", max_tokens=200)
    print_slowly(setup_info)
    
    # Vercel setup
    vercel_info = get_ai_assistance("Explain what Vercel is and why we're using it for deployment.", max_tokens=100)
    print_slowly(vercel_info)
    vercel_token = setup_vercel()
    if not vercel_token:
        return
    
    # Stripe setup
    stripe_info = get_ai_assistance("Describe what Stripe is and why we need an API key for our application.", max_tokens=100)
    print_slowly(stripe_info)
    stripe_api_key = setup_stripe()
    
    # Save credentials to .env file
    try:
        with open('.env', 'w') as f:
            f.write(f"VERCEL_TOKEN={vercel_token}\n")
            f.write(f"STRIPE_API_KEY={stripe_api_key}\n")
        print_slowly("Credentials saved to .env file.")
    except Exception as e:
        print(f"Error saving credentials: {str(e)}")
    
    # Deployment process
    deployment_info = get_ai_assistance("Explain the process of deploying a Node.js application to Vercel.", max_tokens=150)
    print_slowly(deployment_info)
    deploy_application(vercel_token)
    
    # Final steps
    final_steps = get_ai_assistance("Provide some final steps or best practices after deploying an Incident Management SaaS application.", max_tokens=150)
    print_slowly(final_steps)
    
    print_slowly("Setup and deployment complete!")

if __name__ == "__main__":
    main()