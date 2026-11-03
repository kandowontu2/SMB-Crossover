"""Original one-NMI coroutine cadence and current idle/walk exclusive costs."""
import collections,hashlib,json
from pathlib import Path
import measure_bub_landing_1102_v21 as L
from py65.devices.mpu6502 import MPU

N,Q,P,R,address=L.N,L.Q,L.P,L.R,L.address;O=L.O
PIN='9cf99b438e6f5bc614dc4ccc433707a3796702b7f33a04318a428a1155397f15'


def donor_cadence():
    path=Path('C:/NES/Bubble Bobble (USA).nes');raw=path.read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='e34901acf6917495890ef79ddb33e4641ea309a803d777a27a198e8802c9b4a0'
    c=MPU();m=c.memory;m[0xc000:]=raw[16+7*16384:16+8*16384]
    assert bytes(m[0xce2d:0xce32])==bytes.fromhex('208ccee61f')
    assert bytes(m[0xd1c6:0xd1cb])==bytes.fromhex('a90120e3ce')
    assert int.from_bytes(bytes(m[0xcefe:0xcf00]),'little')+1==0xd1be
    frame=-1;players=[];yields=[];samples=[]
    def call(pc,y=0,clock=False):
        c.pc=pc;c.sp=0xfd;c.y=y;c.stPushWord(0x5ffe)
        for steps in range(5000):
            if c.pc==0x5fff:return
            if clock and c.pc==0xce4d:
                # The exact29Bclock ends at its post-clockaudio boundary.
                c.pc=(c.stPopWord()+1)&65535;continue
            if c.pc in[0xd28e,0xd24d,0xd1e7]:
                if c.pc==0xd1e7:players.append(dict(frame=frame,actor=c.x,OAM=c.y,source_air_subclock=m[0x28]))
                # Explicit actor/init/input callbacks are irrelevant to the
                # scheduler opportunity count, and are not timed or replaced
                # in a ROM. Original CE8C/CEE3/D1C6 control bytes execute.
                c.pc=(c.stPopWord()+1)&65535;continue
            if c.pc==0xcee3:yields.append(dict(frame=frame,delay=c.a,process=m[0x1c]))
            c.step()
        raise AssertionError(('original coroutine bound',frame,hex(c.pc)))
    call(0xceaf,y=2)
    for frame in range(122):
        before=len(players);call(0xce8c);call(0xce30,clock=True)
        if frame<8:samples.append(dict(frame=frame,actor_opportunities=len(players)-before,clock=m[0x1f],process_delay=m[0x12],air_subclock=m[0x28]))
    byframe=collections.Counter(z['frame']for z in players)
    assert all(byframe[i]==2 for i in range(2,122))and all(byframe[i]==0 for i in[0,1])
    assert all(z['delay']==1 and z['process']==2 for z in yields)
    assert collections.Counter(z['actor']for z in players)=={0x2e:120,0x42:120}
    return dict(original_SHA256=hashlib.sha256(raw).hexdigest(),NMI_scheduler_calls=122,
        startup_yields=2,steady_NMI_calls=120,steady_Bub_opportunities=120,steady_Bob_opportunities=120,
        source_yield_delay=1,global_30Hz_divider=False,first_frames=samples,
        source_bindings={f'{a:04X}..{b-1:04X}':hashlib.sha256(bytes(m[a:b])).hexdigest()for a,b in[(0xce07,0xce4d),(0xce8c,0xcefa),(0xd1be,0xd1e7)]},
        scope='Actual originalfixedbank scheduler/processconstructor/yield/playerouterloop and29Bpost-updateclock. Declared scheduler context uses only playerprocess2; actual actor/input/sprite-init callbacks are counted/skipped attypedentries, PPU/audio excluded. Proves oneBub+oneBob updateopportunity perNMIafterstartup, not fulloriginalgame timing or crowd/no-lag performance. Original air subclock is separate from global scheduling.')


