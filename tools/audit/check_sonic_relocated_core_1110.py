"""Stdout-only mapped-RAM differential qualification of the relocated Sonic core.

Replays the frozen donor/reference fixture generator without running its file
producer. No native RAM lifetime, ROM, hook or raw identity is admitted here.
"""
import argparse
import ast
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import random
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/reference'))
import sonic_sms_relocated_core_1110 as Build
import check_sonic_original_composed_frame_1110 as Frozen

RealCPU=Frozen.Prior.NesMPU
OLD_CHECKER_PIN='0f2b560dd97bc4ff8d6614b381e13b65ad6c58cefd500b118d809022803379f5'
PROOF_PIN='1ae399417eb3ce4de5dfdaddbf017d9398d4b2399988db175662124a277a11ca'
STOP=0x5b00
HOST_CANARY=bytes((i*73+41)&255 for i in range(65536))
RAM2_CANARY=bytes((i*29+97)&255 for i in range(8192))
RAM3_CANARY=bytes((i*43+53)&255 for i in range(8192))


def digest(data):
    return sha256(data).hexdigest()


class PrivateMemory(list):
    """Test-only actual A3/C2 maps; other memory is guarded host canary data."""
    def __init__(self,program,source=None,stale_operands=None):
        super().__init__(HOST_CANARY)
        self.program=program
        self.rawtags=(254,3,2,255)
        self.ram2=bytearray(RAM2_CANARY)
        self.ram3=bytearray(RAM3_CANARY)
        self.ram3[:len(program['image'])]=program['image']
        if stale_operands:
            for address,value in stale_operands.items():self.ram3[address-0xa000]=value
        self.writes=[]
        if source is not None:
            self.ram2[:256]=bytes(source[:256])
            for ptr in (0x8c,0xae):
                value=source[ptr]|source[ptr+1]<<8
                moved=translate_pointer(program,value)
                self.ram2[ptr:ptr+2]=moved.to_bytes(2,'little')
            self.ram2[0x800:0x1800]=bytes(source[0x6000:0x7000])
            self.ram2[0x1800:0x1900]=bytes(source[0x7000:0x7100])
        self.initial_host=HOST_CANARY
        self.initial2=bytes(self.ram2)
        self.initial3=bytes(self.ram3)

    def __getitem__(self,address):
        if isinstance(address,slice):return[self[i]for i in range(*address.indices(65536))]
        if 0xa000<=address<0xc000:return self.ram3[address-0xa000]
        if 0xc000<=address<0xe000:return self.ram2[address-0xc000]
        return list.__getitem__(self,address)

    def __setitem__(self,address,value):
        if isinstance(address,slice):
            for at,byte in zip(range(*address.indices(65536)),value):self[at]=byte
            return
        value&=255
        self.writes.append((address,value))
        if 0xa000<=address<0xc000:
            assert address in self.program['SMC_operands'],('Unowned code write',hex(address))
            self.ram3[address-0xa000]=value
        elif 0xc000<=address<0xe000:
            assert 0xc000<=address<0xc100,('State/world/header write',hex(address))
            self.ram2[address-0xc000]=value
        else:
            assert 0x17b<=address<0x200,('Shared RAM/ZP/mapper write',hex(address),value)
            list.__setitem__(self,address,value)

    def verify(self):
        assert self.rawtags==(254,3,2,255)
        for lo,hi in ((0,0x17b),(0x200,0xa000),(0xe000,0x10000)):
            assert bytes(list.__getitem__(self,slice(lo,hi)))==self.initial_host[lo:hi],('Host canary',hex(lo),hex(hi))
        assert self.ram2[256:]==self.initial2[256:],'Private fixture map/flags/clock/header canary'
        current,original=bytearray(self.ram3),bytearray(self.initial3)
        for at in self.program['SMC_operands']:current[at-0xa000]=original[at-0xa000]=0
        assert current==original,'Instruction/table/header canary'


def translate_pointer(program,value):
    if value in program['source_to_target']:return program['source_to_target'][value]
    if 0x6000<=value<0x7000:return value+0x6800
    return value


