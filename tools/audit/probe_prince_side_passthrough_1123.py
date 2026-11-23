"""Prince BED1 versus existing BF90 native-side tail, actual c1 CPU paths.

Explicit source component contexts; no ROM patches, image files or Mesen.
"""
from collections import Counter
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import check_prince_epoch_current_1123 as Q

E,N,W,B=Q.Epoch,Q.N,Q.W,Q.B
H=E.H


def tag(m,pc):return m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else -1


def prepared(seed,a,y,p):
    m=N.fork(seed)
    m.raw_page(1,161);m.raw_page(2,201)
    N.put(m,CurrentBank=161,CurrentBankC=201)
    m[0x16a]=a;m[0x16c]=0xb0;m[0x16d]=0xbf;m[0x179]=38;m[0x162]=0x9c
    c=N.NesMPU(memory=m,pc=0xbee9)
    c.a,c.x,c.y,c.p,c.sp=a,0,y,p,224
    c.stPushWord(0x5aff);c.stPush(p|0x30)
    for _ in range(20):
        if c.pc==0xbed1:break
        c.step()
    else:raise AssertionError('Actual selected38 BED1 prefix')
    assert c.a==38 and c.sp==220
    return m,c


def execute(m,c,direct=False,gated=False):
    if direct:c.pc=0xbf90
    if gated:c.pc=0xbfa4
    initial_cycles=c.processorCycles
    probes=[];sites=[];far=[];minimum=c.sp
    for _ in range(30000):
        if c.pc==0x5b00:break
        minimum=min(minimum,c.sp)
        where=tag(m,c.pc)
        if c.pc==0x15a:far.append([c.a,hex(m[0x16c]+256*m[0x16d])])
        if (where,c.pc)in((193,0xb0b6),(2,0xdf1e),(2,0xdf8d),(193,0xaf27),(213,0xa8dc)):
            sites.append([where,hex(c.pc)])
        if c.pc==0x958b and where==254:
            probes.append(dict(A=c.a,X=c.x,Y=c.y,P=c.p,SP=c.sp,
                native_y=N.get(m,'Player_Y_Position'),speed=N.get(m,'Player_Y_Speed'),
                scratch=list(m[0:11]),maps=list(m.rawtags)))
        assert m[c.pc],('Side component BRK',hex(c.pc),m.rawtags)
        c.step()
    else:raise AssertionError(('Side return bound',hex(c.pc),m.rawtags))
    assert c.sp==224
    return dict(regs=[c.a,c.x,c.y,c.p,c.sp],CPU=c.processorCycles-initial_cycles,probes=probes,sites=sites,far=far,minimum_SP=minimum)


