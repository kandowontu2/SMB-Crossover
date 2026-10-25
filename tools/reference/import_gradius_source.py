"""Pin a small annotated Gradius reference; original ROM remains the authority."""
from pathlib import Path
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
REV = "314625258387309119e69e37aaf3365197235119"
FILES = ("src/player.js", "src/powerup.js", "src/weapons.js", "src/state.js",
         "src/oam.js", "src/collision.js", "src/hud.js", "src/hudpackets.js",
         "src/enemies.js", "src/terrain.js", "tools/export_metasprites.py", "tools/export_assets.py")


def main():
    dest = ROOT / "reference/gradius-nes"
    dest.mkdir(parents=True, exist_ok=True)
    records = []
    for relative in FILES:
        url = f"https://raw.githubusercontent.com/Fabulu/Mixup/{REV}/games/gradius/{relative}"
        target = dest / Path(relative).name
        if not target.exists():
            request = urllib.request.Request(url, headers={"User-Agent": "SMB-Crossover-research"})
            target.write_bytes(urllib.request.urlopen(request, timeout=30).read())
        records.append(dict(file=target.relative_to(ROOT).as_posix(), url=url,
                            sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    rom = Path("C:/NES/Gradius (USA).nes")
    raw = rom.read_bytes()
    manifest = dict(revision=REV, files=records, original_rom=str(rom),
        original_rom_sha256=hashlib.sha256(raw).hexdigest(),
        original_rom_sha1=hashlib.sha1(raw).hexdigest(),
        authority="Numbers and pixels must be checked against the original USA ROM, not accepted from this translation alone.")
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
