"""Move Mini's native lift admission to camera-right; never use player proximity."""
import argparse
import json
from pathlib import Path
from itertools import product

import measure_mini_audio_1108_v1 as M
from profile_mini_busy_1108_v1 import fixture
from check_mini_lift_admission_fast_1108_v1 import setup_main

ROOT = M.ROOT
BASE = ROOT/'build/mini-box-terrain-visible-1110/candidate.nes'
PIN = '6af068b73709880ee5e2e07c8d9c9df1724bde1774f2dc67f16dff32bb73d018'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--camera-gate', action='store_true')
    args = ap.parse_args()
    out = args.output
    out.mkdir(exist_ok=True)
    raw = BASE.read_bytes()
    assert M.sha(raw) == PIN
    bundle = M.bundle(raw)
    fast = (ROOT/'tools/reference/mini_lift_admission_fast_1108_v1.s').read_text()
    admission = (ROOT/'tools/reference/mini_lift_admission_1108_v1.s').read_text()
    spawn = (ROOT/'tools/reference/mini_lift_spawn_1108_v1.s').read_text()
    definitions = fast.split('.segment')[0]
    scan = fast.split('.segment "MINI_LIFT_SCAN"\n')[1].split('.segment')[0]
    scan = definitions+'MiniLiftScopeBank=$ae6e\nScanBits=$ae7d\n'+scan
    newer_scan = scan.replace('Player_PageLoc = $5c', 'Player_PageLoc = $071e').replace(
        'Player_X_Position = $75', 'Player_X_Position = $0720')
    # Same scan windows now describe the camera right edge. Their lower bounds
    # are precisely 32px before each native left edge: 528,656,832.
    allocate = admission.split('.segment "MINI_LIFT_ALLOCATE"\n')[1].split('.segment')[0]
    defs = ''.join(f'{n}=${M.address(bundle,n):04x}\n' for n in ('Enemy_Flag','Enemy_ID','Enemy_State'))
    allocate = defs+'MiniLiftActor=$c30b\nMiniLiftSpawnBank=$bfe3\n'+allocate
    newer_allocate = allocate.replace('Construct:\n', 'Construct:\n    ldy $071e ; Camera right page, retained by native farcall.\n')
    spawn = spawn.replace('.segment "MINI_LIFT_SPAWN"', '.segment "CODE"').replace('.ifdef MINI_LIFT_CHAIN', '.if 1')
    newer_spawn = spawn.replace('    lda Player_PageLoc\n', '    tya\n    nop ; Preserve the exact constructor extent and public addresses.\n')
    patches = []
    changed = bytearray(raw)
    for name, bank, pc, capacity, fill, before, after in (
        ('scan',24,0xbbcf,49,0xff,scan,newer_scan),
        ('allocate',36,0xb6d0,48,0xff,allocate,newer_allocate),
        ('spawn',78,0xbcc7,57,0xff,spawn,newer_spawn),
    ):
        old,_ = M.assemble(out/(name+'-old'),before,pc,capacity)
        new,_ = M.assemble(out/(name+'-new'),after,pc,capacity)
        old=old.ljust(capacity,bytes([fill]));new=new.ljust(capacity,bytes([fill]))
        at=16+bank*8192+(pc&8191)
        assert raw[at:at+capacity]==old,(name,'source preimage')
        assert len(new)==capacity
        changed[at:at+capacity]=new
        patches.append(dict(file_offset=at,old_hex=old.hex(),new_hex=new.hex(),role=name))
    if args.camera_gate:
        import hashlib
        kernel_path=ROOT/'build/mini-kernel-transport-1109/v2/kernel.bin'
        old_kernel=kernel_path.read_bytes()
        signature=bytes.fromhex('a55c38e902c902b0')
        assert old_kernel.count(signature)==1
        index=old_kernel.index(signature)
        # Same eight bytes; compare the camera page rounded down to even.
        # Only pages2/3 enter the lift scan. The following displacement stays.
        new_kernel=old_kernel.replace(signature,bytes.fromhex('ad1e0729fec902d0'))
        at=lambda page:1048592+1024*page
        def component(code):
            code=code.ljust(5120,b'\xff')
            # Preserve the current optimized cold loader/metadata exactly.
            # Validate the existing complete-payload cookie before rebinding.
            payload=code+raw[at(967):at(969)]
            return dict(code=code,cookie=bytes([0xa7,41,1])+hashlib.sha256(payload).digest()[:13])
        old_image=component(old_kernel)
        new_image=component(new_kernel)
        cookie=16+65*8192+0x1003
        for offset,before,after,role in ((at(962),old_image['code'],new_image['code'],'camera coarse gate'),
                                        (cookie,old_image['cookie'],new_image['cookie'],'Mini complete payload cookie')):
            assert raw[offset:offset+len(before)]==before
            changed[offset:offset+len(after)]=after
            patches.append(dict(file_offset=offset,old_hex=before.hex(),new_hex=after.hex(),role=role))
        (out/'kernel.bin').write_bytes(new_kernel)
        (out/'kernel.lbl').write_bytes(kernel_path.with_suffix('.lbl').read_bytes())
    b=M.bundle(changed)
    b['segs']['lift']=dict(start=str(0xbbcf),ooffs=str(16+24*8192+0x1bcf))
    b['syms']['MiniLiftTick']=dict(val=str(0xbbcf),seg='lift')
    seed=fixture(b,0,False,False)
    rows=[]
    for right,player,seen,occupied,area in product(
        (527,528,559,560,607,608,655,656,687,688,735,736,831,832,863,864,911,912),
        (40,400,720), (0,7), (False,True), (0,5)):
        m=M.N.fork(seed)
        setup_main(m,player,seen,0,area)
        M.N.put(m,ScreenLeft_X_Pos=(right-255)&255,ScreenLeft_PageLoc=(right-255)>>8,
                ScreenRight_X_Pos=right&255,ScreenRight_PageLoc=right>>8,CurrentBankC=2)
        m[0x5116]=2
        for slot in range(6):
            m[M.address(b,'Enemy_Flag')+slot]=int(occupied)
            m[M.address(b,'Enemy_ID')+slot]=6
        result=M.N.invoke(m,'MiniLiftTick',a=0,x=0,y=0,p=0x31)
        bit=1 if 528<=right<=607 else 2 if 656<=right<=735 else 4 if 832<=right<=911 else 0
        expected=bool(bit and not seen and not occupied and area==5)
        lifts=[s for s in range(6) if m[M.address(b,'Enemy_Flag')+s] and m[M.address(b,'Enemy_ID')+s]==0x25]
        assert bool(lifts)==expected,(right,player,seen,occupied,area,lifts)
        if expected:
            assert len(lifts)==1
            slot=lifts[0]
            x=m[M.address(b,'Enemy_X_Position')+slot]+256*m[M.address(b,'Enemy_PageLoc')+slot]
            assert x=={1:560,2:688,4:864}[bit],(right,player,x)
            assert m[M.address(b,'Enemy_Y_Position')+slot]==192
            assert m.ram[2][0x30c]==bit
        rows.append(result['CPU'])
    report=dict(passed=True,parent_SHA256=PIN,expected_memory_only_SHA256=M.sha(changed),patches=patches,
                cases=len(rows),cpu_range=[min(rows),max(rows)],camera_right_trigger=[528,656,832],
                native_left_edges=[560,688,864],initial_top=192,
                scope='Source-preimage and actual native constructor CPU proof; no native visibility, lifecycle or IRQ qualification yet.')
    (out/'proof.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='patches'}))


if __name__=='__main__':main()
