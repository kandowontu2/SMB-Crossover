"""Build a private Mini profile candidate from the exact delivered image."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

from prepare_selected_native_packet_v1 import R, sha
from profile_mini_mario_1103 import BASE, ROM

PARENT = '9d291cb7562aad3a21e575386d0d6461dc39eab5cbd34c85856ae8a1f1d2b622'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve()
    assert sha(ROM) == PARENT
    raw = bytearray(ROM.read_bytes())
    out.mkdir()
    source = R / 'tools/reference/mini_mario_frame_auth_1103.s'
    addresses = [0xafda, 0xaba4, 0xafea, 0xa7c5, 0xb003, 0xaa78]

    def offset(bank, pc):
        return 16 + bank * 8192 + (pc & 8191)

    def bytes_line(values):
        return '.byte ' + ','.join(f'${n:02x}' for n in values)

    symbols = ['.export CookieLows, CookieTableLo, CookieTableHi']
    for group, segment in [(range(4), 'COOKIES_A'), (range(4, 6), 'COOKIES_B')]:
        symbols.append(f'.segment "{segment}"')
        for i in group:
            start = offset(65, addresses[i])
            symbols += [f'Cookie{i}:', bytes_line(raw[start:start+16])]
    symbols += ['.segment "COOKIES_A"', 'CookieLows:', bytes_line(a & 255 for a in addresses),
                'CookieTableLo: .byte ' + ','.join(f'<Cookie{i}' for i in range(6)),
                '.segment "AUTH"', 'CookieTableHi: .byte ' + ','.join(f'>Cookie{i}' for i in range(6))]
    table = out / 'headers.s'
    table.write_text('\n'.join(symbols) + '\n')
    spans = [('COOKIES_A', 20, 0xbd28, 76), ('AUTH', 20, 0xbd86, 156),
             ('COOKIES_B', 20, 0xbe34, 36), ('BRIDGE', 65, 0xaf27, 40)]
    cfg = out / 'auth.cfg'
    cfg.write_text('MEMORY {\n' + ''.join(
        f'{name}: start=${pc:04x}, size={size}, file="{(out/(name+".bin")).as_posix()}";\n'
        for name, _, pc, size in spans) + '}\nSEGMENTS {\n' + ''.join(
        f'{name}: load={name}, type=ro;\n' for name, *_ in spans) + '}\n')
    cc = R / 'tools/Windows/cc65/bin'
    objects = []
    for item in [source, table]:
        obj = out / (item.stem + '.o')
        subprocess.run([cc/'ca65.exe', item, '-o', obj], check=True)
        objects.append(obj)
    subprocess.run([cc/'ld65.exe', '-C', cfg, *objects, '-o', out/'unused.bin'], check=True)
    patches = []
    for name, bank, pc, size in spans:
        data = (out/(name+'.bin')).read_bytes()
        at = offset(bank, pc)
        before = bytes(raw[at:at+size])
        if bank == 20:
            assert before == bytes([0xea])*size
        else:
            assert before.hex() == 'ada17d48a2038ea17d8e1651a00fb9e0dfd108d00a8810f6cae001d0e9b00118688da17d8d165160'
        assert len(data) <= size
        raw[at:at+len(data)] = data
        patches.append(dict(bank=bank, pc=pc, offset=at, before=before[:len(data)].hex(), after=data.hex()))
    rom = out/'mini-frame-auth.nes'
    rom.write_bytes(raw)
    for ext in ('.lbl', '.dbg'):
        shutil.copyfile(ROM.with_suffix(ext), rom.with_suffix(ext))
    (out/'controller.lua').write_text(BASE.read_text().replace(PARENT, sha(rom)))
    (out/'candidate.json').write_text(json.dumps(dict(parent_SHA256=PARENT,
        candidate_SHA256=sha(rom), patches=patches), indent=2)+'\n')
    print(sha(rom))


if __name__ == '__main__':
    main()
