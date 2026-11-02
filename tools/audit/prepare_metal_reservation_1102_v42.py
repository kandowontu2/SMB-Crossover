"""Repair Metal's native zero reservation header inside its existing renderer."""
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha
from private_build_outputs_v1 import validate

O = R / 'build/metal-reservation-1102-v42'
S = R / 'build/metal-storm-idle-shots-1101-v41'
BASE = R / 'build/excitebike-pose-1101-v3/current4.nes'
PIN = 'cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'


def main():
    O.mkdir(exist_ok=True)
    assert sha(BASE) == PIN
    source = (S / 'component.s').read_text(encoding='utf-8')
    text = source
    for name in ['MsRenderDraw', 'Ms12Movement']:
        old = name + ':\n jsr MsRSave'
        assert text.count(old) == 1
        text = text.replace(old, name + ':\n jsr MsRenderGraphics\n jsr MsRSave')
    # The private C2 header cannot survive transport bank restoration. Use the
    # same stable native zero byte as Ex; ObjectMetasprite is set to zero first.
    assert text.count('lda #<MsEmptyPose') == text.count('lda #>MsEmptyPose') == 1
    text = text.replace('lda #<MsEmptyPose', 'lda #<ObjectMetasprite')
    text = text.replace('lda #>MsEmptyPose', 'lda #>ObjectMetasprite')
    (O / 'component.s').write_text(text, encoding='utf-8', newline='\n')
    for name in ['body-compact.bin']:
        (O / name).write_bytes((S / name).read_bytes())
    (O / 'component.cfg').write_text((S / 'component.cfg').read_text().replace(S.as_posix(), O.as_posix()))
    (O / 'native-cookie.bin').write_bytes(bytes(16))
    cc = R / 'tools/Windows/cc65/bin'

    def compile_source():
        for cmd in [[cc / 'ca65.exe', '-g', '--bin-include-dir', O,
                     '--bin-include-dir', R / 'build/metal-storm-host-1101-v1',
                     '--bin-include-dir', R / 'build/metal-storm-render-host-1101-v7',
                     O / 'component.s', '-o', O / 'component.o'],
                    [cc / 'ld65.exe', '-C', O / 'component.cfg', O / 'component.o',
                     '-o', O / 'unused.bin', '-Ln', O / 'component.lbl']]:
            cmd = list(map(str, cmd))
            validate(cmd, O, cwd=R)
            q = subprocess.run(cmd, capture_output=True, text=True)
            assert q.returncode == 0, q.stderr

    compile_source()
    actor = (O / 'native-actor.bin').read_bytes()
    render = (O / 'native-render.bin').read_bytes()
    extra = (O / 'native-extra.bin').read_bytes()
    assert len(render) <= 3072 and len(extra) <= 352
    cookie = bytes([167, 35, 42]) + hashlib.sha256(actor + render + extra + text.encode()).digest()[:13]
    (O / 'native-cookie.bin').write_bytes(cookie)
    compile_source()
    raw = bytearray(BASE.read_bytes())
    patches = []

    def patch(at, old, new, role):
        assert len(old) == len(new) and raw[at:at + len(old)] == old, role
        raw[at:at + len(new)] = new
        patches.append(dict(role=role, offset=at, bytes=len(new), before_SHA256=hashlib.sha256(old).hexdigest(),
                            after_SHA256=hashlib.sha256(new).hexdigest()))

    for role, bank, off in [('auth', 25, 0x1f9e), ('finish', 99, 0x176e)]:
        patch(16 + bank * 8192 + off, (S / f'native-{role}.bin').read_bytes(),
              (O / f'native-{role}.bin').read_bytes(), role + ' complete-cookie binding')
    for p in O.glob('native-*.bin'):
        if p.name not in ['native-cookie.bin', 'native-actor.bin', 'native-render.bin',
                          'native-extra.bin', 'native-auth.bin', 'native-finish.bin']:
            assert p.read_bytes() == (S / p.name).read_bytes(), p.name
    # The actor and later private leaves contain genuine relocated references
    # to renderer labels. Rebind these in their already allocated carriers.
    for i, page in enumerate([247, 248, 249, 250, 827, 828, 829, 830]):
        before = (S / 'native-actor.bin').read_bytes()[i * 1024:(i + 1) * 1024]
        after = actor[i * 1024:(i + 1) * 1024]
        # Preserve the separately owned final header/padding bytes unchanged.
        patch(16 + 1048576 + page * 1024, before, after, f'Existing Metal actor carrier{page}')
    for i, page in enumerate([831, 500, 494]):
        before = ((S / 'native-render.bin').read_bytes() + bytes(3072))[:3072][i * 1024:(i + 1) * 1024]
        after = (render + bytes(3072 - len(render)))[i * 1024:(i + 1) * 1024]
        patch(16 + 1048576 + page * 1024, before, after, f'Existing Metal renderer carrier{page}')
    before = (S / 'native-extra.bin').read_bytes()
    patch(16 + 1048576 + 499 * 1024 + 0x2a0, before, extra,
          'Existing Metal extra leaves after immutable art prefix')
    candidate = O / 'candidate.nes'
    candidate.write_bytes(raw)
    overrides = {n: int(a, 16) for a, n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',
                                                    (O / 'component.lbl').read_text(), re.M)}
    lines = []
    for line in BASE.with_suffix('.lbl').read_text().splitlines():
        m = re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)', line)
        if not m or m[2] not in overrides:
            lines.append(line)
    lines.extend(f'al {a:06X} .{n}' for n, a in sorted(overrides.items()))
    candidate.with_suffix('.lbl').write_text('\n'.join(lines) + '\n')
    os.link(BASE.with_suffix('.dbg'), candidate.with_suffix('.dbg'))
    q = dict(assembled=True, installed=False, native=False, ROM_SHA256=sha(candidate),
             parent_ROM_SHA256=PIN, renderer_bytes=len(render), renderer_grant_bytes=3072,
             extra_bytes=len(extra), new_resident_ROM_bytes=0, new_RAM_bytes=0,
             patches=patches,
             scope='Stable native zero reservation established before movement/draw. Authentic actor, packets, '
                   'physics, contacts and all other-owner bytes retained. Palette/name and native proof remain open.',
             bindings={str(p.relative_to(R)): sha(p) for p in [Path(__file__), BASE,
                 S / 'component.s', S / 'component.cfg', O / 'component.s', O / 'component.cfg',
                 O / 'native-cookie.bin', O / 'native-render.bin']})
    (O / 'assembly.json').write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in q.items() if k not in ['patches', 'bindings']}))


if __name__ == '__main__':
    main()
