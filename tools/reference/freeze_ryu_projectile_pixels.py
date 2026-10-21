"""Freeze independent 2.02 sheet silhouettes; never read NES CHR/pose tables."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
source = next((ROOT / "reference/crossover2/images").glob("*_Ryu000.png"))
sheet = Image.open(source).convert("RGBA")
frames = []
for n in range(8):
    top, column = (222, n) if n < 4 else (243, n - 4)
    image = sheet.crop((130 + column * 21, top, 150 + column * 21,
                        top + (20 if n < 4 else 21)))
    image.putdata([(0, 0, 0, 0) if p[:3] == (111, 49, 152) else p
                   for p in image.get_flattened_data()])
    image = image.crop(image.getbbox())
    frames.append(["".join("1" if image.getpixel((x, y))[3] else "0"
                           for x in range(image.width))
                   for y in range(image.height)])
out = ROOT / "tests/fixtures/ryu-projectile-pixels"
out.with_suffix(".json").write_text(json.dumps({
    "source": source.relative_to(ROOT).as_posix(),
    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "frames": frames,
}, indent=2) + "\n")
out.with_suffix(".lua").write_text(
    "-- Frozen pinned 2.02 sheet silhouettes, independent of NES CHR/tables.\nreturn {\n"
    + "".join(" {" + ",".join(json.dumps(row) for row in pic) + "},\n"
              for pic in frames) + "}\n")

# Independently unpack the remaining flame frames from the pinned SWF masks
# and transforms. The source never mirrors any Ryu projectile by velocity.
from prepare_crossover import frames as swf_frames
from build_remaining_art import extract
items = list(ET.parse(ROOT / "reference/crossover2/main.xml").getroot().iter("item"))
symbols = {}
for item in items:
    if item.get("type") in ("SymbolClassTag", "ExportAssetsTag") and item.find("tags") is not None:
        symbols.update({name.text: value.text for value, name
                        in zip(item.find("tags"), item.find("names"))})
sprite = next(item for item in items if item.get("type") == "DefineSpriteTag"
              and item.get("spriteId") == symbols["RyuProjectile"])
fire = []
for image in extract(swf_frames(sprite), 36, sheet)[8:16]:
    image = image.crop(image.getbbox())
    fire.append(["".join("1" if image.getpixel((x, y))[3] else "0"
                         for x in range(image.width))
                 for y in range(image.height)])
fire_out = ROOT / "tests/fixtures/ryu-fire-projectile-pixels"
fire_out.with_suffix(".json").write_text(json.dumps({
    "source": source.relative_to(ROOT).as_posix(),
    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "xml_sha256": hashlib.sha256((ROOT / "reference/crossover2/main.xml").read_bytes()).hexdigest(),
    "swf_frames": list(range(9, 17)), "frames": fire,
}, indent=2) + "\n")
fire_out.with_suffix(".lua").write_text(
    "-- Frozen SWF matrix/mask silhouettes, independent of NES CHR/tables.\nreturn {\n"
    + "".join(" {" + ",".join(json.dumps(row) for row in pic) + "},\n"
              for pic in fire) + "}\n")
