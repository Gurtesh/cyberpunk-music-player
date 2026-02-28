# Cyberpunk Music Player for Raspberry Pi Walkman

A sleek, cyberpunk-themed music player UI built with PyQt5 for Raspberry Pi 4B, featuring system monitoring, weather display, and interactive controls. Designed to run on a Raspberry Pi with a DAC (such as Moondrop Dawn Pro) for high-resolution audio playback.

![Demo Screenshot](https://via.placeholder.com/800x450?text=Cyberpunk+Music+Player)

## Features

- **Cyberpunk UI**: Glitch effects, neon colors, circular progress bar, and futuristic widgets.
- **Music Control**: Play/pause, skip, volume, and seek using MPRIS2 or playerctl.
- **System Monitoring**: Real‑time CPU, RAM, and temperature display.
- **Weather Widget**: Current temperature and conditions (requires OpenWeatherMap API key).
- **Album Art Fetching**: Automatically retrieves cover art from Last.fm (demo key included).
- **Responsive Layout**: Fixed overlapping issues; widgets are positioned to avoid collisions.
- **Customizable**: Easily change colors, city for weather, and other parameters.

## Hardware Requirements

- Raspberry Pi 4B (8GB RAM recommended)
- DAC (e.g., Moondrop Dawn Pro) for high‑res audio
- Display (HDMI or touchscreen)
- Optional: Physical buttons for control

## Software Requirements

- Python 3.7+
- PyQt5
- Pillow (PIL)
- requests
- dbus‑python
- psutil (optional, for system stats)

All dependencies are listed in `requirements.txt`.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Gurtesh/cyberpunk-music-player.git
   cd cyberpunk-music-player
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Obtain an OpenWeatherMap API key (free at https://home.openweathermap.org/api_keys).

4. Edit `v3.0.py` and replace `YOUR_OPENWEATHERMAP_API_KEY` with your actual key (line ~126).

## Usage

Run the player with:

```bash
python v3.0.py
```

The player will start in full‑screen mode (adjustable in code). Use the on‑screen controls:

- **Circular progress bar**: Click to seek, long‑press to toggle play/pause.
- **Volume slider**: Adjust audio output.
- **System stats**: Displayed at bottom‑left.
- **Weather**: Displayed at top‑right.

### Keyboard Shortcuts

- `Space` – Play/Pause
- `Left/Right` – Skip tracks
- `Up/Down` – Volume up/down
- `F11` – Toggle fullscreen
- `Esc` – Exit

## Configuration

You can modify the following constants in `v3.0.py`:

- `WEATHER_CITY` – change the city for weather updates (default: `"Winnipeg,CA"`)
- Color schemes – adjust the RGB values in the `CircularProgress` and style sheets.
- Widget positions – tweak the `move()` calls in `CyberpunkMusicPlayer.__init__`.

## Project Structure

- `v3.0.py` – Main application (the only file you need to run).
- `requirements.txt` – Python dependencies.
- `README.md` – This file.
- `LICENSE` – MIT License.

## Troubleshooting

- **“No module named 'PyQt5'”** – Ensure PyQt5 is installed (`pip install PyQt5`).
- **Weather not updating** – Verify your OpenWeatherMap API key and internet connection.
- **Album art not showing** – The Last.fm demo key may be rate‑limited; replace with your own key if desired.
- **Overlapping widgets** – The layout has been fixed in version 4.1; if overlaps persist, adjust margins in `main_layout.setContentsMargins()`.

## License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by retro‑futuristic cyberpunk aesthetics.
- Uses OpenWeatherMap API for weather data.
- Album art provided by Last.fm (demo key).
- Built with PyQt5 and Python.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

*Enjoy the music and the glow of neon!*