"""Descriptor-only selected-player Star palette proposal over exact174fa.

This recipe generates detached bytes and checks current source ownership. It
does not compose a ROM, overlay CPU memory, run gameplay, or write artifacts.
"""
from hashlib import sha256
import json
from pathlib import Path

import compose_bub_native_palette_current_1115 as Previous

R, B, W = Previous.R, Previous.B, Previous.W
PIN = Previous.CANDIDATE
PREVIOUS_SHA = '1b3e655bb5d44a0230d690d6dcc7ebd70959e5200fc661ece80f0758f95f58e6'
START, OLD_END, SPARE_END = 0xb438, 0xb455, 0xb53a
OLD = bytes.fromhex('b906c14c41b4b902c148ad00c3d00c684829034903d0046829fc606860')
H = lambda v: sha256(v).hexdigest()


def measured_bytes(star_timer, native_attributes):
    """Keep both entry anchors and the existing common JMP target fixed."""
    data = bytearray(OLD[:9])
    labels, branches = {}, []

    def emit(*values): data.extend(values)
    def label(name): labels[name] = START + len(data)
    def branch(opcode, name):
        emit(opcode, 0); branches.append((len(data) - 1, name))

    label('Common')
    emit(0x48)                         # PHA original private attribute
    emit(0xad, star_timer & 255, star_timer >> 8)
    branch(0xf0, 'Ordinary')            # Inactive: exact delivered mapper
    emit(0x98, 0x29, 0xf0)             # Legal selected Y=00/08; scans >=10
    branch(0xd0, 'Ordinary')
    emit(0xad, 0x00, 0xc3, 0x29, 0xfe) # Foreign identity2..255 unchanged
    branch(0xd0, 'Ordinary')
    emit(0x68)                         # Selected real Bub/Bob during Star
    emit(0x4d, native_attributes & 255, native_attributes >> 8)
    emit(0x29, 0xfc)
    emit(0x4d, native_attributes & 255, native_attributes >> 8)
    emit(0x60)
    label('Ordinary')
    # The saved original attribute is still on the stack here. This is the
    # exact old common body after its PHA; only its two branches relocate.
    emit(0xad, 0x00, 0xc3)
    branch(0xd0, 'ReturnOriginal')
    emit(0x68, 0x48, 0x29, 0x03, 0x49, 0x03)
    branch(0xd0, 'ReturnOriginal')
    emit(0x68, 0x29, 0xfc, 0x60)
    label('ReturnOriginal'); emit(0x68, 0x60)
    for offset, name in branches:
        delta = labels[name] - (START + offset + 1)
        assert -128 <= delta <= 127
        data[offset] = delta & 255
    assert len(data) == 56 and labels['Common'] == 0xb441
    return bytes(data), labels