def main():
    cadence=donor_cadence();_,b,layout,route=L.bundle();rom=O/'combined-current-landing.nes';b['raw']=rom.read_bytes();assert P.sha(b['raw'])==PIN
    owner=P.P.labels(L.B/'native-event-v9-owner.lbl');routes=P.P.labels(L.B/'native-proxy-routes.lbl')
    points={(193,owner['CoCheckCode']):'CoCheckCode',(193,owner['CoCheckHeaders']):'CoCheckHeaders'}
    for name in['BbNativeTile23','BbNativeTile84','BbNativeProxiesIn','BbNativeProxiesOut','BbNativeShiftCamera']:
        points[(3,layout['labels'][name])]=name
    for name in['BlockBufferCollision','AreaParserCore','CrossoverLevelColumn','RenderAreaGraphics','DrawLevelLoop']:
        if name in b['syms']:
            points[(((L.E.G.B.location(b,name)-16)//8192)|128,address(b,name))]=name
    native=N.NesMPU;cases=[]
    for identity in[0,1]:
        m=Q.fresh(b,route,identity);L.E.main_fields(m)
        for phase,keys in[('idle',0),('walk',1)]:
            buckets=collections.Counter();rows=collections.Counter();counts=collections.Counter();inclusive=collections.defaultdict(list);stack=[];ppu=collections.Counter();totals=[]
            class Trace(native):
                def step(self):
                    mem=self.memory;pc=self.pc;tag=mem.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else-1
                    while stack and(pc,self.sp,tag)==(stack[-1]['ret'],stack[-1]['sp'],stack[-1]['tag']):
                        z=stack.pop();inclusive[z['name']].append(self.processorCycles-z['cycles'])
                    name=points.get((tag,pc))
                    if name:
                        counts[name]+=1;ret=(mem[0x100+((self.sp+1)&255)]+256*mem[0x100+((self.sp+2)&255)]+1)&65535
                        rt=mem.rawtags[(ret-0x8000)//8192]if ret>=0x8000 else-1
                        stack.append(dict(name=name,ret=ret,sp=(self.sp+2)&255,tag=rt,cycles=self.processorCycles))
                    if tag==193 and pc==routes['ExDispatch']:
                        target=mem[address(b,'FarcallJmpTarget_SMC')+1]+256*mem[address(b,'FarcallJmpTarget_SMC')+2]
                        assert 0xb08c<=target<=0xb0fb and(target-0xb08c)%3==0;rows[(target-0xb08c)//3]+=1
                    if mem[pc]in[0x8d,0x8e,0x8c]:
                        a=mem[(pc+1)&65535]+256*mem[(pc+2)&65535]
                        if a in[0x2006,0x2007]:ppu[a]+=1
                    if tag==3:bucket='original_source'if 0xa100<=pc<0xb53a else'private_native_bridge'
                    elif tag==2 and 0xd320<=pc<0xd400:bucket='private_helper'
                    elif tag==193 and 0xae00<=pc<0xb013:bucket='shared_owner_auth'
                    elif tag==193 and(0xa740<=pc<0xa800 or 0xb08c<=pc<0xb0fe):bucket='shared_overlay_dispatch'
                    elif tag==207:bucket='shared_high_router'
                    elif 0x15a<=pc<0x17c:bucket='RAM_farcall'
                    else:bucket='other_native_host'
                    before=self.processorCycles;result=native.step(self);buckets[bucket]+=self.processorCycles-before;return result
            N.NesMPU=Trace
            try:
                startclock=m.ram[2][0x1f]
                for epoch in range(8):
                    N.put(m,FrameCounter=epoch+(8 if phase=='walk'else 0),SavedJoypadBits=keys,SavedJoypad1Bits=keys,VRAM_Buffer1_Offset=0)
                    totals.append(N.invoke(m,'GameCoreRoutine',x=0,y=0)['CPU'])
            finally:N.NesMPU=native
            assert not stack and sum(totals)==sum(buckets.values())and(m.ram[2][0x1f]-startclock)&255==8
            cases.append(dict(identity=identity,phase=phase,Main_calls=8,source_updates=8,mean_Main_CPU_cycles=sum(totals)/8,
                min_Main_CPU_cycles=min(totals),max_Main_CPU_cycles=max(totals),exclusive_instruction_cycles=dict(buckets),
                service_rows=dict(sorted(rows.items())),entry_calls=dict(counts),
                inclusive_costs={n:dict(calls=len(v),total=sum(v),mean=sum(v)/len(v),maximum=max(v))for n,v in inclusive.items()},
                direct_executed_PPU_stores={f'{a:04X}':v for a,v in ppu.items()},
                scope='Exactcurrent9cf actualGameCore legalemptyground arena; CPU costs exclude IRQ/NMI/stalls. Inclusive nested costs must not be summed. No instrumented/emulated state mutation beyond declared input/epoch/VRAMqueue fixture fields.'))
    out=dict(passed=True,ROM_written=False,source_mutated=False,native=False,ROM_sha256=PIN,original_cadence=cadence,CPU_cases=cases,
        conclusions=['Original playerprocess deliberatelyyields1NMI; no sourceglobal30Hzdivider explains currentidle/walkhalf-rate. Sourceairscheduling is separate and mustnotbeaccelerated.',
            'Currenttypedowner/header/router/farcall and native/source terrainprobe counts are measured separately. EmptyCPUfixture directPPUstores/column-rendercalls identify whether terrainpainting is partofthis budget.',
            'No cachedownerflag or authbypass proposedasimplemented. Any future reduction requires exactframe/owner/fullheader/lifetime/retirement/badheader/cookie and actualIRQ/lagNMI proof before changing sharedcode.'],
        bindings={str(p.relative_to(R)):P.sha(p.read_bytes())for p in[Path(__file__),rom,O/'combined-current-landing.json',O/'landing-v21-layout.json',L.B/'native-event-v9-owner.s',L.B/'native-proxy-routes.s']})
    dst=O/'clock-bridge-profile-v46.json';assert not dst.exists();dst.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(passed=True,original=cadence,CPU_cases=[{k:c[k]for k in['identity','phase','mean_Main_CPU_cycles','entry_calls','service_rows','inclusive_costs','direct_executed_PPU_stores']}for c in cases])))


if __name__=='__main__':main()
