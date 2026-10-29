"""Assemble pinned original DK source and compare all local ROM payload bytes."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "build/source-acquisition/dk-bowser-2026-10-29/dk/source"
OUT = ROOT / "build/dk-original-source-match-v1"
ROM = Path("C:/NES/Donkey Kong (World) (Rev 1).nes")
ASM6 = Path("C:/Users/kando/Documents/ChatGPT/SNES Ports/upstream-nes/asm6.exe")


def bound(path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return dict(path=str(path), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def main():
    assert not (OUT / "proof.json").exists(), "Frozen source-match result"
    acquisition = ROOT / "build/source-acquisition/dk-bowser-2026-10-29/acquisition.json"
    manifest = json.loads(acquisition.read_text())
    sources = {Path(row["path"]).resolve(): row for row in manifest["files"]}
    raw = ROM.read_bytes()
    assert bound(ROM)["sha256"] == "226c6f698f60b0a07157bd031004820789469884615fef7bdd862c3157e89d27"
    assert raw[:6] == bytes.fromhex("4e45531a0101") and len(raw) == 24592
    OUT.mkdir(exist_ok=True)
    inputs = []
    for name in ["Defines.asm", "DonkeyKongDisassembly.asm", "JPRemap.asm", "iNES_Header.asm"]:
        path = SOURCE / name
        assert bound(path) == {k: sources[path.resolve()][k] for k in ["path", "bytes", "sha256"]}
        data = path.read_bytes()
        copy = OUT / name
        if copy.exists():
            assert copy.read_bytes() == data
        else:
            copy.write_bytes(data)
        inputs.append(bound(path))
    # Exact user's local CHR, not a downloaded image or newly drawn substitute.
    gfx = OUT / "DKGFX.bin"
    if gfx.exists():
        assert gfx.read_bytes() == raw[16 + 16384:]
    else:
        gfx.write_bytes(raw[16 + 16384:])
    command = [str(ASM6), "-l", "DonkeyKongDisassembly.asm", "rebuilt.nes", "rebuilt.lst"]
    result = subprocess.run(command, cwd=OUT, capture_output=True, text=True)
    (OUT / "assemble.log").write_text(result.stdout + result.stderr)
    proof = dict(status="Original source build; no host implementation/native claim", command=command,
                 exit=result.returncode, original=bound(ROM), compiler=bound(ASM6),
                 acquisition=bound(acquisition), original_inputs=inputs, CHR=bound(gfx), native=False)
    if result.returncode == 0:
        rebuilt = (OUT / "rebuilt.nes").read_bytes()
        differences = [i for i, (a, b) in enumerate(zip(raw, rebuilt)) if a != b]
        proof.update(rebuilt=bound(OUT / "rebuilt.nes"), listing=bound(OUT / "rebuilt.lst"),
                     exact_size=len(raw) == len(rebuilt), differences=differences,
                     full_PRG_CHR_payload_exact=len(raw) == len(rebuilt) and raw[16:] == rebuilt[16:],
                     header_only=all(i < 16 for i in differences),
                     payload_SHA256=hashlib.sha256(rebuilt[16:]).hexdigest())
    proof["passed"] = result.returncode == 0 and proof["full_PRG_CHR_payload_exact"]
    (OUT / "proof.json").write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps(proof, indent=2))
    assert proof["passed"], "Inspect retained source-build result"


if __name__ == "__main__":
    main()
