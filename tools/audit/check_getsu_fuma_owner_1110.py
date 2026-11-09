"""Link a sixth cold owner on exact c8 and exercise the live loader in memory."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

import check_getsu_atlas_page_1110 as Page
import check_getsu_fuma_host_motion_1110 as Host
from check_prince_native_link_1102_v43 import ControllerBus
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU


R, PIN, SHA = Page.R, Page.PIN, Page.SHA
N = Page.Front.N
PAGES = (991, 992)
STATE, CODE = 0xc000, 0xa000
CO, COLD, RETIRE, AUTH = 193, 0xae00, 0xae0a, 0xaee2
SMC = (0x162, 0x16a, 0x16c, 0x16d, 0x179)
WORKER = R / 'build/bubble-bobble-source-1101-v1/common-split.s'
INCLUDE = R / 'tools/reference/bubble_bobble_common_cold_1102_v4.inc'
TYPED = R / 'tools/reference/getsu_fuma_typed_cold_1110.s'
ART_PROOF = R / 'build/getsu-atlas-ownership-1110/atlas-page.json'
BODY = (Host.BRIDGE, Host.HOST_SWORD, Host.SOURCE, Host.SWORD)
CURRENT = 0x7da1


def one(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new)


def assemble(output, source, layout):
    with tempfile.TemporaryDirectory(prefix='asm-', dir=output) as folder:
        temp = Path(folder)
        src, cfg, obj, binary, labels = (temp / ('payload.' + ext) for ext in ('s', 'cfg', 'o', 'bin', 'lbl'))
        src.write_text(source)
        cfg.write_text('MEMORY {\n' + ''.join(f'  {name}: start=${pc:04x},size=${size:x},file=%O;\n'
                                             for name, pc, size, _ in layout) +
                       '}\nSEGMENTS {\n' + ''.join(f'  {seg}: load={name},type=ro;\n'
                                                   for name, _, _, segs in layout for seg in segs) + '}\n')
        cc = R / 'tools/Windows/cc65/bin'
        subprocess.run([cc / 'ca65.exe', src, '-o', obj], check=True)
        subprocess.run([cc / 'ld65.exe', '-C', cfg, obj, '-o', binary, '-Ln', labels], check=True)
        return binary.read_bytes(), {row.split()[2][1:]: int(row.split()[1], 16)
                                     for row in labels.read_text().splitlines()}


def worker(output, b):
    src = WORKER.read_text()
    inc = one(INCLUDE.read_text(), ' ldy #0\n sty $5130\n bit $2002', ' ldy #0\n bit $2002')
    mini = '\n.segment "BB_COLD_MAP"\n.byte 1,0,9,$d0\n.word 967\n'
    layout = (('MAIN', 0xaf40, 0xc0, ('BB_COLD_PROPOSAL',)), ('MAP', 0xb9d6, 0x2a, ('BB_COLD_MAP',)))
    expanded = lambda text: one(src, '.include "bubble_bobble_common_cold_1102_v4.inc"', text) + mini
    old, old_labels = assemble(output, expanded(inc), layout)
    raw = b['raw']
    for at, data in ((Page.Front.off(123, 0xaf40), old[:0xbf]), (Page.Front.off(123, 0xb9d6), old[0xbf:])):
        assert raw[at:at + len(data)] == data
    inc = one(inc, ' cmp (R0),y\n jne BbColdNo', ' cmp (R0),y\n bne BbColdNo')
    inc = one(inc, ' sta $2000\n lda #0\n sta R2', ' sta $2000\n sty R2')
    inc = one(inc, ' inc R2\n ldy #0\n lda R2', ' inc R2\n lda R2')
    inc = one(inc, ' bne BbColdCopyRow\n sec\n rts', ' bne BbColdCopyRow\n rts')
    descriptor = '\n.export GfColdDescriptor\nGfColdDescriptor:\n .byte 2,2,1,$d0\n .word 991,992\n'
    inc = one(inc, 'BbColdDescriptors:', descriptor + 'BbColdDescriptors:')
    new, labels = assemble(output, expanded(inc), layout)
    assert len(old) == len(new) and old[0x95:] == new[0x95:]
    assert labels['GfColdDescriptor'] == 0xafcd and old_labels['BbColdExDescriptor'] == labels['BbColdExDescriptor'] == 0xafd5
    assert old_labels['BbColdBBDescriptor'] == labels['BbColdBBDescriptor'] == 0xafe9
    return old[:0x95], new[:0x95]


def kernel(output, b):
    source = '\n'.join(path.read_text(encoding='utf-8') for path in BODY)
    names = {name for line in source.splitlines() if line.startswith('.import ')
             for name in line.removeprefix('.import ').split(', ')}
    defs = {**{'Gf' + name: STATE + i for i, name in enumerate(Host.FIELDS)},
            'GfStateStart': STATE, 'GfStateSize': len(Host.FIELDS)}
    defs.update({name: address(b, name) for name in names - defs.keys() if not name.startswith('Gf')})
    source = '\n'.join(f'{name}=${value:04x}' for name, value in defs.items()) + '\n' + source
    source = '.macpack longbranch\n' + re.sub(r'^\.(?:import .+|macpack longbranch)\n', '', source, flags=re.M)
    source += '\n.segment "VECTORS"\n.res $72,$ff\n'
    segs = ('VECTORS', 'GETSU_HOST_MOTION', 'GETSU_HOST_SWORD', 'GETSU_MOTION', 'GETSU_SWORD')
    data, labels = assemble(output, source, (('BODY', CODE, 0x800, segs),))
    assert 0x72 < len(data) <= 0x800 and labels['GfHostReset'] == CODE + 0x72
    return data, labels, defs['GfInitialized']


def physical(b, atlas):
    p = Page.load_json(ART_PROOF)
    assert p['passed'] and p['current_SHA256'] == PIN
    assert p['replacement_atlas_SHA256'] == SHA(atlas)
    stock = Page.load_json(Page.AUTHORITY)['exact_finite_domains']
    assert not set(PAGES) & set(p['actual_SMB3Plus']['published'] + p['actual_current_menu']['published'])
    assert not set(PAGES) & set(p['legacy_writer_rebind']['reservations'])
    for page in PAGES:
        assert [name for name, pages in stock.items() if page in pages] == ['Historical SMB3Plus retained conservative emission']
    return [dict(page=page, **Page.span(b['raw'], Page.CHR + 1024 * page, 1024)) for page in PAGES]


def image(b, raw_kernel, typed, old_worker, new_worker, atlas):
    raw = b['raw']
    trial, patches = bytearray(raw), []
    body = raw_kernel.ljust(2048, b'\xff')
    cookie = bytes((0xa7, 42, 1)) + hashlib.sha256(body + atlas).digest()[:13]

    def patch(bank, pc, old, new):
        at = Page.Front.off(bank, pc)
        assert trial[at:at + len(old)] == old and len(old) == len(new), (bank, hex(pc))
        trial[at:at + len(new)] = new
        patches.append(dict(physical_PRG=bank, CPU_half_open=[pc, pc + len(old)], file_offset=at,
                            old_hex=old.hex(), new_hex=new.hex()))

    def word(value):
        return value.to_bytes(2, 'little')

    assert 15 < len(typed) <= 81
    pos = location(b, 'M3Form6ChrLo')
    assert pos == Page.Front.off(91, 0xb1ba) and address(b, 'M3Form6ChrLo') == 0xd1ba
    assert 'M3Form6ChrLo:\n .res 81,$ea' in (Page.SOURCE / 'src/smb3_mario_art.inc').read_text()
    # The sole byte-pattern collision is in native music stream data.
    pattern = bytes.fromhex('20bab1')
    assert raw[16:Page.CHR].count(pattern) == 1 and raw.find(pattern, 16, Page.CHR) == 852312
    music = next(seg for seg in b['segs'].values() if seg['name'] == '"X5_FULL_MUSIC_04"')
    assert int(music['ooffs'], 0) <= 852312 < int(music['ooffs'], 0) + int(music['size'], 0)
    assert not any(bytes.fromhex(value) in raw[16:Page.CHR] for value in ('4cbab1', '20bad1', '4cbad1'))
    patch(91, 0xb1ba, b'\xea' * len(typed), typed)
    patch(123, 0xaf40, old_worker, new_worker)

    extra_at = Page.Front.off(65, 0xab72)
    extra = raw[extra_at:extra_at + 98]
    assert SHA(extra) == SHA(bytes.fromhex(
        'a9408d6c01a9af8d6d01a9fb205a019020ad02604926f005490e4ad014a95e8d6c01a9d28d6d01a903205a0190034cbfaf60'
        'a72602657b3e759d1533a69f8180f23ddaa4eac50378afabafa7b0aad593e9e0f9afbfafdfb9008f7a0c0000d9bbd600'))
    descriptors = (0xafd5, 0xbf93, 0xafe9, 0xdfe0, 0xb9f9, 0xafcd)
    cookies = (0xafda, 0xaba4, 0xafea, 0xa7c5, 0xb003, 0xab81, 0xaa78)
    retirees = (0, 0xd98f, 0xbb7a, 0xd60c, 0, 0)

    def planes(rows):
        return bytes(z & 255 for z in rows) + bytes(z >> 8 for z in rows)

    far_tail = bytes.fromhex('a9ba8d6c01a9b18d6d01a9db4c5a01')
    parts = far_tail + cookie + planes(descriptors)
    assert len(parts) == 43
    parts = parts.ljust(50, b'\xea') + extra[50:66] + planes(cookies) + planes(retirees)
    patch(65, 0xab72, extra, parts.ljust(98, b'\xea'))
    for pc, old, new in ((0xaf0f, 0xabc0, 0xab91), (0xaf14, 0xabc5, 0xab97),
                         (0xaf1f, 0xabba, 0xabbb), (0xaf5f, 0xabca, 0xabc2), (0xaf67, 0xabcf, 0xabc8)):
        patch(65, pc, word(old), word(new))
    for pc, old, new in ((0xaee9, 5, 6), (0xaf07, 5, 6), (0xaf50, 4, 5), (0xa80e, 5, 6)):
        patch(65, pc, bytes((old,)), bytes((new,)))
    assert raw[Page.Front.off(65, 0xb01b):Page.Front.off(65, 0xb01f)] == bytes.fromhex('c9059043')
    assert raw[Page.Front.off(65, 0xa750):Page.Front.off(65, 0xa754)] == bytes.fromhex('c9059006')
    for i, page in enumerate(PAGES):
        at = Page.CHR + page * 1024
        trial[at:at + 1024] = body[i * 1024:(i + 1) * 1024]
    return dict(b, raw=bytes(trial)), patches, cookie, body


def blank(b):
    saved = N.Bus
    N.Bus = ControllerBus
    try:
        m = N.fresh(b)
    finally:
        N.Bus = saved
    for k in (2, 3):
        m.ram[k][:] = b'\x9d' * 8192
        m.ram[k][0x1fe0:0x1ff0] = b'\0' * 16
    return m


def scene(m, owner):
    m.raw_page(2, 2)
    N.put(m, CurrentBankC=2, SelectedCharacter=owner, OperMode=1, OperMode_Task=3, GameEngineSubroutine=8,
          GamePauseStatus=0, FrameCounter=0, Player_X_Position=48, Player_PageLoc=0, Player_Y_Position=176,
          Player_Y_HighPos=1, NmiDisable=255, DisableScreenFlag=1, Mirror_PPUMASK=0, Mirror_PPUCTRL=160,
          FamilyMainCommit=1, ReloadCHRBank=0, NumberofLives=2)
    m.ppuctrl = 160
    m[0x2001] = 0


def invoke(m, target, bank=CO):
    m[0x16a], m[0x16c], m[0x16d] = 83, target & 255, target >> 8
    c = NesMPU(memory=m, pc=0x15a)
    c.a, c.x, c.y, c.p, c.sp = bank, 71, 109, 0x21, 224
    c.stPushWord(0x5aff)
    low = 224
    for _ in range(4_000_000):
        if c.pc == 0x5b00:
            break
        low = min(low, c.sp)
        assert m[c.pc] != 0, ('linked BRK', hex(c.pc), m.rawtags, m[0x6002])
        c.step()
    else:
        raise AssertionError(('cold bound', hex(c.pc), m.rawtags))
    assert c.sp == 224
    return dict(A=c.a, X=c.x, Y=c.y, P=c.p & 0xef, CPU=c.processorCycles, minimum_SP=low)


def clear_logs(m):
    m.writes.clear()
    m.ram_writes.clear()
    m.ppu_log.clear()
    m.blocked.clear()


def headers(m):
    return tuple(bytes(m.ram[k][0x1fe0:0x1ff0]) for k in (2, 3))


def cold(m, owner):
    scene(m, owner)
    before = m.ppu_reads
    clear_logs(m)
    result = invoke(m, COLD)
    assert (result['A'], result['X'], result['Y'], result['P']) == (83, 71, 109, 0x21), (owner, result)
    result['PPU_reads'] = m.ppu_reads - before
    assert m.rawtags[2] == m[CURRENT] == 2 and m.ppuctrl == 160
    return result


def qualification(base, trial, cookie, body, labels, initialized):
    seeds, foreign = {}, {}
    for owner in range(37, 42):
        print('Comparing complete current cold owner', owner, flush=True)
        old, new = blank(base), blank(trial)
        x, y = cold(old, owner), cold(new, owner)
        assert old.ram == new.ram and x['PPU_reads'] == y['PPU_reads']
        assert tuple(old.chr_latches) == tuple(new.chr_latches) and old.ppu_log == new.ppu_log
        assert tuple(old.rawtags) == tuple(new.rawtags) and [old[i] for i in SMC] == [new[i] for i in SMC]
        foreign[owner] = dict(before=x, after=y)
        clear_logs(new)
        seeds[owner] = new
    own = blank(trial)
    result = cold(own, 42)
    assert headers(own) == (cookie, cookie) and bytes(own.ram[2][:256]) == b'\0' * 256
    assert bytes(own.ram[3][:2048]) == body and result['PPU_reads'] == 4100
    writes = [(bank, value) for bank, at, value in own.ram_writes if at == 0x1fe0]
    assert writes[-2:] == [(3, 0xa7), (2, 0xa7)] and all(value == 0 for _, value in writes[:-2])
    clear_logs(own)
    n = N.fork(own)
    assert cold(n, 42)['PPU_reads'] == 0 and n.ram == own.ram
    rejects = 0
    for bank in (2, 3):
        for i in range(16):
            n = N.fork(own)
            n.ram[bank][0x1fe0 + i] ^= 1
            assert not invoke(n, AUTH)['P'] & 1 and not n.ram_writes
            rejects += 1
    assert invoke(N.fork(own), AUTH)['P'] & 1
    n = N.fork(own)
    assert not invoke(n, 0xb08c)['P'] & 1 and not n.ram_writes  # Public selector still excludes raw42.
    n = N.fork(own)
    n.ram[2][initialized - STATE] = 0x51
    assert invoke(n, labels['GfHostReset'], bank=3)['A'] == 0 and n.ram[2][initialized - STATE] == 0
    assert invoke(n, labels['GfHostMove'], bank=3)['P'] & 1 and n.ram[2][initialized - STATE] == 1

    guards, faults = [], []
    for name, fields in (('foreign', dict(SelectedCharacter=43)), ('title', dict(OperMode=0)),
                         ('uncommitted', dict(FamilyMainCommit=0)), ('visible', dict(DisableScreenFlag=0)),
                         ('mask', dict(Mirror_PPUMASK=24)), ('NMIzero', dict(NmiDisable=0))):
        n = blank(trial)
        scene(n, 42)
        N.put(n, **fields)
        old = [bytes(row) for row in n.ram]
        count = n.ppu_reads
        assert not invoke(n, COLD)['P'] & 1 and [bytes(row) for row in n.ram] == old and n.ppu_reads == count
        guards.append(name)
    for fault in (None, (2, 0), (3, 0), (3, 1024)):
        n = blank(trial)
        scene(n, 42)
        n.corrupt_at = fault
        if fault is None:
            n.protection = [0, 0]
        assert not invoke(n, COLD)['P'] & 1 and headers(n) == (b'\0' * 16, b'\0' * 16)
        faults.append(fault if fault else 'write protection')

    transitions = []
    for owner, seed in seeds.items():
        for before, dest, expected in ((seed, 42, own), (own, owner, seed)):
            n = N.fork(before)
            out = cold(n, dest)
            assert headers(n) == headers(expected)
            if dest == 42:
                assert bytes(n.ram[2][:256]) == b'\0' * 256 and bytes(n.ram[3][:2048]) == body
            transitions.append(dict(from_owner=owner if dest == 42 else 42, to_owner=dest, **out))
    n = N.fork(own)
    N.put(n, SelectedCharacter=0)
    invoke(n, RETIRE)
    assert n.ram[2][0x1fe0] == n.ram[3][0x1fe0] == 0
    assert not invoke(n, AUTH)['P'] & 1
    return dict(foreign=foreign, cold=result, warm=True, poisoned_header_bytes=rejects, guards=guards, faults=faults,
                transitions=transitions, foreign_selected_retire=True, loaded_reset_and_motion=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    output = parser.parse_args().output.resolve()
    assert output.is_relative_to(R / 'build')
    output.mkdir(exist_ok=True)
    base = Page.bundle()
    atlas = (Page.ASSET.parent / 'atlas.chr').read_bytes()
    pages = physical(base, atlas)
    old_worker, new_worker = worker(output, base)
    typed, _ = assemble(output, TYPED.read_text(), (('REMOTE', 0xb1ba, 81, ('TYPED',)),))
    code, labels, initialized = kernel(output, base)
    trial, patches, cookie, body = image(base, code, typed, old_worker, new_worker, atlas)
    print(json.dumps(dict(linked=len(code), typed=len(typed), cookie=cookie.hex(), pages=pages)), flush=True)
    cpu = qualification(base, trial, cookie, body, labels, initialized)
    (output / 'kernel.bin').write_bytes(body)
    receipt = dict(passed=True, CPU_only=True, ROM_written=False, scene_admitted=False, parent_SHA256=PIN,
                   expected_memory_only_SHA256=SHA(trial['raw']), code_pages=pages, patch_PRG=patches,
                   kernel_bytes=len(code), kernel_SHA256=SHA(body), kernel_labels=labels, cookie=cookie.hex(),
                   typed_leaf_bytes=len(typed), code_RAM3_A_half_open=[CODE, CODE + 0x800],
                   state_RAM2_C_half_open=[STATE, STATE + 0x100], active_source_state_bytes=len(Host.FIELDS),
                   publication='Both standard RAM2/3 $DFE0 headers use the payload-derived raw42 cookie.',
                   guards_preserved='B013 scene and A750 public dispatch still exclude raw42. Vector bytes remain inactive.',
                   CPU=cpu, limits=['Current controlled cold scope. No final scene/routing grant, native gameplay, IRQ replay or ROM emit.'],
                   bindings={p.relative_to(R).as_posix(): SHA(p.read_bytes()) for p in
                             (Path(__file__), Page.ROM, WORKER, INCLUDE, TYPED, ART_PROOF, *BODY)})
    (output / 'proof.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(passed=True, CPU=cpu)))


if __name__ == '__main__':
    main()
