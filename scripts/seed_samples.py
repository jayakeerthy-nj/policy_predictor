from pathlib import Path
import shutil


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    target = root / "data" / "samples"
    target.mkdir(parents=True, exist_ok=True)

    source_dirs = [root / "inflation", root / "market"]
    copied = 0
    for source_dir in source_dirs:
        if not source_dir.exists():
            continue
        for file in source_dir.iterdir():
            if file.is_file() and not file.name.startswith("."):
                shutil.copy2(file, target / file.name)
                copied += 1
    print(f"Copied {copied} sample files to {target}")


if __name__ == "__main__":
    main()

