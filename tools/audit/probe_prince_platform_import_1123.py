"""Seeded CPU prototype for real native Prince platform support, exact3ce.

This is NOT a candidate ROM, natural route, funded placement or Mesen pass.
It borrows $7C00 SRAM solely for isolated Worker/platform CPU fixtures;
that slab overlaps shared inventory and MUST NOT run the complete host frame.
The two private call sites authenticate; actual actor/collision/carry execute.
No source animation, native head, body/side collision or installed bytes change.
"""
import argparse
import json
import re
from pathlib import Path
from unittest.mock import patch

from py65.assembler import Assembler
import probe_prince_life_support_current_1123 as Q

H, W, N = Q.H, Q.W, Q.N
ORIGIN = 0x7c00  # Unfunded diagnostic slab, not a production allocation.
IMPORT, MATERIAL = 0xb376, 0xd6d1
IMPORT_PRE = bytes.fromhex('20d1b3')
MATERIAL_PRE = bytes.fromhex('20e2bd')
LEFT, CENTER, INITIAL_TOP = 1008, 1024, 192
CODE_SHA = '7639f934d5f6cbb95ff2c4a0c709e1209fa553e20881e2496887c999d7f370f1'
QUALIFIED_ROM = '6201e3b6680659fc1b1fab4e09125f9dc05e3b9e2b9a9beebcb656ef1bc2f36f'
QUALIFIED_RECEIPT = 'e77cb16cd291d7f37c44d0c2f3f6582d2fc8cacb220ae787fc670936ddc2d306'
WITHDRAWN_RECEIPTS = {
    '6f327508773b3a34b661e379ea59767f0a24f25a38747d5daae060fe46079939':
        'Unfunded7C00 overlaps inventory; partial PlayerCtrlRoutine repeated constructor. Not an uninterrupted donor ride.',
    'd641a4194401f7d9fbf6e3b442523a0940284a2608dc000546424a5c4879efbb':
        'Same invalid full-host fixture; C0B5 constructor writes invalidate original-landing qualification.',
}

ASM = '''
Import:
 php
 pha
 txa
 pha
 tya
 pha
 jsr Support
 bcc ImportDone
 sec
 sbc $c611
 sta $c089
 lda #0
 sbc #0
 sta $c08a
 lda $c089
 sec
 ; Original WorldPlaceAligned uses logical anchor SourceY+Origin+3.
 ; Keep animated C088 exclusively in the actual PhysicalFoot routine.
 sbc #3
 sta $c089
 lda $c08a
 sbc #0
 sta $c08a
 lda $c611
 sta $c08b
 jsr $c312
 lda $c084
 sta $c086
 lda $c085
 sta $c087
ImportDone:
 pla
 tay
 pla
 tax
 pla
 plp
 jmp $b3d1
Material:
 jsr $bde2
 bne MaterialDone
 php
 pha
 txa
 pha
 tya
 pha
 jsr Support
 bcc MaterialReject
 sta $c07f
 sta $c09b
 lda #0
 sta $c080
 sta $c09c
 lda #1
 sta $c09f
 pla
 tay
 pla
 tax
 pla
 plp
 lda #1
 rts
MaterialReject:
 pla
 tay
 pla
 tax
 pla
 plp
MaterialDone:
 rts
Support:
 lda SelectedCharacter
 cmp #38
 jne Fail
 lda GameEngineSubroutine
 cmp #8
 jne Fail
 lda WorldNumber
 ora LevelNumber
 ora TimerControl
 ora GamePauseStatus
 jne Fail
 lda AreaAddrsLOffset
 cmp #5
 jne Fail
 lda AreaType
 cmp #1
 jne Fail
 lda $c0ab
 cmp #167
 jne Fail
 lda $c6cf
 jeq Fail
 lda Player_Y_HighPos
 cmp #1
 jne Fail
 lda Player_State
 ora Player_Y_Speed
 jne Fail
 ldx #5
Slot:
 lda Enemy_Flag,x
 cmp #1
 bne Next
 lda Enemy_ID,x
 cmp #37
 bne Next
 lda Enemy_State,x
 bne Next
 lda Enemy_Y_HighPos,x
 cmp #1
 bne Next
 lda Enemy_BoundBoxCtrl,x
 cmp #5
 bne Next
 lda Enemy_X_Position,x
 cmp #240
 bne Next
 lda Enemy_PageLoc,x
 cmp #3
 bne Next
 txa
 cmp PlatformCollisionFlag,x
 bne Next
 lda Player_Y_Position
 clc
 adc #32
 bcs Next
 cmp Enemy_Y_Position,x
 bne Next
 lda Player_X_Position
 clc
 adc #13
 tay
 lda Player_PageLoc
 adc #0
 pha
 tya
 sec
 sbc Enemy_X_Position,x
 tay
 pla
 sbc Enemy_PageLoc,x
 bne Next
 cpy #43
 bcs Next
 lda Enemy_Y_Position,x
 sec
 rts
Next:
 dex
 jpl Slot
Fail:
 clc
 rts
'''


