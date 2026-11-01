"""Execute linked roster admission, cold-cache, pose and native NMI paths."""
from pathlib import Path
import argparse,hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import check_hogan_current_bounded_v1 as C
from prepare_wwf_roster_package_bounded_v1 import decode
from check_tmnt_render_oa import address,location
from verify_native_relocation import NesMPU
J=R/'build/wwf-roster-native-1101-v1';P=R/'build/ready76-menu-fixed-v5'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def nmi(m):
    C.put(m,NmiDisable=0)
    c=NesMPU(memory=m,pc=0x5b00);c.sp=224;c.p=0x31;c.a=85;c.x=55;c.y=91
    banks=(C.get(m,'CurrentBank'),C.get(m,'CurrentBankC'))
    before=bytes(m[0x15a:0x17b]);c.nmi();low=c.sp;steps=0;music=0
    for steps in range(200000):
        if c.pc==0x5b00 and c.sp==224:break
        low=min(low,c.sp)
        if c.pc==address(m.bundle,'WfAudio_E4DE') and m.rawtags[1]==1:music+=1
        assert m[c.pc]!=0,('NMI BRK',hex(c.pc),m.rawtags,c.sp)
        c.step()
    else:raise AssertionError(('NMI return bound',hex(c.pc),c.sp))
    assert bytes(m[0x15a:0x17b])==before,'NMI changed foreground transport SMC'
    assert (c.a,c.x,c.y)==(85,55,91),'NMI changed interrupted AX/Y'
    assert (C.get(m,'CurrentBank'),C.get(m,'CurrentBankC'))==banks,'NMI changed foreground software bank owners'
    assert m.rawtags[1]==C.get(m,'CurrentBank') and m.rawtags[2]==C.get(m,'CurrentBankC'),('NMI bank restoration',m.rawtags,C.get(m,'CurrentBank'),C.get(m,'CurrentBankC'))
    return dict(cycles=c.processorCycles,minimum_SP=low,instructions=steps,original_music_ticks=music)


def ready(b,variant):
    m=C.fresh(b);C.put(m,CrossoverMenuIndex=28)
    for name in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:C.invoke(m,name)
    for _ in range(variant):
        C.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
        C.invoke(m,'CrossoverMenuInput')
    assert C.get(m,'FmGroups')&7==variant
    C.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0)
    start=C.invoke(m,'CrossoverMenuInput')
    assert C.get(m,'CrossoverMenuState')==0 and C.get(m,'FmGroups')&7==variant,'Start erased alternate identity'
    C.invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    C.invoke(m,'PauseRoutine',a=0)
    if variant&1:C.put(m,GuestAudioCharacter=29,GuestNativeEnable=15)
    for setup in range(600):
        if C.get(m,'OperMode_Task')==3 and C.get(m,'GameEngineSubroutine')==8:break
        C.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
        C.invoke(m,'GameLoop');nmi(m)
    else:raise AssertionError(('Parser/entrance bound',variant))
    assert m.ram[2][address(b,'WfHostReady')-0xc000]==167
    assert m.ram[2][0x2b]==[5,0,1,2,3,4][variant],('Original actor identity',variant,m.ram[2][0x2b])
    return m,setup


