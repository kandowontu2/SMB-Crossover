"""Join the ordinary donor float at both velocity updates and jump control."""
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

P=R/'build/smb3plus-kick-host-1031-v1'
O=R/'build/smb3plus-peach-float-host-1031-v1';J=O/'joint'
S=R/'tools/reference/smb3plus_peach_float_1031_v1.s'
N=R/'build/smb3plus-peach-float-donor-native-1031-v1/discovery'


def once(text,old,new):
    assert text.count(old)==1,(old,text.count(old))
    return text.replace(old,new)


def main():
    assert not O.exists()
    parent=json.loads(B.read(P/'handoff.json'));B.bound(parent)
    native=json.loads(B.read(N/'capture/binding.json'));B.bound(native)
    assert native['exit_code']==0
    old=load(P/'joint/candidate.nes')
    shutil.copytree(P/'joint',J)
    def rt(text):return text.replace(str(P/'joint'),str(J)).replace((P/'joint').as_posix(),J.as_posix())
    for p in J.rglob('*'):
        if p.is_file() and p.suffix in ['.s','.inc','.cfg']:B.write(p,rt(B.read(p)))
    code=B.read(S)
    # All real producers keep Expired in0/1 and Ready in0/1/2. Preserve the
    # ordinary source state machine while fitting existing constant-table spans.
    code=once(code,' lda MbFloatExpired\n cmp #1\n beq Clear',' lda MbFloatExpired\n bne Clear')
    code=once(code,' lda MbFloatReady\n cmp #1\n bne Done',' lda MbFloatReady\n beq Done')
    code=once(code,' lda M3Native::Pad_Holding\n and #$80\n beq End',' lda M3Native::Pad_Holding\n bpl End')
    parts={m[1]:m[0]+'\n' for m in re.finditer(r'\.proc (\w+)\n.*?\.endproc',code,re.S)}
    # Split one source function at an unconditional magnitude/sign boundary.
    head,tail=parts['MbPeachFloatWobble'].split('Sign:\n',1)
    head=head.replace(' bne Sign',' jmp MbPeachFloatSign')
    head+=' jmp MbPeachFloatSign\n.endproc\n'
    tail=tail.removesuffix('.endproc\n')
    tail=tail.replace('Positive','MbFloatSignPositive')
    sign='::MbPeachFloatSign:\n'+tail
    body=J/'src/smb3_native_controller.inc';text=B.read(body)
    text=once(text,' STA Player_XHi,X\n RTS',' JSR ::MbPeachVelocityEnd\n RTS')
    text=once(text,' LDA Player_RootJumpVel\n sec',' JSR ::MbPeachJumpRoot\n sec')
    calls=text.count(' JSR Player_JumpFlyFlutter\n');assert 4<=calls<=8,calls
    text=text.replace(' JSR Player_JumpFlyFlutter\n',' JSR ::MbPeachAfterJump\n')
    B.write(body,text)
    art=J/'src/smb3_mario_art.inc';text=B.read(art)
    inserts={0:['MbPeachFloatApply','MbPeachFloatExpire'],1:['MbPeachJumpRoot'],
             3:['MbPeachFloatReturn'],4:['MbPeachFloatSink']}
    for i,names in inserts.items():
        needle=f' .res 81-(*-M3Form{i}ChrHi),2\n'
        text=once(text,needle,''.join(parts[n] for n in names)+needle)
    match=re.search(r'M3Form5ChrLo: \.byte ([0-9,]+)\n',text);assert match
    low=match[1];assert len(low.split(','))==81
    text=text[:match.start()]+'M3Form5ChrLo:\n'+parts['MbPeachVelocityEnd']+parts['MbPeachFloatClear']+' .res 81-(*-M3Form5ChrLo),2\n'+text[match.end():]
    for i,names in [(5,['MbPeachFloatCheck','MbPeachFloatActive']),(6,['MbPeachAfterJump'])]:
        match=re.search(rf'M3Form{i}ChrHi: \.byte ([0-9,]+)\n',text)
        assert match and [int(v) for v in match[1].split(',')]==[2]*81
        text=text[:match.start()]+f'M3Form{i}ChrHi:\n'+''.join(parts[n] for n in names)+f' .res 81-(*-M3Form{i}ChrHi),2\n'+text[match.end():]
    for mark in ['<','>']:
        text=once(text,mark+'M3Form5ChrLo',mark+'MbFloatForm5ChrLo')
    match=re.search(r'M3NativePalettes: \.byte [^\n]+\n',text);assert match
    assert B.read(J/'src/smb3_mario_render.s').count('M3NativePalettes')==0
    text=text[:match.start()]+'M3NativePalettes:\n'+head+' .res 24-(*-M3NativePalettes),2\n'+text[match.end():]
    B.write(art,text)
    render=J/'src/smb3_mario_render.s';text=B.read(render)
    text=once(text,' jsr MbPaletteIndex\n .res 37-3,$ea\n',
        ' jsr MbPaletteIndex\n jmp MbFloatPaletteResume\nMbFloatPaletteBody:\n'+sign+
        ' .res 37-6-(*-MbFloatPaletteBody),$ea\nMbFloatPaletteResume:\n')
    B.write(render,text)
    state=code[:code.index('.proc MbPeachVelocityEnd')]
    B.write(J/'smb3plus_float_state.inc',state)
    B.write(J/'smb3plus_float_source.s',code)
    B.write(J/'smb3plus_float_data.s','.pushseg\n.segment "M3_GFX"\nMbFloatForm5ChrLo:\n .byte '+low+
        '\nMbFloatDataEnd:\n.assert MbFloatDataEnd<=$d400,lderror,"Preserve Rogue Dawn upper audio"\n.popseg\n')
    B.write(J/'entrypoint.s',B.read(J/'entrypoint.s')+'\n.include "smb3plus_float_state.inc"\n.include "smb3plus_float_data.s"\n')
    recipes=[]
    for label in ['main-build','union-build','chr-build','final-link']:
        cmd=[rt(s) for s in json.loads(B.read(P/(label+'.json')))['command']]
        validate(cmd,J,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        B.write(O/(label+'.json'),json.dumps(dict(command=cmd,returncode=p.returncode,
            stdout=p.stdout,stderr=p.stderr),indent=2)+'\n')
        assert p.returncode==0,(label,p.stderr)
        recipes.append(O/(label+'.json'))
    from prepare_cv3_dmc_mirror import prepare
    prepare(R,J/'candidate.nes');new=load(J/'candidate.nes')
    checked=[]
    for name,s in old['syms'].items():
        if name.startswith('M3') and s.get('type')=='lab':
            assert address(old,name)==address(new,name),name
            checked.append(name)
    assert old['raw'][:16]==new['raw'][:16]
    assert old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
    d=dict(status='PRIVATE_ORDINARY_PEACH_FLOAT_SOURCE_JOIN_NOT_ADMITTED',source=True,native=False,
        installed=False,menu_unlocked=False,parent=parent['candidate'],candidate=B.sha(J/'candidate.nes'),
        native_donor_handoff_sha256=B.sha(N/'capture/binding.json'),
        public_M3_labels_preserved=len(checked),CHR_byte_exact=True,jump_control_calls=calls,
        state=dict(first=0x5c64,end_exclusive=0x5c68,owner='existing selected17 private5C overlay; reset by genuine M3Reset'),
        hooks=['Both original X/Y velocity integrator exits','Genuine initial jump root','After each genuine dry JumpFlyFlutter'],
        relocation='Only the form5 low CHR table moves within C91; pointer consumers use the relocated81 exact bytes. Final high-pointer outputs and all label PCs stay fixed.',
        limits=['Actual source/graphics/ISR controls and native host integration remain required.',
            'Single active body uses donor P1 float, including160 ticks at two velocity callbacks per update.',
            'SMB terrain is resolved by the native host after movement; donor ground-pound extension and custom stomp delay are not joined here.',
            'Original kick SFX bridge and growth/slide/ground-pound art consumers remain incomplete.',
            'No playable admission, installed change, full1-1 or every-powerup claim.'],
        bindings={str(p):B.sha(p) for p in [Path(__file__),S,P/'handoff.json',N/'capture/binding.json',
            N/'capture/ram-float-entry.bin',N/'capture/float-boundaries.csv',body,art,render,
            J/'smb3plus_float_state.inc',J/'smb3plus_float_source.s',J/'smb3plus_float_data.s',J/'entrypoint.s',
            J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',*recipes]})
    B.write(O/'source-stage.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps({k:v for k,v in d.items() if k!='bindings'},indent=2))


if __name__=='__main__':main()
