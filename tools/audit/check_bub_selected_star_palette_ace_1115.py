"""Exact selected-Star mapper source gates; stdout, no artifact outputs."""
import argparse
from collections import Counter
from hashlib import sha256
import inspect
import json
from types import SimpleNamespace

from py65.devices.mpu6502 import MPU
import compose_bub_selected_star_palette_ace_1115 as C
from check_ff_head_lifetime_irq_1110 import clone

B, W, N = C.B, C.W, C.N
LAB = json.loads((C.R/'build/bub-upgrades-root-1102-v48/proposal.json').read_text())['labels']
DOMAINS = [(0x2e,0),(0x42,8)]+[(x,0x10+(x-0x68)*2)for x in range(0x68,0x80,4)]+[(x,0x88+(x-0x88)*2)for x in range(0x88,0xc4,4)]


def expected(identity,y,timer,value,native):
    if identity in(0,1)and y<16 and timer:
        return(value&252)|(native&3)
    return value&252 if identity==0 and value&3==3 else value


class Memory(list):
    recording=False
    def __setitem__(self,at,value):
        if self.recording:self.writes.append(at)
        return super().__setitem__(at,value)


def finite(raw):
    memory=Memory([0]*65536);memory[0xa000:0xc000]=C.code(raw)
    cpu=MPU(memory=memory);counts=Counter();cycles=Counter();minimum=255
    def case(identity,y,timer,native,value,p,side,group):
        nonlocal minimum
        memory.recording=False;memory[0xc300]=identity;memory[0x79c]=timer
        memory[0x587]=native;at=0xc102+side+y;memory[at]=value
        cpu.pc,cpu.sp,cpu.a,cpu.x,cpu.y,cpu.p=(0xb43e if side==0 else 0xb438),236,85,(value+native)&255,y,p
        cpu.stPushWord(0x5aff);memory.writes=[];memory.recording=True;start=cpu.processorCycles
        for _ in range(40):
            if(cpu.pc,cpu.sp)==(0x5b00,236):break
            cpu.step();minimum=min(minimum,cpu.sp)
        else:raise AssertionError('Finite mapper bound')
        memory.recording=False
        e=expected(identity,y,timer,value,native)
        ep=(p&~130)|(128 if e&128 else 0)|(2 if e==0 else 0)
        assert(cpu.a,cpu.x,cpu.y,cpu.sp,cpu.p)==(e,(value+native)&255,y,236,ep),(group,identity,y,timer,native,value,p,side)
        assert memory[at]==value and memory[0x587]==native
        assert all(0x100<=at<0x200 for at in memory.writes),memory.writes
        counts[group]+=1;cycles[group,cpu.processorCycles-start]+=1
    # Full byte cross product at both entries, both selected identities.
    for identity in(0,1):
      for side in(0,4):
       for native in range(256):
        for value in range(256):case(identity,identity*8,35,native,value,0x61,side,'all_attribute_native_bytes')
    # Status/data factor: all256 statuses, attributes, four palette phases.
    # Every instruction that reads P sees only N/Z freshly set by its own
    # load/logic. The full native high-bit product is covered above.
    for identity in(0,1):
      for side in(0,4):
       for native in range(4):
        for value in range(256):
         for p in range(256):case(identity,identity*8,1,0xa0|native,value,p,side,'all_status_attribute_phases')
    # All legal scan rows, inactive selected hero, foreign identities; no
    # synthetic malformed-Y invocation is called a legal gameplay caller.
    for identity in(0,1,2,255):
      for x,y in DOMAINS:
       for timer in(0,35):
        for side in(0,4):
         for value in range(256):case(identity,y,timer,0xe2,value,0xe9,side,'legal_rows_inactive_foreign')
    return dict(passed=True,actual6502_cases=dict(counts),factorization_explicit=True,
        all256native_attributes_and256original_attributes=True,all256statuses_bothentries=True,
        cycles={group:sorted(c for(g,c)in cycles if g==group)for group in counts},
        minimum_SP=minimum,only_stack_writes=True,X_Y_SP_CVID_exact=True,NZ_matches_mapped_A=True)


def call(m,pc,*,x=0x2e,y=0,p=0x61,observe=None):
    c=N.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=83,x,y,p,224;c.stPushWord(0x5aff)
    start=c.processorCycles
    for _ in range(300000):
        if(c.pc,c.sp)==(0x5b00,224):return c,c.processorCycles-start
        if observe:observe(m,c)
        assert m[c.pc],('BRK',hex(c.pc));c.step()
    raise AssertionError(('Call bound',hex(pc),hex(c.pc)))


def setup(seed):
    m=clone(seed);m.raw_page(1,3);m.raw_page(2,2)
    N.put(m,CurrentBank=3,CurrentBankC=2,CurrentOAMOffset=0,GuestOamRotationActive=0,NmiDisable=255)
    return m