def check(b):
    parent=C.collect(C.scoped_load(P/'candidate.nes'));actual=C.collect(b)
    changes=[k for k in actual if actual[k]!=parent[k]]
    assert changes==[(28,v)for v in range(1,6)],changes
    assert sum(not x['pending']for x in actual.values())==81
    assert b['raw'][location(b,'WfAtomicRti')]==64
    blob=(J/'metadata.chr').read_bytes();offsets=(J/'wf-meta-offsets.bin').read_bytes();cookies=(J/'wf-cookies.bin').read_bytes()
    rows=[];poses=0;clamps=0
    for v in range(6):
        m,setup=ready(b,v);print('Ready variant '+str(v),flush=True)
        at=int.from_bytes(offsets[v*2:v*2+2],'little');meta=blob[at:at+1687]
        assert bytes(m.ram[2][0xa42:0xa42+1687])==meta
        assert bytes(m.ram[2][0x1fe0:0x1ff0])==cookies[16*v:16*v+16]
        assert bytes(m.ram[3][0x1fe0:0x1ff0])==cookies[16*v:16*v+16]
        # These isolated public worker calls normally run inside Main's busy
        # phase; the actual parser above has just returned and cleared it.
        C.put(m,FamilyMainCommit=1)
        assert C.invoke(m,'WfCheck')['P']&1
        for i in range(16):
            m.ram[2][0x1fe0+i]^=1
            assert not C.invoke(m,'WfCheck')['P']&1,('Poisoned cookie',v,i)
            nmi(m)
            m.ram[2][0x1fe0+i]^=1
        costs=[]
        for group in range(meta[0]+1):
            g=group if group<meta[0]else 0
            start=meta[2+2*g];end=meta[4+2*g]if g+1<meta[0]else meta[1]
            for frame in range(end-start+1):
                f=frame if frame<end-start else 0
                width,cells=decode(meta,g,f)
                for face in [0,1]:
                    m.ram[2][0x32]=group;m.ram[2][0x34]=frame;m.ram[2][0x3a]=face
                    z=C.invoke(m,'WfGraphics');assert z['P']&1
                    want=[4*len(cells)]
                    for t,r,x,y,page in cells:want.extend([t,r|(64 if face else 0),y&255,(width-x if face else x)&255])
                    out=address(b,'WfRenderBuffer')-0xc000
                    assert list(m.ram[2][out:out+len(want)])==want,('Linked pose',v,group,frame,face)
                    page=cells[0][4];physical=546+page if page<58 else 442+page-58 if page<76 else 629+page-76
                    assert C.get(m,'CurrentCHRBank')==physical&255
                    assert C.get(m,'X5ChrMode')&3==physical>>8
                    costs.append(z['CPU']);poses+=1;clamps+=group!=g or frame!=f
        # Fresh controller/parser state, without injected pose fields.
        m,_=ready(b,v);x0=C.get(m,'Player_X_Position');xs=[];ys=[];audio=[]
        for age in range(180):
            keys=(1 if 70<=age<140 else 0)|(128 if 95<=age<113 else 0)|(64 if 145<=age<149 else 0)
            C.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
            z=C.invoke(m,'GameLoop');xs.append(C.get(m,'Player_X_Position')+256*C.get(m,'Player_PageLoc'));ys.append(C.get(m,'Player_Y_Position'))
            if age<70:assert xs[-1]==x0,('Idle drift',v,age)
            assert C.get(m,'GameEngineSubroutine')!=11,('Unexpected injury',v,age)
            sound=nmi(m);assert sound['original_music_ticks']==1,('Missing own source music',v,age,sound)
            audio.append(sound['cycles'])
        assert max(xs)-min(xs)>10 and ys[90]-min(ys[95:140])>30
        rows.append(dict(variant=v,setup_Main=setup,poses=len(costs),pose_cycles=[min(costs),max(costs)],gameplay_Main=180,NMI_cycles=[min(audio),max(audio)],jump_rise=ys[90]-min(ys[95:140])))
        print(json.dumps(rows[-1]),flush=True)
    return dict(menu_identities=86,playable=81,Start_A_cases=688,admissions=changes,compiled_pose_cases=poses,fallback_cases=clamps,all_cookie_bytes_rejected=True,rows=rows)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();o=a.output.resolve();o.mkdir(exist_ok=True)
    report=dict(passed=False,source_CPU=True,native=False,candidate=sha(J/'candidate.nes'))
    try:report['checks']=check(C.scoped_load(J/'candidate.nes'));report['passed']=True
    except Exception as e:report.update(failure=repr(e),traceback=traceback.format_exc())
    report['bindings']={str(p):sha(p)for p in[Path(__file__),J/'candidate.nes',J/'candidate.dbg',J/'assembly-stage.json',Path(C.__file__)]}
    (o/'controls.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='bindings'}));assert report['passed']


if __name__=='__main__':main()
