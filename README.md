# Duo Crawler

A Python-based crawler for downloading and organizing Duolingo course content, including stories, guidebooks, and audio files.

## Quick Start

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
# or: winget install astral-sh.uv                # Windows

# Clone and setup
git clone <repository-url>
cd duo-crawler
uv sync

# Configure credentials
cp .env.example .env
# Edit .env with your Duolingo credentials

# Run the crawler
uv run duo-crawler base-info
```

## Features

- Download Duolingo course information and content
- Extract and organize story content with audio files
- Generate MP3 files from audio segments
- Support for multiple languages (Chinese, Spanish, Japanese)
- Command-line interface for easy automation
- Batch processing capabilities

## Requirements

- Python 3.10 or higher
- Valid Duolingo account credentials
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer (recommended)

## Why uv?

This project uses [uv](https://docs.astral.sh/uv/) for dependency management because it's:
- ⚡ **10-100x faster** than pip for package installation
- 🔒 **Reliable** with automatic dependency resolution
- 🎯 **Simple** - creates virtual environments automatically
- 🌍 **Cross-platform** - works on Windows, macOS, and Linux

## Installation

### Option 1: Automated Setup (Recommended)

For quick setup, use the provided setup scripts:

**Windows:**
```bash
# Run the setup script
setup.bat
```

**Linux/macOS:**
```bash
# Make the script executable and run
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Installation

#### Prerequisites

First, install [uv](https://docs.astral.sh/uv/), a fast Python package installer and resolver:

**Windows:**
```bash
# Using winget
winget install astral-sh.uv

# Or using pip
pip install uv
```

**macOS:**
```bash
# Using Homebrew
brew install uv

# Or using curl
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Quick Installation

```bash
# Clone the repository
git clone <repository-url>
cd duo-crawler

# Install with uv (creates virtual environment automatically)
uv sync
```

### Development Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd duo-crawler
```

2. Install with development dependencies:
```bash
# uv will automatically create a virtual environment and install all dependencies
uv venv .venv --python=3.10
```

3. Activate the virtual environment:
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### Alternative: Manual pip installation

If you prefer using pip:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file in the project root directory with your Duolingo credentials:

```env
authorization=your_authorization_token
user_id=your_user_id
```

### Getting Your Credentials

1. Log into Duolingo in your web browser
2. Open Developer Tools (F12)
3. Go to the Network tab
4. Refresh the page and look for API requests
5. Find a request to `duolingo.com` and copy the `Authorization` header value
6. Your `user_id` can be found in the response data of user-related API calls

## Usage

### Command Line Interface

The project provides a CLI for various operations:

```bash
# Using uv (recommended)
uv run duo-crawler base-info

# Or if virtual environment is activated
duo-crawler base-info

# Or run directly with Python
uv run python -m cli base-info
```

### Python API

You can also use the crawler programmatically:

```python
from duolingo import DuoCrawler

# Initialize the crawler
crawler = DuoCrawler()

# Download course information
crawler.download_courses(overwrite=False)

# Download story content and static files
crawler.download_story_static_files(overwrite=False)

# Generate MP3 files from stories
crawler.generate_story_mp3_files(overwrite=False)

# Download and process course parts
crawler.download_part_static_files(overwrite=False)
crawler.generate_part_mp3_files(overwrite=False)
```

## Project Structure

```
duo-crawler/
├── cli.py                 # Command-line interface
├── duolingo.py           # Main crawler class
├── main.py               # Basic usage example
├── setup.sh              # Linux/macOS setup script
├── setup.bat             # Windows setup script
├── pyproject.toml        # Project configuration (uv compatible)
├── requirements.txt      # Fallback pip requirements
├── README.md             # This file
├── LICENSE               # MIT license
├── .env.example          # Environment variables template
├── .env                  # Environment variables (not tracked)
├── .gitignore            # Git ignore rules
└── stuff/                # Downloaded content
    ├── course/           # Course data
    ├── course-es/        # Spanish course data
    ├── course-ja/        # Japanese course data
    ├── course-zh/        # Chinese course data
    └── static/           # Static files (audio, images)
```

## Features in Detail

### Course Content Download
- Downloads complete course structures
- Extracts lesson content and metadata
- Organizes content by language and course type

### Story Processing
- Downloads Duolingo story content
- Extracts audio segments
- Converts audio to MP3 format using pydub
- Maintains story structure and metadata

### Audio Processing
- Automatic audio file generation
- MP3 conversion and optimization
- Batch processing capabilities

## Dependencies

- **requests**: HTTP requests for API communication
- **pydub**: Audio file processing and conversion
- **python-dotenv**: Environment variable management
- **click**: Command-line interface framework

## Development

### Running Tests

```bash
# Using uv
uv run pytest

# Or with activated virtual environment
pytest
```

### Code Formatting

```bash
# Using uv
uv run black .

# Or with activated virtual environment
black .
```

### Type Checking

```bash
# Using uv
uv run mypy .

# Or with activated virtual environment
mypy .
```

### Linting

```bash
# Using uv
uv run flake8 .

# Or with activated virtual environment
flake8 .
```

### Adding Dependencies

```bash
# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Remove a dependency
uv remove package-name
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational purposes only. Please respect Duolingo's terms of service and rate limits when using this crawler. The authors are not responsible for any misuse of this software.

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Make sure your `.env` file contains valid credentials
2. **Network Timeouts**: The crawler includes retry logic, but very slow connections may still timeout
3. **File Permission Errors**: Ensure the script has write permissions to the `stuff/` directory
4. **Audio Processing Errors**: Make sure you have the required audio codecs installed for pydub

### Getting Help

If you encounter issues:
1. Check the error message and logs
2. Verify your configuration in `.env`
3. Ensure all dependencies are properly installed
4. Check the [Issues](https://github.com/yourusername/duo-crawler/issues) page for known problems

## Changelog

### Version 1.0.0
- Initial release
- Basic crawling functionality
- CLI interface
- Audio processing capabilities
