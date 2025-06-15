# Llama API Integration

This guide explains how to set up and use the Llama API with the TravelAgent service.

## Prerequisites

1. Python 3.8 or higher
2. Required Python packages (install via `pip install -r requirements.txt`):
   - `requests`
   - `python-dotenv`
   - `langchain`
   - `langchain-core`
   - `langchain-community`
3. A valid Llama API key

## Getting Started

### 1. Set Up Environment Variables

Create or update your `.env` file in the backend directory with the following variables:

```env
# Required: Your Llama API key
LLAMA_API_KEY=your_api_key_here

# Optional: Override the default API URL if needed
# LLAMA_API_URL=https://api.llama.com/v1/chat/completions

# Backward compatibility with existing code
META_API_KEY=${LLAMA_API_KEY}
```

### 2. Initialize the TravelAgent

```python
from app.services.langchain.agent import TravelAgent

# Initialize with default settings
agent = TravelAgent(
    model_name="Llama-4-Maverick-17B-128E-Instruct-FP8",
    temperature=0.7,
    max_tokens=500
)

# Process a message
response = agent.process_message("Hello, can you help me plan a trip?")
print(response)
```

## API Configuration

### Available Models

- `Llama-4-Maverick-17B-128E-Instruct-FP8` (default)
- Other models as provided by the Llama API

### Configuration Options

```python
agent = TravelAgent(
    model_name="Llama-4-Maverick-17B-128E-Instruct-FP8",  # Model to use
    temperature=0.7,      # Controls randomness (0.0 to 1.0)
    max_tokens=500,      # Maximum tokens to generate
    top_p=0.9,           # Nucleus sampling parameter
    frequency_penalty=0,  # Penalize new tokens based on frequency
    presence_penalty=0,   # Penalize new tokens based on presence
    **other_kwargs       # Additional model-specific parameters
)
```

## Testing

Run the test suite to verify your setup:

```bash
# Run all tests
python test_travel_agent.py

# Run with more verbose output
pytest -v test_travel_agent.py
```

## Error Handling

The API client handles various error conditions:

- **Authentication Errors**: Invalid or missing API key
- **Rate Limiting**: Too many requests
- **API Errors**: Server-side issues or invalid requests

Check the logs for detailed error messages and stack traces.

## Performance Considerations

- **Rate Limits**: Be aware of the API's rate limits
- **Response Times**: Network latency will affect response times
- **Token Usage**: Monitor token usage to avoid unexpected costs

## Security

- Never commit your API key to version control
- Use environment variables for sensitive information
- Consider using a secrets management service in production

## License

This integration is provided under the MIT License. The Llama API is subject to its own terms of service and usage policies.