def assemble(text, symbols):
    lines = [line.split(';', 1)[0].strip() for line in text.splitlines()]
    labels = {line[:-1]: ORIGIN for line in lines if line.endswith(':')}
    labels.update(symbols)
    asm = Assembler(N.NesMPU(memory=[0] * 65536))
    inverse = dict(jne='BEQ', jeq='BNE', jpl='BMI')
    for lap in range(4):
        out = bytearray()
        for line in lines:
            if not line:
                continue
            if line.endswith(':'):
                labels[line[:-1]] = ORIGIN + len(out)
                continue
            line = re.sub(r'\b[A-Za-z_][A-Za-z_0-9]*\b',
                          lambda m: f'${labels[m[0]]:04x}' if m[0] in labels else m[0], line)
            line = re.sub(r'#(\d+)\b', lambda m: f'#${int(m[1]):02x}', line)
            op, *args = line.split()
            pc = ORIGIN + len(out)
            if op in inverse:
                out.extend(asm.assemble(f'{inverse[op]} ${pc + 5:04x}', pc=pc))
                out.extend(asm.assemble('JMP ' + args[0], pc=pc + 2))
            else:
                if lap == 3 and op.upper() in ('BCC', 'BCS', 'BEQ', 'BNE', 'BMI', 'BPL'):
                    delta = int(args[0][1:], 16) - pc - 2
                    assert -128 <= delta <= 127, (line, delta)
                out.extend(asm.assemble(line, pc=pc))
    assert ORIGIN + len(out) < 0x8000
    return bytes(out), labels


def symbols(raw):
    b = dict(W.Symbols.bundle(), raw=raw)
    names = ('SelectedCharacter GameEngineSubroutine WorldNumber LevelNumber TimerControl '
             'GamePauseStatus AreaPointer AreaAddrsLOffset AreaType Player_Y_HighPos Player_Y_Position '
             'Player_State Player_Y_Speed Player_X_Position Player_PageLoc Enemy_Flag '
             'Enemy_ID Enemy_State Enemy_Y_HighPos Enemy_BoundBoxCtrl Enemy_X_Position '
             'Enemy_PageLoc Enemy_Y_Position PlatformCollisionFlag').split()
    return {name: W.address(b, name) for name in names}


