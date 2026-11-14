# 🎙️ Raaj AI Voice Console

> **Next-Gen Intelligent Voice, Search & Productivity Assistant**

Raaj AI Voice Console is a modern AI-powered web assistant designed to combine **voice interaction, web search, YouTube, productivity tools, Smart Notes, WhatsApp messaging, and utility features** into a single responsive dashboard.

The project provides a futuristic AI dashboard experience with a responsive interface designed for **mobile phones, tablets, and laptops/desktops**.

---

## 🚀 Live Demo

🌐 **Live Application:**  
https://yolovisionstudiopro-rs.streamlit.app/

---

## ✨ Features

### 🎙️ AI Voice & Chat
- Voice command input
- Text command input
- Speech recognition
- AI assistant responses
- Voice response support
- Command history
- Browser-based microphone support

### 🎬 YouTube Studio
- Search YouTube
- Play YouTube videos
- Search songs
- Open YouTube directly

Example:
```text
play Nazar Lagi
```

```text
search youtube for Python tutorial
```

### 🌐 Web Search
- Open Google
- Google search
- Gmail
- GitHub
- LinkedIn
- ChatGPT

Examples:
```text
open google
search google for Python
open gmail
open github
open linkedin
open chatgpt
```

### 🌤️ Weather & World
Dedicated area for weather and world-related information.

### 📖 Wikipedia Hub
Search and explore general knowledge.

### 📝 Smart Notes
Create and store quick notes inside the application.

### 💬 WhatsApp Portal
Create WhatsApp chat links with a phone number and message.

> Direct WhatsApp Web automation may require a local desktop environment. Cloud deployments should use WhatsApp links or an official WhatsApp API.

### 🛠️ Tools & Fun
- 🧮 Instant Math Solver
- 🔐 Password Generator
- 🪙 Coin Flip
- 🎲 Dice Roller

---

# 🎨 UI / UX

Raaj AI uses a futuristic AI dashboard design:

- Dark futuristic interface
- Glassmorphism cards
- Neon gradients
- AI-inspired visual elements
- Animated voice waveform
- Glowing microphone interaction
- Rounded cards
- Responsive navigation
- Modern typography
- Interactive tool cards
- Mobile-friendly layout

---

# 📱 Responsive Design

### 📱 Mobile — 320px–767px
- Hamburger navigation
- Bottom navigation
- Full-width command input
- Touch-friendly buttons
- Stacked feature cards

### 📲 Tablet — 768px–1199px
- Collapsible navigation
- Responsive card grid
- Optimized spacing
- Touch-friendly controls

### 💻 Laptop / Desktop — 1200px+
- Full sidebar
- Large AI hero section
- Voice waveform
- Feature dashboard
- Utility tools
- Quick actions
- Session statistics

---

# 🧰 Technology Stack

## Frontend
- Streamlit
- Gradio
- HTML
- CSS
- JavaScript

## Backend / Application Logic
- Python

## Voice & Speech
- SpeechRecognition
- Browser microphone
- gTTS / TTS support

## Web & Automation
- PyWhatKit
- YouTube
- Google Search

## Deployment
- Streamlit Community Cloud
- GitHub

---

# 📁 Project Structure

```text
Raaj-AI-Voice-Console/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── Alexa_adv.py
├── Alexa_raj.py
├── Play_a_video.py
├── whatsapp_msg.py
│
└── assets/
    ├── logo/
    ├── icons/
    └── images/
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/raaj-ai-voice-console.git
cd raaj-ai-voice-console
```

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
```

Activate:

```bash
.venv\\Scripts\\activate
```

## 3. Upgrade pip

```bash
python -m pip install --upgrade pip
```

## 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

---

# 📦 Requirements

Example `requirements.txt`:

```text
streamlit>=1.40,<2
gradio>=6,<7
SpeechRecognition>=3.10,<4
gTTS>=2.5,<3
```

---

# ▶️ Run the Application

```bash
streamlit run app.py
```

Normally available at:

```text
http://localhost:8501
```

---

# 🎙️ Voice Commands

Examples:

```text
hello
open youtube
open google
open gmail
open github
open linkedin
open chatgpt
play Nazar Lagi
search youtube for Python tutorial
search google for Streamlit
what time is it
today date
```

---

# 🧠 Application Architecture

```text
                ┌──────────────────────┐
                │   User Interaction   │
                └──────────┬───────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
         Text Input                Voice Input
              │                         │
              │                  Speech Recognition
              │                         │
              └────────────┬────────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │ Command Processor │
                 │  handle_command() │
                 └─────────┬─────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   Web Search          YouTube          Productivity
        │                  │                  │
        ▼                  ▼                  ▼
    Google            YouTube             Notes
    Websites          Search/Play         Tools
                                           WhatsApp
                                           Math
                                           Password
                                           Games
