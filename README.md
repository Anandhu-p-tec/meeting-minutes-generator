Description:
meeting-minutes-generator/
├── app/ # FastAPI backend logic
│ ├── main.py # Entry point of the FastAPI API
│ ├── config.py # Global configuration (API keys, model settings, etc.)
│ └── modules/ # Core processing modules
│ ├── preprocessing.py # Transcript preprocessing module
│ ├── summarizer.py # Summarization module using OpenAI/Gemini API
│ ├── exporter.py # Export meeting minutes to Word (.docx)
│ └── schema.py # MeetingMinutes data schema
│
├── ui/ # Gradio user interface
│ └── interface.py # Simple web interface using Gradio
│
├── requirements.txt # List of required Python packages
├── run.py # Script to run both FastAPI API and Gradio UI
└── .env # Environment variables (API keys)

How to Run
Install dependencies:
pip install -r requirements.txt

Set up your API Key:

Create a .env file in the project root with your API key:
OPENAI_API_KEY=your_openai_api_key_here

    # OR if using Gemini:

    GEMINI_API_KEY=your_gemini_api_key_here

Run the application:
python ui/interface.py

Open your browser and visit:
http://localhost:7860

Requirements
Python 3.9 or higher

All libraries listed in requirements.txt

⚠️ Notes
You must provide a valid OpenAI or Gemini API key to use the summarizer.py and exporter.py modules.

This application currently supports exporting meeting minutes to .docx (Word) format only.

The Gradio interface is a minimal UI for demo and testing purposes.

🛠️ Future Enhancements
Add support for more export formats (PDF, JSON, etc.)

Improve the Gradio web interface for usability

Add advanced preprocessing options (noise filtering, timestamping, etc.)

Optimize performance for large audio files

Let me know if you'd like me to also:

Add badges (e.g., Python version, license)

Create a sample screenshot or logo

Write sample usage with API calls (curl, Postman, etc.)

Or generate the final README.md file for you automatically.