def cold(raw):
    import replay_bub_combined_route_1113 as Old
    source=inspect.getsource(Old.cold_contracts)
    source=source.replace('parent=U.combined_reverse(raw)','parent=Current.inverse(raw)',1)
    source=source.replace('sha256(parent).hexdigest()==B.PIN','sha256(parent).hexdigest()==Current.PIN',1)
    source=source.replace('a72702dac1da2fc79faa02b5b5381392',raw[C.COOKIE:C.COOKIE+16].hex())
    ns=dict(Old.__dict__,Current=C,PIN=C.CANDIDATE)
    exec(compile(source,__file__+':actual-current-cold','exec'),ns)
    return ns['cold_contracts'](raw)


def paired_fields(a,b,*,allowed_pose=(),allowed_oam=()):
    for bank in range(len(a.ram)):
      for at,(x,y)in enumerate(zip(a.ram[bank],b.ram[bank])):
        if x==y:continue
        assert(bank,at)in allowed_pose,('private state',bank,hex(at),x,y)
    for at in range(0x800):
        if a[at]!=b[at]:assert at in allowed_oam,('native state',hex(at),a[at],b[at])
    assert a.rawtags==b.rawtags and bytes(a.vram)==bytes(b.vram)


def normalize_static(m,parent):
    m.ram[3][0x1438:0x1470]=C.code(parent)[0x1438:0x1470]
    for bank in(2,3):m.ram[bank][0x1fe0:0x1ff0]=C.OLD_COOKIE


def pair(raw):
    parent=C.inverse(raw);counts=Counter();cost=Counter()
    for identity in(0,1):
        seeds=[B.cold(image,identity)[0]for image in(parent,raw)]
        # Declared visual component fixtures, not natural pickups or actors.
        for x,y in (row for row in DOMAINS if row[1]>=16 or row[1]==identity*8):
          for timer in(0,1,35):
           for phase in range(4):
            for left,right in((0,255),(0x23,0xe3),(0x43,0x81),(0xff,0x7f)):
             models=[];cpus=[];cycles=[]
             for seed in seeds:
                m=setup(seed);N.put(m,StarInvincibleTimer=timer,Player_SprAttrib=0xa0|phase)
                for at,value in((0xc100,100),(0xc104,100),(0xc103,96),(0xc107,104),
                                 (0xc101,0),(0xc105,2),(0xc102,left),(0xc106,right)):
                    m.ram[2][at+y-0xc000]=value
                cpu,cy=call(m,LAB['BbNativePair'],x=x,y=y,p=0xe9)
                models.append(m);cpus.append(cpu);cycles.append(cy)
             a,b=models;ca,cb=cpus
             assert(ca.a,ca.x,ca.y,ca.p,ca.sp)==(cb.a,cb.x,cb.y,cb.p,cb.sp)
             ea,eb=(expected(identity,y,timer,v,phase)for v in(left,right))
             assert b.ram[2][0x3e6]==ea and b.ram[2][0x3e2]==eb
             # MetaspriteRenderLoop consumes records from length down to0;
             # C3E6(left) is emitted first, C3E2(right) second.
             assert b[0x202]==ea&0xf3 and b[0x206]==eb&0xf3,(
                 identity,x,y,timer,phase,left,right,b[0x202],b[0x206],ea,eb)
             normalize_static(b,parent)
             paired_fields(a,b,allowed_pose={(2,0x3e2),(2,0x3e6)},allowed_oam={0x202,0x206})
             for at,v in((0x102+y,left),(0x106+y,right)):assert b.ram[2][at]==v
             counts['selected'if y<16 else'scan']+=1
             cost[identity,'active'if timer else'inactive','hero'if y<16 else'scan',cycles[1]-cycles[0]]+=1
    return dict(passed=True,actual_full_Pair_cases=dict(counts),all22legal_XY_rows_per_identity=True,
        upper_NO_PALETTE_flip_priority_and_private_data_exact=True,
        actual_pair_cost_deltas=[dict(identity=i,star=t,caller=k,cycles=d,count=n)for(i,t,k,d),n in sorted(cost.items())],
        scope='Declared complete visual caller fixtures; no natural actor/item claim')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--gate',choices=('finite','cold','pair'),required=True);args=ap.parse_args()
    parent=C.load_current();raw,composition=C.proposal(parent);assert C.inverse(raw)==parent
    result={'finite':finite,'cold':cold,'pair':pair}[args.gate](raw)
    text=json.dumps(result,sort_keys=True,separators=(',',':'))
    print('RESULT '+json.dumps(dict(gate=args.gate,composition=composition,result=result,
        receipt_SHA256=sha256(text.encode()).hexdigest(),output_files=0),separators=(',',':')),flush=True)


if __name__=='__main__':main()
