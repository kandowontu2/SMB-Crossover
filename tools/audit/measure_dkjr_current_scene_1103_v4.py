"""Real InitScreen -> common cold -> scene36 DK40 admission proposal.

Preserves the frozen101 manager and all compiled private90 inputs. The only
proposed scene change is the existing source CMP3 immediate becoming4.
"""
from pathlib import Path
import collections,json,sys
import check_dkjr_current_menu_1103_v3 as UI
import measure_dkjr_prince_owner_1103_v101 as P
import check_dkjr_entrance_order_1103_v88 as E
import check_prince_strike_cold_1103_v131 as C
V,N,F,R,O=UI.V,UI.N,UI.F,UI.R,UI.O
address,location,off,sha=UI.address,UI.location,UI.off,UI.sha


def stage():
    base,q=P.image();raw=bytearray(base['raw']);frontend=json.loads((R/'docs/qa/allocations/prince-current-frontend-1103-v105.json').read_text())
    for row in frontend['approved_exact_patches']:
        at=row['file_offset'];before=bytes.fromhex(row['old_hex']);after=bytes.fromhex(row['new_hex']);assert raw[at:at+len(before)]==before;raw[at:at+len(after)]=after
    ui=json.loads((O/'current-menu-v2.json').read_text())
    for row in ui['patches']:
        at=row['file_offset'];before=bytes.fromhex(row['old_hex']);after=bytes.fromhex(row['new_hex']);assert raw[at:at+len(before)]==before;raw[at:at+len(after)]=after
    text='''.setcpu "6502"
SelectedCharacter=$6002
.segment "SCENE"
.export CoSceneGate,CoSceneGateEnd
CoSceneGate:
 php
 pha
 lda SelectedCharacter
 sec
 sbc #37
 cmp #3
 bcc CoSceneGate+($b062-$b013)
 pla
 plp
 jmp $ac1d
 .res 2,$ea
CoSceneGateEnd:
'''
    cfg='MEMORY{S:start=$b013,size=19,file=%O;}SEGMENTS{SCENE:load=S,type=ro;}'
    old,L=UI.B.assemble('current-scene-old-v4',text,cfg);at=off(65,0xb013);assert old==raw[at:at+19]
    new,L=UI.B.assemble('current-scene-new-v4',text.replace('cmp #3','cmp #4'),cfg)
    changes=[i for i,(a,z)in enumerate(zip(old,new))if a!=z];assert changes==[9] and old[9]==3 and new[9]==4
    before=dict(base,raw=bytes(raw));raw[at:at+19]=new
    return before,dict(base,raw=bytes(raw)),q,dict(physical_PRG=65,CPU_half_open=[0xb01c,0xb01d],file_offset=at+9,old_hex='03',new_hex='04',role='Actual19B CoSceneGate source bounded37..39 becomes37..40; no new code/data extent, foreign tail/frames unchanged')


def endpoint(base,owner,p):
    m=N.Bus(base);m.raw_page(1,193);N.put(m,CurrentBank=193,SelectedCharacter=owner)
    c=N.NesMPU(memory=m,pc=0xb013);c.a=83;c.x=71;c.y=109;c.p=p;c.sp=224
    for _ in range(20):
        if c.pc in [0xb062,0xac1d]:break
        c.step()
    else:raise AssertionError('Scene gate endpoint')
    return dict(PC=c.pc,A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,stack=list(m[0x1de:0x1e1]),maps=m.rawtags[:],SMC=list(m[0x15a:0x17b]))


