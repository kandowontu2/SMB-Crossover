"""Genuine four-class menu/Start/native entrance/Main sequence, no RAM preload.

This is an explicit CPU scene/controller-byte fixture, not a native controller
replay. Initial native state is projected from the existing legal scene setup;
all FF code comes only from the actual forced-blank buffered cartridge loader.
"""
from pathlib import Path
import collections,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_fx_epoch_heartbeat_controls_v8 as A
import dragon_power_gameplay_controls_v1 as D
from check_tmnt_render_oa import address,location
H,E,T,L=A.H,A.E,A.T,A.L
N=R/'build/ff-current-ready-v2';H.O=N/'joint'


def invoke(m,name,**kwargs):
    old=m.rawtags[:];events=[];ram=[]
    names=['IcGlobalInit','SunnyGlobalInit','QwBoot','ArGenResolve','QwMenuResolve',
        'FwMuxMenuResolve','FwMuxMenuA','ArGenSceneInit','QwSceneInit','FwSceneInit',
        'FwLoad','FwEnsure','FwAreaReset','MoveAllSpritesOffscreen','FwSvcMovement',
        'FfMovement','FfHostWeapons','FfWeapons','FfHostDrawShots','FfGraphics',
        'FwSvcFeet','FwSvcSide','FwSvcHead','FwSvcWall','FwGenAfterTerrain']
    points={}
    for n in names:
        pc=address(m.bundle,n);tag=3 if n.startswith('Ff')else((location(m.bundle,n)-16)//8192)|128
        points[(pc,tag)]=n
    def observe(mem,c,i):
        if not 0x8000<=c.pc<0xe000:return
        tag=mem.rawtags[(c.pc-0x8000)//8192]
        if tag in[1,2,3]:ram.append([i,c.pc,tag])
        if(c.pc,tag)in points:events.append([i,points[(c.pc,tag)]])
    c=H.start(m,name,**kwargs);live=bytes(m[0x1e1:0x200]);c,low=H.finish(m,c,observe)
    assert c.sp==224 and bytes(m[0x1e1:0x200])==live
    assert m.rawtags[1]==old[1]and H.get(m,'CurrentBank')==old[1]
    assert m.rawtags[2]==H.get(m,'CurrentBankC')
    return dict(entry=name,AXYP_SP=[c.a,c.x,c.y,c.p,c.sp],CPU=c.processorCycles,
        minimum_SP=low,counts=dict(collections.Counter(n for _,n in events)),events=events,
        source_RAM_instructions=len(ram),PPU_reads=m.ppu_reads,
        Selected=H.get(m,'SelectedCharacter'),variant=H.get(m,'FfVariant'),
        X=H.get(m,'Player_X_Position'),Y=H.get(m,'Player_Y_Position'))


def fresh(b,variant):
    q=D.setup(b,22);m=H.make(b)
    # Native legal-scene inputs only. No RAM1/2/3 code/cache data is supplied.
    for a in list(range(0x800))+list(range(0x5c00,0x6000)):list.__setitem__(m,a,q.m[a])
    m.ram[0][:]=bytes(q.m[a]for a in range(0x6000,0x8000))
    for a in range(0x6000,0x8000):list.__setitem__(m,a,q.m[a])
    H.put(m,SelectedCharacter=0,CurrentBank=m.rawtags[1],CurrentBankC=m.rawtags[2],
        OperMode=0,DisableScreenFlag=0,Mirror_PPUMASK=24,Mirror_PPUCTRL=160,NmiDisable=255,
        FamilyMainCommit=1,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
    m.ppuctrl=160
    invoke(m,'PrimaryGameSetup')
    H.put(m,SelectedCharacter=0,FfVariant=variant,CrossoverMenuIndex=21,CrossoverMenuState=2,
        CrossoverMenuButtons=0,CrossoverContinue=0,OperMode=0,DisableScreenFlag=0,
        Mirror_PPUMASK=24,Mirror_PPUCTRL=160,NmiDisable=255,FamilyMainCommit=1,
        SavedJoypad1Bits=0,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0)
    return m


def four_classes(b):
    rows=[]
    for variant in range(4):
        m=fresh(b,variant);steps=[]
        for name in['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:
            z=invoke(m,name);steps.append(z)
            assert z['Selected']==22 and z['variant']==variant
            assert z['PPU_reads']==0 and z['source_RAM_instructions']==0,('cold menu source execution',variant,z)
        assert H.get(m,'FfVariant')==variant
        # The real Start handler preserves the selected class across actual
        # inventory/new-game resets and post-Ice constructors.
        H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0)
        start=invoke(m,'CrossoverMenuInput');steps.append(start)
        assert start['AXYP_SP'][0]==16 and H.get(m,'CrossoverMenuState')==0
        assert start['Selected']==22 and start['variant']==variant
        assert start['source_RAM_instructions']==0 and m.ppu_reads==0
        assert start['counts'].get('IcGlobalInit')==1 and start['counts'].get('SunnyGlobalInit')==1
        H.put(m,OperMode=1,OperMode_Task=0,DisableScreenFlag=1,Mirror_PPUMASK=0,
            NmiDisable=255,FamilyMainCommit=1)
        for name in['LoadAreaPointer','InitializeArea']:steps.append(invoke(m,name))
        H.put(m,ScreenRoutineTask=0,VRAM_Buffer1_Offset=0)
        scene=invoke(m,'InitScreen');steps.append(scene)
        for name in['QwSceneInit','ArGenSceneInit','FwSceneInit','MoveAllSpritesOffscreen']:
            assert scene['counts'].get(name)==1,('actual scene chain',variant,name,scene)
        H.exact(m)
        assert m.ppu_reads==16400 and H.get(m,'FfReady')==247 and H.get(m,'FfVariant')==variant
        assert H.get(m,'SmFreezeLastBlue')==128 and H.get(m,'SmFreezePalettePending')==192
        # Run the actual complete native screen/area parser and entrance.
        # The v1 fixture skipped this stage and therefore removed its floor.
        native_setup=[]
        for tick in range(600):
            if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
            H.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,
                A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255,FamilyMainCommit=1)
            z=invoke(m,'GameLoop');flush=A.consume(m)
            native_setup.append(dict(tick=tick,mode_task=H.get(m,'OperMode_Task'),
                screen_task=H.get(m,'ScreenRoutineTask'),engine=H.get(m,'GameEngineSubroutine'),
                CPU=z['CPU'],normal_NMI=flush))
        else:raise AssertionError(('actual screen/entrance bound',variant,native_setup[-8:]))
        assert H.get(m,'GameEngineSubroutine')==8 and H.get(m,'OperMode_Task')==3
        block=address(b,'Block_Buffer_1');assert any(m[block:block+416]),'Genuine native area parser did not construct world cells'
        frames=[]
        for age in range(32):
            keys=1|(128 if 4<=age<12 else 0)|(64 if 16<=age<24 else 0)
            H.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,
                A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=0,
                NmiDisable=255,FamilyMainCommit=1)
            z=invoke(m,'GameLoop')
            assert z['Selected']==22 and z['variant']==variant
            assert z['counts'].get('FfMovement')==1,('actual FF movement once',variant,age,z)
            assert z['counts'].get('FfWeapons')==1,('actual source weapon update once',variant,age,z)
            assert z['counts'].get('FfHostDrawShots')==1,('actual early source draw once',variant,age,z)
            assert H.get(m,'NmiDisable')==0 and not H.get(m,'MmDeathFlag')
            H.exact(m)
            flush=A.consume(m)
            frames.append(dict(age=age,input=keys,**z,actual_pose=H.get(m,'FfPose'),
                action=H.get(m,'FfAction'),fresh=H.get(m,'FfFresh'),jump=H.get(m,'FfJump'),
                normal_NMI=flush,projectiles=[m[address(b,'FfProjectile')+i]for i in[0,12,24]]))
        assert max(r['X']for r in frames)>min(r['X']for r in frames),('no actual source movement',variant)
        assert any(r['jump']for r in frames),('no actual source jump',variant)
        assert any(r['action']for r in frames),('no actual source attack input',variant)
        rows.append(dict(variant=variant,steps=steps,actual_native_screen_and_entrance=native_setup,Main=frames))
    return dict(classes=len(rows),actual_Main_updates=sum(len(r['Main'])for r in rows),rows=rows,
        FF_RAM3_never_preloaded=True,actual_source_movement_weapons_earlydraw_once=True)


def main():
    p=dict(passed=False,native=False,admitted=False,installed=False,source_CPU_fixture=True,checks={})
    try:
        b=H.C.qualified(N/'joint/candidate.nes')
        p['checks']['four_class_cold_sequence']=four_classes(b)
        p['passed']=True
    except Exception as e:p.update(error=repr(e),traceback=traceback.format_exc())
    files=[Path(__file__),Path(A.__file__),Path(E.__file__),Path(D.__file__),Path(H.__file__),
        N/'source-closure.json',N/'joint/candidate.nes',N/'joint/candidate.dbg']
    p['bindings']={str(f.resolve()):L.sha(f)for f in files if f.exists()}
    out=N/('cold-controls-v2.json'if p['passed']else'cold-negative-v2.json');assert not out.exists()
    out.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=p['passed'],path=str(out),error=p.get('error'))),flush=True);assert p['passed']


if __name__=='__main__':main()
