"""Actual encoded tier2 cold/full route, earned reload and reached ISR proof."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import inspect,json
import compose_prince_sword_tier2_1115 as C
import replay_prince_sword_tier2_full_1115 as Replay
import check_prince_full_reload_budget_1115 as Budget
import audit_prince_upgrade_reload_1115 as Diagnosis

N,W,Frames,Game=Budget.N,Budget.W,Budget.Frames,Budget.B.Candidate.Game
BASE_CPU=N.NesMPU

def cold(raw):
    assert C.digest(raw)==C.CANDIDATE
    def parent(image):assert image==raw;return raw
    with patch.object(Game,'proof_parent',parent):return Game.cold(raw)

def state(m):return Diagnosis.state(m)

def earned_components(m,frame,raw):
    """Fork actual earned Flower; invoke public components, never seed upgrade."""
    before=state(m);assert before['native_PlayerStatus']==2 and before['Sword']==1 and before['lives']==2
    def clone():
        b=N.fork(m);b.__class__=W.ControllerBus;return b
    warm=clone()
    for _ in range(32):warm.controller_pad=0;frame(warm,whole_pass=True)
    assert state(warm)['native_PlayerStatus']==2 and state(warm)['Sword']==1
    area=clone();N.invoke(area,'ChgAreaMode',a=0,x=0,y=0,p=0x21);requested=state(area);active=0
    for tick in range(360):
        area.controller_pad=0;frame(area,whole_pass=True);s=state(area)
        if s['Ready']==0xa7 and(s['task'],s['engine'])==(3,8):
            assert s['native_PlayerStatus']==2 and s['Sword']==1 and s['HP']>0 and s['lives']==2
            active+=1
            if active==25:break
    else:raise AssertionError('Earned Flower public area component failed')
    death=clone();N.invoke(death,'KillPlayer',a=0,x=0,y=0,p=0x21)
    assert N.get(death,'PlayerStatus')==0 and N.get(death,'GameEngineSubroutine')==11
    continued=clone();N.invoke(continued,'NativeRareRunGameOverCore::ContinueGame',a=0,x=0,y=0,p=0x21)
    assert N.get(continued,'PlayerStatus')==0
    # Public menu entry with rendering already off is an explicit component;
    # the source PPU does not reproduce real vblank.
    menu=clone();N.put(menu,CrossoverMenuState=1,DisableScreenFlag=1,Mirror_PPUMASK=0,VRAM_Buffer1_Offset=0)
    N.invoke(menu,'CrossoverMenuInput',a=0,x=0,y=0,p=0x21);assert N.get(menu,'PlayerStatus')==0
    return dict(passed=True,actual_earned_Flower=before,warm32=state(warm),compiled_ChgAreaMode_requested=requested,
        compiled_area_Main=tick+1,compiled_area25active=state(area),explicit_KillPlayer=state(death),
        explicit_Continue_native_PlayerStatus=N.get(continued,'PlayerStatus'),compiled_menu_screen_entry_native_PlayerStatus=N.get(menu,'PlayerStatus'),
        scope='Genuinely earned state followed by public reload/death/continue/menu components; not natural pipe/death/menu gameplay',
        menu_source_vblank_limitation=True,upgrade_or_health_seeds=0)

def actual(raw):
    text=Replay.controller(raw);metadata=Replay.metadata(raw)
    print(json.dumps(dict(event='tier2-full-metadata',**metadata),separators=(',',':')),flush=True)
    parent=C.inverse(raw);parts=C.Packet.extract(raw)[1];rows=C.Plan.arrays(parent)[3]
    counts=Counter();seen=set();contexts=[];minimum=255;trace=sha256();opening_contexts=[]
    targets={0xc7b3,0xc7ba,0xc7d3,0xc7d7,0xc7f4,0xc0f6,0xc0fa}
    def pair(cpu,kind):
        nonlocal minimum
        regs=(cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp,cpu.pc);trials=[];before=[]
        for restore in(False,True):
            b=N.fork(cpu.memory);b.__class__=W.ControllerBus
            if restore:
                for row in rows:
                    lo=row['live_CPU_half_open'][0]&8191;b.ram[2][lo:lo+len(row['old'])]=row['old']
            c=BASE_CPU(memory=b,pc=cpu.pc);c.a,c.x,c.y,c.p,c.sp=regs[:5]
            before.append(dict(private=[bytes(x)for x in b.ram],native=bytes(b[:0x800]),maps=b.rawtags[:],
                transport=(bytes(b[3:11]),bytes(b[0x15a:0x17b]),b.chr_latches[:]),upper=bytes(b[0x101+c.sp:0x200]),skip=N.get(b,'NmiSkipped')))
            c.irq()if kind=='IRQ'else c.nmi();trials.append((c,b))
        for steps in range(100000):
            a,ma=trials[0];b,mb=trials[1]
            assert(a.a,a.x,a.y,a.p&239,a.sp,a.pc)==(b.a,b.x,b.y,b.p&239,b.sp,b.pc)
            minimum=min(minimum,a.sp)
            if(a.pc,a.sp)==(regs[5],regs[4]):break
            assert a.sp<=regs[4]and ma.rawtags==mb.rawtags
            assert not(ma.rawtags[(a.pc-0x8000)//8192]==2 and any(lo<=a.pc<hi for lo,hi in(row['live_CPU_half_open']for row in rows)))if a.pc>=0x8000 else True
            code=bytes(ma[a.pc:a.pc+3]);assert code==bytes(mb[b.pc:b.pc+3])and ma[a.pc]
            trace.update(bytes((a.pc&255,a.pc>>8,a.sp,a.p&239))+code);a.step();b.step()
        else:raise AssertionError('Paired tier2 ISR return bound')
        assert(a.a,a.x,a.y,a.p&239,a.sp,a.pc)==(*regs[:3],regs[3]&239,*regs[4:])
        effects=[]
        for(c,b),prior in zip(trials,before,strict=True):
            assert[bytes(x)for x in b.ram]==prior['private']and b.rawtags==prior['maps']
            assert(bytes(b[3:11]),bytes(b[0x15a:0x17b]),b.chr_latches[:])==prior['transport']
            assert bytes(b[0x101+regs[4]:0x200])==prior['upper']
            assert N.get(b,'NmiSkipped')==(prior['skip']+(kind=='busyNMI'))&255
            effects.append(bytes(b[:0x800]))
        assert effects[0]==effects[1];counts[kind]+=1
    class CPU(BASE_CPU):
        def step(self):
            b=self.memory
            if hasattr(b,'rawtags')and self.pc in targets and b.rawtags[2]==2 and b.bundle.get('raw')==raw:
                key=(self.pc,self.sp,self.p&4)
                if key not in seen:
                    seen.add(key);contexts.append(dict(PC=self.pc,SP=self.sp,P=self.p,native_PlayerStatus=N.get(b,'PlayerStatus')))
                    if not self.p&4:pair(self,'IRQ')
                    if N.get(b,'NmiDisable')==255:pair(self,'busyNMI')
            return super().step()
    components=None;receipts=[];ticks=0;loads=json.loads;complete=Frames.frame
    def capture(*args,**kwargs):
        value=loads(*args,**kwargs)
        if isinstance(value,dict)and'later_route'in value:receipts.append(value)
        return value
    def frame(m,*args,**kwargs):
        nonlocal ticks,components
        result=complete(m,whole_pass=True);ticks+=1
        if components is None and m.ram[2][0x6ee]==1 and N.get(m,'PlayerStatus')==2:
            print(json.dumps(dict(event='actual-earned-tier2',Main=ticks,state=state(m)),separators=(',',':')),flush=True)
            # Avoid the route's Lua callback subclass during explicit clones.
            with patch.object(N,'NesMPU',BASE_CPU):components=earned_components(m,complete,raw)
            print(json.dumps(dict(event='earned-area-death-menu-components',**components),separators=(',',':')),flush=True)
        if ticks%500==0:print(json.dumps(dict(event='actual-tier2-full',Main=ticks,state=state(m)),separators=(',',':')),flush=True)
        return result
    with patch.object(N,'NesMPU',CPU):
        m,opening=cold(raw)
        with patch.object(Game,'controller',lambda image:text),patch.object(Game.json,'loads',capture),patch.object(Game.Frames,'frame',frame):
            proof=Game.route(m,raw,9000)
    assert len(receipts)==1;receipt=receipts[0]
    proof.pop('events',None);proof.pop('sword_trace',None)
    if isinstance(proof.get('flower'),dict):proof['flower']={k:v for k,v in proof['flower'].items()if k!='trace'}
    assert proof['passed']and components and receipt['grounded_1_2_completed_returns']>=25
    assert receipt['Main_entries']==receipt['Main_returns']and not receipt['Main_pending']
    assert N.get(m,'PlayerStatus')==2 and m.ram[2][0x6ee]==1 and N.get(m,'NumberofLives')==2
    assert receipt['new_candidate_readback']['bytes']==4185 and counts['IRQ']and counts['busyNMI']
    return dict(passed=True,metadata=metadata,opening=opening,proof=proof,earned_components=components,
        actual_Main_witness={k:receipt.get(k)for k in('Main_entries','Main_returns','Main_pending','grounded_1_2_completed_returns')},
        actual_readback=receipt['new_candidate_readback'],persistent_sword=receipt['persistent_sword'],terminal=state(m),
        paired_ISR_counts=dict(counts),paired_ISR_contexts=contexts,minimum_ISR_SP=minimum,identical_ISR_trace_SHA256=trace.hexdigest(),
        baseline_restores_only158_owned_bytes=True,paired_native_audio_effects_exact=True,no_private_ISR_writes=True,
        complete_Main_calls=ticks,actual_CPU_ROM_SHA256=C.digest(m.bundle['raw']),outputs=0,Mesen=False,no_gameplay_seeds=True)

def run(parent):
    raw,composition=C.proposal(parent)
    assert C.digest(Path(Budget.__file__).read_bytes())=='6236f925b87fd1a17f6adbd65e5e63e1679ee1f4d88d7dfa07c2011220613955'
    source=inspect.getsource(Budget.run)
    old="current=CurrentCheck.Current.normalize(raw,kind='prince-current-gimmick-7a80')"
    assert source.count(old)==1;source=source.replace(old,'assert C.digest(raw)==C.CANDIDATE',1)
    old="with patch.object(Frames,'frame',frame):q=CurrentCheck.run(raw,full=True)"
    assert source.count(old)==1;source=source.replace(old,"with patch.object(Frames,'frame',frame):q=actual(raw)",1)
    namespace=dict(Budget.__dict__,C=C,actual=actual)
    exec(compile(source,str(Path(__file__))+':unchanged-authenticated-cold-budget','exec'),namespace)
    q=namespace['run'](raw);q['composition']=composition
    q['scope']='Actual encoded candidate ordinary full route and earned public components; native cadence is separate'
    q['receipt_SHA256']=C.digest(json.dumps(q,sort_keys=True,separators=(',',':')).encode());return q

if __name__=='__main__':
    def deny(*a,**k):raise AssertionError('Earned tier2 source proof attempted output or launch')
    with patch.object(Path,'write_text',deny),patch.object(Path,'write_bytes',deny),patch('subprocess.Popen',deny):
        q=run(Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes').read_bytes())
    print(json.dumps(q,separators=(',',':')),flush=True)
