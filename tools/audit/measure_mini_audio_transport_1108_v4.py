"""Measure resident-C macro reads and delayed audio mapper selection on delivered Mini."""

import argparse
from collections import Counter
import json
from pathlib import Path
import re

import measure_mini_audio_1108_v1 as M
from check_mini_audio_mixer_irq_1108_v2 import compose, lag_path


ROM = M.ROOT/'build/mini-frame-budget-1108/candidate.nes'
PIN = 'e90d30c1c9636be6eb304a7b3b1506b862f8171dc2773d809482e25b0a5417df'
DECODER = M.ROOT/'build/mini-audio-1108-v1/decoder-successor.s'
SOURCE = M.ROOT/'src/expanded_audio.s'
CURRENT_CPU = M.N.NesMPU


def memory_patch(image, pc, old, new):
    at = 16+38*8192+(pc&8191)
    assert len(old) == len(new) and image['raw'][at:at+len(old)] == old
    return dict(bank=38,pc=pc,offset=at,preimage=old.hex(),replacement=new.hex())


def assemble_pair(image, output, name, pc, extent, prefix, old, new):
    a, _ = M.assemble(output/(name+'-original'),prefix+old,pc,extent)
    b, labels = M.assemble(output/(name+'-successor'),prefix+new,pc,extent)
    assert len(a) == len(b) == extent
    return memory_patch(image,pc,a,b), labels


def decl(image, names):
    return ''.join(f'{n}=${M.address(image,n):04x}\n' for n in names)


def patch_code(image, output):
    src = SOURCE.read_text()
    prefix = decl(image,('Commands','MapAudioBank','XgAudioDepth','XgAudioPtr',
                        'XgAudioStackLo','XgAudioStackHi','XgAudioStackBank','XgAudioBank','XgMacroLo','XgMacroHi'))
    prefix += '.export Macro,ReturnMacro\n'
    old = src.split('\nMacro:\n',1)[1].split('\nStopCorruptStream:',1)[0]
    old = 'Macro:\n'+old.replace('#.bank(XgMacroLo)','#38')+'\nStopCorruptStream:\n'
    old = M.one(old,'  jcs StopCorruptStream\n','  bcc :+\n  jmp StopCorruptStream\n:\n')
    new = M.one(old, '  jsr MapAudioBank\n  jmp Commands\nReturnMacro:\n',
                'MacroCommandsJump:\n  jmp Commands\n  .res 3,$ea\nReturnMacro:\n')
    new = M.one(new, '  lda XgAudioDepth\n  beq StopCorruptStream\n  dec XgAudioDepth\n  ldx XgAudioDepth\n',
                '  ldx XgAudioDepth\n  beq StopCorruptStream\n  dex\n  stx XgAudioDepth\n')
    new = M.one(new, '  jsr MapAudioBank\n  jmp Commands\n',
                '  txa\n  bne MacroCommandsJump\n  jsr MapAudioBank\n  bmi MacroCommandsJump\n')
    macro_start, macro_end = (M.address(image,n) for n in ('Macro','StopCorruptStream'))
    macro, labels = assemble_pair(image,output,'macro',macro_start,macro_end-macro_start,prefix,old,new)
    assert labels['ReturnMacro'] == M.address(image,'ReturnMacro')

    body = DECODER.read_text()
    new = M.one(body,'Uncompressed:\n  jsr RawByte\nByteResult:\n',
                'Uncompressed:\n  ldy #0\n  lda (XgAudioPtr),y\n  inc XgAudioPtr\n'
                '  bne ByteResult\n  inc XgAudioPtr+1\n  sec\nByteResult:\n')
    new = M.one(new,'ResetLz:\n  lda #0\n','ResetLz:\n  ldx #>XgLzHistory\n  stx XgLzPosition+1\n  lda #0\n')
    new = M.one(new,'  lda #>XgLzHistory\n  sta XgLzPosition+1\n  lda #0                        ; Callers also use ResetLz to clear A.\n','')
    new = M.one(new,'LzByte:\n  lda XgLzRemaining\n','LzByte:\n  ldy #0\n  lda XgLzRemaining\n')
    new = M.one(new,'CopyLz:\n  ldy #0\n','CopyLz:\n')
    new = M.one(new,'RawByte:\n  ldy #0\n','RawByte:\n')
    new = M.one(new,'  clc                           ; pos - (encoded distance + 1).\n','')
    lo, hi = (M.address(image,n) for n in ('Byte','KbAudioFamily'))
    dec, labels = assemble_pair(image,output,'decoder',lo,hi-lo,'',body,new)
    before = M.address(image,'ResetLz')
    after = labels['ResetLz']
    assert before != after and labels['Byte'] == lo
    signature = bytes((0x20,before&255,before>>8))
    start = M.address(image,'ExpandedAudioTick')
    old_audio = image['raw'][16+38*8192:16+39*8192]
    resets = [p for p in range(start,lo) if old_audio[p&8191:(p&8191)+3] == signature]
    assert len(resets) == src.count('jsr ResetLz') == 5
    instructions_after_reset = ['ldx #15','jsr ClearImage','ldx XgAudioSelection',
                                'ldx XgAudioEventSelection','ldx XgAudioSelection']
    source_after = [part.splitlines()[1].strip() for part in src.split('jsr ResetLz')[1:]]
    assert source_after == instructions_after_reset, source_after
    fixes = [memory_patch(image,p,signature,bytes((0x20,after&255,after>>8))) for p in resets]

    old = src.split('\nAdvance:\n',1)[1].split('\nCodecCommands:',1)[0]+'\n'
    old = M.one(old,'.if ::MAPPER_MMC5\n  ora #MMC5_PRG_ROM\n.endif\n  BankPRGA a',
                '  ora #$80\n  sta $5115')
    new = '''  lda XgAudioDelay
  beq Read
  dec XgAudioDelay
  jmp ClearQueues
Read:
  lda XgAudioBank
  ora #$80
  sta $5115
'''
    old += 'CodecCommands:\n'
    prefix = decl(image,('ClearQueues','XgAudioDelay','XgAudioBank'))
    hi = M.address(image,'CodecCommands')
    lo = hi-19
    advance, _ = assemble_pair(image,output,'advance',lo,hi-lo,prefix,old,new)
    return [advance,macro,dec,*fixes], dict(old_ResetLz=before,new_ResetLz=after,callers=resets)


