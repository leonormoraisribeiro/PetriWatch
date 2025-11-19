# PetriWatch

Python application developed in collaboration with **i3S – Instituto de Investigação e Inovação em Saúde** (Porto, Portugal; [www.i3s.up.pt](https://www.i3s.up.pt)).

**PetriWatch** is a lightweight Raspberry Pi tool designed for **automatic, long-term image acquisition**, ideal for *petri dish growth monitoring*, *time-lapse generation*, and *slow biological processes*.

Using the same hardware setup as **WellView**  
(Raspberry Pi 4B + Raspberry Pi HQ Camera on a stereo microscope),  
PetriWatch captures images at user-defined intervals for hours or even days.

---

## Features

- Interval-based image acquisition for time-lapse recording  
- Configurable intervals:
  - **1, 2, 5, 10, 15, 20, 30 minutes**
- Selectable resolutions:
  - **4056 × 3040 (full res)**
  - **2028 × 1520**
  - **1014 × 760**
- Simple GUI using Tkinter
- Live preview mode from Raspberry Pi HQ camera  
- Automatic creation of a folder for each experiment
- Numeric field for total number of frames
- Large, colored **Start Recording** button
- Progress indicator showing acquisition status  
- Stable for long-running experiments (multiple days)

---

## Installation

### 1. Update the system
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install dependencies
```bash
sudo apt install -y python3-tk python3-opencv python3-pil.imagetk
```

### 3. Install git (if needed)
```bash
sudo apt install -y git
```

### 4. Clone the repository
```bash
git clone https://github.com/USERNAME/PetriWatch
cd PetriWatch
```

### 5. Run PetriWatch
```bash
python3 petriwatch.py
```

--

## File Storage
Images are automatically saved under:
```bash
~/Pictures/PetriWatch/{ExperimentName}/frame_00001.png
```
Each experiment gets its own folder.
Images are timestamped and numbered sequentially.

--

## Usage
1. Enter the **experiment name**
2. Select **interval** between captures
3. Select **resolution**
4. Insert the **total number of frames**
5. Optional: open the **live preview**
6. Press **Start Recording** 
7. Acquisition begins; the progress indicator updates automatically
8. The program runs until all frames are captured

--

## Dependencies
Already included with Python:
- Tkinter
- os
- datetime
- threading
- subprocess
Requires installation on Raspberry Pi:
- OpenCV (cv2)
- Pillow (PIL)

--

## Notes
- Ensure rpicam-still is installed for high-resolution captures
- The application is designed for multi-day uninterrupted acquisition
- A UPS or stable power source is recommended for long recordings



