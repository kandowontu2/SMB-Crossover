"""Execute assembled Rogue audio against the original cartridge, CPU only.

Hardware APU publication remains deliberately separate. Compare ordered source
register requests, real assembled image writers, private state and bank/ZP ABI.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/"tools"),str(ROOT/"tools/audit")]
import rogue_dawn_map_v1 as ref
import rogue_dawn_audio_owner_v1 as original
from verify_native_relocation import NesMPU
from prepare_rogue_dawn_audio_driver_v4 import OUT, labels, binding


class Source(original.Memory):
    def __init__(self,raw):
        super().__init__(raw)
        self.requests=[]
        self.volume_reads=[]

    def __setitem__(self,p,v):
        if isinstance(p,int) and 0x4000<=p<=0x4017:
            self.requests.append([p,v])
        super().__setitem__(p,v)


class Host(bytearray):
    def __init__(self,raw,s):
        super().__init__(65536)
        self.raw,self.s=raw,s
        self.banks=[126,62,97,127]
        self.requests=[]
        self.volume_reads=[]
        self.maps=0
        for i,b in enumerate(self.banks):
            self.map(i,b)
        self[s['CurrentBank']]=0xbe
        self[s['CurrentBankC']]=0xe1
        self[s['SelectedCharacter']]=2
        self[s['RdVariant']]=1

    def map(self,i,b):
        self.banks[i]=b
        bytearray.__setitem__(self,slice(0x8000+i*8192,0xa000+i*8192),self.raw[16+b*8192:16+(b+1)*8192])

    def __setitem__(self,p,v):
        if isinstance(p,int):
            assert p<0x8000,('Host ROM write',hex(p))
            assert not 0x4000<=p<=0x4017,('Unqualified hardware APU publication',hex(p),v)
            if p in [0x5115,0x5116]:
                assert v&0x80
                self.map(1 if p==0x5115 else 2,v&127)
                self.maps+=1
        bytearray.__setitem__(self,p,v)


def main():
    proof=OUT/'controls.json'
    assert not proof.exists(),'Preserve completed differential'
    raw=ref.ROM.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==ref.EXPECTED
    candidate=(OUT/'candidate.nes').read_bytes()
    assert hashlib.sha256(candidate).hexdigest()==json.loads((OUT/'build-proof.json').read_text())['candidate']['sha256']
    s=labels(OUT/'candidate.lbl')
    s.update({n:int(a,16)for n,a in re.findall(r'^(\w+)=\$([0-9a-f]+)$',(OUT/'src/driver-imports.inc').read_text(),re.M)})
    graph=json.loads((ROOT/'docs/qa/rogue-dawn-audio-source-closure-2026-10-28.json').read_text())['graph']
    apu={}
    for r in graph['instructions']:
        b=bytes.fromhex(r['bytes'])
        if len(b)==3:
            address=int.from_bytes(b[1:],'little')
            if 0x4000<=address<=0x4017:
                apu[r['pc']+0x2000]=(r['instruction'].split()[0],address,r['mode'])
    upper_indirect_reads=set()

    def call(m,pc,a=0x36,x=0x57,y=0x98,p=0x61,observe=True):
        c=NesMPU(memory=m,pc=pc)
        c.a,c.x,c.y,c.p,c.sp=a,x,y,p,0xfd
        c.stPushWord(0x5aff)
        low=0xfd
        for _ in range(50000):
            if c.pc==0x5b00:
                assert c.sp==0xfd
                return c,low
            assert c.pc>=0x8000,('Bad audio execution',hex(c.pc),getattr(m,'banks',None))
            if c.pc in [0xa553,0xc553]:
                address=(0xb601 if isinstance(m,Source) else 0xd601)+c.y
                m.volume_reads.append(dict(pc=c.pc,y=c.y,address=address,value=m[address]))
            if isinstance(m,Host) and observe and m.banks[(c.pc-0x8000)//8192]==97:
                if c.pc in apu:
                    op,address,mode=apu[c.pc]
                    value=c.y if op=='STY' else c.x if op=='STX' else c.a
                    m.requests.append([address+(c.y if mode=='aby' else 0),value])
                elif c.pc==0xd386:
                    address=m[0xe0]+256*m[0xe1]+c.y
                    assert 0x4000<=address<0x4010
                    m.requests.append([address,c.a])
            elif isinstance(m,Source) and c.pc in [0xba69,0xbae2,0xbb3d]:
                zp=0xec if c.pc==0xba69 else 0xe6
                address=(m[zp]+256*m[zp+1]+c.y)&65535
                if address>=0xa000:
                    upper_indirect_reads.add(address)
                    assert 0xa480<=address<0xc000
            assert m[c.pc]!=0,('BRK',hex(c.pc),getattr(m,'banks',None))
            c.step()
            low=min(low,c.sp)
        raise AssertionError(('Audio nonreturn',hex(c.pc)))

    zps=[0x1e,0x23,0x2e,0x2f,0x79,0xe0,0xe1,0xe2,0xe3,0xe4,0xe5,0xe6,0xe7,0xe8,0xe9,0xea,0xeb,0xec,0xed]
    seed=bytes((i*37+19)&255 for i in range(256))

    def mapped(pointer):
        return pointer+0x2000 if 0xa480<=pointer<0xc000 else pointer

    def compare_state(src,host):
        expected=bytearray(bytearray.__getitem__(src,slice(0x600,0x700)))
        expected[0x1f]=0 # actual061F is read-only projected RdBeamSfx, not audio RAM
        value=mapped(expected[0xec]+256*expected[0xed])
        expected[0xec:0xee]=value.to_bytes(2,'little')
        actual=bytes(host[s['RdaState']:s['RdaState']+256])
        assert actual==expected,('Private RAM difference',[(hex(i),a,b)for i,(a,b)in enumerate(zip(actual,expected))if a!=b][:12])
        expected_zp=bytearray(src[z]for z in zps)
        for i in [5,7,9]:
            value=mapped(expected_zp[i]+256*expected_zp[i+1])
            expected_zp[i:i+2]=value.to_bytes(2,'little')
        actual_zp=host[s['RdaZpState']:s['RdaZpState']+19]
        assert all(a==b for i,(a,b)in enumerate(zip(actual_zp,expected_zp))if i not in [13,14]),('Private ZP difference',actual_zp.hex(),expected_zp.hex())
        assert host[:256]==seed,'Borrowed foreground ZP not restored'
        assert host.banks==[126,62,97,127] and host[s['CurrentBank']]==0xbe and host[s['CurrentBankC']]==0xe1

    def setup(area,missile=0,gear=0,vy=0):
        src,host=Source(raw),Host(candidate,s)
        host[:256]=seed
        src[0x1e],src[0x23],src[0x2f]=3,area,0x1d
        src[0x680],src[0x62c]=1,1
        call(host,s['RdaAudioInit'])
        # Tick the actual original silence owner before the area request.
        call(src,0xc000);call(src,0xc215);call(host,s['RdaAudioTick'])
        call(host,s['RdaAudioSetArea'],a=area)
        src[0x685]=[16,1,8,64,16,128][area]
        for source_address,host_name,value in [(0x10e,'RdMissileMode',missile),(0x6878,'RdGear',gear),(0x308,'RdVY',vy),(0x61f,'RdBeamSfx',0x80|(1 if gear&128 and not missile else 0))]:
            src[source_address]=value
            host[s[host_name]]=value
        compare_state(src,host)
        return src,host

    campaigns=[]
    updates=0
    costs=[]
    digest=hashlib.sha256()
    effects=[(0x680,1<<bit)for bit in range(1,8)]+[(q,1<<bit)for q in [0x681,0x683]for bit in range(8)]
    for area in range(6):
        src,host=setup(area)
        count=0
        for tick in range(384+len(effects)*96+160):
            if tick>=384 and tick<384+len(effects)*96 and (tick-384)%96==0:
                q,flag=effects[(tick-384)//96]
                src[q]|=flag
                call(host,s['RdaAudioSetQueue'],a=src[q],x=q-0x680)
            pause=5 if 384+len(effects)*96<=tick<384+len(effects)*96+64 else 3
            src[0x1e]=pause
            call(host,s['RdaAudioSetMode'],a=pause)
            src.requests=[];host.requests=[]
            rng,_=call(src,0xc000)
            ca,_=call(src,0xc215)
            cb,low=call(host,s['RdaAudioTick'])
            if host.requests!=src.requests:
                negative=dict(status='GENUINE_ASSEMBLED_DIFFERENTIAL_FAILURE',area=area,tick=tick,
                              source_requests=src.requests,assembled_requests=host.requests,
                              source_volume_reads=src.volume_reads[-4:],assembled_volume_reads=host.volume_reads[-4:],
                              candidate=binding(OUT/'candidate.nes'),
                              limits='No pass or host adoption. Preserve source code/data overlapping views; original instructions may also be read as envelope data.')
                target=OUT/'first-actual-differential-negative.json'
                assert not target.exists()
                target.write_text(json.dumps(negative,indent=2)+'\n')
                raise AssertionError(('Ordered request mismatch',area,tick,src.requests,host.requests))
            assert (cb.a,cb.x,cb.y,cb.p&0xcf)==(0x36,0x57,0x98,0x61&0xcf)
            compare_state(src,host)
            for address,value in host.requests:
                target=s['RdaDac']if address==0x4011 else s['RdaFrameControl']if address==0x4017 else s['GuestNativeApu']+address-0x4000
                # Only the final request per register is observable in a buffer.
                if [address,value]==next(q for q in reversed(host.requests)if q[0]==address):
                    assert host[target]==value,('Actual image writer',address,value,host[target])
            costs.append([ca.processorCycles+rng.processorCycles,cb.processorCycles])
            digest.update(bytes(value for _,value in host.requests))
            updates+=1;count+=1
        campaigns.append(dict(area=area,updates=count,effects=len(effects),source_mode5_pause=True))
        print(json.dumps(dict(area=area,updates=count)),flush=True)
    context_cases=context_updates=transition_updates=0
    phases=set()
    def paired_tick(src,host):
        nonlocal updates
        src.requests=[];host.requests=[]
        rng,_=call(src,0xc000)
        ca,_=call(src,0xc215)
        cb,_=call(host,s['RdaAudioTick'])
        if src.requests!=host.requests:
            failure=dict(status='GENUINE_EXTENDED_ASSEMBLED_DIFFERENTIAL_FAILURE',
                         completed_updates=updates,area=src[0x23],phase=src[0x6ef],
                         source_requests=src.requests,assembled_requests=host.requests,
                         candidate=binding(OUT/'candidate.nes'),limits='No pass or shared adoption')
            (OUT/'extended-differential-negative.json').write_text(json.dumps(failure,indent=2)+'\n')
            raise AssertionError(('Extended source request mismatch',updates,src.requests,host.requests))
        compare_state(src,host)
        assert (cb.a,cb.x,cb.y,cb.p&0xcf)==(0x36,0x57,0x98,0x61&0xcf)
        costs.append([ca.processorCycles+rng.processorCycles,cb.processorCycles])
        digest.update(bytes(v for _,v in host.requests))
        updates+=1
    for area in range(6):
        for missile in [0,1]:
            for gear in [0,0x40,0x80,0xc0]:
                for vy in [0,4,0xfc]:
                    for effect in ['beam','screw']:
                        src,host=setup(area,missile,gear|(8 if effect=='screw'else 0),vy)
                        queue,flag=(0x681,0x10)if effect=='beam'else(0x680,0x40)
                        src[queue]=flag
                        call(host,s['RdaAudioSetQueue'],a=flag,x=queue-0x680)
                        for tick in range(96):
                            paired_tick(src,host)
                            context_updates+=1
                        context_cases+=1
        src,host=setup(area)
        # Explicit original phase1 producer fixture; not a wired Main claim.
        src[0x6ef]=1
        host[s['RdaState']+0xef]=1
        for tick in range(260):
            paired_tick(src,host)
            phases.add(src[0x6ef])
            transition_updates+=1
        print(json.dumps(dict(context_area=area,contexts=48,transition_ticks=260)),flush=True)
    assert context_cases==288 and context_updates==27648 and transition_updates==1560
    assert {0,2,3,4,5,6}<=phases,phases
    foreign=0
    for character,variant in [(c,1)for c in range(256)if c!=2]+[(2,v)for v in range(256)if v!=1]:
        for name in ['RdaAudioInit','RdaAudioTick','RdaAudioSetQueue','RdaAudioSetArea','RdaAudioSetMode']:
            host=Host(candidate,s)
            host[s['SelectedCharacter']],host[s['RdVariant']]=character,variant
            host[:256]=seed
            before=bytes(host)
            cb,_=call(host,s[name])
            assert bytes(host[:256])==before[:256]and bytes(host[512:])==before[512:]
            assert (cb.a,cb.x,cb.y,cb.p&0xcf)==(0x36,0x57,0x98,0x61&0xcf)
            assert host.banks==[126,62,97,127]
            foreign+=1
    # Every original lower-bank byte, through the actual compiled mapper reader.
    host=Host(candidate,s)
    reads=0
    for area,bank in enumerate([52,48,53,54,50,51]):
        host[0x23]=area
        for address in range(0x8000,0xa000):
            host[0xe8],host[0xe9]=address&255,address>>8
            c,_=call(host,s['RdaReadRom'],observe=False)
            assert c.a==raw[16+bank*8192+(address&8191)],(area,hex(address),c.a)
            assert host.banks==[126,62,97,127] and host[s['CurrentBank']]==0xbe
            reads+=1
    upper_reads=0
    for address in range(0xa000,0xc000):
        host[0xe8],host[0xe9]=address&255,address>>8
        c,_=call(host,s['RdaReadRom'],observe=False)
        assert c.a==raw[16+49*8192+(address&8191)],('Raw upper data view',hex(address),c.a)
        assert host.banks==[126,62,97,127] and host[s['CurrentBank']]==0xbe
        upper_reads+=1
    report=dict(status='PASS_FINITE_ACTUAL_ASSEMBLED_AUDIO_DIFFERENTIAL_NO_NATIVE',passed=True,native_run=False,
                source=ref.binding(ref.ROM),candidate=binding(OUT/'candidate.nes'),
                campaigns=campaigns,actual_differential_updates=updates,
                foreground_weapon_context_cases=context_cases,weapon_context_updates=context_updates,
                explicit_transition_fixture_updates=transition_updates,transition_phases=sorted(phases),
                foreign_exact_public_API_calls=foreign,
                exhaustive_lower_ROM_reader_bytes=reads,exhaustive_upper_raw_reader_bytes=upper_reads,all_source_lower_bytes_preserved=True,all_source_upper_raw_bytes_preserved=True,
                ordered_register_requests_exact=True,actual_buffer_writers_checked=True,
                private_state_and_source_pointer_projection_exact=True,
                whole_foreground_ZP_and_bank_shadows_restored=True,
                source_CPU_range=[min(r[0]for r in costs),max(r[0]for r in costs)],
                host_CPU_range=[min(r[1]for r in costs),max(r[1]for r in costs)],
                CPU_distributions={name:dict(median=statistics.median(r[i]for r in costs),p95=sorted(r[i]for r in costs)[len(costs)*95//100])for i,name in enumerate(['source','host'])},
                source_indirect_upper_data_reads=sorted(upper_indirect_reads),
                ordered_values_sha256=digest.hexdigest(),
                RNG_cadence_fixture='Explicit source C000 call before every audio tick. Authentic foreground/lag cadence remains open.',
                scope='Real assembled ca65 driver and genuine fixed image writers, six actual source areas,23 single-bit effects per area, gameplay/pause/resume. No stubs or runtime ROM writes. All49152 lower bytes and8192 original upper raw-data bytes read through actual compiled mapper reader. Relocated instructions retain a separate view from original raw operand/envelope bytes.',
                limits='No atomic Main cues, scheduler/mixer adoption, hardware4011/4017 publication, source-to-audio IRQ safety, exhaustive combined priority/scene cancellation or native listening/timing qualification. Transition phase1 and weapon contexts are explicitly typed source fixtures, not real foreground producer wiring.',
                bindings=[binding(p)for p in [Path(__file__),OUT/'build-proof.json',ROOT/'src/rogue_dawn_audio_driver_v4.s',ROOT/'src/rogue_dawn_audio_native_v4.inc',ROOT/'src/rogue_dawn_audio_rng_v4.inc']])
    proof.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k]for k in ['status','actual_differential_updates','exhaustive_lower_ROM_reader_bytes','source_CPU_range','host_CPU_range']}))


if __name__=='__main__':
    main()