```

---

# 🔊 Voice Processing

```text
Microphone
     ↓
Audio Recording
     ↓
Speech Recognition
     ↓
Text Command
     ↓
Command Processor
     ↓
Assistant Response
     ↓
Voice / Text Output
```

---

# 🧩 Gradio Integration

The project includes a Gradio interface for voice and text interaction.

```text
Streamlit
   +
Gradio
   ↓
Unified AI Assistant Experience
```

---

# ☁️ Deployment

## Streamlit Community Cloud

Recommended deployment flow:

```text
GitHub Repository
       ↓
Streamlit Community Cloud
       ↓
app.py
       ↓
requirements.txt
       ↓
Live Web Application
```

Required files:

```text
app.py
requirements.txt
README.md
```

Select:

```text
Main file:
app.py
```

---

# ⚠️ Local vs Cloud Features

### Local Windows environment
Can support machine-dependent features such as:
- Windows PowerShell TTS
- Local browser launching
- Desktop microphone access
- PyWhatKit desktop automation

### Cloud environment
A cloud server cannot directly control your personal computer.

Prefer:
- Browser microphone
- Web links
- API-based integrations
- Cloud-compatible TTS
- WhatsApp links
- External APIs

---

# 🔐 Security

Never upload sensitive information to GitHub.

Do not commit:

```text
.env
API keys
passwords
private tokens
credentials
```

Example:

```text
OPENAI_API_KEY=your_api_key
WEATHER_API_KEY=your_api_key
```

Add to `.gitignore`:

```text
.env
__pycache__/
.venv/
*.pyc
```

---

# 🐛 Troubleshooting

## SpeechRecognition not found

```bash
python -m pip install SpeechRecognition
```

Test:

```bash
python -c "import speech_recognition as sr; print('SpeechRecognition OK')"
```

## Streamlit not found

```bash
python -m pip install streamlit
```

Run:

```bash
python -m streamlit run app.py
```

## Gradio not found

```bash
python -m pip install gradio
```

## Microphone not working

Check:
1. Browser microphone permission
2. Windows microphone permission
3. Correct input device
4. Browser support
5. SpeechRecognition installation

---

# 🔮 Future Improvements

- 🤖 LLM-powered conversational AI
- 🧠 Personalized memory
- 🌦️ Real-time weather API
- 📰 Live news
- 📚 Advanced Wikipedia search
- 🎙️ Continuous voice conversation
- 🗣️ Multiple voice personas
- 🌍 Multi-language support
- 🔐 User authentication
- ☁️ Cloud database
- 📊 User analytics dashboard
- 📱 Progressive Web App support
- 🔔 Notification system
- 🎵 Advanced YouTube controls
- 🧩 Plugin architecture
- ⚡ Real-time streaming responses

---

# 🎯 Project Goals

The main goal of Raaj AI Voice Console is to create a single intelligent interface where users can:

```text
Talk
 ↓
Search
 ↓
Create
 ↓
Automate
 ↓
Explore
```

---

# 👨‍💻 Developer

**Rajendra (Raaj)**

MCA | AI & Data Analytics Enthusiast

### Areas of Interest
- Artificial Intelligence
- Machine Learning
- Data Analytics
- Python
- Web Development
- Generative AI
- Voice AI
- UI/UX

---

# ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

---

## 📄 License

This project is available for educational and personal development purposes.

---

## 🚀 Raaj AI Voice Console

**Talk • Search • Create • Automate • Explore**

> Built with Python, Streamlit, Gradio and modern web technologies.
