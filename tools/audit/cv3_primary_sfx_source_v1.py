"""Authenticate original CV3 audio requests and execute its actual audio CPU.

No emulator worker, waveform, source rewrite, or target installation. APU
traces are actual ROM instructions in a bank-aware isolated 6502 component.
Instruction-entry cycle stamps exclude hardware DMC steals and bus subcycles.
"""
from pathlib import Path
import argparse, csv, hashlib, itertools, json, re, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/audit'))
from verify_native_relocation import NesMPU
from check_tmnt_render_oa import load, address
from robots_weapon_cpu_v1 import Arena

CV3 = Path("C:/NES/Castlevania III - Dracula's Curse (USA).nes")
CV3_SHA = '085ec6395681c7ebfda19c2986069c21a3d27738cc61ada76249de70a07ed7d3'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class OriginalMemory(list):
    def __init__(self, raw):
        super().__init__([0]*65536)
        self.raw, self.banks, self.trace, self.frame = raw, [28,29,30,31], [], -1
        self.pc = self.cycle = 0
        for slot, bank in enumerate(self.banks): self.page(slot, bank)
        self[0x21] = 0x9c  # original saved lower bank, not a target-game alias

    def page(self, slot, bank):
        self.banks[slot] = bank
        list.__setitem__(self, slice(0x8000+slot*8192,0xa000+slot*8192),
                         self.raw[16+bank*8192:16+(bank+1)*8192])

    def __setitem__(self, at, value):
        if isinstance(at, int):
            assert at < 0x8000, ('ROM write', hex(at), value)
            if 0x4000 <= at <= 0x4017:
                self.trace.append(dict(frame=self.frame, cycle=self.cycle, pc=self.pc,
                    bank=self.banks[(self.pc-0x8000)//8192] if self.pc>=0x8000 else -1,
                    address=at, value=value))
            if at == 0x5115:
                bank = value & 0x7e
                self.page(0,bank); self.page(1,bank+1)
            elif at in (0x5116,0x5117): self.page(at-0x5114,value&0x7f)
        list.__setitem__(self,at,value)


class Original:
    def __init__(self, raw):
        self.m=OriginalMemory(raw)
        self.c=NesMPU(memory=self.m)

    def call(self, pc, a=0, x=0, y=0, stop=None):
        c,m=self.c,self.m
        c.pc,c.a,c.x,c.y,c.sp,c.p=pc,a,x,y,0xff,0x24
        c.stPushWord(0x5aff)
        before=c.processorCycles;steps=0
        while c.pc != 0x5b00:
            if stop is not None and c.pc==stop: break
            m.pc,m.cycle=c.pc,c.processorCycles
            c.step();steps+=1
            assert steps<200000, ('original timeout',hex(pc),hex(c.pc),m.banks)
        assert stop is not None or c.sp==0xff
        return dict(cycles=c.processorCycles-before,steps=steps,final_pc=c.pc,
                    a=c.a,x=c.x,y=c.y,sp=c.sp)


def authenticate(raw, ref, bank, ranges):
    rows=[]
    for m in re.finditer(r'^B\d+_([0-9a-f]{4}):.*;\s*((?:[0-9a-f]{2}\s*)+)$',
                         ref.read_text(),re.M|re.I):
        off=int(m[1],16)
        if not any(lo<=off<hi for lo,hi in ranges):continue
        code=bytes.fromhex(m[2]);actual=raw[16+bank*8192+off:16+bank*8192+off+len(code)]
        assert actual==code,(ref,hex(off),actual.hex(),code.hex())
        rows.append(dict(bank=bank,pc=(0x8000 if bank%2==0 else 0xa000)+off,hex=code.hex()))
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    raw=CV3.read_bytes();assert sha(CV3)==CV3_SHA
    source=ROOT/'build/player-guide-agent/cv3-private/reference/source/code'
    auth=authenticate(raw,source/'playerStateProcessing_b1c.s',28,
        [(0x140a,0x1418),(0x1571,0x1594),(0x1d67,0x1d82),(0x1ce0,0x1ceb)])
    auth+=authenticate(raw,source/'playerStateProcessing_b1d.s',29,
        [(0xe52,0xe9b),(0xf77,0xf86),(0x1390,0x139a),(0x1640,0x1645),
         (0x16b2,0x16bc),(0x1823,0x182e),(0x1a69,0x1aa2)])
    (a.output/'authenticated-callsite-bytes.json').write_text(json.dumps(auth,indent=2)+'\n')

    # Source common knife/staff entry reaches the genuine playSound request.
    common=[]
    for char in (1,2):  # original Sypha=1, Grant=2; port alternate IDs differ
        o=Original(raw);o.m[0x54e]=char;o.call(0x940a,a=0x18,stop=0xe25f)
        assert o.c.a==0x72
        common.append(dict(original_player=char,entry=0x940a,request=o.c.a,
                           state=o.m[0x565],request_pc=o.c.pc))

    # Execute the original object dispatcher: guessing axe/cross from one
    # nearby sound callsite would mislabel event14 (cross) as axe (event15).
    objects=[]
    for obj,want in [(1,0x13),(2,0x15),(3,0x14),(5,0x24),(6,0x21),(7,0x1e),(10,0x1f)]:
        o=Original(raw);o.call(0xe227)
        o.m[0x54e+20]=obj;o.m[0x438]=100;o.m[0x41c]=144
        for update in range(40):
            state=o.call(0xae52,stop=0xe25f)
            if state['final_pc']==0xe25f:break
        else:raise AssertionError(('No source projectile request',obj))
        assert o.c.a==want,(obj,o.c.a,want)
        objects.append(dict(object_id=obj,dispatch=0xae52,request=o.c.a,
                            request_update=update,slot=o.c.x))
    alucard=[]
    for power in (0,1,2):
        o=Original(raw);o.call(0xe227)
        o.m[0x54e]=3;o.m[0x3b]=1;o.m[0x8f]=power;o.m[0x438]=100;o.m[0x41c]=144
        o.call(0xba69)
        assert sum(o.m[0x54e+i]==10 for i in range(20,23))==power+1
        for update in range(20):
            state=o.call(0xae52,stop=0xe25f)
            if state['final_pc']==0xe25f:break
        assert state['final_pc']==0xe25f and o.c.a==0x1f and update==16
        alucard.append(dict(power=power,created=power+1,spawn_entry=0xba69,
            request_update=update,request=o.c.a,central_slot=o.c.x))
    (a.output/'original-projectile-requests.json').write_text(json.dumps(dict(
        objects=objects,Alucard=alucard),indent=2)+'\n')

    events={0x72:'Grant/Sypha attack or main-menu select',
            0x1f:'Alucard central fireball activation',
            0x24:'Sypha flame activation',0x21:'Sypha ice activation',
            0x1e:'Sypha lightning activation',0x13:'dagger throw',0x14:'cross throw',
            0x15:'axe throw',0x2f:'Alucard bat transformation'}
    captures=[]
    for event,name in events.items():
        o=Original(raw);o.call(0xe227)  # genuine initSound
        o.m.trace=[];o.m.frame=0
        launch=o.call(0xe25f,a=event)
        initial=list(o.m.trace)
        timing=[]
        for frame in range(180):
            o.m.frame=frame;timing.append(o.call(0xe24e))
        trace=o.m.trace
        file=a.output/f'event-{event:02x}-apu.csv'
        with file.open('w',newline='')as f:
            w=csv.DictWriter(f,fieldnames=['frame','cycle','pc','bank','address','value'])
            w.writeheader();w.writerows(trace)
        touched=sorted({(r['address']-0x4000)//4 for r in trace if 0x4000<=r['address']<=0x400f})
        captures.append(dict(id=event,name=name,launch=launch,launch_writes=initial,
            trace_file=file.name,trace_sha256=sha(file),writes=len(trace),voices=touched,
            active_instruments=[o.m[0x107+i]for i in range(7)],
            maximum_update_cycles=max(x['cycles']for x in timing)))

    # Original DMC precedence is explicit state + actual hardware status.
    # No guessed timers or synthesized mixer policy are used here.
    priority=[]
    for current,request in itertools.product((0,1,4,5,6,8,13),(0x72,0x75)):
        o=Original(raw);o.call(0xe227);o.m.trace=[]
        o.m[0x192]=current;o.m[0x4015]=0x1f;o.m.trace=[]
        o.call(0xe25f,a=request)
        launched=any(r['address']==0x4012 for r in o.m.trace)
        expected=current<5 or request-0x6d>=current
        assert launched==expected,(current,request)
        priority.append(dict(current_index=current,request=request,launched=launched,
                             result_index=o.m[0x192],writes=o.m.trace))
    o=Original(raw);o.call(0xe227);o.m[0x192]=8;o.m[0x4015]=15
    o.call(0xe24e);assert o.m[0x192]==0
    (a.output/'original-priority.json').write_text(json.dumps(priority,indent=2)+'\n')

    payload=raw[16+30*8192+0x240:16+30*8192+0x240+0x441]
    assert payload==raw[16+7*8192+0x240:16+7*8192+0x240+0x441]
    (a.output/'cv3-event72.dmc').write_bytes(payload)

    # Current assembled request failure is rebound to the supplied candidate.
    b=load(a.rom);broken=[]
    for variant,mode,crouch in itertools.product((1,2,3),(0,1),(0,1)):
        q=Arena(b,char=5)
        q.put(Cv3Variant=variant,Cv3Fresh=0x40,RgAudioCharacter=5,
              CrossoverBehaviorVersion=mode,RgCrouch=crouch)
        q.invoke('Cv3WeaponsGate')
        request=q.get('RgSfx');assert request==4
        _,seen=q.invoke('RosterAudioUpdate',traps=('CvAudioInit','CvAudioPlay','CrossoverGraphicsBank'))
        assert 'CvAudioInit'not in seen and 'CvAudioPlay'in seen and q.get('RgSfx')==0
        broken.append(dict(variant=variant,mode=mode,crouch=crouch,request=request,
                           dispatch=seen,request_after=0))
    (a.output/'baseline-failure.json').write_text(json.dumps(dict(passed=False,
        defect_reproduced=True,ROM_sha256=sha(a.rom),cases=broken),indent=2)+'\n')

    report=dict(passed=True,original_ROM_sha256=CV3_SHA,target_ROM_sha256=sha(a.rom),
        source_revision='3272648f2bbf95f6cb11d947feca73b852a99f10',
        authenticated_callsite_bytes=sum(len(bytes.fromhex(r['hex']))for r in auth),
        common_attack_request_cases=common,event_captures=captures,
        actual_original_projectile_dispatch_cases=len(objects),
        actual_original_Alucard_spawn_dispatch_cases=alucard,
        priority_cases=len(priority),ended_DMC_priority_resets=True,
        event72=dict(rate=15,DAC=0,original_start=0xc240,length=len(payload),
                     sha256=sha(a.output/'cv3-event72.dmc'),owner='DMC only',
                     source_priority_index=5,rough_NTSC_duration_ms=1000*len(payload)*8*54/1789773),
        discarded_current_primary_cases=len(broken),
        scope='Actual original ROM audio requests/driver and bank writes in isolated 6502 components. APU CSV gives instruction-entry cycle stamps, excluding hardware bus subcycles/DMC steals. No Mesen, waveform, native target audio, interrupts, visual or campaign acceptance.',
        tool_sha256=sha(__file__))
    (a.output/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
