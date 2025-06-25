# Web Virtual Mouse (Gesture Controlled)
Control your computer using hand gestures—no physical mouse required! This project uses your webcam, MediaPipe, OpenCV, and Python to turn your hand into a virtual mouse for basic tasks like moving the cursor, clicking, scrolling, and more.

⚙️ Tech Stack
1.Python
2.OpenCV
3.MediaPipe
4.PyAutoGUI
5.ScreenBrightnessControl
6.pycaw (for audio control)

🔧 Enhancing Accuracy & Performance (Planned)

To make the virtual mouse more reliable and responsive:
* Gesture Smoothing: Implement moving average filters or Kalman filters to reduce jitter in hand tracking.
* Custom Gesture Training: Allow users to define or train custom gestures for better personalization.
* Dynamic Frame Rate Handling: Adapt processing based on system load to avoid lag.
* Multi-resolution Support: Optimize for different camera resolutions and aspect ratios.
* Environment-Aware Calibration: Detect lighting and background clutter to enhance hand detection accuracy.
* Multi-threading: Use threads or async handling for frame capture and processing to boost performance
