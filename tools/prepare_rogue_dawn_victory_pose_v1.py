"""Use the authentic standing body during Rogue's automatic SMB victory."""
from pathlib import Path
import argparse
import difflib
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(R/'tools'), str(R/'tools/audit')]
import rogue_dawn_map_v1 as ref
from prepare_rogue_dawn_host_body_handoff_v1 import dependencies
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

P = R/'build/rogue-dawn-flagpole-v1'
BODY = R/'build/rogue-dawn-side-v1/body-source.s'
O = R/'build/rogue-dawn-victory-pose-v1'

WORKER = """; Drawing adaptation for SMB's automatic flagpole/castle sequence.
; C94 is already mapped by the genuine RdRenderPlayer call immediately before
; this hook. Select actual source frame8 through the authenticated art tables;
; do not advance animation or modify action/radii/position/health/input.
.pushseg
.segment "ROGUE_DAWN_HOST"
.export RdVictoryPublishChr,RdVictoryPublishEnd
.proc RdVictoryPublishChr
 lda RdSourceAltPalette
 bne Publish
 lda GameEngineSubroutine
 sec
 sbc #4
 cmp #2
 bcs Publish
 ldx RdFacing
 ; Original source standing frame8 resolves to consecutive records7/8.
 ; The build recipe verifies both real lookup bytes before linking.
 lda RdArtRecordLo+7,x
 sta SmPosePtr
 lda RdArtRecordHi+7,x
 sta SmPosePtr+1
 lda RdArtRecordPage+7,x
 clc
 adc #<RD_FIRST_CHR
 sta SmChrBank
 lda #METASPRITE_SAMUS_BODY
 sta ObjectMetasprite
Publish:
 jmp RdBodyPublishChr
.endproc
RdVictoryPublishEnd:
.assert * <= $c000,lderror,"Victory draw exceeds approved A95 tail"
.popseg
"""