class DualCPU(RealCPU):
    program=None
    cases=0
    cycles=[]
    minimum_SP=255
    visited=Counter()
    stale_operands={}

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.initial_source=self.memory.copy()
        self.source_entry=self.pc

    def step(self):
        result=super().step()
        if self.pc==STOP:self.check_relocation()
        return result

    def check_relocation(self):
        program=type(self).program
        m=PrivateMemory(program,self.initial_source,type(self).stale_operands)
        c=RealCPU(memory=m,pc=program['source_to_target'][self.source_entry])
        c.sp,c.p=224,0x30
        c.stPushWord(STOP-1)
        thunks={program['symbols']['RelocatedRead8COperand']:0x8c,
                program['symbols']['RelocatedReadAEOperand']:0xae}
        for _ in range(3000):
            if c.pc==STOP:break
            assert 0xa000<=c.pc<Build.CODE_LIMIT,('Code escaped RAM3',hex(c.pc))
            type(self).minimum_SP=min(type(self).minimum_SP,c.sp)
            type(self).visited[c.pc]+=1
            if c.pc in thunks:
                ptr=thunks[c.pc]
                stored=m[c.pc+1]|m[c.pc+2]<<8
                expected=m[0xc000+ptr]|m[0xc001+ptr]<<8
                assert stored==expected,('Stale private SMC operand',hex(c.pc),hex(stored),hex(expected))
            assert m[c.pc],('Relocated BRK',hex(c.pc))
            c.step()
        else:raise AssertionError(('Relocated frame bound',hex(c.pc)))
        assert (c.a,c.x,c.y,c.p,c.sp)==(self.a,self.x,self.y,self.p,self.sp),(
            'Relocated ABI',type(self).cases,(c.a,c.x,c.y,c.p,c.sp),(self.a,self.x,self.y,self.p,self.sp))
        expected=list(self.memory[:256])
        for ptr in (0x8c,0xae):
            value=expected[ptr]|expected[ptr+1]<<8
            moved=translate_pointer(program,value)
            expected[ptr:ptr+2]=moved.to_bytes(2,'little')
        assert bytes(m.ram2[:256])==bytes(expected),('Relocated full state',type(self).cases,
            [(hex(i),expected[i],m.ram2[i])for i in range(256)if expected[i]!=m.ram2[i]][:20])
        m.verify()
        type(self).stale_operands={address:m[address]for address in program['SMC_operands']}
        type(self).cases+=1
        type(self).cycles.append(c.processorCycles)


def replay_frozen(program):
    """Reuse exact positive generator/one() AST; omit every producer statement."""
    path=Path(Frozen.__file__)
    assert digest(path.read_bytes())==OLD_CHECKER_PIN
    tree=ast.parse(path.read_text())
    main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
    one=deepcopy(next(n for n in main.body if isinstance(n,ast.FunctionDef)and n.name=='one'))
    class UseDual(ast.NodeTransformer):
        def visit_Attribute(self,node):
            if isinstance(node.value,ast.Name)and node.value.id=='Prior'and node.attr=='NesMPU':
                return ast.copy_location(ast.Name(id='DualCPU',ctx=ast.Load()),node)
            return self.generic_visit(node)
    one=UseDual().visit(one)
    # These are exactly the two independent sweeps plus the40 carried episodes.
    begin=next(i for i,n in enumerate(main.body)if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='nes')
    end=next(i for i,n in enumerate(main.body)if isinstance(n,ast.FunctionDef)and n.name=='swap_calls')
    generated=deepcopy(main.body[begin:end])
    setup=ast.parse('''
count=0
template=[0]*65536
template[0x8000:0x8000+len(code)]=code
rng=random.Random(1110)
visits,excludes=Counter(),Counter()
cycles=[]
evidence=Counter()
query_digest=sha256()
episodes=[]
''').body
    finish=ast.parse('''
one(1,0x8c,0x300,0,512<<8,176<<8,32,0,0,5,0,0,0,floor)
assert count==7297 and len(episodes)==40
return dict(cases=count,episodes=episodes,donor_instructions=sum(visits.values()),source_PCs=len(visits))
''').body
    driver=ast.FunctionDef(name='driver',args=ast.arguments(posonlyargs=[],args=[],kwonlyargs=[],kw_defaults=[],defaults=[]),
                           body=setup+[one]+generated+finish,decorator_list=[])
    env=dict(vars(Frozen))
    env.update(DualCPU=DualCPU,code=program['original']['image'],
               syms=program['original']['symbols'],rom=Frozen.DONOR.read_bytes())
    exec(compile(ast.fix_missing_locations(ast.Module(body=[driver],type_ignores=[])),str(path),'exec'),env)
    return env['driver']()


def pointer_leaves(program):
    count=0
    for pointer in (0x8c,0xae):
        entry=program['symbols'][f'RelocatedRead{pointer:02X}']
        for page in (0xc1,0xc7,0xd8):
            for low in (0,255):
                for y in range(256):
                    for p in (0x30,0x31,0x79,0xf9):
                        m=PrivateMemory(program)
                        target=page<<8|low
                        # Direct in-memory source data; no host write API is used.
                        at=(target+y)&65535
                        assert 0xc000<=at<0xdfe0
                        m.ram2[pointer:pointer+2]=target.to_bytes(2,'little')
                        expected=m[at]
                        m.initial2=bytes(m.ram2)
                        c=RealCPU(memory=m,pc=entry)
                        c.a,c.x,c.y,c.p,c.sp=85,73,y,p,224
                        c.stPushWord(STOP-1)
                        for _ in range(16):
                            if c.pc==STOP:break
                            c.step()
                        else:raise AssertionError('Indirect leaf bound')
                        flags=(p&~0x82)|(0x80 if expected&128 else 0)|(2 if expected==0 else 0)
                        assert(c.a,c.x,c.y,c.p,c.sp)==(expected,73,y,flags,224)
                        m.verify();count+=1
    return count


