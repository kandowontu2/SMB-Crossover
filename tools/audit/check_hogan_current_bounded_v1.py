"""Dependency-small, real-code menus and Main checks; no historical fixture trees."""
from pathlib import Path
import argparse,ast,copy,hashlib,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import Memory,address,location
from verify_native_relocation import NesMPU

P=R/'build/contra-force-projectile-contact-1031-v3/joint'
J=R/'build/hogan-current'
O=J/'checks'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
# Reuse the exact established peripheral model without executing its old
# demonstration imports/default-ROM loads. No source files are extracted.
model=R/'tools/audit/arthur_cache_host_controls_v1.py'
node=next(n for n in ast.parse(model.read_text()).body if isinstance(n,ast.ClassDef)and n.name=='OverlayMemory')
namespace={'Memory':Memory}
exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(model),'exec'),namespace)
Bus=namespace['OverlayMemory']


def put(m,**fields):
    for name,value in fields.items():m[address(m.bundle,name)]=value


def get(m,name,i=0):return m[address(m.bundle,name)+i]


def invoke(m,name,*,a=85,x=7,y=91,p=0x31):
    target=address(m.bundle,name)
    put(m,**{})
    m[address(m.bundle,'SafecallA_SMC')+1]=a
    m[address(m.bundle,'FarcallJmpTarget_SMC')+1]=target&255
    m[address(m.bundle,'FarcallJmpTarget_SMC')+2]=target>>8
    c=NesMPU(memory=m,pc=address(m.bundle,'FarCallCommon'))
    c.a=((location(m.bundle,name)-16)//8192)|128;c.x=x;c.y=y;c.p=p;c.sp=224;c.stPushWord(0x5aff)
    counts={};low=c.sp
    points={}
    for n in ['WfMovement','WfHostFrame','WfDrawBody','ShellOrBlockDefeat','ScrollHandler']:
        if n in m.bundle['syms']:
            pc=address(m.bundle,n)
            tag=(2 if pc>=0xc000 else 224)if n.startswith('Wf')else((location(m.bundle,n)-16)//8192)|128
            points[pc,tag]=n
    for _ in range(500000):
        if c.pc==0x5b00:break
        low=min(low,c.sp)
        if c.pc>=0x8000:
            n=points.get((c.pc,m.rawtags[(c.pc-0x8000)//8192]))
            if n:counts[n]=counts.get(n,0)+1
        assert m[c.pc]!=0,('Actual linked BRK',name,hex(c.pc),m.rawtags)
        c.step()
    else:raise AssertionError(('Bounded source call',name,hex(c.pc)))
    assert c.sp==224
    return dict(A=c.a,X=c.x,Y=c.y,P=c.p,CPU=c.processorCycles,minimum_SP=low,counts=counts)


def fresh(b):
    m=Bus(b)
    put(m,OperMode=0,DisableScreenFlag=0,Mirror_PPUMASK=24,Mirror_PPUCTRL=160,NmiDisable=255,
        FamilyMainCommit=1,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,SelectedCharacter=0)
    m.ppuctrl=160
    invoke(m,'PrimaryGameSetup')
    put(m,SelectedCharacter=0,CrossoverMenuState=2,CrossoverMenuButtons=0,CrossoverContinue=0,
        SavedJoypad1Bits=0,SavedJoypad2Bits=0,OperMode=0,DisableScreenFlag=0,
        Mirror_PPUMASK=24,Mirror_PPUCTRL=160,NmiDisable=255,FamilyMainCommit=1,VRAM_Buffer1_Offset=0)
    return m


def fork(m):
    n=list.__new__(type(m));list.extend(n,list.__iter__(m))
    for k,v in m.__dict__.items():setattr(n,k,v if k=='bundle'else copy.deepcopy(v))
    return n


def collect(b):
    counts=[7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,4,1,2,1,6,2,4,2]
    rows={}
    for slot,count in enumerate(counts):
        m=fresh(b);put(m,CrossoverMenuIndex=slot)
        invoke(m,'MenuResolveCharacter');invoke(m,'QueueSelection')
        for v in range(count):
            if v:
                put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
                invoke(m,'CrossoverMenuInput')
            actual=get(m,'MarioVariant')if slot==0 else v
            pending=bool(invoke(m,'FmPending')['P']&1)
            rows[slot,actual]=dict(raw=get(m,'SelectedCharacter'),pending=pending)
            for key in [16,128]:
                for flags in [0x30,0x31,0x71,0xf1]:
                    n=fork(m);put(n,CrossoverMenuButtons=0,SavedJoypad1Bits=key,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
                    invoke(n,'CrossoverMenuInput',p=flags)
                    assert (get(n,'CrossoverMenuState')==0)!=pending,(slot,v,key,flags)
    assert len(rows)==86
    return rows


def consume(m):
    put(m,NmiDisable=0)
    c=NesMPU(memory=m,pc=0x5b00);c.sp=224;c.p=0x31
    smc=bytes(m[0x15a:0x17b]);c.nmi()
    for _ in range(200000):
        if c.pc==0x5b00 and c.sp==224:break
        assert m[c.pc]!=0,('Actual NMI BRK',hex(c.pc));c.step()
    else:raise AssertionError('Actual NMI return bound')
    assert bytes(m[0x15a:0x17b])==smc


def gameplay(b,route=False):
    m=fresh(b);put(m,CrossoverMenuIndex=28)
    for n in ['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:invoke(m,n)
    assert get(m,'SelectedCharacter')==29
    put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0,CrossoverMenuButtons=0)
    start=invoke(m,'CrossoverMenuInput')
    invoke(m,'NativeRareGameMenuRoutineCore::ChkContinue',a=start['A'],x=start['X'],y=start['Y'],p=start['P'])
    invoke(m,'PauseRoutine',a=0)
    for setup in range(600):
        if get(m,'OperMode_Task')==3 and get(m,'GameEngineSubroutine')==8:break
        put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
        invoke(m,'GameLoop');consume(m)
    else:raise AssertionError('Actual parser/entrance bound')
    assert any(m[address(b,'Block_Buffer_1'):address(b,'Block_Buffer_1')+416])
    assert m.ram[2][address(b,'WfHostReady')-0xc000]==167 and m.ppu_reads==49200
    rows=[]
    defeats=0;camera=0
    for age in range(650 if route else 180):
        if age<180:
            keys=(1 if 70<=age<140 else 0)|(128 if 95<=age<113 else 0)|(64 if 145<=age<149 else 0)
        else:
            x=get(m,'Player_X_Position')+256*get(m,'Player_PageLoc')
            near=any(0<get(m,'Enemy_Flag',i)<128 and get(m,'Enemy_ID',i)==6 and not get(m,'Enemy_State',i)&32 and
                     0<get(m,'Enemy_X_Position',i)+256*get(m,'Enemy_PageLoc',i)-x<=40 for i in range(6))
            keys=(64 if age%18<2 else 0)if near else 1
        put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
        result=invoke(m,'GameLoop')
        camera=get(m,'ScreenLeft_X_Pos')+256*get(m,'ScreenLeft_PageLoc')
        defeats+=result['counts'].get('ShellOrBlockDefeat',0)
        row=dict(age=age,input=keys,X=get(m,'Player_X_Position')+256*get(m,'Player_PageLoc'),Y=get(m,'Player_Y_Position'),camera=camera,action=m.ram[2][0x3c],execution=result)
        rows.append(row)
        if age<70:assert row['X']==rows[0]['X'],'Idle drift'
        assert get(m,'GameEngineSubroutine')!=11,'Unexpected natural injury'
        if not get(m,'TimerControl'):
            assert result['counts'].get('WfMovement')==result['counts'].get('WfHostFrame')==result['counts'].get('WfDrawBody')==1
        consume(m)
        if route and age>=180 and camera>=257 and defeats:break
    assert max(x['X']for x in rows)-min(x['X']for x in rows)>10
    rise=rows[90]['Y']-min(x['Y']for x in rows[95:140]);assert rise>30
    assert any(x['action']==15 for x in rows[145:])
    if route:assert camera>=257 and defeats,('Source route/camera/contact bound',row,defeats)
    return dict(parser_Main=setup,gameplay_Main=len(rows),normal_NMI=setup+len(rows),jump_rise=rise,source_punch_seen=True,native_defeat_calls=defeats,maximum_camera=max(x['camera']for x in rows),rows=rows)


def main():
    global J,O
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--joint',type=Path,default=J)
    ap.add_argument('--output',type=Path,default=O)
    ap.add_argument('--route',action='store_true')
    args=ap.parse_args();J=args.joint.resolve();O=args.output.resolve()
    assert O.is_relative_to(R/'build')and O!=R/'build'
    if O.exists():
        assert {p.name for p in O.iterdir()}=={'controls.json'}
        assert not json.loads((O/'controls.json').read_text())['passed']
        output=O/'controls-successor.json'
    else:O.mkdir();output=O/'controls.json'
    report=dict(passed=False,source_CPU=True,native=False)
    try:
        old,new=scoped_load(P/'candidate.nes'),scoped_load(J/'candidate.nes')
        before,after=collect(old),collect(new)
        assert sum(not q['pending']for q in before.values())==74
        for key,row in before.items():
            if key!=(28,0):assert after[key]==row,('Foreign roster changed',key)
        assert before[28,0]['pending']and not after[28,0]['pending']
        assert all(after[28,i]['pending']for i in range(1,6))
        assert sum(not q['pending']for q in after.values())==75
        report['menu']=dict(profiles=86,Start_A_cases=688,private_playable=75,only_new_identity='Hulk Hogan',other_five_WWF_pending=True)
        report['gameplay']=gameplay(new,args.route)
        report['passed']=True
    except Exception as error:
        report.update(error=repr(error),traceback=traceback.format_exc());raise
    finally:
        report.update(candidate=sha(J/'candidate.nes'),scope='Finite real binary CPU scenes and declared mapper/PPU peripheral model. No native, full-level, audio or endurance qualification.',bindings={str(p):sha(p)for p in[Path(__file__),model,J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',P/'candidate.nes']})
        output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items()if k not in ['bindings','gameplay','traceback']}))


if __name__=='__main__':main()