def main():
    global O
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=R/'build/rogue-dawn-victory-pose-v4')
    O = parser.parse_args().output.resolve()
    assert not (O/'build.json').exists(), 'Preserve frozen successor'
    p = json.loads((P/'handoff.json').read_text())
    for b in p['bindings']:
        assert ref.binding(b['path']) == b, b['path']
    old = scoped_load(P/'candidate.nes')
    assert ref.digest(old['raw']) == 'f36632e4d8662d2cc47968f526aac6a77ce9a385b5f00be9a4bb70352aa30132'
    assert old['raw'][location(old,'RdBodyIndex0')+8] == 7
    assert old['raw'][location(old,'RdBodyIndex1')+8] == 8
    start = address(old, 'RdNonSolidBGEnd')
    assert start == 0xbfcd
    at = 16+95*8192+(start & 8191)
    assert old['raw'][at:16+96*8192] == bytes([255])*(0xc000-start)
    O.mkdir(exist_ok=True)
    for name in ['main.c', 'private.cfg']:
        (O/name).write_bytes((P/name).read_bytes())
    body = BODY.read_text()
    anchor = ' jsr RdBodyPublishChr\n'
    assert body.count(anchor) == 1
    (O/'body-source.s').write_text(body.replace(anchor, ' jsr RdVictoryPublishChr\n'))
    life = (BODY.parent/'lifecycle-source.s').read_text()
    anchor = ' plp\n lda RdAnimFrame\n cmp #$f7\n beq Hide\n sec\n rts\nHide:clc'
    assert life.count(anchor) == 1
    life_new = life.replace(anchor, ' plp\n ; Automatic victory freezes source updates, including an F7 hurt flash.\n'
        ' ; The authentic standing draw below owns these two SMB phases.\n'
        ' lda GameEngineSubroutine\n and #$fe\n cmp #4\n beq Show\n'
        ' lda RdAnimFrame\n cmp #$f7\n beq Hide\nShow:sec\n rts\nHide:clc')
    (O/'lifecycle-source.s').write_text(life_new)
    dispatch = (P/'contact-dispatch.s').read_text()
    dispatch_new = dispatch.replace(' php\n pha\n txa\n pha\n', ' txa\n pha\n')
    dispatch_new = dispatch_new.replace('$0107,x', '$0105,x').replace('$0108,x', '$0106,x')
    dispatch_new = dispatch_new.replace(' pla\n tax\n pla\n plp\n', ' pla\n tax\n')
    dispatch_new = dispatch_new.replace(' ; then the three saves above.', ' ; then the saved X above.')
    dispatch_new = dispatch_new.replace('RdBoxOrExit:\n', 'RdBoxOrExit:\n'
        ' ; A/P are dead at both genuine call sites: the selector returns Y,\n'
        ' ; the BG caller immediately loads SmCeilingHit; both targets begin\n'
        ' ; with LDA and establish their own carry before using it. Preserve X.\n')
    assert dispatch_new.count(' pla\n tax\n') == 2
    (O/'contact-dispatch.s').write_text(dispatch_new)
    (O/'source.patch').write_text(''.join(''.join(difflib.unified_diff(a.splitlines(True), z.splitlines(True),
        fromfile='parent/'+name, tofile='victory/'+name)) for name,a,z in [
            ('body-source.s',body,(O/'body-source.s').read_text()),
            ('lifecycle-source.s',life,life_new),('contact-dispatch.s',dispatch,dispatch_new)]))
    (O/'victory-draw.s').write_text(WORKER)
    (O/'entrypoint.s').write_text((P/'entrypoint.s').read_text()+'\n.include "victory-draw.s"\n')
    command = json.loads((P/'build.json').read_text())['executed_commands'][-1]
    command = [v.replace(str(P), str(O)) for v in command]
    ix = command.index('--asm-include-dir')
    command[ix:ix] = ['--asm-include-dir', str(O), '--asm-include-dir', str(P)]
    z = subprocess.run(command, cwd=R, capture_output=True, text=True)
    (O/'build.log').write_text(z.stdout+z.stderr)
    assert z.returncode == 0, (z.stdout+z.stderr)[-5000:]
    prepare(R, O/'candidate.nes')
    b = scoped_load(O/'candidate.nes')
    assert address(b, 'RdNonSolidBGEnd') == start
    assert address(b, 'RdVictoryPublishChr') == start
    end = address(b, 'RdVictoryPublishEnd')
    assert end <= 0xc000
    call = bytes([0x20])+address(old, 'RdBodyPublishChr').to_bytes(2,'little')
    lo = location(old, 'RdBodyGraphics')
    assert old['raw'][lo:lo+100].count(call) == 1
    site = lo+old['raw'][lo:lo+100].index(call)
    # The visibility guard shifts only the remaining selected-owner
    # A95 routines. The linker fixes their genuine absolute references. Keep
    # all other bytes except such exact operand relocations unchanged.
    allowed = {site+1, site+2} | set(range(at, at+end-start))
    begin = location(old,'RdLifeVisible')
    limit = 16+95*8192+0x1f00
    allowed.update(range(begin,limit))
    relocated = {a:address(b,n) for n in old['syms']
        if (a:=address(old,n)) >= address(old,'RdLifeVisible') and a < 0xbf00
        and n in b['syms'] and address(b,n) != a
        and location(old,n)//8192 == begin//8192}
    relocation_sites = []
    # Actual call/jump absolute instructions only. No generic byte-pair waiver.
    for i in range(16,16+1048576-2):
        if old['raw'][i] not in (0x20,0x4c): continue
        a = int.from_bytes(old['raw'][i+1:i+3],'little')
        if a in relocated and b['raw'][i] == old['raw'][i] and int.from_bytes(b['raw'][i+1:i+3],'little') == relocated[a]:
            allowed.update([i+1,i+2])
            relocation_sites.append(dict(file_offset=i,old=hex(a),new=hex(relocated[a])))
    smc = address(old,'FarcallJmpTarget_SMC')
    for i in range(16,16+1048576-9):
        if old['raw'][i] != 0xa9 or old['raw'][i+2:i+6] != bytes([0x8d])+int(smc+1).to_bytes(2,'little')+bytes([0xa9]): continue
        if old['raw'][i+7:i+10] != bytes([0x8d])+int(smc+2).to_bytes(2,'little'): continue
        a = old['raw'][i+1]+256*old['raw'][i+6]
        n = b['raw'][i+1]+256*b['raw'][i+6]
        if a in relocated and n == relocated[a] and all(old['raw'][j] == b['raw'][j] for j in range(i,i+10) if j not in [i+1,i+6]):
            allowed.update([i+1,i+6])
            relocation_sites.append(dict(file_offset=i,kind='genuine_FarcallJmpTarget_SMC_load',old=hex(a),new=hex(n)))
    changes = [i for i,(a,c) in enumerate(zip(old['raw'],b['raw'])) if a != c]
    unexpected = sorted(set(changes)-allowed)
    assert not unexpected, [(hex(i),old['raw'][i-4:i+6].hex(),b['raw'][i-4:i+6].hex()) for i in unexpected[:30]]
    assert b['raw'][site] == 0x20 and int.from_bytes(b['raw'][site+1:site+3], 'little') == start
    deps = dependencies(O/'assembler-full.dep')
    assert O/'body-source.s' in deps and O/'victory-draw.s' in deps
    data = dict(passed=True, source_build_only=True, native_run=False,
                ROM=ref.binding(O/'candidate.nes'), parent=ref.binding(P/'candidate.nes'),
                executed_commands=[command], new_RAM=0, code_bytes=end-start,
                modified_existing_instruction='Standing-draw JSR; selected-owner A95 visibility/dispatch and genuine linked JSR/JMP operand relocations. All CHR unchanged.',
                linked_relocations=relocation_sites, changed_bytes=len(changes),
                bindings=[ref.binding(p) for p in dict.fromkeys(deps+[Path(__file__), P/'handoff.json',
                    O/'private.cfg',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',O/'candidate.map'])])
    (O/'build.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(ROM=data['ROM'], code_bytes=end-start, tail_end=hex(end))))


if __name__ == '__main__':
    main()
