# Brilliant Frames Explorer

This repository is an exploratory project for investigating and understanding how the Brilliant Frame AR glasses work. It's currently in the research and development phase, focusing on understanding the device's capabilities and communication protocols.

## Project Status

🚧 **Experimental** - This is a work in progress and may contain experimental or incomplete features.

## Setup

This project uses `uv` for Python package management.

### Prerequisites

1. Python 3.8 or higher
2. `uv` package manager

### Installation

1. First, install `uv` if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone this repository:
```bash
git clone https://github.com/yourusername/brilliant-frames.git
cd brilliant-frames
```

3. Create and activate a virtual environment using `uv`:
```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

4. Install dependencies:
```bash
uv pip install -r requirements.txt
```

## Usage

To run the camera example:
```bash
uv run camera.py
```

## Project Structure

- `camera.py` - Example script demonstrating camera functionality
- `lua/` - Lua scripts for the Frame device
- `frame_msg.py` - Message handling for Frame communication

## Contributing

This is an exploratory project. Feel free to open issues or submit pull requests if you'd like to contribute to the research and development.

## License

[Add your chosen license here]
