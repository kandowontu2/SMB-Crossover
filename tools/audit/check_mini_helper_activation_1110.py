"""Source-only qualification of camera-relative Mini lift activation."""

import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import tempfile

import check_mini_lift_seen_fast_1110 as Lift
import prepare_mini_contact_lag_native_1110 as Contact
from check_mini_funded_actor_1108_v3 import install, live_stack, registers, slim_fork
from measure_mini_kernel_transport_1109 import compile_source, replace_one


A,L,M,N,R = Lift.A,Lift.L,Lift.M,Lift.N,Lift.R
BASE = R/'build/mini-contact-lag-native-1110/candidate.nes'
PIN = 'd998e71bb6b6aacb7cd3f7f055cf74a791ba68de84347918c8ba27a2bf6fc300'
KERNEL = Contact.KERNEL
SCAN = R/'tools/reference/mini_lift_admission_fast_1108_v1.s'
WORKER,END = 0xbbcf,0xbc00
LEFTS = (560,688,864)
MINIMA = (552,680,856)
LIFT_STATE = (1,0x25,0x40)


def offset(bank,pc):
    return 16+bank*8192+(pc&8191)


def scan_source():
    source = SCAN.read_text()
    defs = source.split('.segment',1)[0]
    body = source.split('.segment "MINI_LIFT_SCAN"\n',1)[1].split('.segment',1)[0]
    defs = replace_one(defs,'Player_PageLoc = $5c','Player_PageLoc = $071e')
    defs = replace_one(defs,'Player_X_Position = $75','Player_X_Position = $0720')
    return defs+'MiniLiftScopeBank=$ae6e\nScanBits=$ae7d\n.segment "CODE"\n'+body


def candidate_source(source,width):
    source = replace_one(source,'cmp #80',f'cmp #{width}')
    return replace_one(source,'.byte $10,$90,$40','.byte $28,$a8,$58')


def kernel_source(source,width):
    lo = source.index('MiniLiftSeenFast:\n')
    hi = source.index('    .res $8c5-(*-MiniStep),$ea\n',lo)
    return source[:lo]+candidate_source(source[lo:hi],width)+source[hi:]


def build(raw,out,width):
    assert M.sha(raw)==PIN
    meta = json.loads(BASE.with_name('proof.json').read_text())
    assert meta['passed'] and meta['candidate_SHA256']==PIN and meta['kernel_SHA256']==M.sha(KERNEL.read_bytes())
    at = offset(24,WORKER)
    assert raw[at:at+END-WORKER]==Lift.ORIGINAL
    thunk = offset(24,0xae6e)
    assert raw[thunk:thunk+len(Lift.THUNK)]==Lift.THUNK
    old_scan = scan_source()
    proposal = replace_one(candidate_source(old_scan,width),'ora #$20','adc #8')
    old_source = KERNEL.with_suffix('.s').read_text()
    old_kernel = KERNEL.read_bytes()
    with tempfile.TemporaryDirectory(prefix='link-',dir=out) as tmp:
        work = Path(tmp)
        old,_ = M.assemble(work/'scan-old',old_scan,WORKER,END-WORKER)
        scan,_ = M.assemble(work/'scan-new',proposal,WORKER,END-WORKER)
        rebuilt,old_labels = compile_source(work,old_source,L.CONFIG)
    assert old==raw[at:at+len(old)]==Lift.ORIGINAL and len(scan)==len(old)==END-WORKER
    assert rebuilt==old_kernel==raw[L.CODE:L.CODE+5120]
    assert raw[L.COOKIE:L.COOKIE+16]==bytes((167,41,1))+A.digest(raw[L.CODE:L.CODE+7168])
    compiled,labels = compile_source(out,kernel_source(old_source,width),L.CONFIG)
    assert len(compiled)==len(old_kernel)==5120 and labels==old_labels
    changed = [i for i,(a,b) in enumerate(zip(old_kernel,compiled,strict=True)) if a!=b]
    assert len(changed)==4 and changed[1:]==list(range(changed[1],changed[1]+3)),changed
    assert bytes(compiled[i] for i in changed)==bytes((width,0x28,0xa8,0x58))
    cookie = A.digest(compiled+raw[L.CODE+5120:L.CODE+7168])
    patches = [L.patch(raw,at,scan,'current same-span native lift scan'),
               L.patch(raw,L.CODE+changed[0],bytes((width,)),'authenticated private seen scan width'),
               L.patch(raw,L.CODE+changed[1],bytes((0x28,0xa8,0x58)),'authenticated private seen scan minima'),
               L.patch(raw,L.COOKIE+3,cookie,'authenticated Mini payload digest')]
    after = install(raw,patches)
    assert after[L.CODE:L.CODE+5120]==compiled
    assert (out/'kernel.lbl').read_bytes()==KERNEL.with_suffix('.lbl').read_bytes()
    return after,patches,labels,changed