def animation_leaves(program):
    # Ordinary trajectories need not encounter every stream loop marker. Run
    # each valid original stream at every index, including its marker, so the
    # third $8C indirect site is exercised by a genuine source animation state.
    rom=Frozen.DONOR.read_bytes();count=0
    for animation in range(26):
        if animation==3:continue
        pointer=int.from_bytes(rom[0x5965+animation*2:0x5967+animation*2],'little')
        last=next(i for i in range(256)if rom[pointer+i]&128)
        for frame in range(last+1):
            memory=[0]*65536
            memory[0x8000:0x8000+4864]=program['original']['image']
            memory[0x31]=animation
            memory[0xa0:0xa3]=[animation,frame,31]
            c=DualCPU(memory=memory,pc=program['original']['symbols']['AnimationRead'])
            c.sp,c.p=224,0x30;c.stPushWord(STOP-1)
            for _ in range(100):
                if c.pc==STOP:break
                c.step()
            else:raise AssertionError('Source animation leaf bound')
            count+=1
    return count


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    assert args.output.resolve()==(R/'build/sonic-relocated-core-1110').resolve()and not args.output.exists()
    assert digest((Build.SOURCE.parent/'proof.json').read_bytes())==PROOF_PIN
    program=Build.build();DualCPU.program=program
    print(json.dumps(dict(reference_byte_exact=True,original_bytes=len(program['original']['image']),
         relocated_bytes=len(program['image']),remaining_code_bytes=Build.CODE_LIMIT-Build.CODE_START-len(program['image']),
         long_branches=len(program['long_branches']),indirect_sites=len(program['indirect_sites']))),flush=True)
    assert len(program['indirect_sites'])==4
    # Every reachable/generated instruction has an absolute private address or
    # a private control target. Zero-page instructions are forbidden statically.
    for index,pc in program['boundaries'].items():
        name,mode=RealCPU.disassemble[program['image'][pc-0xa000]]
        assert mode not in ('zpg','zpx','zpy','inx','iny'),('Borrowed ZP',hex(pc),name,mode)
    result=replay_frozen(program)
    assert DualCPU.cases==7297 and DualCPU.minimum_SP>0x7a
    frame_cycles=[min(DualCPU.cycles),max(DualCPU.cycles)]
    print('All7297 donor/reference/relocated frames and40 carried episodes passed.',flush=True)
    animation_cases=animation_leaves(program)
    leaf_cases=pointer_leaves(program)
    assert all(pc in DualCPU.visited for pc in program['indirect_sites']),(
        'Missing indirect source coverage',[hex(pc)for pc in program['indirect_sites']if pc not in DualCPU.visited])
    report=dict(passed=True,source_CPU_only=True,ROM_written=False,files_written=0,host_RAM_granted=False,
        original_bytes=4864,original_bytes_reproduced=True,relocated_bytes=len(program['image']),
        image_SHA256=digest(program['image']),code_half_open=program['code_half_open'],
        state_half_open=program['state_half_open'],test_fixture_world_half_open=program['fixture_world_half_open'],
        test_fixture_flags_half_open=program['fixture_flags_half_open'],
        remaining_code_bytes=Build.CODE_LIMIT-Build.CODE_START-len(program['image']),
        source_cases=result,relocation_cases=DualCPU.cases,animation_leaf_cases=animation_cases,indirect_leaf_cases=leaf_cases,
        ordinary_frame_cycles=frame_cycles,all_call_cycles=[min(DualCPU.cycles),max(DualCPU.cycles)],minimum_SP=DualCPU.minimum_SP,
        entrypoints=program['entrypoints'],state_fields=program['state_fields'],
        indirect_source_sites=program['indirect_sites'],owned_SMC_operands=program['SMC_operands'],
        relaxed_branches=program['long_branches'],all_host_ZP_RAM_maps_and_headers_guarded=True,
        scope='All7297 frozen positive source/donor cases including40 consecutive80-update episodes '
              'run both the exact4864B fixture and fully relinked A3/C2 core. All256 private state bytes '
              'match with constrained code/world-pointer relocation; finalAXYP/SP exact. No host ZP '
              'instruction or write. Only four private SMC operand bytes may change. Both mapper tags '
              'and every unrelated host/state/map/table/header/clock byte remain guarded.',
        limitations=['Test-only mapped RAM; no host ownership lifetime or cold-load/IRQ/NMI admission.',
                     'Source-world map remains a fixture, not an SMB terrain query adapter.',
                     'No Sonic menu/raw identity/native gameplay/ROM change.'],
        bindings={str(p.relative_to(R)):digest(p.read_bytes())for p in
                  [Path(__file__),Path(Build.__file__),Path(Frozen.__file__),Build.SOURCE,Build.BINARY,
                   Build.SOURCE.parent/'proof.json',R/'docs/qa/allocations/sonic-sms-fairy-repack-1110.json']})
    print(json.dumps(report,separators=(',',':')),flush=True)


if __name__=='__main__':
    main()
