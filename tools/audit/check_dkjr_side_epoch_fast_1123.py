"""Source-only ABI, lifetime, geometry, cold/Main and ISR proof of DK side fast.

Run under run_bounded_build_v1.py with one absent output root. No artifacts,
ROM files or emulator. All timings are linked instruction cycles, not frames.
"""
import json,time
from collections import Counter
from pathlib import Path
from unittest.mock import patch

import compose_dkjr_side_epoch_fast_1123 as C
import check_dkjr_sonic_dispatch_1123 as Q
import check_shared_side_tank_precheck_1110 as Side
import check_mega_giant_resident_1110 as Audio
from check_mini_funded_actor_1108_v3 import registers,live_stack
from py65.devices.mpu6502 import MPU

N,W,B,H,off=Q.N,Q.W,Q.B,C.H,C.off
started=time.monotonic()


def emit(stage,**data):
    print('DK_SIDE_FAST '+json.dumps(dict(stage=stage,seconds=round(time.monotonic()-started,2),**data),
                                    separators=(',',':')),flush=True)


def deny(*a,**k):raise AssertionError('Source verification attempted files/process')


def point(c):
    return (c.memory.rawtags[(c.pc-0x8000)//8192] if c.pc>=0x8000 else -1,c.pc)


def rebound(c,raw):
    z=Q.clone(c);m=z.memory;m.bundle=dict(m.bundle,raw=raw)
    for window,tag in enumerate(tuple(m.rawtags)):
        if tag&128:m.raw_page(window,tag)
    W.clear_logs(m)
    return z


def memory(m):
    # Include reserved stack-page native state (NMI/mapper/etc) below15A;
    # SMC operands and dead stack slots are volatile, live stack is separate.
    return (bytes(m[:0x100]),bytes(m[0x100:0x15a]),bytes(m[0x200:0x800]),
        bytes(m[0x5c00:0x8000]),tuple(map(bytes,m.ram)),tuple(m.rawtags),
        tuple(m.chr_latches),bytes(m.vram),m.ppuctrl,m.ppu_addr,m.toggle,
        m.buffer,m.upper,m.lastset,tuple(m.protection),m[0x16a])


def equal(a,b,label):
    assert registers(a,0xef)==registers(b,0xef),(label,'AXYP/SP',registers(a),registers(b))
    assert live_stack(a)==live_stack(b),(label,'live stack')
    left,right=memory(a.memory),memory(b.memory)
    assert left==right,(label,'native sections',[i for i,(x,y) in enumerate(zip(left,right)) if x!=y])


def finish(c,stop,watch=None):
    for _ in range(300000):
        if (c.pc,c.sp)==stop:return
        if watch:watch(c)
        assert c.memory[c.pc],('Linked BRK',point(c),c.sp)
        c.step()
    raise AssertionError(('Linked execution bound',point(c),c.sp,stop))


def endpoint(c):
    return ((c.memory[0x101+c.sp]+256*c.memory[0x102+c.sp]+1)&65535,c.sp+2)


def foreground_equal(a,b,label):
    assert memory(a)==memory(b),(label,'complete ordinary native/WRAM/mapper/PPU state')
    assert bytes(a[0x1fd:0x200])==bytes(b[0x1fd:0x200]),(label,'root caller stack')


def foreign_units(parent,candidate):
    pages=[raw[off(33,0xa000):off(33,0xa000)+8192] for raw in (parent,candidate)]
    memories=[]
    for page in pages:
        m=[0]*65536;m[0xa000:0xc000]=page;memories.append(m)
    count=0
    for owner in range(256):
        if owner==40:continue
        for status in range(32,256):
            if not status&32:continue
            for admitted in ((False,True)if owner==0 else(False,)):
                results=[]
                for m in memories:
                    m[0x6002]=owner;m[0x16a]=85;m[0x162]=0;m[0x179]=0
                    c=MPU(memory=m,pc=0xbea2);c.a,c.x,c.y,c.p,c.sp=85,7,91,status,236
                    c.stPushWord(0x5aff)
                    for _ in range(120):
                        if c.pc==0xbf38:break
                        if c.pc==0x15a:
                            target=m[0x16c]+256*m[0x16d]
                            if target!=0xbfb0:break
                            c.a=m[0x16a];c.p=(c.p&~1)|int(admitted);c.pc=c.stPopWord()+1
                            continue
                        c.step()
                    else:raise AssertionError('Foreign detached bound')
                    results.append((c.pc,*registers(c,0xef),live_stack(c),
                        m[0x16a],m[0x16c],m[0x16d],m[0x162],m[0x179]))
                assert results[0]==results[1],('foreign',owner,status,admitted,results)
                count+=1
    return count


def qualify(parent):
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        candidate,composition=C.proposal(parent)
        assert C.inverse(candidate)==parent
        result=dict(composition=composition,bindings={Path(p).name:H(Path(p).read_bytes())for p in(C.__file__,__file__)})
        emit('composition',**composition)
        result['foreign_all_owner_status']=foreign_units(parent,candidate)
        seed=Q.enter(parent,'DK')
        for cold in range(300):
            if tuple(N.get(seed,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8):break
            B.main_step(seed,0)
        else:raise AssertionError('DK constructor bound')
        for _ in range(4):B.main_step(seed,0)
        captured=[]
        class Capture:
            def run(self,c,stop):
                def watch(q):
                    if point(q)==(254,0x90e4):captured.append(Q.clone(q))
                finish(c,stop,watch)
        B.main_step(seed,0,Capture())
        assert len(captured)==4 and {c.y for c in captured}=={17,18,19,20}
        cuts={}
        def collect(c,stop):
            tag,pc=point(c)
            selected=(tag==161 and(pc==C.HOOK or C.START<=pc<C.END)or
                tag==213 and(0xa8dc<=pc<0xa900 or 0xb06b<=pc<0xb08f or 0xb8f0<=pc<0xb900)or
                tag==254 and 0x80c2<=pc<0x80c9 or
                pc in(0x15a,0x15d,0x16b,0x16e,0x174,0x17a))
            key=tag,pc,c.sp,c.p&5
            if selected and key not in cuts:
                z=Q.clone(c);z.memory.combined_terminal=stop;cuts[key]=z
        def query(original,image,mutate=None,trace=False):
            c=rebound(original,image)
            if mutate:mutate(c.memory)
            stop=endpoint(c);counts=Counter()
            def watch(z):
                at=point(z)
                for key,location in (('public14',(193,0xb0b6)),('full',(193,0xaf27)),
                    ('epoch',(213,0xa8dc)),('native',(254,0x958b))):
                    if at==location:counts[key]+=1
                if trace:collect(z,stop)
            finish(c,stop,watch)
            return c,counts
        def paired(original,mutate=None,label='',trace=False):
            a,ac=query(original,parent,mutate)
            b,bc=query(original,candidate,mutate,trace)
            equal(a,b,label)
            assert ac['native']==bc['native'] and ac['full']==bc['full'],(label,ac,bc)
            assert bc['epoch']==(1 if bc['public14']==0 else ac['epoch']+1),(label,'epoch flow',ac,bc)
            return a,b,ac,bc
        # Exact AXYP over every valid hardware status, three A/X extremes,
        # four actually reached Y probes; original failure X is significant.
        abi=0;warm_savings=Counter()
        for original in captured:
            for status in range(32,256):
                if not status&32:continue
                for a,x in ((0,0),(85,7),(255,255)):
                    cpu=Q.clone(original);cpu.a,cpu.x,cpu.p=a,x,status
                    left,right,ac,bc=paired(cpu,label=('ABI',original.y,status,a,x),
                        trace=(a,x,status)==(85,7,0x21))
                    assert bc['native']==bc['epoch']==1 and bc['public14']==bc['full']==0
                    warm_savings[left.processorCycles-right.processorCycles]+=1
                    abi+=1
        faults=Counter()
        for original in captured:
            for epoch in range(256):
                def change(m,epoch=epoch):m.ram[2][0x8ff]=epoch
                a,b,ac,bc=paired(original,change,('epoch',original.y,epoch),epoch in(0,1))
                valid=epoch!=0 and epoch==original.memory[0x0e]
                assert bc['public14']==int(not valid) and bc['full']==int(not valid)
                faults['cache_hit'if valid else'epoch_full_fallback']+=1
            for bank in(2,3):
                for byte in range(16):
                    def corrupt(m,bank=bank,byte=byte):
                        m.ram[bank][0x1fe0+byte]^=1;m.ram[2][0x8ff]=0
                    cpu=Q.clone(original);cpu.a,cpu.x,cpu.p=85,7,0x31
                    a,b,ac,bc=paired(cpu,corrupt,('full bad',original.y,bank,byte),byte==0)
                    assert not b.p&1 and bc['native']==0 and bc['full']==bc['public14']==1
                    faults['full_header_rejection']+=1
                for byte in(0,1):
                    def prefix(m,bank=bank,byte=byte):m.ram[bank][0x1fe0+byte]^=1
                    a,b,ac,bc=paired(original,prefix,('warm prefix bad',original.y,bank,byte),True)
                    assert not b.p&1 and bc['native']==0 and bc['full']==1
                    faults['live_prefix_rejection']+=1
            for field,value in(('FrameCounter',0),('GameEngineSubroutine',7),('GamePauseStatus',1),('TimerControl',1)):
                paired(original,lambda m,field=field,value=value:N.put(m,**{field:value}),('scope',field,value))
                faults['unchanged_scope_result']+=1
        # Explicitly retain the 40B idea as a negative ABI fixture, never a proposal.
        text=C.SOURCE.replace(' txa\n pha\n','',1).replace(' pla\n tax\n','',1)
        negative=C.M.assemble(text,dict(FAST=(C.START,44)))
        assert negative['used']['FAST']==40
        bad=bytearray(candidate);at=off(33,C.START);bad[at:at+44]=negative['images']['FAST'].ljust(44,b'\0')
        original=Q.clone(captured[0]);original.x=7
        def poison(m):m.ram[2][0x1fe0]^=1
        old,_=query(original,parent,poison);broken,_=query(original,bytes(bad),poison)
        assert old.x==7 and broken.x==40 and not(old.p&1 or broken.p&1)
        result['forty_byte_negative']=dict(original_X=7,broken_X=40,declined_both=True)
        # Legal, staged cells are component fixtures, not a naturally played scene.
        tiles=0
        for probe in(17,20):
            for tile in range(256):
                for status in(0x21,0x60,0xa5):
                    c=Side.new_leaf(seed,40,0,8,probe,253,191,tile,status)
                    c.memory.ram[2][0x8ff]=c.memory[0x0e]
                    if c.memory[0x0e]==0:
                        N.put(c.memory,FrameCounter=9);c.memory.ram[2][0x8ff]=9
                    paired(c,label=('cell',probe,tile,status))
                    tiles+=1
        result['ABI_and_faults']=dict(actual_reached_probes=4,AXYP_status_cases=abi,
            all_tile_cell_cases=tiles,normal_saved_cycles=dict(warm_savings),faults=dict(faults))
        emit('ABI_and_faults',**result['ABI_and_faults'])
        # Both other native owners and complete retained Rogue byte view.
        base=dict(W.Symbols.bundle(),raw=parent);defaults=N.fresh(base);foreign=0
        for owner in range(256):
            if owner==40:continue
            for tile in(0,0x54,0xc3):
                c=Side.new_leaf(defaults,owner,owner&7,8,17,253,176,tile,0x21)
                a,ac=query(c,parent);b,bc=query(c,candidate)
                equal(a,b,('actual foreign',owner,tile))
                assert ac==bc and a.processorCycles==b.processorCycles
                foreign+=1
        audio=[N.fresh(dict(base,raw=image))for image in(parent,candidate)];reads=0
        for offset in range(256):
            for status in(0x20,0x21,0x60,0x65,0x2c,0xe9):
                a,b=[Audio.call_audio(m,0x87,offset,0,status)[0]for m in audio]
                assert a==b
                expected=parent[off(33,0xbf14)+offset]if offset<36 else 0
                assert b[4]==expected
                reads+=1
        result['foreign_and_Rogue']=dict(actual_foreign_queries=foreign,canonical_Rogue_reads=reads,
            native_Giant_reader_leaf_table_all153_bytes_exact=True)
        emit('foreign_and_Rogue',**result['foreign_and_Rogue'])
        profiles=[]
        for owner in('DK','Sonic','Super','Mini'):
            machines=[Q.enter(image,owner)for image in(parent,candidate)]
            for index in range(300):
                ready=[tuple(N.get(m,n)for n in('OperMode','OperMode_Task','GameEngineSubroutine'))==(1,3,8)for m in machines]
                assert ready[0]==ready[1]
                if all(ready):break
                for m in machines:B.main_step(m,0)
                foreground_equal(*machines,('cold',owner,index))
            else:raise AssertionError(('paired cold',owner))
            phases={}
            for phase,pad,returns in(('settle',0,4),('idle',0,8),('Right',1,16),('jump',129,1),('air',1,10),('land',0,30)):
                savings=[];totals=[0,0];nmis=[0,0]
                for _ in range(returns):
                    for i,m in enumerate(machines):
                        cost,nmi=B.main_step(m,pad);totals[i]+=cost;nmis[i]+=nmi
                    foreground_equal(*machines,(owner,phase))
                    savings.append(totals[0]-totals[1]-sum(savings))
                phases[phase]=dict(returns=returns,saved_cycles=sorted(set(savings)),
                    parent_mean=totals[0]/returns,candidate_mean=totals[1]/returns,
                    NMI_means=[n/returns for n in nmis])
            q=dict(owner=owner,cold_Main_returns=index,phases=phases)
            profiles.append(q);emit('paired_profile',**q)
        result['profiles']=profiles
        needed={C.HOOK}|{i['pc']for i in C.program()['instructions']}
        reached={pc for tag,pc,sp,p in cuts if tag==161}
        eligible={pc for tag,pc,sp,p in cuts if tag==161 and not p&4}
        assert needed<=reached and needed<=eligible,('owned ISR coverage',sorted(needed-reached),sorted(needed-eligible))
        counts=Counter();minimum=255
        for original in cuts.values():
            for kind in('IRQ','busyNMI'):
                if kind=='IRQ'and original.p&4:continue
                a,b=Q.clone(original),Q.clone(original)
                for c in(a,b):N.put(c.memory,NmiDisable=255)
                before=(b.pc,b.sp,registers(b,0xef));stack=live_stack(b)
                private=tuple(map(bytes,b.memory.ram));smc=bytes(b.memory[0x15a:0x17b])
                if kind=='IRQ':b.irq()
                else:b.nmi()
                finish(b,before[:2]);minimum=min(minimum,b.sp)
                assert registers(b,0xef)==before[2]and live_stack(b)==stack
                assert tuple(map(bytes,b.memory.ram))==private and bytes(b.memory[0x15a:0x17b])==smc
                for c in(a,b):finish(c,original.memory.combined_terminal)
                assert registers(a,0xef)==registers(b,0xef)and live_stack(a)==live_stack(b)
                assert tuple(map(bytes,a.memory.ram))==tuple(map(bytes,b.memory.ram))
                assert a.memory.rawtags==b.memory.rawtags and a.memory.chr_latches==b.memory.chr_latches
                assert Q.Old.state(a.memory)==Q.Old.state(b.memory)
                counts[kind]+=1
        result['interrupts']=dict(cuts=len(cuts),cases=dict(counts),minimum_return_SP=minimum,
            all_owned_instructions_reached_IRQ_eligible=True,P_mask='EF; excludes synthetic Break only',
            actual_native_handlers=True,same_full_WRAM_SMC_live_stack_and_continuation=True)
        result.update(passed=True,outputs=0,Mesen=False,walking_frames_qualified=False,
            scope='Actual native ABI plus staged cell/header adversaries; paired compiled-menu cold and ordinary Main; real ISR return/continuation. Not physical cadence or full stage.')
        result['receipt_SHA256']=H(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
        emit('PASS',**result)
        return result


if __name__=='__main__':qualify(C.M.ROM.read_bytes())
