import os
import sys

# Get the OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY environment variable not set.")
    print("Please set your OpenAI API key as an environment variable.")
    sys.exit(1)

# Set the environment variable (in case it wasn't already set)
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

# Run the Flask app
if __name__ == "__main__":
    # Import and run the Flask app
    from app import app
    app.run(debug=True, host='127.0.0.1', port=5000)