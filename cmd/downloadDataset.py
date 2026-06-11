import shutil
import kagglehub
from pathlib import Path


def downloadDataset():
    raw_path = kagglehub.dataset_download(
        "asaniczka/tmdb-movies-dataset-2023-930k-movies"
    )

    target_dir = Path("/app/data/tmdb")

    target_dir.mkdir(parents=True, exist_ok=True)

    # copy dataset into persistent volume
    for item in Path(raw_path).rglob("*"):
        if item.is_file():
            dest = target_dir / item.name
            shutil.copy2(item, dest)

    print("[DATASET] stored at:", target_dir)

    return str(target_dir)


if __name__ == "__main__":
    downloadDataset()
