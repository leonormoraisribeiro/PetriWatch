# PetriWatch

Python application developed in collaboration with **i3S – Instituto de Investigação e Inovação em Saúde** (Porto, Portugal; [www.i3s.up.pt](https://www.i3s.up.pt)).

**PetriWatch** is a lightweight Raspberry Pi tool designed for **automatic, long-term image acquisition**. It was conceived for **Petri dish culture growth monitoring** (and for subsequent time-lapse video generation from the images acquired) and is equally well suited for documenting other slow processes.

The hardware setup used is similar to that of **WellView** (Raspberry Pi 4B + Raspberry Pi HQ Camera), except that a lower magnification C-mount objective is used in place of the stereo microscope.

--- 

## Features

### Image Acquisition

- Time interval-based image acquisition
- Configurable intervals:
  - **1, 2, 5, 10, 15, 20 or 30 minutes**
- Selectable image resolution:
  - **4056 × 3040 (full res)**
  - **2028 × 1520**
  - **1014 × 760**
- Simple GUI using Tkinter
- Live preview mode from Raspberry Pi HQ camera  
- Automatic creation of a folder for each experiment
- Numeric field for setting the total number of frames
- Progress indicator displaying acquisition status  
- Stable for long-running experiments (multiple days)

### Video Generation
- **Optional automatic video creation** at the end of every timelapse (via FFmpeg)
- **Manual video generation tool** available in the GUI:
  - Lists only experiment folders from:
    ```
    ~/Pictures/Timelapses
    ```
  - User selects:
    - Timelapse folder  
    - Output video filename  
    - Framerate (fps)
- Video output encoded as **H.264 (MP4)** for universal compatibility

---

## Installation

### 1. Update the system
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install dependencies
```bash
sudo apt install -y python3-tk python3-opencv python3-pil.imagetk ffmpeg
```

### 3. Install git (if needed)
```bash
sudo apt install -y git
```

### 4. Clone the repository
```bash
git clone https://github.com/leonormoraisribeiro/PetriWatch
cd PetriWatch
```

### 5. Run PetriWatch
```bash
python3 petriwatch.py
```

---

## File Storage
Images are automatically saved under:
```bash
~/Pictures/PetriWatch/{ExperimentName}/frame_00001.png
```
Each experiment gets its own folder.
Images are timestamped and numbered sequentially.

---

## Usage Guide
1. Enter the **experiment name**
2. Select **interval** between captures
3. Select the image **resolution**
4. Insert the **total number of photos**
5. Optional) Enable **"Create video automatically"**
6. Optional: open the **live preview**
7. Press **Start Timelapse** 
8. Acquisition begins; progress is displayed in real-time
9. The program runs until all frames are captured

When finished:
- If auto-video is enabled → MP4 is created automatically
- Otherwise, use "Create Video Manually" to process any past experiment

### Manual Video Creation
Click Create Video Manually in the GUI.
You will be prompted to:
1. Choose an experiment folder (only folders in ~/Pictures/Timelapses are shown)
2. Enter:
  - Framerate (fps)
  - Output filename (default: video.mp4)
3. PetriWatch then calls FFmpeg to create the video.

---

## Dependencies
Already included with Python:
- Tkinter
- datetime
- threading
- subprocess
- pathlib
- json

Requires installation on Raspberry Pi:
- OpenCV (cv2)
- Pillow (PIL)
- FFmpeg (required for video generation)

---

## Notes
- Designed for Raspberry Pi 4 & 5 with HQ Camera
- Works with both rpicam-* and libcamera-* backends
- The application is designed for multi-day uninterrupted acquisition
- A UPS or stable power source is recommended for long recordings

---

## License
This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

This means that:
- You are free to **use**, **modify**, and **redistribute** this software.
- Any distributed modified version must also be released under the **same GPL license**.
- The full license text is available in the [LICENSE](LICENSE) file.

For more details, see the official GNU documentation:  
https://www.gnu.org/licenses/gpl-3.0.en.html

