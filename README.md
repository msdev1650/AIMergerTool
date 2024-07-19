# AIMergerTool

This innovative tool enables users to effectively merge diverse text inputs, including C# code files, into a unified prompt. As a result, AIMergerTool streamlines code-optimization processes and saves valuable time. Key features include an intuitive API key management system, seamless model selection, and efficient response handling.

![1](https://github.com/user-attachments/assets/9322ca30-39ca-40cc-ae4d-699be6502476)

## Features

- User-friendly Tkinter GUI
- Secure API key management
- Support for multiple GPT models
- C# file integration
- Token counting and management
- Debug mode for testing
- Threaded API requests for responsive UI
- Automatic response saving
- Comprehensive error handling and logging

## Installation

1. Clone the repository:

git clone https://github.com/yourusername/AIMergerTool.git




2. Navigate to the project directory:

cd AIMergerTool




3. Install the required dependencies:

pip install -r requirements.txt




## Usage

1. Run the application:

python ai_merger_tool.py




2. On first run, you'll need to enter your OpenAI API key. Click the "Save API Key" button to securely store it for future use.

3. Select a GPT model from the dropdown menu.

4. (Optional) Load standard messages by clicking "Load Standard Messages".

5. Enter your prompt in the text fields:
- Start Message Part: Initial context or instructions
- Middle Message Part: Main content or code to be processed
- End Message Part: Additional instructions or closing remarks

6. To include C# files, click "Open File Explorer" and select the desired files.

7. (Optional) Enable Debug Mode to test without sending requests to the API.

8. Click "Send to GPT" to process your prompt.

9. The GPT response will appear in the "GPT Response" tab.

10. Debug logs can be viewed in the "Debug Logs" tab.

## Configuration

- `start_message.txt` and `end_message.txt`: Customize these files in the project directory to set default start and end messages.
- Max Tokens: Adjust the maximum number of tokens for the API request.
- Manual Token Entry: Enable for fine-grained control over token limits.

## Troubleshooting

- If you encounter issues with the API key, ensure it's correctly entered and saved.
- Check the Debug Logs for detailed error messages and application status.
- Ensure you have an active internet connection for API requests.

## Contributing

Contributions to AIMergerTool are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool interacts with OpenAI's GPT models. Ensure you comply with OpenAI's use-case policy and terms of service when using this tool.
