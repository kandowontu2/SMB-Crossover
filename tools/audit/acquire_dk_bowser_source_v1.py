"""Fetch commit-pinned assembly leaves, without ROMs, CHR or repository clones."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "build/source-acquisition/dk-bowser-2026-10-29"
SOURCES = [
    ("dk", "RussianManSMWC/Donkey-Kong-NES-Disassembly", "343f4c81880a253c0e8ede81fe7c21f205815280",
     ["Defines.asm", "DonkeyKongDisassembly.asm", "JPRemap.asm", "Notes.txt", "README.md", "iNES_Header.asm", "misc/ExtractGFX.py", "misc/README.md"]),
    ("smb3", "captainsouthbird/smb3", "09b1bd81a788de8ceec664a34094e84ddb463117",
     ["README.md", "smb3.asm"] + [f"PRG/prg{i:03}.asm" for i in range(32)]),
]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fetch(url, limit):
    request = urllib.request.Request(url, headers={"User-Agent": "SMBCrossover-source-port"})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read(limit + 1)
    assert len(data) <= limit, url
    return data


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    all_records = []
    repositories = []
    for short, repo, commit, names in SOURCES:
        tree_path = OUT / short / "tree.json"
        tree_path.parent.mkdir(exist_ok=True)
        tree_url = f"https://api.github.com/repos/{repo}/git/trees/{commit}?recursive=1"
        data = tree_path.read_bytes() if tree_path.exists() else fetch(tree_url, 2_000_000)
        tree = json.loads(data)
        assert not tree.get("truncated")
        leaves = {row["path"]: row for row in tree["tree"] if row["type"] == "blob"}
        assert len(names) <= 34
        assert sum(leaves[name]["size"] for name in names) < 3_500_000
        if not tree_path.exists():
            tree_path.write_bytes(data)

        def acquire(name):
            row = leaves[name]
            path = OUT / short / "source" / name
            url = f"https://raw.githubusercontent.com/{repo}/{commit}/{name}"
            content = path.read_bytes() if path.exists() else fetch(url, row["size"])
            assert len(content) == row["size"], name
            assert hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest() == row["sha"], name
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            return dict(path=str(path.resolve()), source_path=name, url=url, bytes=len(content),
                        git_blob_sha1=row["sha"], sha256=digest(content))

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            records = list(executor.map(acquire, names))
        all_records.extend(records)
        repositories.append(dict(repository="https://github.com/" + repo, commit=commit,
                                 tree=dict(path=str(tree_path.resolve()), bytes=len(data), sha256=digest(data)),
                                 files=records))
    result = dict(status="Pinned original assembly sources acquired; not yet matched to local ROMs or ported",
                  repositories=repositories, files=all_records, total_files=len(all_records),
                  total_bytes=sum(row["bytes"] for row in all_records),
                  exclusions="No downloaded ROM, CHR, executable, clone or runtime tree; original graphics must come from user-local ROMs.")
    assert result["total_files"] == 42 and result["total_bytes"] < 4_000_000
    target = OUT / "acquisition.json"
    encoded = (json.dumps(result, indent=2) + "\n").encode()
    if target.exists():
        assert target.read_bytes() == encoded
    else:
        target.write_bytes(encoded)
    print(json.dumps(dict(path=str(target), sha256=digest(encoded), files=len(all_records), bytes=result["total_bytes"])))


if __name__ == "__main__":
    main()