def macro_closure(image):
    lo, hi = (M.location(image,n) for n in ('XgMacroLo','XgMacroHi'))
    count = hi-lo
    raw = image['raw']
    pointers = [raw[lo+i]+256*raw[hi+i] for i in range(count)]
    assert count == 222 and pointers == sorted(set(pointers)) and pointers[0] == 0xc4b0
    end = M.address(image,'ExpandedAudioTick')
    assert end == 0xc858
    base = 16+38*8192-0xc000
    depth = []
    page_cross = []
    for i, (start, limit) in enumerate(zip(pointers,pointers[1:]+[end])):
        pc, children = start, []
        while pc < limit:
            cmd = raw[base+pc]
            pc += 1
            if cmd == 0x1f:
                break
            if cmd == 0xfe:
                continue
            if cmd >= 0x20:
                other = cmd-0x20
                assert 0 <= other < i, (i,other)
                children.append(depth[other])
            else:
                assert cmd < 16 or cmd in (0x15,0x1d), (i,cmd)
                pc += 1
        assert pc == limit and raw[base+pc-1] == 0x1f, (i,hex(pc),hex(limit))
        depth.append(1+max(children,default=0))
        if start>>8 != pc>>8:
            page_cross.append(i)
    return dict(exact_entries=count,half_open_C_window_range=[pointers[0],end],
                finite_maximum_depth=max(depth),macro_records_crossing_pages=page_cross)


def compare(a, b):
    old = M.hardware
    try:
        M.hardware = lambda m:[(pc,v) for pc,v in old(m) if pc != 0x5115]
        M.compare_state(a,b)
    finally:
        M.hardware = old
    previous, new = [[v for pc,v in old(m) if pc == 0x5115] for m in (a,b)]
    trace = iter(previous)
    assert all(any(v == x for v in trace) for x in new), (previous,new)
    return len(previous)-len(new)