def root_guard(parent,image):
    import compose_prince_side_current_1123 as S
    guarded,_=S.compose(parent)
    assert H(guarded)==S.CORRECTED
    seed=Q.enter(image,'Prince')
    def prepare(scene,rom,a,y,p):
        m=N.fork(scene);m.bundle=dict(m.bundle,raw=rom)
        for window,rawtag in enumerate(m.rawtags):
            if rawtag&128:m.raw_page(window,rawtag)
        m.raw_page(1,161);m.raw_page(2,201);N.put(m,CurrentBank=161,CurrentBankC=201)
        m[0x16a]=a;m[0x16c]=0x17;m[0x16d]=0xe2
        c=N.NesMPU(memory=m,pc=0xbea2);c.a,c.x,c.y,c.p,c.sp=a,0,y,p,224
        c.stPushWord(0x5aff)
        for _ in range(40):
            if c.pc==0xbed1:break
            c.step()
        else:raise AssertionError('Actual BEA2 prefix to BED1 hook')
        assert(m[0x16c],m[0x16d])==(0xb0,0xbf),'Prefix repairs stale incoming FarLo/FarHi'
        return m,c
    names=('cold_valid','cold_no_headers','cold_no_payload','cold_bad_C2','cold_bad_A3',
           'hot_valid','hot_no_epoch','hot_bad_C2','hot_bad_A3','hot_pause','hot_water')
    rows=[];count=0
    for name in names:
        scene=N.fork(seed)
        if name.startswith('hot_'):
            scene[0x5fff]=1;scene[0x1f9]=0x52;scene[0x1fa]=0x83
            scene[0xe]=scene.ram[2][0xa9]=40;scene.ram[2][0xaa]=1
            N.put(scene,GameEngineSubroutine=8,GamePauseStatus=0,TimerControl=0)
        if name in('cold_no_headers','hot_bad_C2','cold_bad_C2'):scene.ram[2][0x1fe0]=0
        if name in('cold_no_headers','hot_bad_A3','cold_bad_A3'):scene.ram[3][0x1fe0]=0
        if name=='cold_no_payload':scene.ram[2][:]=bytes(8192);scene.ram[3][:]=bytes(8192)
        if name=='hot_no_epoch':scene.ram[2][0xaa]=0
        if name=='hot_pause':N.put(scene,GamePauseStatus=1)
        if name=='hot_water':N.put(scene,AreaType=0,SwimmingFlag=1)
        for a in(0,0xa5):
            for y in(52,55):
                for p in(0x20,0xf1):
                    left,c=prepare(scene,image,a,y,p);right,d=prepare(scene,guarded,a,y,p)
                    before=[bytes(scene.ram[i][0x1fe0:0x1ff0])for i in(2,3)]
                    old=execute(left,c);new=execute(right,d)
                    assert old['regs']==new['regs']and len(old['probes'])==len(new['probes']),(name,old,new)
                    assert left.rawtags==right.rawtags and left.chr_latches==right.chr_latches
                    nd=[i for i,(x,z)in enumerate(zip(left[:0x800],right[:0x800]))if x!=z]
                    assert all(i in(0x162,0x16c,0x16d,0x179)or 0x17b<=i<=0x1e0 for i in nd),(name,nd)
                    pd=[(bank,i)for bank in range(len(left.ram))for i,(x,z)in enumerate(zip(left.ram[bank],right.ram[bank]))if x!=z]
                    assert all(bank==2 and i==0x1f32 for bank,i in pd),(name,pd)
                    assert [bytes(right.ram[i][0x1fe0:0x1ff0])for i in(2,3)]==before
                    assert new['far'][0]==[213,'0xb0b0']
                    fast=len(new['far'])==1
                    if not fast:
                        assert new['far'][1:]==old['far'],(name,old['far'],new['far'])
                        assert new['far'][1]==[217,'0xbc58'],'Legacy restores its own FarLo/FarHi'
                        assert (left[0x16c],left[0x16d])==(right[0x16c],right[0x16d])
                    if a==0 and y==52 and p==0x20:
                        rows.append(dict(context=name,fast=fast,old=old,new=new,
                            final_FarLo_FarHi=[right[0x16c],right[0x16d]],private_diff=[[b,hex(i)]for b,i in pd]))
                    count+=1
    return dict(ROM=H(guarded),baseline=H(image),cases=count,
        cold_entry_epoch=list(seed.ram[2][0xa9:0xac]),examples=rows,
        stale_initial_FarLo_FarHi_repaired_by_BEa2=True,
        every_rejected_guard_restores_original_legacy_dispatch=True,
        AXYPSP_native_gameplay_headers_maps_CHR_equal=True,
        excluded_native_transport_SMC_and_dead_stack=True,
        sole_private_difference_allowed='C2 DF32 dispatch JMP low, assigned before every DF31 range dispatch',
        full_Main_ISR_foreign_or_native_not_claimed=True)


