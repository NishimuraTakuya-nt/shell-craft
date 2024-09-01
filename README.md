# cmd-craft

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)
- AWS CLI
- Bitwarden CLI

## Environment Setup

To set up the environment variables for this project:

1. Copy the sample environment file:
   ```
   cp .env.sample .env
   ```

2. Replace the placeholder values with your actual configuration details:

Remember: Never commit your `.env` file to version control as it may contain sensitive information.

## Python Environment Setup

1. Create a virtual environment (optional but recommended):
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

2. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

To use the AWS authentication script:

1. Ensure your environment variables are set correctly in the `.env` file.

2. Make the script executable:
   ```
   chmod +x totp_to_sts_token.py
   ```

3. Run the script:
   ```
   ./totp_to_sts_token.py
   ```

The script will output JSON-formatted AWS session credentials, which can be used for AWS CLI or SDK authentication.

## Troubleshooting

If you encounter any issues:

1. Ensure all prerequisites are installed and up to date.
2. Verify that your `.env` file contains the correct information.
3. Check that your AWS CLI is configured with the correct profile.

For more detailed error messages, review the script's output.

## Contributing

Instructions for how to contribute to your project.

## License

Specify your project's license here.