# Safe Night-Time Navigation Assistant

## 📌 Project Overview

The Safe Night-Time Navigation Assistant is a driver-monitoring prototype designed to detect signs of driver drowsiness using a camera.

The system uses computer vision to detect the driver's face and eyes. If the driver's eyes remain undetected for a predefined period, the system identifies a possible drowsiness event and provides an audible warning.

## 🎯 Objective

The main objective of this project is to develop a computer-vision-based safety assistant that can:

- Monitor the driver's face
- Detect the driver's eyes
- Identify prolonged eye closure
- Detect possible drowsiness
- Generate an audible warning
- Display the driver's current monitoring status
- Record drowsiness events in a log file

## 🛠️ Technologies Used

- Python
- OpenCV
- NumPy
- Computer Vision
- Haar Cascade Classifiers
- Windows `winsound`
- VS Code

## ⚙️ System Features

### 1. Face Detection

The system uses OpenCV's Haar Cascade classifier to detect the driver's face.

### 2. Eye Detection

The detected face region is analyzed to identify the driver's eyes.

### 3. Drowsiness Detection

If the driver's eyes remain undetected continuously for the configured duration, the system identifies a possible drowsiness event.

### 4. Audible Alert

A Windows system beep is generated when drowsiness is detected.

### 5. Driver Status UI

The application displays statuses such as:

- AWAKE
- BLINK / CHECKING
- EYES CLOSED
- DROWSINESS ALERT!
- NO FACE DETECTED

### 6. Event Logging

Detected drowsiness events are recorded with timestamps in:

```text
drowsiness_log.txt