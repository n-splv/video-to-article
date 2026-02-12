import importlib.resources
import re
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Callable
import webbrowser

import markdown

from video_to_article.download_utils import download_subtitles_and_description
from video_to_article.generator import Generator, get_generator
from video_to_article.logging_config import logger


@dataclass(kw_only=True)
class Pipeline:
    model: str
    output_dir: Path
    overwrite: bool
    skip_review: bool
    open_browser: bool
    generator_kwargs: dict

    def __post_init__(self):
        self.generator = get_generator(self.model, **self.generator_kwargs)

    def run(self, video_url: str):
        logger.info("Downloading subtitles and description")
        download_result = download_subtitles_and_description(video_url, self.output_dir)
        logger.info('Processing "%s"', download_result.video_title)
        cache_kwargs = {
            "video_dir": download_result.video_dir,
            "overwrite": self.overwrite,
        }

        transcript = uninterrupted_text(
            raw_srt=download_result.raw_srt,
            **cache_kwargs,
        )

        article_text = article(
            transcript=transcript,
            description=download_result.raw_description,
            title=download_result.video_title,
            generator=self.generator,
            **cache_kwargs,
        )

        if not self.skip_review:
            review_text = review(
                article_text=article_text,
                generator=self.generator,
                **cache_kwargs,
            )
            final_text = "\n\n---\n#Review\n".join([article_text, review_text])
        else:
            final_text = article_text
        
        html_content = markdown_to_html(final_text, download_result.video_title)
        result_path = download_result.video_dir / f"{download_result.video_title}.html"
        result_path.write_text(html_content, encoding="utf-8")
        if self.open_browser:
            webbrowser.open(result_path.resolve().as_uri())


def cached_step(fn: Callable[..., str]) -> Callable[..., str]:
    @wraps(fn)
    def wrapper(*args, video_dir: Path, overwrite: bool = False, **kwargs) -> str:
        cache_path = video_dir / f"{fn.__name__}.md"

        if cache_path.exists() and not overwrite:
            logger.info(f"Reading {fn.__name__} from cache")
            return cache_path.read_text()

        logger.info(f"Making {fn.__name__}")
        result = fn(*args, **kwargs)
        cache_path.write_text(result)
        return result

    return wrapper


# SRT format: sequence number, timestamp line, text lines, blank line
# Example:
#   1
#   00:00:00,160 --> 00:00:05,440
#   Hello world
#
SRT_TIMESTAMP_PATTERN = re.compile(
    r"\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,.]\d{3}"
)

# Auto-generated subtitles often include these artifacts
SUBTITLE_NOISE_PATTERNS = ["[music]", "[applause]", "[laughter]", "[cheering]"]
SUBTITLE_NOISE_REGEX = re.compile(
    "|".join(re.escape(p) for p in SUBTITLE_NOISE_PATTERNS), re.IGNORECASE
)


@cached_step
def uninterrupted_text(*, raw_srt: str) -> str:
    """Parse SRT subtitle file into continuous text."""
    lines = raw_srt.splitlines()

    text_parts = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines and sequence numbers
        if not line or line.isdigit():
            i += 1
            continue

        # Found timestamp line - collect the text block that follows
        if SRT_TIMESTAMP_PATTERN.match(line):
            i += 1
            block_text = []

            # Collect text until next empty line, sequence number, or timestamp
            while i < len(lines):
                text_line = lines[i].strip()
                if not text_line or text_line.isdigit() or SRT_TIMESTAMP_PATTERN.match(text_line):
                    break

                # ">> " prefix indicates speaker change in some subtitle formats
                if text_line.startswith(">> "):
                    text_line = text_line[3:]

                text_line = SUBTITLE_NOISE_REGEX.sub("", text_line)
                block_text.append(text_line)
                i += 1

            if block_text:
                text_parts.append(" ".join(block_text))
            continue

        i += 1

    result = " ".join(text_parts)

    # Normalize whitespace
    result = re.sub(r"\s+", " ", result)

    # Fix missing space after sentence-ending punctuation (common in auto-subs)
    result = re.sub(r"([.!?])([A-Z])", r"\1 \2", result)

    if result:
        result = result[0].upper() + result[1:]

    return result.strip()


@cached_step
def article(*, transcript: str, description: str | None, title: str, generator: Generator) -> str:
    system_prompt = importlib.resources.read_text(
        "video_to_article", "prompt/make_article.txt", encoding="utf-8"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Title: {title}\n\nTranscript: {transcript}\n\nDescription: {description}"},
    ]
    return generator.generate(messages)


@cached_step
def review(*, article_text: str, generator: Generator) -> str:
    system_prompt = importlib.resources.read_text(
        "video_to_article", "prompt/review.txt", encoding="utf-8"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": article_text},
    ]
    return generator.generate(messages)


def markdown_to_html(md_content: str, title: str) -> str:
    template = importlib.resources.read_text(
        "video_to_article", "template.html", encoding="utf-8"
    )
    html_body = markdown.markdown(md_content, extensions=["fenced_code", "tables"])
    return template.replace("{{title}}", title).replace("{{content}}", html_body)