def main():
    before,after,manager,patch=stage();parity=0;own=[]
    for owner in range(256):
        for p in [0x20,0x21,0x30,0x31,0x70,0xf1]:
            a,b=endpoint(before,owner,p),endpoint(after,owner,p)
            if owner!=40:assert a==b;parity+=1
            else:assert a['PC']==0xac1d and b['PC']==0xb062;own.append(dict(P=p,old=a['PC'],new=b['PC']))
    # Use the established exact MMC5 PPU-readback model. Cold is reached from
    # native InitScreen, never directly from CoCold or public scene36.
    C.N.Bus=C.C.C.C.V.ControllerBus
    m=N.fresh(after);C.fields(m,40)
    for bank in [2,3]:m.ram[bank][:]=bytes([0x9d])*8192;m.ram[bank][0x1fe0:0x1ff0]=bytes(16)
    N.put(m,Player_X_Position=0,Player_Y_Position=0,Player_Y_HighPos=0,GameEngineSubroutine=0,ScreenRoutineTask=0,VRAM_Buffer1_Offset=0)
    needed=['InitScreen','HuFresh','Entrance_GameTimerSetup','PlayerEntrance','GameCoreRoutine'];points=collections.Counter();chain=[]
    pcs={(0xb013,193):'CoSceneGate',(0xb062,193):'ExSceneOwn',(0xae00,193):'CoCold',(0xb0f8,193):'public_scene36',(0xb0b9,193):'public_Fresh15'}
    L=json.loads((P.O/'native-entrance-v89-layout.json').read_text())['labels']
    for name in ['DkjrInitialize','DkjrNativeFresh','DkNativeMain','DkPauseThaw']:
        if name in L:pcs[L[name],3 if L[name]<0xc000 else 2]=name
    def watch(c):
        if c.pc>=0x8000:
            name=pcs.get((c.pc,c.memory.rawtags[(c.pc-0x8000)//8192]))
            if name:points[name]+=1
    init=F.invoke(m,'InitScreen',watch=watch)
    cookie=(P.O/'native-cookie-v90.bin').read_bytes();assert bytes(m.ram[2][0x1fe0:0x1ff0])==bytes(m.ram[3][0x1fe0:0x1ff0])==cookie
    assert points['CoSceneGate']and points['ExSceneOwn']and points['CoCold']and points['public_scene36']
    assert m.ram[2][0x8fe]==1 and N.get(m,'Player_Y_Position')==0 and N.get(m,'Player_Y_HighPos')==0
    chain.append(dict(stage='actual_InitScreen_cold_scene36',ready=1,post_constructor_nativeY=0,events=dict(points)))
    N.put(m,PlayerEntranceCtrl=2,AltEntranceControl=0,JoypadOverride=0,AreaType=1,AreaPointer=0,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,ScreenRight_X_Pos=255,ScreenRight_PageLoc=0,GameTimerSetting=1,FetchNewGameTimerFlag=1)
    F.invoke(m,'HuFresh',watch=watch);assert m.ram[2][0x8fe]==1
    F.invoke(m,'Entrance_GameTimerSetup',watch=watch);F.invoke(m,'PlayerEntrance',watch=watch);assert N.get(m,'GameEngineSubroutine')==8
    for name in ['Block_Buffer_1','Block_Buffer_2']:
        at=address(after,name);m[at:at+208]=bytes(208)
        for row in [11,12]:m[at+row*16:at+row*16+16]=bytes([0x54])*16
    for slot in range(6):m[address(after,'Enemy_Flag')+slot]=0
    N.put(m,DisableScreenFlag=0,Mirror_PPUMASK=30,TimerControl=0,FrameCounter=1,SavedJoypadBits=0,SavedJoypad1Bits=0,VRAM_Buffer1_Offset=0,OperMode_Task=3);m[0x2001]=30
    F.invoke(m,'GameCoreRoutine',watch=watch);last=E.snapshot(m)
    assert (last['nativeX'],last['nativeY'],last['nativeHighY'],last['sourceX'],last['sourceY'],last['ready'])==(40,176,1,32,191,2),last
    chain.append(dict(stage='genuine_entrance_and_first_actual_engine8',**last,events=dict(points)))
    # Actual global reset follows B0C5->B100->CoRetire. No private opcode may
    # be required after its authenticated headers are invalidated.
    F.invoke(m,'HuReset',watch=watch);assert m.ram[2][0x1fe0]==m.ram[3][0x1fe0]==0 and N.get(m,'SelectedCharacter')==40
    q=dict(passed=True,source_proposal_only=True,ROM_written=False,menu_admitted=False,native_qualified=False,combined101_input_SHA256=manager['expected_memory_only_SHA256'],frontend105_preserved=True,frontend_v2_preserved=True,pre_scene_memory_SHA256=sha(before['raw']),expected_memory_only_SHA256=sha(after['raw']),scene_patch=patch,scene_grant_required=True,foreign_scene_endpoint_AXYP_SP_maps_SMC_cases=parity,intended40_cases=own,actual_chain=chain,actual_reset_retire_headers_invalidated_identity_retained=True,direct_scene36_scope_correction='Frozen100/97 publicB0F8 fixture proves private scene behavior after caller admission. It did not execute native InitScreen classification, which remains CMP3 in101/83. This distinct source proposal qualifies CMP4 from actual InitScreen before real entrance; it does not rewrite those earlier receipts.',remaining=['Actual scene active/forcedblank/cookie-poison/previous-owner retirement/lifecycle/IRQ+FF+nested proof on finalcombined source remains necessary.','No shared native/menu grant, native capture, life/respawn/stage/GameSelect/full1-1 or helper claim.'],bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),Path(P.__file__),Path(UI.__file__),P.O/'native-combined-owner-v101-measurement.json',P.O/'native-entrance-ready-v100.json',O/'current-menu-v2.json',O/'current-menu-v3-CPU.json',R/'tools/audit/prepare_prince_public_routes_1102_v24.py',R/'src/screen_render.s']})
    (O/'current-scene-v4-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','intended40_cases']}))


if __name__=='__main__':
    try:main()
    except Exception as e:
        (O/'current-scene-v4-negative.json').write_text(json.dumps(dict(passed=False,exception=repr(e)),indent=2)+'\n');raise