def metadata(raw):
    assert isinstance(raw, bytes) and H(raw) == PIN
    assert H(Path(Previous.__file__).read_bytes()) == PREVIOUS_SHA
    parent = Previous.inverse(raw)
    # Reuse the frozen source-retirement proof, without relaxing its40a API.
    baseline = Previous.A.metadata(parent)
    image = Previous.code(raw)
    assert image[START-0xa000:OLD_END-0xa000] == OLD
    spare = image[OLD_END-0xa000:SPARE_END-0xa000]
    assert spare == b'\xff' * 229
    assert raw[Previous.COOKIE:Previous.COOKIE+16] == Previous.cookie(raw)
    bundle = dict(W.Symbols.bundle(), raw=raw)
    timer = W.address(bundle, 'StarInvincibleTimer')
    attributes = W.address(bundle, 'Player_SprAttrib')
    assert attributes == 0x587
    new, labels = measured_bytes(timer, attributes)
    end = START + len(new)
    old = image[START-0xa000:end-0xa000]

    lab = json.loads((R/'build/bub-upgrades-root-1102-v48/proposal.json').read_text())['labels']
    native = (R/'build/bub-upgrades-root-1102-v48/native.bin').read_bytes()
    # Draw and selected actor selector have no changes since their retained
    # linked source. Pair differs only at the two already delivered loaders.
    pieces = {}
    for name, endpc in (('BbNativeActor', lab['BbNativeInput']),
                        ('BbNativeDraw', lab['BbNativePair'])):
        pc = lab[name]
        data = bytearray(native[pc-0xb540:endpc-0xb540])
        if name == 'BbNativeDraw':
            # Delivered empty-loop optimization replaces this four-byte scan
            # initializer by JMP B3E2/NOP. Its nonempty fallback must replay
            # exactly X68/Y10 then resume BD63; it never changes player draw.
            hook = lab['BbNativeDrawBubbles']
            assert hook == 0xbd5f and data[hook-pc:hook-pc+4] == bytes.fromhex('a268a010')
            data[hook-pc:hook-pc+4] = bytes.fromhex('4ce2b3ea')
        current = image[pc-0xa000:endpc-0xa000]
        assert data and current == data, (name, hex(pc), hex(endpc),
            [(hex(pc+i), a, b)for i,(a,b)in enumerate(zip(data,current))if a!=b][:20])
        pieces[name] = dict(pc=pc, end=endpc, SHA256=H(data), bytes=data.hex())
    word = lambda n: int(n).to_bytes(2,'little')
    empty_path = R/'tools/audit/bub_empty_loops_1113.py'
    assert H(empty_path.read_bytes()) == '996003a033e7eb2a1e4139a472d136fd6b6e5ce0b26f1d6969497fac89874ca0'
    tail = native.index(bytes.fromhex('a9008de106a9e18d066b'),lab['BbNativeDrawAdvance']-0xb540)+0xb540
    guards = tuple(range(0xc068,0xc080,4))+tuple(range(0xc088,0xc0c4,4))
    check = bytes((0xad,))+word(guards[0])+b''.join(bytes((0x0d,))+word(a)for a in guards[1:])
    fast = bytes.fromhex('a900a2c4a000b8384c')+word(tail)
    guard = b'\x48'+check+bytes((0xd0,len(fast)+1,0x68))+fast+b'\x68\xa2\x68\xa0\x10\x4c'+word(0xbd63)
    assert len(guard) == 86 and image[0x13e2:0x1438] == guard
    pieces['EmptyDrawScan'] = dict(pc=0xb3e2,end=0xb438,SHA256=H(guard),bytes=guard.hex(),
        noactors_skips_all_scan_calls=True,nonempty_fallback_XY=[0x68,0x10],resume=0xbd63)
    pairpc, pairend = lab['BbNativePair'], lab['BbNativePairDone'] + 1
    pair = bytearray(native[pairpc-0xb540:pairend-0xb540])
    for pc, before, after in Previous.EDITS[:2]:
        logical = B.PAGES.index((pc-Previous.A.CH)//1024)*1024 + (pc-Previous.A.CH)%1024
        assert pairpc-0xa000 <= logical < pairend-0xa000
        at = logical - (pairpc-0xa000)
        assert pair[at:at+3] == bytes.fromhex(before)
        pair[at:at+3] = bytes.fromhex(after)
    assert image[pairpc-0xa000:pairend-0xa000] == pair
    pieces['BbNativePair'] = dict(pc=pairpc, end=pairend, SHA256=H(pair))
    # All adjacent words in this complete active private component, including
    # tables and vectors, are censused; coincidental words are not disassembly.
    ingress = []
    for i in range(len(image)-1):
        target = int.from_bytes(image[i:i+2], 'little')
        if START <= target < end:
            ingress.append(dict(word_pc=0xa000+i, target=target))
    assert ingress == [dict(word_pc=0xb43c,target=0xb441),
                       dict(word_pc=0xbdfb,target=0xb43e),
                       dict(word_pc=0xbe01,target=0xb438)], ingress
    assert not [n for n, pc in lab.items() if START <= pc < end]
    assert baseline['pair']['direct_callers'] == [0xbd5c, 0xbd77]
    pair_words = [0xa000+i for i in range(len(image)-1)
                  if image[i:i+2] == pairpc.to_bytes(2,'little')]
    assert pair_words == [0xbd5d,0xbd78], pair_words
    helper = raw[Previous.A.CH+441*1024:Previous.A.CH+442*1024]
    helper_words = [dict(word_pc=0xd000+i,target=int.from_bytes(helper[i:i+2],'little'))
                    for i in range(0x320,0x3ff)
                    if START <= int.from_bytes(helper[i:i+2],'little') < end]
    assert helper_words == [], helper_words
    source = (R/'build/bub-upgrades-root-1102-v48/native.s').read_text()
    assert source.count('jsr BbNativePair\n') == 2
    # No Star reader or Player_SprAttrib store is introduced; the two repeated
    # XOR reads need the native attribute stable for this short leaf. Actual
    # reached IRQ/busy-NMI execution remains a required post-grant test.
    formula_cases = 0
    for original in range(256):
        for native_attr in range(256):
            result = ((original ^ native_attr) & 0xfc) ^ native_attr
            assert result == (original & 0xfc) | (native_attr & 3)
            formula_cases += 1
    file = Previous.A.CH+B.PAGES[(START-0xa000)//1024]*1024+START%1024
    descriptor = dict(name='SelectedPlayerStarPoseMapper', space='private3',
        pc=START, end=end, file=file, before=old.hex(), after=new.hex(),
        before_SHA256=H(old), after_SHA256=H(new))
    return dict(parent=PIN, granted=False, mounted=False, ROM_composed=False,
        CPU_executed=False, output_files=0, code_before_SHA256=H(image),
        fields=dict(StarInvincibleTimer=timer, Player_SprAttrib=attributes),
        source_fragments=pieces, labels=labels, descriptor=descriptor,
        code_owned_bytes=len(new), newly_consumed_spare_bytes=len(new)-len(OLD),
        existing_cookie=dict(file=Previous.COOKIE, size=16,
            before=raw[Previous.COOKIE:Previous.COOKIE+16].hex(),
            regenerated_only_after_grant=True),
        proposed_owned_bytes=len(new)+16,
        remaining_spare=dict(pc=end, end=SPARE_END, size=SPARE_END-end,
            SHA256=H(image[end-0xa000:SPARE_END-0xa000])),
        source_declared_spare=dict(pc=OLD_END,end=SPARE_END,size=len(spare),SHA256=H(spare)),
        current_component_word_ingress=ingress,
        current_Pair_word_consumers=pair_words,
        actual_helper_executable_word_ingress=helper_words,
        caller_domain=dict(selected=[[0x2e,0],[0x42,8]],
            captured_proxies=[[x,0x10+(x-0x68)*2]for x in range(0x68,0x80,4)],
            bubbles=[[x,0x88+(x-0x88)*2]for x in range(0x88,0xc4,4)],
            manual_invalid_Y_domain_not_claimed=True),
        detached_python_formula_cases=formula_cases,
        ABI_proposal='X/Y/SP and CVID preserved; A is the mapped attribute and NZ describes it; original private attributes, owner/status/input, R0..7 and native palettes unchanged. Selected legal hero Y00/08 with identity0/1 and timer>0 replaces only low2 with native Player_SprAttrib low2. All other calls use exact prior mapper semantics.',
        remaining_gates=['root exact source lease','finite actual6502 mapper/status and bothentries',
            'full Pair alllegal callers and renderer NO_PALETTE/flip/priority cases',
            'actual reached IRQ/busyNMI including between repeated native attribute reads',
            'cold/inverse/ownership/foreign/death/expiry and natural M/F/S/L regressions',
            'root native Star pictures bothidentities and native world palette/CHR preservation'])


if __name__ == '__main__':
    raw = Previous.ROM.read_bytes()
    q = metadata(raw)
    text = json.dumps(q, sort_keys=True, separators=(',', ':'))
    print('RESULT '+text, flush=True)
    print('RECEIPT '+H(text.encode()), flush=True)
