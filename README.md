# SpeechNote - Intelligent Teleprompter for Presentations

## Project Overview

SpeechNote is an intelligent teleprompter application designed for presenters. It provides real-time text guidance for presentations through TTML (Timed Text Markup Language) subtitle files. The application features a beautiful UI interface, precise time control, and flexible display modes.

## note.py Functionality

`note.py` is the core file of the project, implementing a desktop application based on PyWebView that provides real-time text display and teleprompter functionality for presentations.

### Main Function Modules

#### 1. **TTML File Parsing**
- Supports opening and parsing TTML format subtitle files
- Extracts timecodes (begin/end) and text content from subtitles
- Converts subtitle content into an internal timeline data structure

#### 2. **Presentation Timing System**
- **Real-time Countdown**: Displays the remaining time until the end of the presentation
- **Time Warning**: The timer turns red when less than 30 seconds remain
- **Precise Synchronization**: Synchronizes precisely with timecodes in the TTML file
- **Pause Mechanism**: Supports pause and resume functionality with automatic pause duration accumulation

#### 3. **Interactive Controls**
- **Spacebar Operations**:
  - Initial state: Long press 3 seconds to prepare
  - Countdown state: Release spacebar to start presentation
  - During presentation: Short press to pause, long press 3 seconds to reset
  - Paused state: Short press to resume, long press 3 seconds to reset

#### 4. **Display Modes**

**Regular Mode**:
- Large font current line display (42px bold)
- Progress bar reflects current sentence progress in real-time
- Preview of next text line
- Bottom status indicator
- Complete time countdown display

**Compact Mode**:
- Window resizes to 230×120 pixels
- Compact interface layout
- Automatic text scrolling (when progress exceeds 50%)
- Time displayed as seconds (e.g., "45s")
- Convenient for long-term display in screen corner

#### 5. **Visual Feedback**
- **Real-time Progress Bar**: Shows playback progress of the current sentence
- **Pause Overlay**: Displays "Paused" message when paused
- **Text Fade Effect**: Text transparency reduces when paused
- **Status Indicator Bar**: Real-time application state information

#### 6. **UI Design Features**
- Modern design with light theme support
- Responsive layout automatically adapts to window size
- Smooth transition animations and interactive feedback
- Customizable light/dark mode support (CSS variables)

## Usage Guide

### Install Dependencies

```bash
pip install pywebview
```

### Run Application

```bash
python note.py
```

### Operation Workflow

1. **Start Application**
   - Application displays "Open Script File (TTML)" button on startup

2. **Load File**
   - Click the button to open file selection dialog
   - Select a .ttml format subtitle file
   - After loading, the teleprompter interface appears

3. **Start Presentation**
   - Hold spacebar for 3 seconds, wait for countdown to complete
   - After seeing ">>> Release spacebar to start <<<" message, release the spacebar
   - Presentation officially starts, text and timer synchronize in real-time

4. **During Presentation**
   - Short press spacebar: Pause presentation (can be resumed anytime)
   - Long press spacebar for 3 seconds: Reset presentation (return to initial state)
   - Observe timer and progress bar to maintain presentation pace

5. **Switch Display Mode**
   - Click the toggle icon in the bottom right corner
   - Switch between regular and compact modes

### TTML File Format Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="zh-CN" xmlns="http://www.w3.org/ns/ttml">
  <body>
    <div>
      <p begin="00:00:00" end="00:00:03">Hello everyone, welcome to today's presentation</p>
      <p begin="00:00:03" end="00:00:08">Today I will share three key points with you</p>
      <p begin="00:00:08" end="00:00:12">First, let's start with the first point</p>
    </div>
  </body>
</tt>
```

## Keyboard Shortcuts

| Operation | Effect |
|-----------|--------|
| Long press spacebar 3 seconds (initial state) | Enter countdown preparation |
| Release spacebar (countdown state) | Start presentation |
| Short press spacebar (during presentation) | Pause presentation |
| Long press spacebar 3 seconds (during/paused) | Reset presentation |
| Short press spacebar (paused state) | Resume presentation |

## Window Dimensions

- **Regular Mode**: 1000 × 600 pixels
- **Compact Mode**: 230 × 120 pixels
- **Minimum Size Limit**: 230 × 120 pixels

## Tech Stack

- **Python**: Core language
- **PyWebView**: Cross-platform desktop application framework
- **HTML/CSS/JavaScript**: Frontend interaction and interface rendering
- **DOM API**: Real-time UI updates

## Use Cases

- 📢 Presentation competitions and public speaking
- 🎓 Teaching lectures and academic presentations
- 🎤 Video recording and live streaming
- 💼 Business presentations and product launches
- 🗣️ Any scenario requiring precise time-controlled text display

---

**Version**: 1.0  
**Last Updated**: February 5, 2026
