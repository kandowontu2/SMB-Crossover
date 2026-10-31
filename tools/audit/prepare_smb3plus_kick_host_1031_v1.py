"""Join the donor's big-Toad kick at its actual native animation call site."""
from pathlib import Path
import json
import re
import shutil
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
from private_build_outputs_v1 import validate
from check_tmnt_render_oa import load,address

P=R/'build/smb3plus-body-host-1030-v3'
O=R/'build/smb3plus-kick-host-1031-v1';J=O/'joint'
C=R/'build/smb3plus-kick-caller-1031-v1/caller-controls.json'


def once(text,old,new):
    assert text.count(old)==1,(old,text.count(old))
    return text.replace(old,new)


def main():
    assert not O.exists()
    parent=json.loads(B.read(P/'handoff.json'));B.bound(parent)
    caller=json.loads(B.read(C));B.bound(caller)
    assert caller['passed'] and len(caller['cases'])==56
    old=load(P/'joint/candidate.nes')
    shutil.copytree(P/'joint',J)
    def rt(s):return s.replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix())
    for p in J.rglob('*'):
        if p.is_file() and p.suffix in ['.s','.inc','.cfg']:B.write(p,rt(B.read(p)))
    motion=J/'src/smb3_mario_motion.s'
    text=once(B.read(motion),'Native:\n farcall M3Step\n lda Player_Rel_XPos\n sta Player_Pos_ForScroll\n rts',
        'Native:\n jmp MbMappedStep\n .res 25-(*-Native),$ea ; Preserve the original public suffix.')
    B.write(motion,text)
    # While A92 owns the original controller, C91 holds the extension. Map C
    # before entering the source controller; restore it before native callers
    # resume. PLA changes only NZ, which the original final LDA also sets.
    helper='''; No new RAM. Native C mapping is stacked for this single step.
.pushseg
.segment "M3_LOGIC"
.proc MbMappedStep
 lda CurrentBankC
 pha
 BankPRGC #.bank(M3ArtBegin)
 farcall M3Step
 pla
 sta CurrentBankC
 sta $5116
 lda Player_Rel_XPos
 sta Player_Pos_ForScroll
 rts
.endproc
MbKickLogicEnd:
.assert MbKickLogicEnd<=$af00,lderror,"Preserve Rogue Dawn audio at AF00"
.popseg
'''
    B.write(J/'smb3plus_kick_host.s',helper)
    B.write(J/'entrypoint.s',B.read(J/'entrypoint.s')+'\n.include "smb3plus_kick_host.s"\n')
    native=J/'src/smb3_native_controller.inc'
    text=once(B.read(native),'GndMov_Big:\n JSR Player_GroundHControl\n JSR Player_JumpFlyFlutter\n JSR Player_SoarJumpFallFrame',
        'GndMov_Big:\n JSR Player_GroundHControl\n JSR Player_JumpFlyFlutter\n JSR ::MbToadBigFrame')
    B.write(native,text)
    art=J/'src/smb3_mario_art.inc';text=B.read(art)
    match=re.search(r'M3Form4ChrHi: \.byte ([0-9,]+)\n',text)
    assert match and [int(v) for v in match.group(1).split(',')]==[2]*81
    assert ' lda #2 ; All original high-table entries are2;' in B.read(J/'src/smb3_mario_render.s')
    kick='''M3Form4ChrHi:
.proc MbToadBigFrame
 jsr M3Native::Player_SoarJumpFallFrame
 lda M3Variant
 cmp #2
 bne Done
 ; Original38:AC91..ACC9, reached only from big-form dry control.
 lda M3Native::Pad_Holding
 and #4
 bne Done
 bit M3Native::Pad_Input
 bvc Animate
 lda M3Native::Player_TailAttack
 bne Animate
 lda #12
 sta M3Native::Player_TailAttack
 lda #$10
 sta M3Native::Sound_QLevel2
Animate:
 lda M3Native::Player_TailAttack
 beq Done
 lsr
 lsr
 tay
 lda #$2d
 sta M3Native::Player_Frame
 lda M3Native::Player_TailAttack
 cmp #5
 bne Done
 lda #0
 sta M3Native::Player_TailAttack
Done:rts
.endproc
 .res 81-(*-M3Form4ChrHi),2
'''
    B.write(art,text[:match.start()]+kick+text[match.end():])
    recipes=[]
    for label in ['main-build','union-build','chr-build','final-link']:
        cmd=[rt(s) for s in json.loads(B.read(P/(label+'.json')))['command']]
        validate(cmd,J,cwd=R)
        result=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        B.write(O/(label+'.json'),json.dumps(dict(command=cmd,returncode=result.returncode,
            stdout=result.stdout,stderr=result.stderr),indent=2)+'\n')
        assert result.returncode==0,(label,result.stderr)
        recipes.append(O/(label+'.json'))
    from prepare_cv3_dmc_mirror import prepare
    prepare(R,J/'candidate.nes')
    new=load(J/'candidate.nes')
    checked=[]
    for name,s in old['syms'].items():
        if name.startswith('M3') and s.get('type')=='lab':
            assert address(old,name)==address(new,name),name
            checked.append(name)
    assert old['raw'][:16]==new['raw'][:16]
    assert old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
    d=dict(status='PRIVATE_BIG_TOAD_KICK_SOURCE_JOIN_NOT_ADMITTED',source=True,native=False,
        installed=False,menu_unlocked=False,parent=parent['candidate'],candidate=B.sha(J/'candidate.nes'),
        public_M3_labels_preserved=len(checked),CHR_byte_exact=True,
        hook='Big-form dry GndMov_Big after SoarJumpFallFrame, before later power/special frames.',
        existing_state='Player_TailAttack; no new RAM or independent attack timer.',
        limits=['Source controls and native integration remain required.',
            'Source QLevel2=$10 request is retained, but the existing host still drops this SFX request.',
            'Peach float and remaining special form consumers are not completed by this change.',
            'No new menu admission, installation or full1-1/every-powerup claim.'],
        bindings={str(p):B.sha(p) for p in [Path(__file__),P/'handoff.json',C,motion,native,art,
            J/'smb3plus_kick_host.s',J/'entrypoint.s',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',*recipes]})
    B.write(O/'source-stage.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps({k:v for k,v in d.items() if k!='bindings'},indent=2))


if __name__=='__main__':main()
