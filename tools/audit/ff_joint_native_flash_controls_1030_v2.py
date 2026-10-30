"""Native FF flash, unchanged foreign draw outputs and exact interrupt frames."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_joint_body_palette_controls_1030_v1 as P
import ff_host_pickups_vectors_v2 as V
from ff_wram_host_isr_v4 import clone
from check_tmnt_render_oa import address,location
H=P.H;M=P.M;sha=P.sha
OLD=R/'build/ff-joint-body-palette-1030-v2'
O=R/'build/ff-joint-native-flash-1030-v1';H.O=O/'joint'


def seed(b,selected=22):
    m=P.seed(b)
    H.put(m,SelectedCharacter=selected,CurrentOAMOffset=0,PlayerOutlinesOff=1,
          SmFreezeRenderState=0,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0,TimerControl=0,
          GamePauseStatus=0,MmDeathFlag=0,RgDrawFirst=0,GuestOamRotationActive=0)
    for n,count in [('ObjectMetasprite',24),('Enemy_Flag',6),('Enemy_ID',6),
                    ('Enemy_State',6),('MmEnemyFlash',6),('AvFrozen',6),('AvFrozenHi',6)]:
        for i in range(count):m[address(b,n)+i]=0
    m[512:768]=[248,0,0,0]*64
    return m


def enemy(m,slot=0,flash=0,bowser=False,duplicate=False):
    b=m.bundle
    for n,v in [('Enemy_Flag',1),('Enemy_ID',address(b,'Bowser')if bowser else 6),
                ('Enemy_PageLoc',0),('Enemy_X_Position',150+slot*5),('Enemy_Y_Position',160),
                ('Enemy_Y_HighPos',1),('Enemy_SprAttrib',3),('MmEnemyFlash',flash)]:
        m[address(b,n)+slot]=v
    if duplicate:
        assert slot>0
        m[address(b,'Enemy_Flag')+slot]=0x80
        m[address(b,'Enemy_ID')]=address(b,'Bowser')
        m[address(b,'Enemy_Flag')]=1
        m[address(b,'MmEnemyFlash')]=flash
    return address(b,'METASPRITE_GOOMBA_WALKING_1')


def signature(m,c):
    # All33 SMC operands describe each genuine transport's current call, not
    # a callee's persistent application state. They are asserted live at ISR.
    exclude=set(range(0x100,0x200))|set(range(0x5114,0x5118))|{
        address(m.bundle,'CurrentBank'),address(m.bundle,'CurrentBankC')}
    state=bytes(m[i]for i in range(0x8000)if i not in exclude)
    writes=[(a,v)for a,v in m.writes if a not in exclude]
    return state,writes,(c.a,c.x,c.y,c.p,c.sp),m.rawtags[:],[bytes(x)for x in m.ram]


def flash(b):
    base=seed(b);rows=[]
    for slot,age,dup in itertools.product(range(6),range(25),[0,1]):
        if dup and slot==0:continue
        pair=[]
        for selected in [4,22]:
            m=P.duplicate(base);H.put(m,SelectedCharacter=selected)
            meta=enemy(m,slot,age,bowser=bool(dup),duplicate=bool(dup))
            c,_=H.invoke(m,'DrawMetasprite',x=meta,y=slot+1)
            # Source-native Link already has the exact same native flash
            # calculation, duplicate ownership and completed actor span.
            pair.append((bytes(m[512:768]),H.get(m,'CurrentOAMOffset'),H.get(m,'R3'),
                         (c.a,c.x,c.y,c.p,c.sp),m.rawtags[:]))
        assert pair[0]==pair[1],('FF must use genuine native flash',slot,age,dup,pair)
        if age:
            want=[2,1,2,3][((24-age)//2+1)&3]
            assert pair[1][2]&3==want and pair[1][2]&8
        rows.append([slot,age,dup,pair[1][1],pair[1][2]])
    return dict(passed=True,actual_FF_vs_native_Link_actor_pairs=len(rows),rows=rows,
                native_flash_colors_and_validated_Bowser_rear_ownership_exact=True)


def foreign_actor(old,new):
    seeds=[seed(old),seed(new)];rows=[]
    for selected,slot,age,p in itertools.product([n for n in range(33)if n!=22],[0,5],[0,12],[0x30,0x71]):
        pair=[];cost=[]
        for b,base in zip([old,new],seeds):
            m=P.duplicate(base);H.put(m,SelectedCharacter=selected)
            meta=enemy(m,slot,age);m.writes.clear();m.ram_writes.clear()
            c,_=H.invoke(m,'DrawMetasprite',x=meta,y=slot+1,p=p)
            pair.append(signature(m,c));cost.append(c.processorCycles)
        assert pair[0]==pair[1],('foreign actual actor',selected,slot,age,p)
        assert cost[1]-cost[0]==(0 if selected==address(new,'CHARACTER_LINK') else 7),('actual native Link bypass vs new probe',selected,cost)
        rows.append([selected,slot,age,p,cost[1]-cost[0]])
    return dict(passed=True,actual_foreign_actor_pairs=len(rows),rows=rows,extra_CPU_per_actor_range=[0,7],native_Link_direct_bypass_CPU=0,
                all_application_state_ordered_writes_AXYP_SP_OAM_and_maps_exact=True)


def drawall(old,new):
    seeds=[seed(old),seed(new)];rows=[]
    for selected,freeze,offset in itertools.product([n for n in range(33)if n!=22],[0,1],[0,64]):
        if freeze and selected!=2:continue
        pair=[];cost=[]
        for b,base in zip([old,new],seeds):
            m=P.duplicate(base);H.put(m,SelectedCharacter=selected,SmFreezeRenderState=freeze,
                                    CurrentOAMOffset=offset,SpriteShuffleOffset=1)
            meta=enemy(m,0,12)
            m[address(b,'ObjectMetasprite')+1]=meta
            m.writes.clear();m.ram_writes.clear()
            c,_=H.invoke(m,'SamusFreezeDrawAll')
            pair.append(signature(m,c));cost.append(c.processorCycles)
        assert pair[0]==pair[1],('foreign genuine complete DrawAll',selected,freeze,offset)
        rows.append([selected,freeze,offset,cost[0],cost[1],cost[1]-cost[0]])
    return dict(passed=True,actual_complete_foreign_DrawAll_pairs=len(rows),rows=rows,
                extra_CPU_range=[min(r[-1]for r in rows),max(r[-1]for r in rows)],
                actual_Samus_freeze_and_original_return_contract_exact=True)


def whole_main(old,new):
    seeds=[M.setup(old),M.setup(new)];rows=[]
    for selected,face,joy in itertools.product([0,1,2,3,4,11],[1,2],[0,1]):
        pair=[];cost=[]
        for b,base in zip([old,new],seeds):
            m=P.duplicate(base);H.put(m,SelectedCharacter=selected,PlayerFacingDir=face,
                SavedJoypadBits=joy,Left_Right_Buttons=joy,A_B_Buttons=0,VRAM_Buffer1_Offset=0,
                NmiDisable=255,SmFreezeRenderState=0)
            m.writes.clear();m.ram_writes.clear()
            c,_=M.invoke_main(m,lambda *_:None)
            pair.append(signature(m,c));cost.append(c.processorCycles)
        assert pair[0]==pair[1],('foreign complete Main',selected,face,joy)
        rows.append([selected,face,joy,cost[1]-cost[0]])
    return dict(passed=True,actual_complete_foreign_Main_pairs=len(rows),rows=rows,
                legal_offline_scene_fixture_not_native_campaign=True,
                extra_CPU_range=[min(r[-1]for r in rows),max(r[-1]for r in rows)])


def isr(b):
    base=seed(b);snapshots=[]
    for selected,freeze in [(0,0),(2,0),(2,1),(22,0)]:
        m=P.duplicate(base);H.put(m,SelectedCharacter=selected,SmFreezeRenderState=freeze)
        if selected==22:H.invoke(m,'FwHostGraphics')
        meta=enemy(m,0,12);m[address(b,'ObjectMetasprite')+1]=meta
        seen=set()
        def observe(mem,c,step):
            op=bytes(mem[c.pc:c.pc+3]);tag=mem.rawtags[(c.pc-0x8000)//8192]if c.pc>=0x8000 else -1
            important=op in[b'\x8d\x15\x51',b'\x8d\x16\x51'] or c.pc in[address(b,n)for n in[
                'FwNativeDrawAll','FwNativeFlashProbe','SamusFreezeFlashOwner','SmFreezeNativeFlashEnemy','SamusFreezeRenderFinish']]
            if important or step<10:
                key=(c.pc,tag,op)
                if key not in seen:seen.add(key);snapshots.append((selected,freeze,step,clone(mem,c)))
        H.invoke(m,'SamusFreezeDrawAll',hook=observe)
    rows=[]
    for selected,freeze,step,(state,cpu)in snapshots:
        for kind in['NMI','IRQ']:
            m,c=clone(state,cpu);H.put(m,NmiDisable=255)
            if kind=='IRQ'and c.p&c.INTERRUPT:continue
            r=V.interrupt(m,c,kind);H.finish(m,c);H.exact(m)
            rows.append(dict(selected=selected,freeze=freeze,step=step,**r))
    return dict(passed=True,real_lag_NMI_and_IRQ_cases=len(rows),snapshots=len(snapshots),rows=rows,
                actual_Main_queue_writer_contract=True,all33SMC_AXYP_live_page1_R01_R67_rawmaps_and_RAM3_exact=True)


def palette_regression(b):
    result={}
    for n,fn in [('source_rows',P.source_colors),('colors',P.colors),('capacity',P.capacity),
                 ('transitions',P.transitions),('cold',P.cold_and_foreign),('native_NMI',P.native_consumption),
                 ('Main',P.actual_main),('ISR',P.interruptions)]:
        r=fn(b);assert r['passed'];result[n]={k:v for k,v in r.items()if k!='rows'}
    return dict(passed=True,checks=result,cold_mode_ASL_optimization_actual_controls_exact=True)


def main():
    out=O/'native-flash-controls-v2.json';assert not out.exists()
    p=dict(passed=False,native=False,admitted=False,checks={})
    try:
        h=json.loads((O/'source-closure.json').read_text())
        for f,v in h['bindings'].items():assert sha(f)==v,f
        old=H.C.qualified(OLD/'joint/candidate.nes');new=H.C.qualified(H.O/'candidate.nes')
        for n,fn in [('actual_FF_flash',lambda:flash(new)),('foreign_actors',lambda:foreign_actor(old,new)),
                     ('foreign_DrawAll',lambda:drawall(old,new)),('foreign_Main',lambda:whole_main(old,new)),
                     ('actual_ISR',lambda:isr(new)),('palette_regression',lambda:palette_regression(new))]:
            p['checks'][n]=fn();print(n,'PASS',flush=True)
        p['passed']=True
    except Exception as e:p.update(error=repr(e),traceback=traceback.format_exc())
    p['bindings']={str(f.resolve()):sha(f)for f in[Path(__file__),Path(P.__file__),Path(M.__file__),Path(H.__file__),Path(V.__file__),
        O/'source-closure.json',H.O/'candidate.nes',H.O/'candidate.dbg',OLD/'joint/candidate.nes',OLD/'joint/candidate.dbg']}
    target=out if p['passed']else O/'native-flash-controls-negative-v2.json';assert not target.exists()
    target.write_text(json.dumps(p,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=p['passed'],checks=list(p['checks']),error=p.get('error'),path=str(target))),flush=True)
    assert p['passed']


if __name__=='__main__':main()
