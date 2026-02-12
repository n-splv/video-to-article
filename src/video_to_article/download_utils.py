import re
from pathlib import Path
from typing import NamedTuple

import yt_dlp


TRACKER_FILENAME = ".v2afiletracker"


class DownloadResult(NamedTuple):
    raw_srt: str
    raw_description: str | None
    video_title: str
    video_dir: Path


def download_subtitles_and_description(video_url: str, output_dir: Path) -> DownloadResult:
    """
    Download subtitles and organize into output_dir/channel/video_title/.

    :raises ValueError: if tracker file is empty
    :raises FileNotFoundError: if subtitle file not found
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    tracker_path = output_dir / TRACKER_FILENAME

    template = "%(channel)s -- %(requested_subtitles.:.filepath)l"
    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "writedescription": True,
        "subtitleslangs": ["en"],
        "subtitlesformat": "srt",
        "paths": {"home": str(output_dir)},
        "print_to_file": {"after_video": [(template, TRACKER_FILENAME)]},
        "quiet": True,
        # "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    return _organize_subtitle_and_description_files(output_dir, tracker_path)


def _organize_subtitle_and_description_files(output_dir: Path, tracker_path: Path) -> DownloadResult:
    content = tracker_path.read_text().strip()
    tracker_path.unlink()

    if not content:
        raise ValueError(f"Tracker file {tracker_path} is empty")

    channel_name, subtitle_file_path = content.split(" -- ", 1)

    # yt_dlp writes absolute path via %(filepath)l when paths.home is set
    subtitle_file = Path(subtitle_file_path)
    if not subtitle_file.exists():
        raise FileNotFoundError(f"Subtitle file not found: {subtitle_file}")

    raw_srt = subtitle_file.read_text(encoding="utf-8")

    video_title = _clean_video_title(subtitle_file)
    directory_name = _video_title_to_directory_name(video_title)

    video_dir = output_dir / channel_name / directory_name
    video_dir.mkdir(parents=True, exist_ok=True)

    # yt-dlp writes description next to the subtitle with same base name + .description
    description_file = subtitle_file.parent / f"{subtitle_file.stem}.description"
    raw_description = None
    if description_file.exists():
        target_description_path = video_dir / "description.txt"
        description_file.rename(target_description_path)
        raw_description = target_description_path.read_text(encoding="utf-8")

    target_path = video_dir / "raw.srt"
    subtitle_file.rename(target_path)

    return DownloadResult(
        raw_srt=raw_srt,
        raw_description=raw_description,
        video_title=video_title,
        video_dir=video_dir,
    )


# Characters that look like or behave like trailing space but str.strip() does not remove.
_INVISIBLE_TRAILING = "\u200b\u200c\u200d\ufeff"  # ZWSP, ZWNJ, ZWJ, BOM

# Fullwidth punctuation (e.g. from YouTube titles) → ASCII equivalents.
_FULLWIDTH_PUNCT_TO_ASCII = str.maketrans(
    "！＂＇（），－．：；？［］",
    "!\"'(),-.:;?[]",
)


def _strip_video_id_brackets(text: str) -> str:
    """Remove video ID in brackets, e.g. ' [pMqyg1cDk9I]' from 'Title [pMqyg1cDk9I].en'."""
    return re.sub(r"\s*\[.*?]\s*", "", text)


def _strip_language_code(text: str) -> str:
    """Remove language code extension, e.g. .en or .en.srt from the end of a stem."""
    return re.sub(r"\.[a-zA-Z]{2}(\.srt)?$", "", text, flags=re.IGNORECASE)


def _clean_video_title(subtitle_file: Path) -> str:
    """Remove [video_id] and language code for display and for directory naming."""
    raw_stem = subtitle_file.stem
    result = (
        _strip_language_code(_strip_video_id_brackets(raw_stem))
        .strip()
        .strip(_INVISIBLE_TRAILING)
        .translate(_FULLWIDTH_PUNCT_TO_ASCII)
    )
    return result


def _video_title_to_directory_name(video_title: str) -> str:
    """
    Slugify a cleaned video title for use as a directory name.
    Example: "Kittens are 99% cute" -> "kittens_are_99_cute"
    """
    video_title = video_title.lower().strip()
    video_title = re.sub(r"[^a-z0-9]+", "_", video_title)
    video_title = re.sub(r"_+", "_", video_title).strip("_")
    return video_title
