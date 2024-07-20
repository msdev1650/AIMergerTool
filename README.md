# AI Merger Tool

AI Merger Tool is an advanced application that facilitates the seamless integration of diverse text inputs, including C# code files, into a unified prompt. This tool significantly streamlines code optimization processes, enhances productivity, and saves valuable time for developers and AI enthusiasts.

![AI Merger Tool Interface](https://github.com/user-attachments/assets/2959a5fc-abc1-42b3-bbd9-00292cfcb1a5)

## Key Features

- **Intuitive Tkinter GUI**: User-friendly interface for easy navigation and operation.
- **Secure API Key Management**: Encrypted storage and handling of OpenAI API keys.
- **Multi-Model Support**: Compatibility with a wide range of GPT models.
- **C# File Integration**: Seamless incorporation of C# files into prompts.
- **Token Management**: Real-time token counting and limit enforcement.
- **Debug Mode**: Test functionality without sending API requests.
- **Threaded API Requests**: Ensures a responsive UI during processing.
- **Automatic Response Saving**: Organizes and stores GPT responses efficiently.
- **Comprehensive Logging**: Detailed error handling and debugging information.

## Installation

1. Clone the repository:

git clone https://github.com/yourusername/AIMergerTool.git




2. Navigate to the project directory:

cd AIMergerTool




3. Install required dependencies:

pip install -r requirements.txt




## Usage Guide

1. Launch the application:

python ai_merger_tool.py




2. First-time setup: Enter and save your OpenAI API key.

3. Select your preferred GPT model from the dropdown menu.

4. Construct your prompt:
- Start Message: Set initial context or instructions.
- Middle Message: Input main content or code for processing.
- End Message: Add final instructions or closing remarks.

5. For C# file integration, use the "Open File Explorer" button.

6. (Optional) Enable Debug Mode for testing without API calls.

7. Click "Send to GPT" to process your prompt.

8. View GPT responses in the dedicated tab.

9. Access debug information in the "Debug Logs" tab.

## Advanced Configuration

- Customize default messages in `active_templates/start_message.txt` and `active_templates/end_message.txt`.
- Adjust token limits using the Max Tokens feature.
- Fine-tune token control with Manual Token Entry mode.

## Troubleshooting

- Verify API key correctness if experiencing authentication issues.
- Consult Debug Logs for detailed error messages and application status.
- Ensure a stable internet connection for API interactions.

## Contributing

We welcome contributions to AI Merger Tool! Please submit your Pull Requests for review.

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for full details.

## Disclaimer

AI Merger Tool interacts with OpenAI's GPT models. Users are responsible for ensuring compliance with OpenAI's use-case policies and terms of service.