def run_scenarios(original, successor):
    rows = []
    for char, length in [(41,720),*( (n,48) for n in (0,1,2,3,6,7,8,9,12,13,14,15,16,17,18,23,24,29,32,35,36,37,38,39,40))]:
        a,b = M.seed(original,char),M.seed(successor,char)
        old_cost, new_cost, saved, maps = [], [], [], []
        for t in range(length):
            for m in (a,b):
                m.writes.clear()
                M.N.put(m,AreaMusicQueue=(1 if t == 0 else 2 if t == 137 else 8 if t == 420 else 0),
                        EventMusicQueue=(4 if t in (30,231) else 64 if t == 508 else 0),
                        Square1SoundQueue=(32 if t%37 == 14 else 0),Square2SoundQueue=int(t%63==9),
                        NoiseSoundQueue=int(t%61==10),GamePauseStatus=int(t%128 in (85,86,87)),FrameCounter=t&255)
            before, regs_before = M.direct(a,'AudioUpdate')
            after, regs_after = M.direct(b,'AudioUpdate')
            assert regs_before == regs_after,(char,t,regs_before,regs_after)
            try:
                maps.append(compare(a,b))
            except AssertionError as e:
                raise AssertionError((char,t,before,after)) from e
            old_cost.append(before);new_cost.append(after);saved.append(before-after)
        rows.append(dict(selected=char, updates=length, baseline_mean=sum(old_cost)/length,
                         successor_mean=sum(new_cost)/length, baseline_peak=max(old_cost),
                         successor_peak=max(new_cost), cycle_savings=[min(saved),max(saved)],
                         average_saved=sum(saved)/length, fewer_A_mapper_writes=sum(maps)))
    return rows


def nmi(m, force_lag):
    m.writes.clear()
    M.N.put(m,NmiDisable=255 if force_lag else 0)
    lag, regular = lag_path(m)
    cpu = CURRENT_CPU(memory=m,pc=0x5b00)
    cpu.sp,cpu.p = 214,0x20
    cpu.nmi()
    visits = Counter()
    for _ in range(80000):
        if (cpu.pc,cpu.sp) == (0x5b00,214):
            break
        if cpu.pc in (lag,regular):
            visits[cpu.pc] += 1
        assert m[cpu.pc] != 0, (hex(cpu.pc),m.rawtags)
        cpu.step()
    else:
        raise AssertionError(('Actual NMI execution bound',hex(cpu.pc)))
    assert visits == Counter({lag if force_lag else regular:1}),visits
    return cpu.processorCycles,(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp)


def check_interrupts(original, successor):
    rows=[]
    for kind in ('normal','lag'):
        a,b = M.seed(original,41),M.seed(successor,41)
        original_cost,new_cost=[],[]
        for t in range(96):
            for m in (a,b):
                M.N.put(m,AreaMusicQueue=1 if t == 0 else 0,Square1SoundQueue=32 if t%32==14 else 0,
                        VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0,FrameCounter=t)
            old,arch1 = nmi(a,kind == 'lag')
            new,arch2 = nmi(b,kind == 'lag')
            assert arch1 == arch2
            compare(a,b)
            original_cost.append(old);new_cost.append(new)
        changes = [x-y for x,y in zip(original_cost,new_cost)]
        rows.append(dict(kind=kind, calls=len(changes), baseline_peak=max(original_cost),
                         successor_peak=max(new_cost), mean_saved=sum(changes)/len(changes),
                         saved_range=[min(changes),max(changes)]))
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    a.output.mkdir(exist_ok=True)
    raw=ROM.read_bytes()
    assert M.sha(raw)==PIN
    before=M.bundle(raw)
    proof=macro_closure(before)
    patches, reset=patch_code(before,a.output)
    after_raw=compose(raw,patches)
    after=M.bundle(after_raw)
    tests=run_scenarios(before,after)
    print('Whole AudioUpdate',json.dumps(tests[0]),flush=True)
    interrupts=check_interrupts(before,after)
    result=dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=M.sha(after_raw),patches=patches,
                macro_C_window=proof,reset_private_relink=reset,actual_AudioUpdate=tests,
                true_NMI_CPU=interrupts,
                intentionally_changed='Elide A-window bank writes for resident-C macro entry/nested return and delay-only ticks. '
                                      'Outer return still restores the compressed stream A bank. Original IO write order '
                                      'and values exact except the named redundant $5115 writes.',
                source_bindings={p.relative_to(M.ROOT).as_posix():M.sha(p.read_bytes()) for p in
                                (Path(__file__),SOURCE,DECODER,M.ROOT/'src/reset.s')},
                scope='Actual source and current in-memory ROM. Exact full application state, ordered APU/expansion/PPU '
                      'writes, final maps and AXYP/SP. CPU timing excludes NES DMA stalls. No ROM emitted.')
    (a.output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('passed','expected_memory_only_SHA256','true_NMI_CPU')}))


if __name__=='__main__':
    main()
