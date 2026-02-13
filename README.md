# video-to-article

Turn YouTube videos into articles: downloads subtitles and description with [yt-dlp](https://github.com/yt-dlp/yt-dlp), then uses an AI model to draft an article and optionally add a critical review section. Output is saved as HTML (and intermediate files) under a per-video directory.

**Mac users new to the command line:** see [MAC_SETUP.md](MAC_SETUP.md) for installing Python, Homebrew, and running the tool in Terminal.

## Install

```bash
pip install video-to-article
```

For local models (MLX on Apple Silicon):

```bash
pip install video-to-article[mlx-lm]
```

On M3 Pro Mac we recommend the **Qwen/Qwen3-8B** model: `v2a <url> -m Qwen/Qwen3-8B`.

You can also install from source with [uv](https://docs.astral.sh/uv/): `uv sync` then `uv run v2a ...`.

## Setup

- **OpenAI:** For cloud models, set `OPENAI_API_KEY`. Get a key at [API keys](https://platform.openai.com/api-keys).
- **YouTube / yt-dlp:** Subtitle download uses EJS and impersonation (included). For full compatibility, a JavaScript runtime on your PATH is recommended so yt-dlp can run its challenge solver (otherwise you may see warnings and some videos may fail). Install [Deno](https://deno.com) if you don’t have one—e.g. `brew install deno` (macOS) or see [Deno’s install guide](https://docs.deno.com/runtime/getting_started/installation/) for Linux/Windows.

## Usage

```text
Usage: v2a [OPTIONS] VIDEO_URLS...

Convert YouTube videos to articles using AI.

Extra options (e.g. --temperature 0.7) are passed to the model.

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    video_urls      VIDEO_URLS...  YouTube video URLs to process [required]                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────╮
│ --model        -m      TEXT  Model name or path [default: gpt-5.2]                                      │
│ --output-dir   -o      PATH  Output directory for results [default: articles]                           │
│ --open-browser / --no-open-browser        Open the result HTML in the browser [default: open-browser]   │
│ --overwrite    -f            Overwrite cached step results                                              │
│ --skip-review                Skip the critical review step                                              │
│ --help                       Show this message and exit.                                                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

Example:

```bash
v2a "https://www.youtube.com/watch?v=..." -o articles
```

Run `v2a --help` anytime for the same reference.

## Contributing

Contributions are welcome. In particular, support for other LLM clients (e.g. for Linux or Windows, or other cloud providers) would make the tool more useful—see the generator layer and open an issue or PR.

## License

[MIT](LICENSE)
