"""Exercise the real scene consumer and Main with explicit raw34 admission.

The menu remains closed. Raw34 is assigned once after a genuine old-menu Start;
the native parser, InitScreen, collision, camera, Main and NMI then run normally
in the CPU/mapper model. This is not a native emulator/controller qualification.
"""
from pathlib import Path
import collections,hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
import check_hogan_current_bounded_v1 as C
import ff_host_pickups_vectors_v2 as V
from check_karnov_ingress_1101_v1 import endpoint
from check_tmnt_render_oa import address,location
O=R/'build/karnov-host-resource-base-1101-v1';J=R/'build/menu-wwf-compact-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
COUNTS=[7,2,2,2,2,4,2,2,2,3,3,2,2,2,3,1,4,4,4,2,2,4,1,2,8,1,2,1,6,2,4,2]
RAM=['KrConstruct','KrMovement','KrPostTerrain','KrSourceFrame','KrSourceWeapons','KrGraphics','KrDraw','KrColors']
ROM=['KrSceneInit','KrLoad','ThSceneInit','WfScene','BwScene','S2InitScreenPrepare','PlayerBGCollision','PlayerCtrlRoutine','ScrollHandler']

def invoke(m,name,observer=None,**kw):
    points={}
    for n in RAM+ROM:
        if n not in m.bundle['syms']:continue
        pc=address(m.bundle,n);tag=3 if n in RAM else((location(m.bundle,n)-16)//8192)|128;points[pc,tag]=n
    counts=collections.Counter();c=H.start(m,name,**kw)
    def hook(mem,c,i):
        if observer:observer(mem,c,i)
        if c.pc>=32768:
            n=points.get((c.pc,mem.rawtags[(c.pc-32768)//8192]))
            if n:counts[n]+=1
    c,low=H.finish(m,c,hook)
    return dict(regs=[c.a,c.x,c.y,c.p,c.sp],CPU=c.processorCycles,minimum_SP=low,counts=dict(counts))

def main():
    q=dict(passed=False,source_CPU=True,native=False,installed=False,menu_admitted=False)
    paths=[Path(__file__),O/'terrain-assembly.json',O/'candidate.nes',O/'candidate.dbg',O/'kr-kernel.bin',J/'candidate.nes',J/'candidate.dbg']
    try:
        stage=json.loads((O/'terrain-assembly.json').read_text());assert stage['passed']and stage['scene']
        q['private_menu_enabled']=stage.get('menu',False)
        for p,h in stage['bindings'].items():assert sha(p)==h,p
        old,new=[H.C.qualified(p/'candidate.nes')for p in [J,O]]
        # The exact InitScreen source replacement must only change the genuine
        # farcall immediates, not the old rendering guard or scene continuation.
        chunks=[b['raw'][location(b,'InitScreen'):location(b,'InitScreen')+48]for b in [old,new]]
        offsets=[i for i,(a,z)in enumerate(zip(*chunks))if a!=z]
        assert offsets==[12,17,22]and all(chunks[0][i-1]==chunks[1][i-1]==0xa9 for i in offsets),('Actual same-sized scene call operands',offsets)
        assert[ chunks[0][i]for i in offsets]==[address(old,'ThSceneInit')&255,address(old,'ThSceneInit')>>8,((location(old,'ThSceneInit')-16)//8192)|128]
        assert[ chunks[1][i]for i in offsets]==[address(new,'KrSceneInit')&255,address(new,'KrSceneInit')>>8,157]
        # Every existing menu identity keeps the whole old scene callback's
        # outputs. Source caches are loaded by the real old callback, not copied
        # into the fixture. The new wrapper is a foreign-owner no-op afterward.
        prefix=location(old,'ThPostNativeHot')-location(old,'HotPlayerGraphics')
        assert prefix==location(new,'ThPostNativeHot')-location(new,'HotPlayerGraphics')
        for name,size in [('HotPlayerGraphics',prefix),('HotNewCharacterDraw',226)]:
            assert old['raw'][location(old,name):location(old,name)+size]==new['raw'][location(new,name):location(new,name)+size]
        identities=0;scene_pairs=0;post_pairs=0;post_extra_cycles=set()
        for slot,total in enumerate(COUNTS):
            pair=[C.fresh(b)for b in [old,new]]
            for m in pair:C.put(m,CrossoverMenuIndex=slot);C.invoke(m,'MenuResolveCharacter');C.invoke(m,'QueueSelection')
            for variant in range(total):
                if variant:
                    for m in pair:C.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0);C.invoke(m,'CrossoverMenuInput')
                pending=[bool(C.invoke(m,'FmPending')['P']&1)for m in pair]
                if stage.get('menu')and(slot,variant)==(7,1):
                    assert pending==[True,False]and H.get(pair[1],'SelectedCharacter')==34
                    continue
                assert pending[0]==pending[1]
                if pending[1]:continue
                identities+=1;results=[];states=[]
                for m,name in zip(pair,['ThSceneInit','KrSceneInit']):
                    H.put(m,OperMode=1,FamilyMainCommit=1,DisableScreenFlag=1,Mirror_PPUMASK=0,NmiDisable=255,NumberofLives=2)
                    results.append(invoke(m,name,p=0x71))
                    states.append(([bytes(z)for z in m.ram],bytes(m[3:256]),bytes(m[0x200:0x800]),bytes(m[0x5c00:0x8000]),m.rawtags[:],H.get(m,'CurrentBankC'),m.chr_latches[:],m.ppu_reads))
                assert results[0]['regs']==results[1]['regs']and states[0]==states[1],('Old scene state/ABI',slot,variant,results,[a==z for a,z in zip(*states)])
                assert not results[1]['counts'].get('KrConstruct')and not results[1]['counts'].get('KrLoad')
                for p in [0x30,0x71,0xff]:
                    results=[]
                    for m in pair:
                        result,_,cpu=endpoint(m,'ThPostNativeHot',p);results.append((result,cpu.processorCycles))
                    assert results[0][0]==results[1][0],('Original post-BG child/AXYP/SP',slot,variant,p,results)
                    extra=results[1][1]-results[0][1];assert 4<=extra<=5,(slot,variant,'Foreign post-BG selector cost',extra)
                    post_extra_cycles.add(extra);post_pairs+=1
                scene_pairs+=1
        assert identities==85
        print('All85 real existing identities retain scene chain/ABI/RAM/maps PASS',flush=True)
        def fresh():
            m=L.make(new);H.put(m,SelectedCharacter=34,FmAlts=1);result=invoke(m,'InitScreen');assert result['counts'].get('KrConstruct')==1 and result['counts'].get('KrLoad')==1
            assert m.ram[3]==(O/'kr-kernel.bin').read_bytes()and m.ram[2][address(new,'KrReady')&8191]==167
            return m,result
        seed,first=fresh();assert seed.ppu_reads==16400
        preserved=[]
        for field,value in [(0x65,130),(0x68,128),(0x300,71),(0x400,29),(0x7fd,67)]:seed.ram[2][field]=value;preserved.append((field,value))
        for i in range(9):seed.ram[2][0x6e+3*i]=132
        H.put(seed,AreaAddrsLOffset=1,WorldNumber=1,PlayerFacingDir=2);reads=seed.ppu_reads;second=invoke(seed,'InitScreen')
        assert seed.ppu_reads==reads and second['counts'].get('KrConstruct')==1
        assert all(seed.ram[2][i]==v for i,v in preserved),'Scene transfer lost source gear/stock/health'
        assert all(seed.ram[2][0x6e+3*i]==0 for i in range(9))and seed.ram[2][0x62]==128
        assert seed.ram[2][address(new,'KrWorld')&8191]==1 and seed.ram[2][address(new,'KrArea')&8191]==1
        H.put(seed,NumberofLives=3,SavedJoypadBits=1,FrameCounter=1);r=invoke(seed,'HuMovement');assert r['regs'][3]&1 and seed.ram[2][address(new,'KrLives')&8191]==3
        assert seed.ram[2][0x65]==130
        H.put(seed,NumberofLives=2);r=invoke(seed,'InitScreen');assert r['counts'].get('KrConstruct')==1
        assert all(seed.ram[2][i]==0 for i in [0x65,0x68,0x300,0x400,0x7fd]),'Lost-life context retained gear/stock'
        H.put(seed,CurrentPlayer=1);seed.ram[2][0x65]=2;invoke(seed,'InitScreen');assert seed.ram[2][0x65]==0
        print('Real InitScreen cold/warm/area/life/extra-life boundaries PASS',flush=True)
        # Start Rygar through real menu, then explicitly assign the unadmitted
        # new runtime ID. This closes scene/Main ownership without pretending
        # the pending character is already selectable by the user.
        m=C.fresh(new);H.put(m,CrossoverMenuIndex=7)
        C.invoke(m,'MenuResolveCharacter');C.invoke(m,'QueueSelection')
        if stage.get('menu'):
            H.put(m,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0)
            C.invoke(m,'CrossoverMenuInput');C.invoke(m,'DrawSelectionPreview')
            assert H.get(m,'SelectedCharacter')==34 and H.get(m,'FmAlts')&1
        H.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0)
        C.invoke(m,'GameMenuRoutine');assert H.get(m,'OperMode')==1
        if stage.get('menu'):assert H.get(m,'SelectedCharacter')==34 and H.get(m,'FmAlts')&1
        else:H.put(m,SelectedCharacter=34,FmAlts=1)
        C.invoke(m,'PauseRoutine',a=0)
        setup=[]
        for tick in range(600):
            if H.get(m,'OperMode_Task')==3 and H.get(m,'GameEngineSubroutine')==8:break
            H.put(m,SavedJoypadBits=0,SavedJoypad1Bits=0,SavedJoypad2Bits=0,A_B_Buttons=0,Left_Right_Buttons=0,Up_Down_Buttons=0,NmiDisable=255)
            r=invoke(m,'GameLoop');setup.append(dict(tick=tick,task=H.get(m,'OperMode_Task'),screen=H.get(m,'ScreenRoutineTask'),engine=H.get(m,'GameEngineSubroutine'),Main=r));C.consume(m)
        else:raise AssertionError(('Actual scene/parser/entrance bound',setup[-1]))
        assert m.ram[3]==(O/'kr-kernel.bin').read_bytes()and m.ram[2][address(new,'KrReady')&8191]==167
        previous=V.pending_store
        def pending(mem,c,slot,op):
            if previous(mem,c,slot,op):return True
            reg=0x5115 if slot==1 else 0x5116;value={0x8d:c.a,0x8e:c.x,0x8c:c.y}.get(mem[c.pc])
            return value is not None and bytes(mem[c.pc+1:c.pc+3])==reg.to_bytes(2,'little')and value==H.get(mem,'CurrentBank'if slot==1 else'CurrentBankC')
        V.pending_store=pending
        def foreground(mem):
            fields=['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','Player_X_Scroll','Player_Pos_ForScroll','Player_Y_Speed','Player_X_Speed','FrameCounter','CurrentBank','CurrentBankC']
            return [bytes(z)for z in mem.ram],bytes(mem[0x200:0x300]),bytes(mem[3:11]),bytes(mem[0x15a:0x17b]),mem.rawtags[:],[H.get(mem,n)for n in fields]
        rows=[];main_cuts=0;minimum_ISR_SP=255;minimum_ISR_context=None
        for tick in range(120):
            keys=(1 if tick<35 else 0)|(128 if 8<=tick<28 else 0)|(64 if 80<=tick<84 else 0)
            H.put(m,SavedJoypadBits=keys,SavedJoypad1Bits=keys,SavedJoypad2Bits=0,A_B_Buttons=keys&192,Left_Right_Buttons=keys&3,Up_Down_Buttons=keys&12,NmiDisable=255)
            tracing=tick in [0,12,40,82];origin=C.fork(m)if tracing else None;trace=[]
            r=invoke(m,'GameLoop',observer=(lambda mem,c,i:trace.append((c.pc,mem.rawtags[1],mem.rawtags[2],c.sp,mem.rawtags[(c.pc-32768)//8192]if c.pc>=32768 else None)))if tracing else None)
            if tracing:
                low=min(z[3]for z in trace);positions={0,len(trace)-2,next(i for i,z in enumerate(trace)if z[3]==low)}
                for n in ['KrMovement','KrSourceFrame','KrSourceWeapons','KrPostTerrain','KrDraw','MetaspriteRenderLoop']:
                    pc=address(new,n);tag=((location(new,n)-16)//8192)|128 if n=='MetaspriteRenderLoop'else 3
                    positions.add(next(i for i,z in enumerate(trace)if z[0]==pc and z[4]==tag))
                for atcut,kind in itertools.product(sorted(positions),['IRQ','NMI']):
                    z=C.fork(origin);z.writes.clear();z.ram_writes.clear();events=[]
                    def interrupt(mem,c,i):
                        if i==atcut:events.append(V.interrupt(mem,c,kind))
                    actual=invoke(z,'GameLoop',observer=interrupt)
                    assert actual['regs']==r['regs']and actual['counts']==r['counts']and foreground(z)==foreground(m),('Actual Main interrupted resumption',tick,atcut,kind,events)
                    assert len(events)==1
                    if events[0]['minimum_SP']<minimum_ISR_SP:
                        minimum_ISR_SP=events[0]['minimum_SP'];minimum_ISR_context=dict(tick=tick,cut=atcut,kind=kind,PC=hex(trace[atcut][0]),raw_A=trace[atcut][1],raw_C=trace[atcut][2])
                    main_cuts+=1
            row=dict(tick=tick,input=keys,X=H.get(m,'Player_X_Position')+256*H.get(m,'Player_PageLoc'),Y=H.get(m,'Player_Y_Position'),state=H.get(m,'Player_State'),engine=H.get(m,'GameEngineSubroutine'),Main=r);rows.append(row)
            assert row['engine']==8,('Unexpected normal Main engine mode',row)
            for n in ['KrMovement','KrSourceFrame','KrSourceWeapons','KrPostTerrain','KrDraw','PlayerBGCollision']:
                assert r['counts'].get(n)==1,('Actual sole Main worker',n,row)
            C.consume(m)
        q['setup']=setup;q['frames']=rows
        trajectory=dict(minimum_Y=min(r['Y']for r in rows),last_Y=rows[-1]['Y'],poses=sorted({r['state']for r in rows}),samples=[(r['tick'],r['X'],r['Y'],r['state'])for r in rows if r['tick']%10==0])
        assert min(r['Y']for r in rows)<176 and rows[-1]['Y']==176,('Actual source jump/landing',trajectory)
        assert rows[0]['X']<max(r['X']for r in rows)
        q['minimum_Main_ISR_SP']=minimum_ISR_SP;q['minimum_Main_ISR_context']=minimum_ISR_context
        assert minimum_ISR_SP-0x7b>=12,('Actual live Main ISR stack needs at least twelve bytes above SMC operands',minimum_ISR_SP,minimum_ISR_context)
        q.update(passed=True,ROM_sha256=stage['ROM_sha256'],existing_identity_scene_pairs=scene_pairs,existing_post_BG_pairs=post_pairs,foreign_post_BG_extra_cycles=sorted(post_extra_cycles),InitScreen_operand_offsets=offsets,cold_scene=first,warm_scene=second,warm_area_source_fields_preserved=preserved,new_life_resets_gear=True,extra_life_keeps_movement=True,Main_runtime_assignment_fixture=not stage.get('menu',False),real_Karnov_Select_Start=stage.get('menu',False),actual_parser_updates=len(setup),actual_Main_updates=len(rows),completed_normal_NMIs=len(setup)+len(rows),actual_Main_ISR_cuts=main_cuts,minimum_Main_ISR_SP=minimum_ISR_SP,source_cold_loader_reads=16400,setup=setup,frames=rows,scope='Actual InitScreen scene consumer with original Wf/Bw/S2/Th callback chain, genuine cold cache loader and native parser/Main/NMI in CPU/mapper model. All85 old menu identity scene outputs exact. With menu mode, real Select and Start retain raw34 with no runtime assignment; otherwise the historical explicit assignment fixture is used. Source stock/health/gear fields in lifecycle checks are deliberate fixtures. Live Main IRQ/forced-blank NMI cuts supplement complete normal NMI executions between updates. No earned item, native emulator/controller/raster/playthrough, combat, audio or nightly claim.')
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
    q['bindings']={str(p.resolve()):sha(p)for p in paths}
    (O/'scene-CPU-controls.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','traceback','setup','frames']}));assert q['passed'],q.get('error')

if __name__=='__main__':main()
