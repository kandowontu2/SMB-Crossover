"""Compose the source-backed Mini empty-scene renderer and graphics shortcut."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import hashlib
import re

from apply_mini_tile_fast_1103_v2 import transform

from prepare_selected_native_packet_v1 import R, sha

PARENT = R/'build/mini-idle-constants-1103/mini-idle-fast.nes'
PIN = '4ff069b3474077a1f3f8924b530780dee7a81c2a32d759f8fbe2defcf91e3f4c'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert sha(PARENT) == PIN
    out = args.output.resolve()
    out.mkdir(exist_ok=True)
    spans = [('DRAW_GATE', 20, 0xbd28, 76, 0xea), ('DRAW_FAST', 20, 0xbd86, 110, 0xea),
             ('GFX_GATE', 66, 0xb55e, 40, 0xff), ('GFX_BODY', 66, 0xbecf, 49, 0xff),
             ('BG_WRAPPER', 20, 0xbdf4, 46, 0xea),
             ('BG_GUARD', 20, 0xbbce, 50, 0xff), ('BG_PROBES', 20, 0xbe34, 36, 0xea),
             ('BG_SIDES', 20, 0xbecc, 52, 0xff),
             ('MINI_CONSTANT_GATE', 79, 0xaada, 38, 0xff),
             ('MINI_CONSTANT_FOREIGN', 79, 0xb53a, 18, 0xea),
             ('GFX_FIREBALL', 66, 0xb48a, 26, 0xff),
             ('MINI_FB_ATTACK', 89, 0xbcc0, 160, 0xea),
             ('MINI_FB_HELPERS', 89, 0xbd72, 178, 0xea),
             ('MINI_FB_META', -1, 0xd239, 37, 0xff),
             ('MINI_FB_LIFE', -1, 0xd2d0, 16, 0xff),
             ('MINI_FB_ART', -1, 0xd2e0, 32, 0xff)]
    cfg = out/'render.cfg'
    cfg.write_text('MEMORY {\n'+''.join(
        f'{name}: start=${pc:04x}, size={size}, file="{(out/(name+".bin")).as_posix()}";\n'
        for name, _, pc, size, _ in spans)+'}\nSEGMENTS {\n'+''.join(
        f'{name}: load={name}, type=ro;\n' for name, *_ in spans)+'}\n')
    cc = R/'tools/Windows/cc65/bin'
    obj = out/'render.o'
    subprocess.run([cc/'ca65.exe', R/'tools/reference/mini_mario_empty_draw.s', '-o', obj], check=True)
    fireobj=out/'fireball.o'
    subprocess.run([cc/'ca65.exe', R/'tools/reference/mini_mario_fireball_1103.s', '-o', fireobj], check=True)
    subprocess.run([cc/'ld65.exe', '-C', cfg, '-D', 'MiniLinkedInit=$a3bc', obj, fireobj,
                    '-o', out/'unused.bin', '-Ln', out/'render.lbl'], check=True)
    raw = bytearray(PARENT.read_bytes())
    patches = []

    def patch(bank, pc, old, new):
        at = (1048592+967*1024+(pc&1023)) if bank == -1 else 16+bank*8192+(pc&8191)
        assert len(old) == len(new) and raw[at:at+len(old)] == old, (bank, hex(pc))
        raw[at:at+len(old)] = new
        patches.append(dict(bank=bank, pc=pc, before=old.hex(), after=new.hex()))

    # CdQueueHud's two source-guaranteed taken JMPs are shortened to branches.
    # The exact entry and external call sites stay fixed; its final two bytes
    # become adjacent source padding for the state25/26 constant predicate.
    hud_packet=R/'build/mini-constant-funding-1103-v1'
    hud_old=(hud_packet/'chip-hud-reference.bin').read_bytes()
    hud_new=(hud_packet/'chip-hud-fast.bin').read_bytes()
    assert len(hud_old)==338 and len(hud_new)==336
    assert hashlib.sha256(hud_new).hexdigest()=='2be548e74657bb6c5c00cf0f829b99573f141bc3224ee1b663bb339afa7608b5'
    patch(79,0xa98a,hud_old,hud_new+b'\xff\xff')
    for name, bank, pc, size, fill in spans:
        data = (out/(name+'.bin')).read_bytes()
        assert len(data) <= size
        patch(bank, pc, bytes([fill])*len(data), data)
    patch(4, 0xa2b1, bytes.fromhex('8d6a01a9c58d6c01a9b38d6d01a9be4c5a01'),
          bytes.fromhex('8d6a01a9288d6c01a9bd8d6d01a9944c5a01'))
    patch(66, 0xb3c2, bytes.fromhex('08488a'), bytes.fromhex('4c5eb5'))
    patch(86, 0xa5f9, bytes.fromhex('4c86a7'), bytes.fromhex('4cf4a7'))
    patch(86, 0xa7f4, b'\xff'*10, bytes.fromhex('e029d0034ce8a54c86a7'))
    # GmExtraNrPortrait's source-owned unlabeled .word$FFFF is immediately
    # before GmOnlyCommon B840. Both bytes are unreachable data after JMP.
    patch(79, 0xb83b, bytes.fromhex('4c7ebfffff'), bytes.fromhex('c9294cdaaa'))
    # The current compiled platform/body wrapper owns the BG tail in bank93.
    # Preserve its real bounding-box call, then route the no-argument native
    # BG operation through the Mini preflight.
    patch(93, 0xaff0, bytes.fromhex('205aad'), bytes.fromhex('4cf8bf'))
    patch(93, 0xbff8, b'\xff'*8, bytes.fromhex('205aada9bd4cf3af'))
    patch(93, 0xaff3, bytes.fromhex('4c5b9b')+b'\xff'*10,
          bytes.fromhex('8d6d01a9f48d6c01a9944c5a01'))
    kernel_parent = R/'build/mini-idle-constants-1103/mini-idle'
    source = kernel_parent.with_suffix('.s').read_text()
    needle = ' lda MiniHeadPending\n beq @headspeed'
    assert source.count(needle) == 1
    # GuestLandingLimit is caller-local scratch in GuestLandingWindow.
    # Mini publishes its pending-head bit before entering the native BG
    # routine, which may then reuse that scratch for its landing threshold.
    source = source.replace(needle, ' lda MiniHeadPending\n sta $6006\n beq @headspeed')
    before = ' lda #1\n sta SsChrActive\n lda #0\n sta ObjectMetasprite'
    assert source.count(before) == 1
    source = source.replace(before, ' lda #0\n sta ObjectMetasprite')
    before = ' lda #1\n sta X5WideChrActive\n sta ReloadCHRBank'
    assert source.count(before) == 1
    source = source.replace(before, ' lda #1\n sta SsChrActive\n sta X5WideChrActive\n sta ReloadCHRBank')
    original_attrs=bytes(raw[1048592+967*1024+768:1048592+968*1024])
    source,encoded_attrs=transform(source,original_attrs)
    # The caller already maps the authenticated Mini C2/A3 overlay. Metadata
    # D239 is a complete public draw return; D24F is the weapon farcall leaf.
    before=' jmp MiniHostYes          ;34 weapon tail handled (no source projectile)'
    assert source.count(before)==1
    source=source.replace(before,' jmp $d24f               ;34 native Mini fireball actor')
    assert source.count('MiniHostFresh:\n jsr MiniInit')==1
    source=source.replace('MiniHostFresh:\n jsr MiniInit','MiniHostFresh:\n jsr $d2d0')
    before=' pla\n plp\n sec\n rts\nMiniPoseTile:'
    assert source.count(before)==1
    source=source.replace(before,' pla\n plp\n jmp $d239\nMiniPoseTile:')
    before=' sta SsChrPhysical\n lda #$83\n sta X5ChrMode+4'
    assert source.count(before)==1
    source=source.replace(before,' sta SsChrPhysical\n lda #$c7\n sta CurrentCHRBank+5\n lda #$83\n sta X5ChrMode+4\n sta X5ChrMode+5')
    kernel_asm = out/'mini-zero.s'
    kernel_asm.write_text(source)
    kernel_obj = out/'mini-zero.o'
    subprocess.run([cc/'ca65.exe', kernel_asm, '-o', kernel_obj], check=True)
    kernel_cfg = R/'build/mini-mario-power-contract-1103-v51/mini-host-v56.cfg'
    kernel_bin = out/'mini-zero.bin'
    subprocess.run([cc/'ld65.exe', '-C', kernel_cfg, kernel_obj, '-o', kernel_bin,
                    '-Ln', out/'mini-zero.lbl'], check=True)
    code = kernel_bin.read_bytes()
    assert len(code) <= 5120
    kernel_labels={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(out/'mini-zero.lbl').read_text(),re.M)}
    assert kernel_labels['MiniInit']==0xa3bc
    start, end = 1048592+962*1024, 1048592+967*1024
    assert raw[start:end] == kernel_parent.with_suffix('.bin').read_bytes().ljust(5120,b'\xff')
    raw[start:end] = code.ljust(5120,b'\xff')
    attrs_at=1048592+967*1024+768
    assert raw[attrs_at:attrs_at+256]==original_attrs
    raw[attrs_at:attrs_at+256]=encoded_attrs
    cookie = 16+65*8192+0x1003
    raw[cookie+3:cookie+16] = hashlib.sha256(raw[start:end+2048]).digest()[:13]
    # Retain the already-tested root direct-dispatch/performance composition.
    # Its eight independently source-funded spans are disjoint from this
    # two-shot change, and every literal preimage is still required here.
    direct_path=R/'build/mini-final-candidate-1103/candidate.json'
    direct=json.loads(direct_path.read_text())
    assert direct['ROM_SHA256']=='f552fd7ba20d4bdee4455c1f577ef966197dd792a2b885e8ecaf2a32dd40a481'
    assert len(direct['patches'])==8
    for q in direct['patches']:
        patch(q['bank'],q['pc'],bytes.fromhex(q['old_hex']),bytes.fromhex(q['new_hex']))
    rom = out/'mini-empty-draw.nes'
    rom.write_bytes(raw)
    for ext in ['.lbl', '.dbg']:
        shutil.copyfile(PARENT.with_suffix(ext), rom.with_suffix(ext))
    (out/'candidate.json').write_text(json.dumps(dict(candidate_SHA256=sha(rom),
        parent_SHA256=PIN, patches=patches,kernel_bytes=len(code),kernel_labels=kernel_labels,
        native_fireball_actor_unchanged=True,
        fireball=dict(pool=2,admission='first empty, fresh B only; both busy blocks new shot',control=8,opaque_extent=[4,4],visible_origin=[6,4],
                      spawn_offsets=[2,-6],metadata_graphic_offset=0x2e0,tile=0x6f,
                      bounds_convention='Existing native control8 uses edge offsets6,4,10,8; native collision comparisons include equal edges.'),
        encoded_attributes_SHA256=hashlib.sha256(encoded_attrs).hexdigest(),
        cookie=raw[cookie:cookie+16].hex(),
        root_direct_manifest_SHA256=sha(direct_path),
        reachable_Roll_pad_protected='B53A JMP B54C; foreign helper beginsB53D',
        chip_hud_factor='A98A338B ->336B; MiniConstants beginsAADA'), indent=2)+'\n')
    print(sha(rom))


if __name__ == '__main__':
    main()
