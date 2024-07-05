import os
from pathlib import Path


def remove_sourcemap_comment_from_css(directory_path: Path):
    for css_file in directory_path.glob("*.css"):
        with open(css_file, "r", encoding="utf-8") as file:
            lines = file.readlines()

        if lines and lines[-1].strip().startswith("/*# sourceMappingURL="):
            lines.pop()

            with open(css_file, "w", encoding="utf-8") as file:
                file.writelines(lines)

            print(f"Removed sourceMappingURL from {css_file}")


if __name__ == "__main__":
    directory_path = Path(__file__).parent.parent.joinpath(
        "nicegui_tabulator/core/libs"
    )
    remove_sourcemap_comment_from_css(directory_path)
