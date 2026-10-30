"""Actual native enemy constructor prefix and logical FF flash cadence."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import ff_joint_terrain_hooks_controls_1030_v1 as T
import ff_joint_actual_main_v2 as M
from ff_wram_host_isr_v4 import clone
import ff_host_pickups_vectors_v2 as V
from check_tmnt_render_oa import address,location
H=T.H;sha=T.sha
P=R/'build/ff-joint-terrain-hooks-1030-v3'
O=R/'build/ff-joint-combat-hooks-1030-v3'
H.O=O/'joint'


def prefix(m,x,p=0x71,observer=None):
    c=H.start(m,'CheckpointEnemyID',a=0x55,x=x,y=91,p=p)
    end=address(m.bundle,'CheckpointEnemyID')+41
    for i in range(20000):
        if c.pc==end and m.rawtags[1]==135:break
        if observer:observer(m,c,i)
        assert m[c.pc]!=0,('prefixBRK',hex(c.pc),m.rawtags)
        c.step()
    else:raise AssertionError('prefix bounded')
    return c


def state(m,c):
    s=T.sig(m,c)
    # The new genuine farcall publishes its own dispatch target. Old/new final
    # SMC operands differ; actual ISR controls preserve each live operand.
    return(s[0][:256]+s[0][256+33:],s[1],s[2],s[3])


def fixture(seed,selected,x):
    m=T.fixture(seed,selected)
    for n in['MmEnemyHealthLo','MmEnemyHealthHi','MmEnemyFlash','RgEnemyStun','LsrFrozenPose','AvFrozen','AvFrozenHi']:
        m[address(m.bundle,n)+x]=0x79
    H.put(m,GuestBodyPrev=0x3f,GuestBodyNow=0x3f,FfHits=0x3f)
    for i in range(3):m[address(m.bundle,'FfProjectile')+i*12+9]=0x3f
    m.writes.clear();m.ram_writes.clear()
    return m


def constructors(old,new):
    seeds=[T.T.base(b)for b in[old,new]];rows=[]
    for selected,x,p in itertools.product([n for n in range(33)if n!=22],range(6),[0x30,0x71]):
        pair=[];cycles=[]
        for seed in seeds:
            m=fixture(seed,selected,x);c=prefix(m,x,p)
            pair.append(state(m,c));cycles.append(c.processorCycles)
        assert pair[0]==pair[1],('foreign native clear prefix',selected,x,p)
        rows.append([selected,x,p,cycles[1]-cycles[0]])
    own=[]
    flags=[0x30|n for n in range(256)if n&0x30==0]
    for x,p in itertools.product(range(6),flags):
        m=fixture(seeds[1],22,x);c=prefix(m,x,p);mask=0x3f&~(1<<x)
        for n in['MmEnemyHealthLo','MmEnemyHealthHi','MmEnemyFlash','RgEnemyStun','LsrFrozenPose','AvFrozen','AvFrozenHi']:
            assert m[address(new,n)+x]==0,n
        assert H.get(m,'GuestBodyPrev')==H.get(m,'GuestBodyNow')==mask
        assert H.get(m,'FfHits')==mask
        assert [m[address(new,'FfProjectile')+i*12+9]for i in range(3)]==[mask]*3
        assert(c.a,c.x,c.y,c.p)==(mask,x,91,(p&~0x82)|(0x02 if mask==0 else 0))
        H.exact(m);own.append([x,p,mask])
    # Complete actual source initialization, including same-ID slot reuse.
    complete=[]
    for x in range(6):
        m=fixture(seeds[1],22,x)
        m[address(new,'Enemy_ID')+x]=6
        m[address(new,'Enemy_Y_Position')+x]=160
        m[address(new,'Enemy_Y_HighPos')+x]=1
        c,_=H.invoke(m,'CheckpointEnemyID',x=x)
        assert H.get(m,'FfHits')==0x3f&~(1<<x)
        H.exact(m);complete.append(x)
    return dict(foreign_prefix_cases=len(rows),all64flags_FF_slot_reuse_cases=len(own),complete_native_Goomba_init_slots=complete,
       foreign_extra_CPU=[min(r[-1]for r in rows),max(r[-1]for r in rows)],rows=rows,own=own)


def poisoned(new):
    seed=T.T.base(new);rows=[]
    for byte,x in itertools.product(range(16),[0,5]):
        m=fixture(seed,22,x);m.ram[3][0x1fe0+byte]^=1
        before=bytes(m[0x5c00:0x5c80]);hits=H.get(m,'FfHits');projectiles=bytes(m[address(new,'FfProjectile'):address(new,'FfProjectile')+36])
        prefix(m,x)
        assert bytes(m[0x5c00:0x5c80])==before
        assert H.get(m,'FfHits')==hits and bytes(m[address(new,'FfProjectile'):address(new,'FfProjectile')+36])==projectiles
        assert m[address(new,'MmEnemyHealthLo')+x]==0
        rows.append([byte,x])
    return dict(cases=len(rows),native_clear_executes_but_invalid_RAM3_never_executes=True,rows=rows)


def flash(new):
    rows=[];seed=T.T.base(new)
    for engine,pause,timer,dead in itertools.product([4,5,8],[0,1],[0,1],[0,1]):
        m=T.fixture(seed,22,engine=engine);H.put(m,GamePauseStatus=pause,TimerControl=timer,MmDeathFlag=dead)
        initial=[2,1,0,4,255,2]
        for x,v in enumerate(initial):
            m[address(new,'Enemy_Flag')+x]=0;m[address(new,'MmEnemyFlash')+x]=v
        for i in range(36):m[address(new,'FfProjectile')+i]=0
        H.invoke(m,'FwHostWeapons')
        active=engine==8 and not(pause or timer or dead)
        expected=[max(v-1,0)for v in initial]if active else initial
        assert list(m[address(new,'MmEnemyFlash'):address(new,'MmEnemyFlash')+6])==expected
        H.exact(m);rows.append([engine,pause,timer,dead,active])
    m=M.setup(new);initial=[2,1,0,4,255,2]
    for x,v in enumerate(initial):
        m[address(new,'Enemy_Flag')+x]=0;m[address(new,'MmEnemyFlash')+x]=v
    for i in range(36):m[address(new,'FfProjectile')+i]=0
    H.put(m,SavedJoypadBits=0,A_B_Buttons=0,Left_Right_Buttons=0,VRAM_Buffer1_Offset=0,NmiDisable=255)
    calls=[]
    def observe(mem,c,i):
        if c.pc==address(new,'FfHostWeapons')and mem.rawtags[1]==3:calls.append(i)
    M.invoke_main(m,observe)
    assert len(calls)==1
    assert list(m[address(new,'MmEnemyFlash'):address(new,'MmEnemyFlash')+6])==[max(v-1,0)for v in initial]
    H.exact(m)
    return dict(guard_cases=len(rows),actual_full_Main_weapon_calls=len(calls),once_per_logical_update=True,rows=rows)


def isr(new):
    seed=T.T.base(new);snapshots=[]
    for selected in[0,22]:
        m=fixture(seed,selected,3);seen=set()
        def observe(mem,c,step):
            op=bytes(mem[c.pc:c.pc+3])
            if step<18 or op in[b'\x8d\x15\x51',b'\x8d\x16\x51']or c.pc in[
                  address(new,'FwNativeEnemyInit'),address(new,'FwCheck'),address(new,'FfHostNewEnemy')]:
                key=(c.pc,mem.rawtags[1],op)
                if key not in seen:seen.add(key);snapshots.append((selected,step,clone(mem,c)))
        prefix(m,3,observer=observe)
    rows=[]
    for selected,step,(state,cpu)in snapshots:
        for kind,lag in itertools.product(['NMI','IRQ'],[0,255]):
            m,c=clone(state,cpu);H.put(m,NmiDisable=lag)
            if kind=='IRQ'and c.p&c.INTERRUPT:continue
            v=V.interrupt(m,c,kind);H.finish(m,c)
            H.exact(m);rows.append(dict(selected=selected,step=step,lag=lag,**v))
    return dict(cases=len(rows),all33SMC_APXY_live_page1_R01_R67_maps_verified=True,rows=rows)


def main():
    out=O/'combat-controls-v1.json';assert not out.exists();p=dict(passed=False,native=False,admitted=False,checks={})
    try:
        h=json.loads((O/'source-closure.json').read_text())
        for f,v in h['bindings'].items():assert sha(f)==v,f
        old=H.C.qualified(P/'joint/candidate.nes');new=H.C.qualified(O/'joint/candidate.nes')
        for n,fn in[('native_constructors',lambda:constructors(old,new)),('poisoned_cookie',lambda:poisoned(new)),
                     ('flash_cadence',lambda:flash(new)),('actual_ISR',lambda:isr(new))]:
            p['checks'][n]=fn();print(n,'PASS',flush=True)
        p['passed']=True
    except Exception as e:p.update(error=repr(e),traceback=traceback.format_exc())
    p['bindings']={str(f.resolve()):sha(f)for f in[Path(__file__),Path(T.__file__),Path(M.__file__),Path(V.__file__),
       O/'source-closure.json',O/'joint/candidate.nes',O/'joint/candidate.dbg',P/'joint/candidate.nes',P/'joint/candidate.dbg']}
    target=out if p['passed']else O/'combat-controls-negative-v1.json';assert not target.exists()
    target.write_text(json.dumps(p,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=p['passed'],error=p.get('error'),path=str(target))),flush=True);assert p['passed']


if __name__=='__main__':main()
