"""Exact5c89/6201 native85 mirror caller-domain audit; stdout, RAM only."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from py65.devices.mpu6502 import MPU
from py65.disassembler import Disassembler
import compose_prince_lift_reach_1123 as Lift
import compose_dkjr_sonic_dispatch_1123 as Shared
import profile_prince_empty_current_1123 as Profile

PIN = '5c89b9b727a6c718edccd873bbdff69409e4280c7e0db4e1c3c169304c6a84c9'
H = lambda b: sha256(b).hexdigest()


def at(bank, pc):
    return 16 + bank * 8192 + (pc & 8191)


def selector_domain(mem):
    stops={0xa738:'quick',0xaee2:'full',0xb031:'foreign',0xa7eb:'decline',
           0xab4f:'decline',0xae0a:'retire'}
    counts=Counter(); quick_rows=Counter(); witnesses={}; cases=0
    for row in range(38):
        entry=0xb029 if row==37 else 0xb08c+3*row
        for owner in range(256):
            # All combinations of C,Z,V,N. D/I do not control these paths;
            # SED is never executed, and ADC/SBC are native binary NES math.
            for bits in range(16):
                p=0x30 | (bits&1) | ((bits&2)) | ((bits&4)<<4) | ((bits&8)<<4)
                mem[0x6002]=owner;mem[0x16c]=0x8c+3*row;mem[0x16d]=0xb0
                mem[0x16a]=83
                c=MPU(memory=mem,pc=entry);c.a,c.x,c.y,c.p,c.sp=83,71,109,p,210
                path=[]
                for _ in range(100):
                    if c.pc in stops:
                        kind=stops[c.pc];break
                    path.append(c.pc)
                    assert mem[c.pc],(row,owner,hex(c.pc))
                    c.step()
                else:raise AssertionError(('Public-domain bound',row,owner,path))
                if kind=='quick':
                    assert row not in (0,19,29),(row,owner,path)
                    assert owner in (40,41,43),(row,owner,path)
                    assert mem[0x16c]==0x8c+3*row and mem[0x16d]==0xb0
                    quick_rows[row]+=1
                    witnesses.setdefault(row,dict(owner=owner,entry=entry,path_SHA256=H(bytes().join(pc.to_bytes(2,'little') for pc in path))))
                counts[kind]+=1;cases+=1
    assert set(quick_rows)==set(range(38))-{0,19,29}
    return dict(cases=cases,stops=dict(counts),live_mirror_rows=sorted(quick_rows),
                unreachable_from_public_rows=[0,19,29],quick_witnesses=witnesses)


def retire_closure(mem):
    c=MPU(memory=mem);dis=Disassembler(c);todo=[0xae0a];seen={};external=set();far=[]
    while todo:
        pc=todo.pop()
        if pc in seen:continue
        assert 0xa000<=pc<0xc000,hex(pc)
        size,text=dis.instruction_at(pc);op,mode=c.disassemble[mem[pc]]
        assert op not in ('BRK','???'),(hex(pc),text)
        seen[pc]=text;following=pc+size
        if op in ('JMP','JSR'):
            assert mode=='abs',(hex(pc),text)
            target=mem[pc+1]+256*mem[pc+2]
            if target in (0x80c2,0x015a):
                external.add(target)
                if target==0x015a:far.append(dict(pc=pc,before=bytes(mem[pc-24:pc+3]).hex()))
            else:todo.append(target)
            if op=='JSR':todo.append(following)
        elif mode=='rel':
            delta=mem[pc+1];todo.extend((following,following+delta-(256 if delta&128 else 0)))
        elif op not in ('RTS','RTI'):todo.append(following)
    assert not any(pc in seen for pc in (0xa738,0xa743,0xaaf7,0xaee2))
    assert external<={0x80c2,0x015a}
    assert sorted((site['pc'],site['before'][-10:]) for site in far)==[
        (0xab7e,'a9db4c5a01'),(0xaf76,'a903205a01'),(0xafbc,'a9be4c5a01')]
    return dict(instructions=len(seen),external_leafs=sorted(external),
                farcall_sites=far,
                code_SHA256=H(b''.join(pc.to_bytes(2,'little')+text.encode()+b'\0' for pc,text in sorted(seen.items()))))


def direct_callers(parent):
    expected={(33,0xbfc4):0xa8dc,(59,0xa26d):0xb8b9,(65,0xa738):None,
        (66,0xaa4b):0xb569,(66,0xb45b):0xb451,(66,0xb53b):0xb406,
        (78,0xafe3):0xb57e,(79,0xbfe2):0xb866,(86,0xa36a):0xb0bc,(86,0xa637):0xb400}
    found={};rows=[]
    for bank in range(128):
        block=parent[16+bank*8192:16+(bank+1)*8192]
        for index in range(len(block)-4):
            if block[index:index+2]!=bytes.fromhex('a9d5') or block[index+2:index+5] not in (bytes.fromhex('205a01'),bytes.fromhex('4c5a01')):continue
            key=(bank,0xa000+index)
            assert key in expected,('Unclassified immediate-D5 farcall',key)
            target=expected[key]
            if target is not None and key!=(86,0xa36a):
                prefix=bytes((0xa9,target&255,0x8d,0x6c,1,0xa9,target>>8,0x8d,0x6d,1))
                assert block[index-10:index]==prefix,key
            found[key]=target
            rows.append(dict(bank=bank,pc=key[1],target=target,kind='variable_public_rows' if target is None else 'fixed',
                exact_preimage_SHA256=H(block[max(0,index-10):index+5])))
    assert found==expected
    stage=bytes.fromhex('08a9bc8d6c01a9b08d6d014c6aa3ea')
    assert parent[at(86,0xa2a9):at(86,0xa2a9)+15]==stage
    assert parent[at(86,0xa36a):at(86,0xa36a)+11]==bytes.fromhex('a9d5205a01b0034c54a428')
    assert parent[at(65,0xa738):at(65,0xa738)+8]==bytes.fromhex('a9d5205a014cd5a7')
    # The separate bank79 rare selector supplies D5 via a shared tail, so it
    # is not in the immediate-call census. Its nonzero branch fixes TargetHi
    # to B4, then stores bounded Y as TargetLo before after-NextBank transport.
    assert parent[at(79,0xb854):at(79,0xb854)+5]==bytes.fromhex('a9d54ccfbf')
    assert parent[at(79,0xbfcf):at(79,0xbfcf)+9]==bytes.fromhex('48a9b48d6d0168d011')
    tail=parent[at(79,0xbfe9):at(79,0xbfe9)+22]
    assert tail[:13]==bytes.fromhex('8d6201c0249002a024988d6c01'),tail.hex()
    # Retained source introduced this table as duplicate private checks;
    # public service addresses are in bank65, never native85 exports.
    source=(Shared.M.R/'tools/reference/mini_mario_idle_fast.s').read_text()
    assert '.segment "BANK_ENTRY"\n .repeat 38\n  jmp CheckMini\n .endrepeat' in source
    box=(Shared.M.R/'tools/reference/mini_box_transport_1110_v1.s').read_text()
    assert 'MiniBoxService = $b0bc' in box and 'lda #$d5\n    jsr FarCall' in box
    return dict(immediate_D5_farcall_sites=rows,sole_variable_site=[65,0xa738],
        sole_fixed_mirror_entry=[85,0xb0bc],fixed_box_stage=[86,0xa2a9],
        additional_D5_rare_caller=dict(setter=[79,0xb854],shared_tail=[79,0xbfcf],
            target_high=0xb4,Y_domain=[0,36],target_low_domain=[0,108],target_low_step=3,tail_hex=tail.hex(),no_mirror_target=True),
        source_private_mirror_table=True,arbitrary_forged_FarCall_targets_outside_contract=True)


def native85_closure(parent,callers):
    mem=bytearray(65536);mem[0xa000:0xc000]=parent[at(85,0xa000):at(85,0xa000)+8192]
    c=MPU(memory=mem);dis=Disassembler(c)
    todo=[site['target'] for site in callers['immediate_D5_farcall_sites'] if site['target'] is not None and site['target']!=0xb0bc]
    todo.extend(0xb400+3*row for row in range(37))
    seen={};external=set();indirect=[];mirrors=set();far=[]
    while todo:
        pc=todo.pop()
        if pc in seen:continue
        if 0xb08f<=pc<0xb0fe:
            mirrors.add(pc);continue
        if not 0xa000<=pc<0xc000:
            external.add(pc);continue
        size,text=dis.instruction_at(pc);op,mode=c.disassemble[mem[pc]]
        assert op not in ('BRK','???'),('native85 closure',hex(pc),text)
        seen[pc]=text;following=pc+size
        if op in ('JMP','JSR'):
            if mode!='abs':indirect.append([pc,text]);continue
            dest=mem[pc+1]+256*mem[pc+2]
            todo.append(dest)
            if dest in (0x015a,0x015d):
                far.append(dict(pc=pc,target=dest,before=bytes(mem[pc-20:pc+3]).hex()))
            if op=='JSR':todo.append(following)
        elif mode=='rel':
            delta=mem[pc+1];todo.extend((following,following+delta-(256 if delta&128 else 0)))
        elif op not in ('RTS','RTI'):todo.append(following)
    assert not mirrors and not indirect
    immediate_banks={}
    for site in far:
        pc=site['pc']
        if site['target']==0x015d:
            assert pc==0xb4aa
            assert bytes(mem[pc-19:pc-14])==bytes.fromhex('a9038d6201')
            immediate_banks[pc]=3
        else:
            assert mem[pc-2]==0xa9,(hex(pc),site)
            assert mem[pc-1]!=0xd5,(hex(pc),site)
            immediate_banks[pc]=mem[pc-1]
    assert len(immediate_banks)==12
    return dict(instructions=len(seen),external=sorted(external),indirect=indirect,
                reached_mirror_entries=sorted(mirrors),farcall_sites=far,
                exact_sink_banks=immediate_banks,all_nested_farcall_banks_other_than_D5=True)


def main():
    raw = Profile.D.Old.ROM.read_bytes()
    assert H(raw) == PIN
    parent = Lift.recover_parent(raw)
    assert H(parent) == Profile.PIN
    Profile.authentication(parent)
    diff65 = [i for i in range(at(65,0xa000),at(65,0xa000)+8192) if raw[i] != parent[i]]
    assert all(Profile.Prince.Packet.COOKIE <= i < Profile.Prince.Packet.COOKIE+16 for i in diff65),diff65
    assert raw[at(85, 0xa000):at(85, 0xa000)+8192] == parent[at(85, 0xa000):at(85, 0xa000)+8192]
    mem = bytearray(65536)
    mem[0xa000:0xc000] = parent[at(65, 0xa000):at(65, 0xa000)+8192]
    dis = Disassembler(MPU(memory=mem))
    rows = []
    for row in range(38):
        pc = 0xb029 if row==37 else 0xb08c + 3*row
        assert row==37 or mem[pc] == 0x4c,(row,hex(pc),mem[pc])
        target = pc if row==37 else mem[pc+1] + mem[pc+2]*256
        ins=[]; cursor=target
        for _ in range(12):
            size,text=dis.instruction_at(cursor)
            ins.append([cursor,text]);cursor+=size
            if text.startswith(('JMP','RTS','RTI')):break
        rows.append(dict(row=row,entry=pc,target=target,first_instructions=ins))
    domain=selector_domain(mem)
    retired=retire_closure(mem)
    callers=direct_callers(parent)
    private85=native85_closure(parent,callers)
    assert parent[at(85,0xb08f):at(85,0xb08f)+111]==bytes.fromhex('4cdca8')*37
    report=dict(passed=True,stage='public-domain-and-caller-census',installed_SHA256=PIN,parent_SHA256=H(parent),
        source_SHA256=H(Path(__file__).read_bytes()),native65_SHA256=H(mem[0xa000:0xc000]),
        native85_SHA256=H(parent[at(85,0xa000):at(85,0xa000)+8192]),rows=[r for r in rows if r['row'] in (0,9,12,13,14,19,28,29,34,37)],
        selector_domain=domain,retire_body=retired,callers=callers,native85_fixed_root_closure=private85,
        conditional_funding=dict(typed_unreachable_native85_half_open=[[0xb0c5,0xb0c8],[0xb0e3,0xb0e6]],
            additional_bytes=6,source_bytes_each='4cdca8',not_row28=True,
            if_variable_site_retargets_row16=dict(remaining_mirror=[0xb0bc,0xb0bf],
                reclaimed_half_open=[[0xb08f,0xb0bc],[0xb0bf,0xb0fe]],bytes=108),
            if_variable_site_retargets_row12=dict(retained_entries=[0xb0b0,0xb0bc],
                reclaimed_half_open=[[0xb08f,0xb0b0],[0xb0b3,0xb0bc],[0xb0bf,0xb0fe]],bytes=105,
                contiguous_UTIL_capacity_through_B0B0=69),
            native65_A7DA_A7E4_hex=parent[at(65,0xa7da):at(65,0xa7e4)].hex(),
            A7DA_ownership_not_claimed=True),
        outputs=0,ROM_written=False,candidate_composed=False)
    encoded=json.dumps(report,sort_keys=True,separators=(',',':')).encode()
    print('PRINCE MIRROR DOMAIN '+json.dumps(dict(report=report,receipt_SHA256=H(encoded)),separators=(',',':')),flush=True)


if __name__ == '__main__':
    main()