def private(m, pc, *, a=85, x=0, y=0, p=0x31, bound=100000):
    m.raw_page(1, 3)
    m.raw_page(2, 2)
    N.put(m, CurrentBank=3, CurrentBankC=2)
    cpu = N.NesMPU(memory=m, pc=pc)
    cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp = a, x, y, p, 224
    cpu.stPushWord(0x5aff)
    maps = set()
    for _ in range(bound):
        if cpu.pc == 0x5b00:
            break
        if cpu.pc >= 0x8000:
            maps.add((cpu.pc & 0xe000, m.rawtags[(cpu.pc - 0x8000) // 8192]))
        assert m[cpu.pc] != 0, ('Mapped prototype BRK', hex(cpu.pc), m.rawtags)
        cpu.step()
    else:
        raise AssertionError(('Bounded prototype call', hex(pc), hex(cpu.pc)))
    assert cpu.sp == 224
    return dict(regs=[cpu.a, cpu.x, cpu.y, cpu.p, cpu.sp], maps=sorted(maps), cycles=cpu.processorCycles)


def patch_model(m, code, labels):
    assert bytes(m.ram[3][IMPORT - 0xa000:IMPORT - 0xa000 + 3]) == IMPORT_PRE
    assert bytes(m.ram[2][MATERIAL - 0xc000:MATERIAL - 0xc000 + 3]) == MATERIAL_PRE
    m[ORIGIN:ORIGIN + len(code)] = code
    for bank, pc, target in ((3, IMPORT, labels['Import']), (2, MATERIAL, labels['Material'])):
        m.ram[bank][pc & 8191:(pc & 8191) + 3] = bytes((0x20, target & 255, target >> 8))


def slot(m, name, value, i=5):
    m[W.address(m.bundle, name) + i] = value


def scene(seed, x=1016, top=192):
    m = N.fork(seed)
    # Declared translated scene, NOT an earned replay checkpoint.
    N.put(m, Player_X_Position=x & 255, Player_PageLoc=x >> 8,
          Player_Y_Position=top - 30, Player_Y_HighPos=1, Player_Y_Speed=1,
          Player_State=2, ObjectOffset=5, Player_BoundBoxCtrl=0,
          ScreenLeft_X_Pos=192, ScreenLeft_PageLoc=3,
          ScreenRight_X_Pos=191, ScreenRight_PageLoc=4,
          TimerControl=0, CurrentOAMOffset=64, FrameCounter=1)
    for i in range(6):
        slot(m, 'Enemy_Flag', 0, i)
    for name, value in (('Enemy_Flag', 1), ('Enemy_ID', 37), ('Enemy_State', 0),
                        ('Enemy_PageLoc', LEFT >> 8), ('Enemy_X_Position', LEFT & 255),
                        ('Enemy_Y_Position', top), ('Enemy_Y_HighPos', 1)):
        slot(m, name, value)
    N.invoke(m, 'CheckpointEnemyID', x=5)
    # Match the existing authored32px managers' explicit native bbox choice;
    # the stock Easy constructor alone selects the wider default platform.
    assert N.get(m, 'Enemy_BoundBoxCtrl', 5) in (5, 6)
    slot(m, 'Enemy_BoundBoxCtrl', 5)
    slot(m, 'PlatformCollisionFlag', 255)
    s = m.ram[2]
    for at, value in ((0x60f, x + 8), (0x84, 208), (0x86, 208), (0x89, 77)):
        s[at:at + 2] = value.to_bytes(2, 'little')
    for at, value in ((0x611, 128), (0x8b, 128), (0x88, 3), (0x615, 255),
                      (0x616, 0), (0x617, 15), (0x618, 0), (0x6c0, 0), (0xa6, 0)):
        s[at] = value
    return m


def native_platform(m):
    N.put(m, ObjectOffset=5, CurrentOAMOffset=64)
    N.invoke(m, 'GetPlayerOffscreenBits', x=0)
    N.invoke(m, 'RelativePlayerPosition', x=0)
    N.invoke(m, 'BoundingBoxCore', x=0, y=0)
    N.invoke(m, 'RunLargePlatform', x=5)
    return dict(flag=N.get(m, 'PlatformCollisionFlag', 5), top=N.get(m, 'Enemy_Y_Position', 5),
                y=N.get(m, 'Player_Y_Position'), state=N.get(m, 'Player_State'),
                speed=N.get(m, 'Player_Y_Speed'))


def rejection_matrix(landed, code, labels):
    def source_equal(a,b):
        skip = set(range(MATERIAL & 8191, (MATERIAL & 8191) + 3))
        return all(x == y or i in skip for i,(x,y) in enumerate(zip(a.ram[2],b.ram[2])))
    cases = (
        ('rising', 'Player_Y_Speed', 255, None),
        ('air', 'Player_State', 2, None),
        ('inactive', 'Enemy_Flag', 0, 5),
        ('duplicate', 'Enemy_Flag', 2, 5),
        ('enemy', 'Enemy_ID', 6, 5),
        ('dead', 'Enemy_State', 32, 5),
        ('foreign-marker', 'Enemy_State', 64, 5),
        ('wrong-width', 'Enemy_BoundBoxCtrl', 6, 5),
        ('wrong-left', 'Enemy_X_Position', 239, 5),
        ('wrong-page', 'Enemy_PageLoc', 4, 5),
        ('offscreen-actor', 'Enemy_Y_HighPos', 2, 5),
        ('stale-slot', 'PlatformCollisionFlag', 4, 5),
        ('no-contact', 'PlatformCollisionFlag', 255, 5),
        ('above-plane', 'Player_Y_Position', 159, None),
        ('below-plane', 'Player_Y_Position', 161, None),
        ('offscreen-player', 'Player_Y_HighPos', 0, None),
        ('foreign-owner', 'SelectedCharacter', 37, None),
        ('wrong-world', 'WorldNumber', 1, None),
        ('wrong-level', 'LevelNumber', 1, None),
        ('wrong-loaded-area', 'AreaAddrsLOffset', 4, None),
        ('water', 'AreaType', 0, None),
        ('pause', 'GamePauseStatus', 1, None),
        ('timer', 'TimerControl', 1, None),
        ('engine', 'GameEngineSubroutine', 7, None),
    )
    done = []
    for name, field, value, actor in cases:
        old = N.fork(landed)
        if actor is None:
            N.put(old, **{field: value})
        else:
            slot(old, field, value, actor)
        new = N.fork(old)
        patch_model(new, code, labels)
        a, b = private(old, 0xb3d1), private(new, labels['Import'])
        assert a['regs'] == b['regs'] and source_equal(old,new), (name,a['regs'],b['regs'],[(hex(i+0xc000),u,v)for i,(u,v)in enumerate(zip(old.ram[2],new.ram[2]))if u!=v][:16])
        done.append(name)
    for name, x in (('left-no-overlap', 994), ('right-no-overlap', 1038)):
        old = N.fork(landed)
        N.put(old, Player_X_Position=x & 255, Player_PageLoc=x >> 8)
        new = N.fork(old)
        patch_model(new, code, labels)
        a, b = private(old, 0xb3d1), private(new, labels['Import'])
        assert a['regs'] == b['regs'] and source_equal(old,new), name
        done.append(name)
    for name, at in (('unready', 0xab), ('no-health', 0x6cf)):
        old = N.fork(landed)
        old.ram[2][at] = 0
        new = N.fork(old)
        patch_model(new, code, labels)
        a, b = private(old, 0xb3d1), private(new, labels['Import'])
        assert a['regs'] == b['regs'] and source_equal(old,new), name
        done.append(name)
    signed = 0
    for sy in (0, 64, 128, 250):
        for delta in (-20, -3, 0, 3, 20):
            m = N.fork(landed)
            patch_model(m, code, labels)
            m.ram[2][0x611] = sy
            m.ram[2][0x88] = delta & 255
            private(m, labels['Import'])
            private(m, 0xc312)  # Actual PpWorldPhysicalFoot.
            top=N.get(m,'Enemy_Y_Position',5)
            origin=int.from_bytes(m.ram[2][0x89:0x8b],'little')
            assert(sy+origin+3)&65535==top
            assert int.from_bytes(m.ram[2][0x84:0x86], 'little') == (top+delta-3)&65535
            assert m.ram[2][0x611] == sy
            signed += 1
    return dict(rejected=done, signed_origin_and_projection_cases=signed,
                rejected_Source_RAM_and_AXYPSP_exact=True, input_P=0x31)


def authored(seed):
    m = N.fork(seed)
    N.put(m, AreaPointer=37, AreaType=1, WorldNumber=0, LevelNumber=0,
          AreaDataOffset=0, AreaObjectPageLoc=0, AreaObjectPageSel=0,
          BackloadingFlag=0, BehindAreaParserFlag=0)
    N.invoke(m, 'GetAreaDataAddrs')
    at = W.address(m.bundle, 'AreaObjectLength')
    m[at:at + 3] = [255] * 3
    for col in range(75):
        N.put(m, CurrentPageLoc=col // 16, CurrentColumnPos=col % 16,
              BlockBufferColumnPos=col % 32)
        N.invoke(m, 'AreaParserCore')
    block = W.address(m.bundle, 'Block_Buffer_2')
    assert m[block + 7 * 16 + 9] == 16 and m[block + 7 * 16 + 10] == 17
    return m


def pipe_pairs(seed, code, labels):
    parsed = authored(seed)
    count = 0
    for x in (898, 912, 929, 941, 943):
        for pad in (0, 1, 2, 8, 65, 129):
            old = scene(parsed, x=x)
            for i in range(6):
                slot(old, 'Enemy_Flag', 0, i)
            N.put(old, Player_Y_Position=112, Player_State=0, Player_Y_Speed=0,
                  SavedJoypad1Bits=pad, SavedJoypadBits=pad, A_B_Buttons=pad & 192,
                  Left_Right_Buttons=pad & 3, Up_Down_Buttons=pad & 12,
                  FrameCounter=100 + count)
            old.ram[2][0x611] = old.ram[2][0x8b] = 64
            old.ram[2][0x84:0x88] = bytes((144, 0, 144, 0))
            new = N.fork(old)
            patch_model(new, code, labels)
            a, b = (private(m, 0xb36e) for m in (old, new))
            assert a['regs'] == b['regs'], (x,pad)
            for bank, skip in ((2, set(range(MATERIAL & 8191, (MATERIAL & 8191) + 3))),
                               (3, set(range(IMPORT & 8191, (IMPORT & 8191) + 3)))):
                assert all(u == v or i in skip for i,(u,v) in enumerate(zip(old.ram[bank],new.ram[bank]))), (x,pad,bank)
            assert old.rawtags == new.rawtags and old.chr_latches == new.chr_latches
            assert bytes(old[0:256]) == bytes(new[0:256]), (x,pad,'native-zero-page')
            count += 1
    return dict(actual_authored_pipe_isolated_Worker_pairs=count, original_source_RAM_and_native_ZP_exact=True,
                native_registers_flags_mapper_CHR_exact=True)


def falling_landing(seed, code, labels):
    m = scene(seed)
    s = m.ram[2]
    s[0x611] = s[0x8b] = 114
    s[0x84:0x88] = bytes((194,0,190,0))
    s[0x616],s[0x617],s[0x618],s[0xa6] = 18,104,3,3
    landed = native_platform(m)
    assert landed['flag'] == 5 and landed['y'] + 32 == landed['top']
    assert [s[i]for i in(0x616,0x617,0x618)]==[18,104,3]
    patch_model(m,code,labels)
    rows=[];writers=[];original=N.NesMPU;stable=0;misses=0
    class Trace(original):
        def step(self):
            before=[s[i]for i in(0x616,0x617,0x618)]
            pc=self.pc;tag=m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else None
            result=super().step()
            after=[s[i]for i in(0x616,0x617,0x618)]
            if before!=after:writers.append(dict(pc=pc,bank=tag,before=before,after=after))
            return result
    for tick in range(96):
        N.put(m,FrameCounter=(120+tick)&255,SavedJoypad1Bits=0,SavedJoypadBits=0,
              A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0)
        if tick==0:
            with patch.object(N,'NesMPU',Trace):private(m,0xb36e)
        else:private(m,0xb36e)
        q=native_platform(m)
        row=[tick,q['top'],q['y'],q['flag'],s[0x616],s[0x617],s[0x618],s[0x6cf],
             N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')]
        if not rows or row[4:7]!=rows[-1][4:7]:rows.append(row)
        assert s[0x6cf]==5 and N.get(m,'NumberofLives')==2,('Original airborne landing harm',rows)
        attached=q['flag']==5 and q['y']+32==q['top']
        misses+=not attached
        stable=stable+1 if attached and [s[i]for i in(0x616,0x617,0x618)]==[0,15,0]else 0
    assert [s[i]for i in(0x616,0x617,0x618)]==[0,15,0],rows
    assert stable>=25,('Original airborne landing did not retain25 idle native contacts',stable,rows)
    assert writers and all(w['bank']in(2,3)and not ORIGIN<=w['pc']<ORIGIN+len(code)
                           and not 0xc0b0<=w['pc']<0xc100 for w in writers),writers
    return dict(updates=96,initial_source_action_pose_mode=[18,104,3],native=landed,
                original_landing_states=rows,HP=s[0x6cf],lives=N.get(m,'NumberofLives'),
                actual_donor_state_writers=writers,donor_state_reset_in_bridge=False,
                transient_unattached_updates=misses,settled_contact_returns=stable)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compile-only', action='store_true')
    args = parser.parse_args()
    raw = Q.P.G.ROM.read_bytes()
    parent = raw
    if H(raw) != Q.PIN:
        import compose_dkjr_shinobi_1123 as DK
        if H(parent) != DK.STAR_UNDER:
            import install_mega_giant_item_semantics_1123 as Mega
            assert H(parent) == Mega.CANDIDATE
            parent = Mega.recover_parent(parent)
        assert H(parent) == DK.STAR_UNDER
        parent = DK.recover_parent(parent)
        assert H(parent) == Q.PIN
    binding = Q.authenticate(parent)
    assert Q.P.Packet.extract(raw) == Q.P.Packet.extract(parent)
    b = dict(W.Symbols.bundle(), raw=raw)
    for name in ('GameLoop', 'PositionPlayerOnVPlat', 'Z2PositionOnPlatform', 'RunLargePlatform', 'PlayerCtrlRoutine'):
        at = W.location(b, name)
        assert raw[at:at + 64] == parent[at:at + 64]
    def current_auth(image):
        assert image == raw
        return binding
    cold = Q.P.clone(Q.P.cold, dict(authenticate=current_auth))
    binding = dict(binding, actual=H(raw), authenticated_packet_parent=H(parent))
    code, labels = assemble(ASM, symbols(raw))
    assert len(code)==312 and H(code) == CODE_SHA
    print('PRINCE_PLATFORM_COMPILE ' + json.dumps(dict(ROM=H(raw), code=H(code), bytes=len(code),
          sites=[hex(IMPORT), hex(MATERIAL)], entries={n:hex(labels[n]) for n in ('Import','Material','Support')},
          unfunded_fixture_slab=hex(ORIGIN),
          proposed_actor=dict(id=37, left=LEFT, center=CENTER, initial_top=INITIAL_TOP, width=32),
          scope='Seeded actual-code CPU units; no image placement/natural pickup/native claim'), separators=(',', ':')), flush=True)
    if args.compile_only:
        return

    def deny(*a, **k):
        raise AssertionError('Platform prototype attempted output/native')

    with patch.object(Path, 'write_bytes', deny), patch.object(Path, 'write_text', deny), patch('subprocess.Popen', deny):
        seed = cold(raw)
        # Finish real unmodified Main/NMI epochs before translating fixtures.
        # A partial first PlayerCtrlRoutine is not a stable warm-stage entry.
        for _ in range(12):
            seed.controller_pad=0
            Q.Engine.Frames.frame(seed,cold=True)
        assert [seed.ram[2][i]for i in(0x616,0x617,0x618)]==[0,15,0]
        old = scene(seed)
        landed = native_platform(old)
        assert landed['flag'] == 5 and landed['state'] == 0 and landed['speed'] == 0
        assert landed['y'] + 32 == landed['top']
        contact = N.fork(old)
        new = N.fork(old)
        patch_model(new, code, labels)
        before = bytes(new.ram[2])
        imported = private(new, labels['Import'])
        assert int.from_bytes(new.ram[2][0x84:0x86], 'little') == landed['top'], dict(
            native=landed, fields={n:N.get(new,n) for n in symbols(raw)},
            actor={n:N.get(new,n,5) for n in ('Enemy_ID','Enemy_Flag','Enemy_State','Enemy_Y_HighPos','Enemy_BoundBoxCtrl','Enemy_X_Position','Enemy_PageLoc','PlatformCollisionFlag')},
            source=[new.ram[2][i] for i in (0xab,0x6cf,0x84,0x85)], registers=imported)
        assert new.ram[2][0x611] == before[0x611]
        assert bytes(new.ram[2][0x615:0x619]) == before[0x615:0x619]
        private(old, 0xb36e)
        private(new, 0xb36e)
        print('PRINCE_PLATFORM_FIRST ' + json.dumps(dict(native=landed, import_cpu=imported,
              parent_y=N.get(old, 'Player_Y_Position'), prototype_y=N.get(new, 'Player_Y_Position'),
              source_y_unchanged=new.ram[2][0x611] == before[0x611], outputs=0), separators=(',', ':')), flush=True)
        guards = rejection_matrix(contact, code, labels)
        pipes = pipe_pairs(seed, code, labels)
        landing = falling_landing(seed,code,labels)
        print('PRINCE_PLATFORM_GUARDS ' + json.dumps(dict(guards=guards,pipes=pipes,
              original_airborne_landing=landing,
              native_head_and_side_ROM_bytes_unchanged=True, outputs=0), separators=(',', ':')), flush=True)
        rows = []
        for tick in range(1, 97):
            N.put(new, FrameCounter=tick & 255, SavedJoypad1Bits=0, SavedJoypadBits=0,
                  A_B_Buttons=0, Left_Right_Buttons=0, Up_Down_Buttons=0)
            private(new, 0xb36e)
            q = native_platform(new)
            rows.append((tick, q['top'], q['y'], q['flag'], new.ram[2][0x616], new.ram[2][0x617], new.ram[2][0x618]))
            assert q['flag'] == 5 and q['y'] + 32 == q['top'], ('Actual ride lost', rows[-5:])
            assert new.ram[2][0x6cf] == 5 and N.get(new, 'NumberofLives') == 2
        ride = dict(updates=len(rows), first=rows[:4], last=rows[-4:],
              top_range=[min(r[1] for r in rows), max(r[1] for r in rows)],
              source_animation=[new.ram[2][i] for i in (0x616, 0x617, 0x618)],
              HP=new.ram[2][0x6cf], lives=N.get(new, 'NumberofLives'), binding=binding,
              outputs=0, seeded_scene=True, natural_pickup=False, native=False)
        print('PRINCE_PLATFORM_RIDE ' + json.dumps(ride, separators=(',', ':')), flush=True)
        receipt = dict(passed=True,ROM=H(raw),code_SHA256=H(code),native_landing=landed,
                       import_CPU=imported,guards=guards,pipes=pipes,ride=ride,landing=landing,
                       model_only_edits=True,production_allocation=False,
                       isolated_Worker_and_native_actor_calls=True,complete_host_frame=False,
                       no_actor_admission_or_natural_pickup_claim=True)
        digest = H(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode())
        if H(raw)==QUALIFIED_ROM:assert digest==QUALIFIED_RECEIPT
        print('PRINCE_PLATFORM_RECEIPT ' + json.dumps(dict(passed=True,SHA256=digest,
              actual_ROM=H(raw),code_SHA256=H(code),outputs=0,seeded_CPU_units=True,
              Mesen=False,natural_pickup=False,production_allocation=False),separators=(',',':')),flush=True)


if __name__ == '__main__':
    main()
