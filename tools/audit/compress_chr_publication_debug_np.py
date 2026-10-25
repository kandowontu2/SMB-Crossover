"""Losslessly compact completed debug evidence without removing other files."""
from pathlib import Path
import gzip, hashlib, json

ROOT = Path(__file__).resolve().parents[2]
QA = ROOT / 'build/verification/chr-publication-np'


def main():
    receipt = QA / 'debug-compression.json'
    results = json.loads(receipt.read_text()) if receipt.exists() else []
    for name in ('candidate-v1', 'standard-mmc3', 'standard-mmc5', 'candidate-v2', 'snapshot-v2/roundtrip'):
        source = (QA / name).with_suffix('.dbg').resolve()
        assert source.is_relative_to(QA.resolve())
        target = source.with_suffix('.dbg.gz')
        if not source.exists():
            assert target.exists()
            continue
        raw = source.read_bytes()
        compressed = gzip.compress(raw, mtime=0)
        target.write_bytes(compressed)
        assert gzip.decompress(target.read_bytes()) == raw
        results.append(dict(file=source.name, sha256=hashlib.sha256(raw).hexdigest(),
                            bytes_before=len(raw), bytes_after=len(compressed)))
        source.unlink()
    receipt.write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(results))


if __name__ == '__main__':
    main()