def slot_state(m):
    return tuple(L.snapshot(m,slot) for slot in range(6))


def init_case(seed,right,seen,occupied,owner=41,area=5,world=0,level=0,px=711):
    m = slim_fork(seed)
    L.setup_main(m,px,seen,0,area,world=world,level=level)
    L.camera(m,right)
    N.put(m,SelectedCharacter=owner)
    for slot in range(6):
        m[0x10+slot]=int(bool(occupied>>slot&1))
        m[0x17+slot]=6
    return m


def probe(seed,right,seen,occupied,width,owner=41,area=5,world=0,level=0,px=711):
    m = init_case(seed,right,seen,occupied,owner,area,world,level,px)
    before = slot_state(m)
    result = N.invoke(m,'MiniLiftTick',a=0,x=0,y=0,p=0x31)
    after = slot_state(m)
    index = next((i for i,start in enumerate(MINIMA) if start<=right<start+width),None)
    bit = 0 if index is None else 1<<index
    slot = None
    if owner==41 and area==5 and world==level==0 and not seen&bit and bit and occupied!=63:
        slot = max(i for i in range(6) if not occupied>>i&1)
    if slot is None:
        assert before==after and m.ram[2][0x30c]==seen,(right,seen,occupied,owner,area,world,level)
        return None,result['CPU']
    assert index is not None
    left = LEFTS[index]
    want = (*LIFT_STATE,left&255,left>>8,192,1,5)
    assert after[slot][:8]==want and all(before[s]==after[s] for s in range(6) if s!=slot),(right,slot,after)
    assert m.ram[2][0x30b]==slot+1 and m.ram[2][0x30c]==seen|bit
    return left-(right-255),result['CPU']


def cases(seed,width):
    stats = Counter()
    for right,seen in product(range(512,1024),range(8)):
        rel,_ = probe(seed,right,seen,0,width)
        stats['born' if rel is not None else 'no_candidate_or_seen'] += 1
        if rel is not None:
            stats['visible_birth' if rel<256 else 'offscreen_birth'] += 1
    for start,occupied,delta in product(MINIMA,range(64),(-1,0,7,8,55,56)):
        rel,_ = probe(seed,start+delta,0,occupied,width)
        stats['slot_mask_cases'] += 1
        if rel is not None:
            stats['slot_mask_visible_birth' if rel<256 else 'slot_mask_offscreen_birth'] += 1
    for start,owner,(area,world,level),px in product(MINIMA,range(42),
            ((0,0,0),(5,1,0),(5,0,1),(5,0,0)),(40,711,1000)):
        probe(seed,start,0,0,width,owner,area,world,level,px)
        stats['owner_area_camera_cases'] += 1
    for page in (*range(1,2),*range(4,256)):
        probe(seed,page*256+0x58,0,0,width)
        stats['outside_page_cases'] += 1
    return dict(stats)


