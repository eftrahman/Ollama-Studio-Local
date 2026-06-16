# Ollama Studio

💬 A clean, modern web interface for chatting with your local Ollama models.

Instead of using the terminal every time, you can open a browser and:

- 🧠 chat with installed Ollama models
- 📦 discover and install new models from inside the UI
- 🗂 keep chat history
- 🧾 view code blocks with copy buttons
- 🛠 adjust model settings from a modal

---

## ✨ What You Need

Before running this app, make sure you have:

- `Ollama` installed
- `Python 3` installed
- at least one Ollama model installed
  - or you can install one later from the app's `Discover models` button

---

## 🚀 Quick Start

### 1. Install Ollama

Go to:

`https://ollama.com/download`

Install it like any normal app.

After installation, make sure Ollama is running in the background.

You can test it with:

```bash
ollama --help
```

If that works, Ollama is installed correctly.

---

### 2. Download This Project

If you already have the files, you can skip this step.

If you want to clone it from GitHub:

```bash
git clone <your-repo-url>
cd ollama-web-ui
```

Or just download the ZIP from GitHub and extract it.

---

### 3. Start the Web App

From inside the project folder, run:

```bash
python3 app.py --host 127.0.0.1 --port 7860
```

You should see something like:

```text
Serving http://127.0.0.1:7860
Ollama backend: http://127.0.0.1:11434
```

---

### 4. Open It in Your Browser

Open:

`http://127.0.0.1:7860`

That’s it. 🎉

---

## 📦 Installing Models

You have 2 easy ways to install models.

### Option A: Install from the Web UI

Inside the app:

1. Click `Discover models`
2. Browse the model list
3. Click `Install`

You can also type a custom model name like:

```text
gemma4:e2b
qwen2.5-coder:7b
llama3.1:8b
```

and click `Install`.

### Option B: Install from Terminal

You can also install directly with Ollama:

```bash
ollama pull gemma4:e2b
```

Then return to the web UI and click `Refresh models`.

---

## 🖥 How To Use

### Start a new chat

Click `+ New chat` in the sidebar.

### Pick a model

Open `Settings` and choose your model.

### Send messages

Type in the message box and press:

- `Enter` to send
- `Shift + Enter` for a new line

### Work with code

If the model returns code blocks, you can:

- view them in styled code cards
- copy each code block separately
- copy the whole message if needed

### Manage chats

In the sidebar you can:

- search conversations
- pin chats
- duplicate chats
- delete chats

---

## 🧰 Recommended Models

If you are not sure where to start:

- `gemma4:e2b` → great small general model
- `qwen2.5-coder:7b` → strong for coding
- `llama3.2:3b` → lightweight and fast
- `mistral:7b` → solid all-rounder
- `llava:7b` → for vision/image prompts

---

## ❗ Troubleshooting

### The page says it cannot connect to Ollama

Make sure Ollama is running.

Try:

```bash
ollama list
```

If that command works, Ollama is running.

### `python3` is not found

Install Python 3 first:

`https://www.python.org/downloads/`

Then try again.

### No models appear

This usually means:

- you have not installed a model yet
- or Ollama is not running

Use the `Discover models` button or run:

```bash
ollama pull gemma4:e2b
```

### Model install takes a long time

That is normal for large models. They can be several GBs.

Smaller models download faster.

---

## 🔌 Ports Used

- Web UI: `127.0.0.1:7860`
- Ollama API: `127.0.0.1:11434`

If you want a different web port:

```bash
python3 app.py --host 127.0.0.1 --port 8080
```

Then open:

`http://127.0.0.1:8080`

---

## 🔒 Privacy

This app is designed for local use.

Your chats go to your local Ollama server on:

`127.0.0.1:11434`

That means your prompts stay on your machine unless you intentionally use a model or setup that sends data elsewhere.

---

## 📁 Project Files

- [app.py](/home/eftear/ollama-web-ui/app.py) → local web server and Ollama API bridge
- [index.html](/home/eftear/ollama-web-ui/index.html) → full browser UI

---

## ❤️ For Beginners

If you have never used Ollama before, the easiest path is:

1. Install Ollama
2. Run this app with `python3 app.py`
3. Open the browser page
4. Click `Discover models`
5. Install `gemma4:e2b`
6. Start chatting

That is the simplest working setup.
