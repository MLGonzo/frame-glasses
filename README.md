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

3. Install dependencies from the lock file:
```bash
uv sync
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
- `pyproject.toml` - Project dependencies and metadata
- `uv.lock` - Locked dependencies for reproducible installations

## Contributing

This is an exploratory project. Feel free to open issues or submit pull requests if you'd like to contribute to the research and development.

## License

[Add your chosen license here]
