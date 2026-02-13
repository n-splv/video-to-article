# Mac setup guide (non-technical)

Short guide to get your Mac ready so you can install and run **video-to-article**. For install steps, setup (API key, optional Deno), and usage, see the [main README](../README.md).

---

## 1. Install Homebrew (package manager)

Homebrew lets you install Python and other tools from the Terminal.

1. Open **Terminal**: press **Cmd + Space**, type `Terminal`, press Enter.
2. Go to [brew.sh](https://brew.sh) and copy the one-line install command shown there.
3. In Terminal, paste that line and press Enter. Enter your Mac password when asked (nothing will appear as you type).
4. Wait until it finishes. You only need to do this once.

---

## 2. Install Python and create an environment

You need Python 3 so that `pip install` works. Using a virtual environment keeps this project's packages separate from the rest of your system.

1. In Terminal, install Python via Homebrew:
   ```bash
   brew install python
   ```
2. Create a folder for your work (if you don't have one) and go into it, e.g.:
   ```bash
   mkdir -p ~/video-to-article && cd ~/video-to-article
   ```
3. Create a virtual environment in that folder:
   ```bash
   python3 -m venv .venv
   ```
4. Activate it (you'll do this whenever you open a new Terminal to work on this project):
   ```bash
   source .venv/bin/activate
   ```
   When it's active, you'll see `(.venv)` at the start of the line in Terminal.

Then follow the [Install](../README.md#install) section in the main README to run `pip install video-to-article` (and optional extras). Do that **after** activating the environment as above.

---

## 3. Running the script in Terminal

- **Open Terminal**: Cmd + Space → type `Terminal` → Enter.
- **Go to your project folder** (if needed), e.g.:
  ```bash
  cd ~/video-to-article
  ```
- **Activate the environment** (if you haven't in this window):
  ```bash
  source .venv/bin/activate
  ```
- Run the tool: see [Usage](../README.md#usage) in the main README for the `v2a` command and options.

Example (after install and [Setup](../README.md#setup)):

```bash
v2a "https://www.youtube.com/watch?v=..." -o articles
```

---

**Summary:** Install Homebrew → install Python with `brew install python` → create and activate a venv → then follow [Install](../README.md#install), [Setup](../README.md#setup), and [Usage](../README.md#usage) in the [main README](../README.md).