def run(image):
    seed=Q.enter(image,'Prince')
    for _ in range(4):B.main_step(seed,0)
    assert bytes(seed.ram[2][0x1f8d:0x1f90])==bytes.fromhex('4c8b95')
    assert image[E.Shared.S.off(33,0xbf90):E.Shared.S.off(33,0xbf90)+5]==bytes.fromhex('68284c8b95')
    contexts=[('dry',{})]
    for name,fields in(
        ('water',dict(AreaType=0,SwimmingFlag=1)),
        ('pause',dict(GamePauseStatus=1)),('timer',dict(TimerControl=1)),
        ('not_engine8',dict(GameEngineSubroutine=7)),
        ('alternate_body',dict(PlayerSize=1,CrouchingFlag=1)),
        ('high',dict(Player_Y_Position=40)),('low',dict(Player_Y_Position=200))):
        contexts.append((name,fields))
    rows=[];seen=Counter();differences=Counter();equivalent=Counter();gated_count=0
    for name,fields in contexts+[('bad_C2',{}),('bad_A3',{}),('epoch_invalid',{}),
                                 ('active_main',{}),('active_bad_C2',{}),('active_bad_A3',{})]:
        scene=N.fork(seed);N.put(scene,**fields)
        if name=='bad_C2':scene.ram[2][0x1fef]^=1
        if name=='bad_A3':scene.ram[3][0x1fef]^=1
        if name=='epoch_invalid':scene.ram[2][0xaa]=0
        if name.startswith('active_'):
            scene[0x5fff]=1;scene[0x1f9]=0x52;scene[0x1fa]=0x83
            scene[0xe]=scene.ram[2][0xa9]=40;scene.ram[2][0xaa]=1
            N.put(scene,GameEngineSubroutine=8,GamePauseStatus=0,TimerControl=0)
            if name=='active_bad_C2':scene.ram[2][0x1fe0]=0
            if name=='active_bad_A3':scene.ram[3][0x1fe0]=0
        for a in(0,0xa5):
            for y in(52,53,54,55):
                for p in(0x20,0x21,0x71,0xf1):
                    left,c=prepared(scene,a,y,p)
                    right=N.fork(left)
                    d=N.NesMPU(memory=right,pc=0xbf90)
                    d.a,d.x,d.y,d.p,d.sp=c.a,c.x,c.y,c.p,c.sp
                    guarded=N.fork(left);g=N.NesMPU(memory=guarded,pc=0xbfa4)
                    g.a,g.x,g.y,g.p,g.sp=c.a,c.x,c.y,c.p,c.sp
                    old=execute(left,c);new=execute(right,d,True)
                    guard=execute(guarded,g,gated=True)
                    assert guard['regs']==old['regs']and len(guard['probes'])==len(old['probes']),(name,old,guard)
                    if old['probes']:
                        lp,gp=old['probes'][0],guard['probes'][0]
                        assert all(lp[k]==gp[k]for k in('Y','native_y','speed','scratch')),(name,lp,gp)
                    assert guarded.rawtags==left.rawtags and guarded.chr_latches==left.chr_latches
                    guarded_native=[i for i,(x,z)in enumerate(zip(left[:0x800],guarded[:0x800]))if x!=z]
                    assert all(i in(0x162,0x16c,0x16d,0x179)or 0x17b<=i<=0x1e0 for i in guarded_native),(name,guarded_native)
                    guarded_private=[(bank,i)for bank in range(len(left.ram))for i,(x,z)in enumerate(zip(left.ram[bank],guarded.ram[bank]))if x!=z]
                    assert all(bank==2 and i==0x1f32 for bank,i in guarded_private),(name,guarded_private)
                    gated_count+=1
                    same=old['regs']==new['regs'] and len(old['probes'])==len(new['probes'])==1
                    if old['probes']:
                        lp,rp=old['probes'][0],new['probes'][0]
                        # The arithmetic service router changes NZCV. 958B
                        # replaces them before any flag-dependent opcode.
                        same=same and all(lp[k]==rp[k]for k in('A','X','Y','native_y','speed','scratch'))
                    equivalent[name]+=same
                    if name not in('bad_C2','bad_A3','active_bad_C2','active_bad_A3'):
                        assert same,(name,a,y,p,old,new)
                    assert left.rawtags==right.rawtags
                    native_diff=[i for i,(x,z)in enumerate(zip(left[:0x800],right[:0x800]))if x!=z]
                    private_diff=[(bank,i)for bank in range(len(left.ram))for i,(x,z)in enumerate(zip(left.ram[bank],right.ram[bank]))if x!=z]
                    for i in native_diff:differences[('native',hex(i))]+=1
                    for bank,i in private_diff:differences[('RAM'+str(bank),hex(i))]+=1
                    key=(name,tuple(tuple(x)for x in old['sites']))
                    seen[key]+=1
                    if a==0 and y==52 and p==0x20:
                        rows.append(dict(context=name,old=old,direct=new,guarded=guard,native_diff=list(map(hex,native_diff)),
                            private_diff=[[bank,hex(i)]for bank,i in private_diff]))
    return dict(cases=sum(seen.values()),examples=rows,
        routes=[dict(context=k[0],sites=k[1],count=v)for k,v in seen.items()],
        equivalent_cases_by_context=dict(equivalent),
        existing_BFA4_guarded_route_equivalent_cases=gated_count,
        differing_locations=[dict(space=k[0],offset=k[1],cases=v)for k,v in differences.items()],
        intact_headers_same_native_data_inputs_and_returned_AXYPSP=True,
        unconditional_direct_not_equivalent_on_rejected_headers=True,
        incoming_NZCV_overwritten_before_use=True,
        mapped_bank_timing_and_transport_scratch_not_identical=True,
        full_Main_ISR_foreign_owner_or_native_not_claimed=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',action='store_true')
    args=parser.parse_args()
    parent=E.Reach.C.Lift.F.Q.P.G.ROM.read_bytes();assert H(parent)==E.PARENT
    def deny(*a,**k):raise AssertionError('Side audit attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        image,_=E.compose(parent)
        at=E.Shared.S.off(126,0x958b)
        assert image[at:at+12]==bytes.fromhex('a901a200488407b93ee11875')
        result=root_guard(parent,image)if args.root else run(image)
    report=dict(passed=True,ROM=result.get('ROM',H(image)),baseline=H(image),parent=H(parent),result=result,outputs=0)
    digest=H(json.dumps(report,sort_keys=True,separators=(',',':')).encode())
    print('PRINCE_SIDE_PASSTHROUGH '+json.dumps(dict(report,SHA256=digest),separators=(',',':')),flush=True)


if __name__=='__main__':main()
