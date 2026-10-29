"""Current workspace budget and read-only lookup of archived build evidence."""
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
# The user raised the workspace cap to70GB on October29.
CAP_BYTES = 70_000_000_000


def locate(path: Path) -> Path:
    """Find a retained file locally or at its recorded external archive path.

    This never restores/copies data into the workspace or follows an arbitrary
    path supplied by a historical recording. Only the cleanup receipt is used.
    """
    path = path.resolve()
    if path.exists():
        return path
    try:
        relative = path.relative_to(ROOT)
    except ValueError:
        raise FileNotFoundError(path) from None
    receipt = ROOT / 'workspace-archive.json'
    if receipt.exists():
        data = json.loads(receipt.read_text())
        archived = any(relative == Path(item['relative'])
                       or relative.is_relative_to(Path(item['relative']))
                       for item in data['directories'])
        if archived:
            archive = Path(data['archive']).resolve()
            candidate = (archive / relative).resolve()
            if candidate.is_relative_to(archive) and candidate.exists():
                return candidate
    raise FileNotFoundError(f'File is absent from both workspace and archive: {path}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--locate', type=Path, help='Print the retained path without copying anything')
    args = parser.parse_args()
    if args.locate:
        print(locate(args.locate))
        return 0
    from playthroughs.roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    print(json.dumps(dict(workspace_bytes=used, cap_bytes=CAP_BYTES,
        headroom_bytes=CAP_BYTES - used, under_cap=used < CAP_BYTES), indent=2))
    return 0 if used < CAP_BYTES else 1


if __name__ == '__main__':
    raise SystemExit(main())