def late_retry(seed,width):
    receipts = []
    for index,(start,left) in enumerate(zip(MINIMA,LEFTS,strict=True)):
        for free_at in (start+7,start+8,start+55,start+56):
            m = init_case(seed,start,0,63)
            old = slot_state(m)
            N.invoke(m,'MiniLiftTick',a=0,x=0,y=0,p=0x31)
            assert slot_state(m)==old and m.ram[2][0x30c]==0
            m[0x12] = 0
            L.camera(m,free_at)
            N.invoke(m,'MiniLiftTick',a=0,x=0,y=0,p=0x31)
            born = m.ram[2][0x30c]==1<<index
            assert born==(free_at<start+width)
            assert all(L.snapshot(m,s)==old[s] for s in range(6) if s!=2)
            if born:
                assert L.snapshot(m,2)[:8]==(*LIFT_STATE,left&255,left>>8,192,1,5)
            receipts.append(dict(initial_right=start,freed_right=free_at,world_left=left,
                                 initial_top=192,born=born,relative_left=left-free_at+255 if born else None))
    return receipts


def seen_equivalence(seed):
    count = 0
    # Compare the candidate's own all-seen leaf to its actual bank24 scan
    # with the identical activation data. Keep the ROM and cookie identical.
    for page,low,flags in product((1,2,3,4),range(256),(0x21,0x65)):
        right = page*256+low
        a,b = [init_case(seed,right,7,0) for _ in range(2)]
        b.ram[3][Lift.CALL-0xa000+1:Lift.CALL-0xa000+3] = b'\x5a\x01'
        old,new = [Lift.helper_call(m,flags,17,99) for m in (a,b)]
        assert registers(old)==registers(new) and live_stack(old)==live_stack(new),(right,flags)
        assert bytes(a[0x15a:0x17b])==bytes(b[0x15a:0x17b]),(right,flags)
        A.P.compare_memory(a,b,ram_exclusions={3:[(Lift.CALL-0xa000+1,Lift.CALL-0xa000+3)]})
        count += 1
    return count


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output',type=Path,required=True)
    cli.add_argument('--width',type=int,choices=(8,56),required=True)
    args = cli.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(R/'build') and not (out/'proof.json').exists()
    out.mkdir(exist_ok=True)
    raw = BASE.read_bytes()
    final,patches,labels,changed = build(raw,out,args.width)
    exact = [(i,i+1) for i in changed]
    cold,_ = A.exact_cold(raw,final,exact)
    seed = L.fixture(L.bundles(raw,final)[1],0,False,False)
    stats = cases(seed,args.width)
    retry = late_retry(seed,args.width)
    seen = seen_equivalence(seed)
    no_pop = not any(row['relative_left'] is not None and row['relative_left']<256 for row in retry)
    assert no_pop==(args.width==8)
    refs = (Path(__file__),SCAN,BASE,BASE.with_name('proof.json'),KERNEL,KERNEL.with_suffix('.s'),
            KERNEL.with_suffix('.lbl'),L.CONFIG,R/'src/common.s',out/'kernel.bin',out/'kernel.s',out/'kernel.lbl')
    proof = dict(passed=True,ROM_written=False,parent_SHA256=PIN,expected_memory_only_SHA256=M.sha(final),
                 patches=patches,exact_changed_code=exact,labels=labels,exact_cold=cold,width=args.width,
                 camera_right_minima=MINIMA,native_left_edges=LEFTS,initial_top=192,
                 strict_offscreen_retry=no_pop,late_slot_retry=retry,constructor_cases=stats,
                 private_seen_scan_equivalence_cases=seen,
                 bindings={str(p.resolve()):M.sha(p.read_bytes()) for p in refs})
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,width=args.width,memory_SHA256=M.sha(final),strict_offscreen_retry=no_pop,
                          constructor_cases=stats,private_seen_scan_equivalence_cases=seen)),flush=True)


if __name__=='__main__':
    main()
