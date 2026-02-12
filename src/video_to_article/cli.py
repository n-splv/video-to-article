from pathlib import Path
from typing import Annotated

import typer

from video_to_article.pipeline import Pipeline


app = typer.Typer(add_completion=False)


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True}
)
def main(
    ctx: typer.Context,
    video_urls: Annotated[
        list[str], typer.Argument(help="YouTube video URLs to process")
    ],
    model: Annotated[
        str, typer.Option("--model", "-m", help="Model name or path")
    ] = "gpt-5.2",
    output_dir: Annotated[
        Path, typer.Option("--output-dir", "-o", help="Output directory for results")
    ] = Path("articles"),
    overwrite: Annotated[
        bool, typer.Option("--overwrite", "-f", help="Overwrite cached step results")
    ] = False,
    skip_review: Annotated[
        bool, typer.Option("--skip-review", help="Skip the critical review step")
    ] = False,
    open_browser: Annotated[
        bool,
        typer.Option(
            "--open-browser/--no-open-browser",
            help="Open the result HTML in the browser [default: open-browser]",
        ),
    ] = True,
):
    """
    Convert YouTube videos to articles using AI.

    Extra options (e.g. --temperature 0.7) are passed to the model.
    """
    generator_kwargs = _parse_extra_args(ctx.args)

    pipeline = Pipeline(
        model=model,
        output_dir=output_dir,
        overwrite=overwrite,
        skip_review=skip_review,
        open_browser=open_browser,
        generator_kwargs=generator_kwargs,
    )

    for video_url in video_urls:
        pipeline.run(video_url)


def _parse_extra_args(args: list[str]) -> dict:
    """
    Parse extra CLI arguments into a dict.
    Handles both --key value and --key=value formats.
    """
    result = {}
    i = 0
    while i < len(args):
        arg = args[i]

        if not arg.startswith("--"):
            i += 1
            continue

        # Handle --key=value format
        if "=" in arg:
            key, value = arg[2:].split("=", 1)
            result[key.replace("-", "_")] = _infer_type(value)
            i += 1
        # Handle --key value format
        elif i + 1 < len(args) and not args[i + 1].startswith("--"):
            key = arg[2:].replace("-", "_")
            result[key] = _infer_type(args[i + 1])
            i += 2
        # Handle --flag (boolean)
        else:
            key = arg[2:].replace("-", "_")
            result[key] = True
            i += 1

    return result


def _infer_type(value: str):
    """Convert string value to appropriate Python type."""
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value
