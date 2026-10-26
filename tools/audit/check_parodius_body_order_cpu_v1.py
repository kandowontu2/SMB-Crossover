"""Execute both actual body records; compare legal reservations and emitter costs."""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import itertools
import json
from check_tmnt_render_oa import address, location
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_roll_renderer import Memory
from verify_native_relocation import NesMPU

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def execute(bundle, bank, pointer, origin, cursor, rotation):
    memory = bytearray(65536)
    for segment in bundle['segs'].values():
        if segment.get('name') == '"SMCCODE"':
            start, size, offset = (int(segment[k], 0) for k in ('start', 'size', 'ooffs'))
            memory[start:start+size] = bundle['raw'][offset:offset+size]
    l = lambda n: address(bundle, n)
    renderer_bank = (location(bundle, 'MetaspriteRenderLoop')-16)//8192
    for name, value in [('CurrentBank', renderer_bank|128), ('CurrentBankC', bank|128),
                        ('CurrentOAMOffset', cursor), ('GuestOamRotationActive', 1),
                        ('RgOamRotation', rotation), ('R0', pointer&255), ('R1', pointer>>8),
                        ('R3', 0), ('R4', origin[0]&255), ('R5', (origin[0]>>8)&255),
                        ('R6', origin[1]&255), ('R7', (1+(origin[1]>>8))&255)]:
        memory[l(name)] = value
    begin = l('Sprite_Y_Position')
    for i in range(64):
        memory[begin+i*4:begin+i*4+4] = bytes([248, 0, 0, 0])
    sp = 0xd9; stop = 0x5b00
    memory[0x101+sp] = (stop-1)&255; memory[0x102+sp] = (stop-1)>>8
    bus = Memory(bundle['raw'], memory, {0x8000:126, 0xa000:renderer_bank, 0xc000:bank, 0xe000:127})
    cpu = NesMPU(memory=bus)
    cpu.pc=l('MetaspriteRenderLoop'); cpu.sp=sp; cpu.a=173; cpu.x=73; cpu.y=19; cpu.p=0x6d
    for _ in range(10000):
        if cpu.pc == stop: break
        cpu.step()
    else: raise AssertionError(('unbounded body renderer', bank, pointer, origin))
    assert cpu.sp == sp+2 and bus.banks[0xa000] == renderer_bank and bus.banks[0xc000] == bank
    oam = bytes(bus.data[begin:begin+256])
    parts = [oam[i:i+4] for i in range(0,256,4)]
    visible = Counter(part for part in parts if part[0]<240)
    return dict(regs=(cpu.a,cpu.x,cpu.y,cpu.p&0xcf,cpu.sp), visible=visible,
                offset=bus.data[l('CurrentOAMOffset')], cycles=cpu.processorCycles,
                store_count=sum(begin<=a<begin+256 for a,v in bus.writes))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--aliases',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); old=scoped_load(a.baseline); new=scoped_load(a.candidate)
    aliases=json.loads(a.aliases.read_text())['all_records']; count=0; deltas=[]; v_cases=0; cases=[]
    origins=[(-16,120),(0,0),(4,24),(32,48),(96,120),(207,191),(247,232),(255,255),(256,120),(96,-8)]
    for key,refs in aliases.items():
        if not any(ref['body'] for ref in refs): continue
        assert all(ref['body'] for ref in refs)
        bank,ptr=map(int,key.split(':')); size=old['raw'][16+bank*8192+ptr%8192]
        for origin,cursor,rotation in itertools.product(origins,(0,128,220-size),(0,128,252)):
            x=execute(old,bank,ptr,origin,cursor,rotation)
            y=execute(new,bank,ptr,origin,cursor,rotation)
            assert x['visible']==y['visible'],('visible complete sprite multiset changed',key,origin,cursor,rotation)
            assert x['offset']==y['offset'] and x['store_count']==y['store_count']
            assert x['regs'][:3]+x['regs'][4:]==y['regs'][:3]+y['regs'][4:]
            assert (x['regs'][3]^y['regs'][3])&~0x40==0,('unexpected return flag change',key,x,y)
            # V is the last coordinate ADC. DrawMetasprite uses C and then LDA
            # after this return; record-only V differences are disclosed below.
            v_cases += x['regs'][3]!=y['regs'][3]
            delta=y['cycles']-x['cycles']; deltas.append(delta); count+=1
            if delta: cases.append(dict(record=key,origin=origin,cursor=cursor,rotation=rotation,delta=delta))
    proof=dict(passed=True,adopted=False,native_run=False,goal_complete=False,
               baseline_ROM_sha256=sha(a.baseline),candidate_ROM_sha256=sha(a.candidate),
               tool_sha256=sha(Path(__file__)),aliases_sha256=sha(a.aliases),body_records=131,
               complete_body_emitter_cases=count,exact_visible_part_multisets=True,
               cursor_and_store_count_exact=True,cycle_delta=dict(min=min(deltas),max=max(deltas)),
               coordinate_ADC_return_V_difference_cases=v_cases,nonzero_cycle_cases=cases,
               scope='Actual CPU emitter and clipping with legal full-body reservations. '
                     'Reordered stores/OAM are intentional. This does not certify NES '
                     'eight-sprite admission, fairness, visible pixels or native cadence.')
    a.output.write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items() if k!='nonzero_cycle_cases'}))


if __name__=='__main__':main()
