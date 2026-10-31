"""Join the four SMB3 identities to the real Select/name/status consumers.

Private candidate only. No admission or Downloads installation is asserted.
Existing function entries remain fixed; only private labels within the two
edited routines may move. The actual producer objects are rebuilt.
"""
from pathlib import Path
import json
import shutil
import subprocess
import sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_smb3plus_peach_float_host_1031_v1 as P
from check_tmnt_render_oa import load,address

H=R/'build/smb3plus-peach-float-host-1031-v4/handoff.json'
O=R/'build/smb3plus-menu-host-1031-v1';J=O/'joint'


def main():
    assert not O.exists()
    h=json.loads(P.B.read(H));P.B.bound(h);parent=Path(h['joint'])
    old=load(parent/'candidate.nes');shutil.copytree(parent,J)
    def rt(text):return text.replace(str(parent),str(J)).replace(parent.as_posix(),J.as_posix())
    for p in J.rglob('*'):
        if p.is_file() and p.suffix in ['.s','.inc','.cfg']:P.B.write(p,rt(P.B.read(p)))
    select=J/'src/character_select.s';text=P.B.read(select)
    text=P.once(text,'  lda M3Variant\n  eor #1\n  sta M3Variant\n',
        '  inc M3Variant\n  lda M3Variant\n  and #3\n  sta M3Variant\n')
    text=P.once(text,'  .res 12,$ea\nGbPitNavContinue:',
        '  .res 9,$ea ; Fund the three-byte four-identity Select cycle.\nGbPitNavContinue:')
    P.B.write(select,text)
    names=J/'src/new_roster_dispatch.s';text=P.B.read(names)
    text=P.once(text,'  lda #28\n  clc\n  adc M3Variant\n  jmp NameIndex\n',
        '  ldx M3Variant\n  lda MbMenuNameIndices,x\n  jmp NameIndex\n')
    tail=' .endif\n.endproc\n.segment "NEW_ROSTER_GATE"'
    text=P.once(text,tail,'  .byte "   SMB3 TOAD    ","   SMB3 PEACH   "\n'+tail.replace('\n.endproc',
        '\n::MbMenuNameIndices:.byte 28,29,45,46\n.endproc'))
    P.B.write(names,text)
    render=J/'src/smb3_mario_render.s';text=P.B.read(render)
    text=P.once(text,' .res 37-6-(*-MbFloatPaletteBody),$ea\n',
        '::MbStatusNameOffsets:.byte 0,7,13,19\n .res 37-6-(*-MbFloatPaletteBody),$ea\n')
    P.B.write(render,text)
    status=J/'src/smb3_mario_dispatch.s';text=P.B.read(status)
    a=text.index('Own:pla\n',text.index('.proc M3StatusNameDispatch\n'))
    z=text.index('.endproc',a)
    old_size=int(old['syms']['M3StatusNameDispatch']['size'])
    text=text[:a]+'''Own:pla
 bne Done ; PLA already supplies the original CMP#0 zero test.
 pha
 txa
 pha
 ldx M3Variant
 lda MbStatusNameOffsets,x
 tax
 ldy #0
Loop:
 lda Names,x
 sta VRAM_Buffer1+11,y
 inx
 iny
 cpy #7
 bcc Loop
 pla
 tax
 pla
Done:rts
; The leading/trailing space is shared at the Toad/Peach boundaries.
Names:.byte "MARIO3 LUIGI3 TOAD3 PEACH3"
'''+f'.assert *-M3StatusNameDispatch<={old_size},error,"Existing status span"\n.res {old_size}-(*-M3StatusNameDispatch),$ea\n'+text[z:]
    P.B.write(status,text)
    logs=[]
    for name in ['main-build','union-build','chr-build','final-link']:
        cmd=[rt(s) for s in json.loads(P.B.read(parent.parent/(name+'.json')))['command']]
        P.validate(cmd,J,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        P.B.write(O/(name+'.json'),json.dumps(dict(command=cmd,returncode=p.returncode,
            stdout=p.stdout,stderr=p.stderr),indent=2)+'\n')
        assert p.returncode==0,(name,p.stderr)
        logs.append(O/(name+'.json'))
    from prepare_cv3_dmc_mirror import prepare
    prepare(R,J/'candidate.nes');new=load(J/'candidate.nes')
    public=[];private=[]
    for name,sym in old['syms'].items():
        if sym.get('type')!='lab':continue
        if address(old,name)==address(new,name):
            if '::' not in name:public.append(name)
            continue
        assert name.startswith(('CrossoverMenuInput::','M3StatusNameDispatch::')),name
        private.append(dict(label=name,old=address(old,name),new=address(new,name)))
    assert old['raw'][:16]==new['raw'][:16]
    assert old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
    d=dict(status='PRIVATE_FOUR_SMB3_MENU_CANDIDATE_NOT_ADMITTED',source=True,native=False,
        installed=False,publication_allowed=False,parent=h['candidate'],candidate=P.B.sha(J/'candidate.nes'),
        joint=str(J),top_level_label_PCs_preserved=len(public),changed_private_labels=private,
        CHR_byte_exact=True,Select_cycle=[0,1,2,3],menu_name_indices=[28,29,45,46],
        status_names=['MARIO3 ','LUIGI3 ',' TOAD3 ',' PEACH3'],
        storage='Existing three-byte navigation padding funds Select. Four status offsets use existing A90 palette NOPs; compact status loop plus shared spaces fits its exact prior span. New menu strings/indices extend the existing A81 names segment only.',
        limits=['Private parent64 plus Toad/Peach source work; does not contain verified Bowser66 fixes.',
            'Actual menu/ABI/foreign/interrupt and native gameplay checks required before publication.',
            'Original ground-pound/custom stomp delay, special graphics and kick sound bridge remain unfinished.'],
        bindings={str(p):P.B.sha(p) for p in [Path(__file__),H,select,names,render,status,
            J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',*logs]})
    P.B.write(O/'source-stage.json',json.dumps(d,indent=2)+'\n')
    print(json.dumps({k:v for k,v in d.items() if k!='bindings'},indent=2))


if __name__=='__main__':main()
