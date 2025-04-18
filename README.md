# Smart Email Assistant

A Streamlit-based AI assistant for managing your Gmail inbox using Langchain and Google Gmail API. This assistant helps you summarize emails, clean your inbox, categorize messages, create filters, and more — all powered by advanced AI models from OpenAI or Google Gemini.

---

## Features

- Summarize unread emails
- Clean up marketing emails older than 30 days
- Auto-categorize emails into Promotions, Work, Personal
- Create Gmail filters automatically
- Interactive chat interface powered by Langchain agents
- Supports Google Gemini and OpenAI models for AI responses
- Unsubscribe newslaters, to avoid unwanted mails.

---

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- A Google Cloud project with Gmail API enabled
- OAuth 2.0 credentials JSON file (`credentials.json`)

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/sonu2164/smart-email-assistant
   cd smart-email-assistant
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up Google API credentials:

   - Rename your Google OAuth client secrets file to `credentials.json` and place it in the project root.
   - The app will generate a `token.json` on first run after authenticating.

5. Create a `.env` file in the project root (optional):

   ```env
   # Optional: Use Google Gemini model by providing your Google API key
   GOOGLE_API_KEY=your_google_api_key_here
   ```

---

## Running the App

Start the Streamlit app with:

```bash
streamlit run app.py
```

This will open the Smart Email Assistant UI in your default browser.

---

## Usage

- Use the chat input to ask questions or give commands related to your Gmail inbox.
- Use the sidebar quick action buttons for common tasks like summarizing unread emails, cleaning marketing emails, categorizing inbox, and creating filters.
- The assistant uses AI models to understand and execute your requests.

---

## Example `.env` file

```env
GOOGLE_API_KEY=your_google_api_key_here
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Author

Developed by [sonu2164](https://github.com/sonu2164)

---

## Future Scopes

- Add a tool to automatically click on the unsubscribe button in emails, enabling users to easily unsubscribe from newsletters they no longer wish to receive.
- Enhance email categorization using machine learning to better understand user preferences and improve sorting accuracy.
- Implement smart reply suggestions to help users quickly respond to common email types.
- Integrate with calendar and task management tools to create events or tasks directly from emails.
- Support multiple email providers beyond Gmail for broader usability.
- Improve natural language understanding to handle more complex and varied user commands.

## Submission

This project is submitted for Quira Quest 25.
