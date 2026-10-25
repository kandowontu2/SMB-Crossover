"""Linked original threshold tables, all512 level sets and deferred choices."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,Memory,address,location
from verify_native_relocation import NesMPU

def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.rom)
    for line in a.rom.with_suffix('.dbg').read_text().splitlines():
        if not line.startswith('sym\t'):continue
        z=dict(v.split('=',1)for v in line[4:].split(',')if '=' in v)
        if z.get('name')=='"ThresholdLo"' and z.get('scope')=='1':b['syms']['ThresholdLo']=z
    source=Path('C:/NES/Zelda II - The Adventure of Link (USA).nes').read_bytes()
    def invoke(m,n):
        c=NesMPU(memory=m,pc=address(b,n));c.sp=0xed;c.stPushWord(0x5aff)
        for _ in range(10000):
            if c.pc==0x5b00:return c
            c.step()
        raise AssertionError(('CPU timeout',n,hex(c.pc)))
    def put(m,n,v):m[address(b,n)]=v&255
    def get(m,n):return m[address(b,n)]
    thresholds=[[200,500,1000,2000,3000,5000,8000,9000],
        [100,300,700,1200,2200,3500,6000,9000],[50,150,400,800,1500,2500,4000,9000]]
    # Authenticate the24linked prices directly against the original USA PRG.
    expected=[int.from_bytes(bytes([source[16+0x1670+cat*8+level+1],source[16+0x1658+cat*8+level+1]]),'little') for cat in range(3) for level in range(8)]
    # Original tables include a zero slot before level1's first price.
    linked=[]
    for name in ['ThresholdLo','ThresholdHi']:
        at=location(b,name);linked.append(list(b['raw'][at:at+24]))
    assert [linked[0][i]+256*linked[1][i] for i in range(24)]==sum(thresholds,[])
    # The prior source-authentication report pins these original ROM tables;
    # retain exact table bytes here, without relying on hand-entered prices.
    assert expected==sum(thresholds,[]),'Original USA tables, native levels1..8'
    cases=defer=0
    for levels,mask in itertools.product(itertools.product(range(8),repeat=3),range(7)):
        m=Memory(b);m.page(1,(location(b,'Z2NextThreshold')-16)//8192)
        put(m,'Z2LevelsLo',levels[0]|levels[1]<<3|(levels[2]&3)<<6)
        put(m,'Z2LevelsHi',128|(levels[2]>>2));put(m,'Z2DeferredMask',mask)
        costs=[thresholds[c][levels[c]] for c in range(3)]
        target=min(v for c,v in enumerate(costs) if not mask&(1<<c))
        invoke(m,'Z2NextThreshold');assert get(m,'R0')+256*get(m,'R1')==target,(levels,mask)
        cases+=1
        for exp in [0,target-1,target,target+1,9000]:
            put(m,'Z2DeferredMask',mask);put(m,'Z2ExpLo',exp);put(m,'Z2ExpHi',exp>>8)
            c=invoke(m,'Z2Defer');nextmask=mask
            if exp>=target:
                for i,v in enumerate(costs):
                    if v==target:nextmask|=1<<i
            accepted=nextmask!=7
            assert bool(c.p&1)==accepted,(levels,mask,exp,'accept')
            assert get(m,'Z2DeferredMask')==(nextmask if accepted else mask)
            defer+=1
    q=dict(passed=True,ROM_sha256=hashlib.sha256(a.rom.read_bytes()).hexdigest(),
        original_ROM_sha256=hashlib.sha256(source).hexdigest(),threshold_sets=cases,
        cancel_boundary_cases=defer,original_24_prices_byte_authenticated=True,
        scope='Actual linked CPU numeric/UI leaves; native control, rendering and restoration are separate checks.')
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
