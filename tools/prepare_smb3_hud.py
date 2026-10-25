"""Repack the original SMB3 power meter into a private copy of the SMB HUD font."""
from pathlib import Path
import argparse, hashlib, json

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', type=Path,
                        default=Path('C:/NES/Super Mario Bros. 3 (USA) (Rev 1).nes'))
    args = parser.parse_args()
    original = args.original.read_bytes()
    assert hashlib.sha256(original).hexdigest() == '1ddc4b429490e298c05fa70389034107c0cb50f671c7c1baaa3f228224afc2e9'
    original_chr = original[16+262144:]
    font = bytearray((ROOT/'chr/characters/packed-mmc5-expanded.chr').read_bytes()[:1024])
    source_tiles = (0xee, 0xef, 0x2c, 0x2d, 0x3c, 0x3d)
    # Original status font starts at physical1K page92. Keep original masks;
    # adapt its black/white pixel indices to the host's status palette.
    colors = (0, 3, 2, 1)
    for destination, tile in zip(range(0x30, 0x36), source_tiles):
        source = original_chr[92*1024+tile*16:92*1024+(tile+1)*16]
        target = bytearray(16)
        for y in range(8):
            for x in range(8):
                bit = 7-x
                color = colors[((source[y] >> bit) & 1) | (((source[y+8] >> bit) & 1) << 1)]
                target[y] |= (color & 1) << bit
                target[y+8] |= (color >> 1) << bit
        font[destination*16:(destination+1)*16] = target
    path = ROOT/'chr/characters/smb3-mario.chr'
    previous = path.read_bytes()
    assert len(previous) in (21504, 22528)
    path.write_bytes(previous[:21504] + font)
    print(json.dumps(dict(bytes=path.stat().st_size, hud_physical_page=545,
                          original_tiles=list(source_tiles),
                          sha256=hashlib.sha256(path.read_bytes()).hexdigest())))


if __name__ == '__main__':
    main()
