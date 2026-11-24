"""Actual installed Prince transport/empty opening profile; stdout only.

Default: read-only CPU instrumentation. --hoist: explicitly translated
RAM-only component proposal. Neither mode generates an image or runs Mesen.
"""
from collections import Counter
import argparse
import json
from pathlib import Path
from unittest.mock import patch

import compose_prince_lift_reach_1123 as Reach
import profile_prince_empty_current_1123 as P

H,W,N,B=Reach.C.H,P.W,P.N,P.B
PIN='5c89b9b727a6c718edccd873bbdff69409e4280c7e0db4e1c3c169304c6a84c9'


def hoisted_plan(parent):
    """RAM component proposal: relocate an existing5B guard, no size grant."""
    once=Reach.L.F.Q.P.G.First.once
    def extend(text):
        text=Reach.compact_import(text)
        text=once(text,' jsr Allocator\n jsr Support\n bcc ImportDone',
                  ' jsr Eligible\n bcc ImportDone\n jsr Allocator\n jsr SupportUnchecked\n bcc ImportDone')
        return once(text,'Support:\n jsr Eligible\n bcc SweepNo\n',
                    'Support:\n jsr Eligible\n bcc SweepNo\nSupportUnchecked:\n')
    def allocator(origin,labels,bundle):
        # Link five bytes earlier so the retained camera/body has its actual
        # new addresses after dropping the transplanted guard.
        code=Reach.allocator(origin-5,labels,bundle)
        assert code[:3]==bytes((0x20,labels['Eligible']&255,labels['Eligible']>>8))
        assert code[3]==0x90
        return code[5:]
    def build(raw):
        return Reach.L.plan(raw,extend=extend,build_allocator=allocator,rewrite_core=Reach.rewrite_core)
    blob,labels,parts,packed,info=Reach.Sweep.compact_plan(parent,width=48,logical_history=True,builder=build)
    at=Reach.PICKUP_STAGE-0xc100;s=parts[2]
    assert s[at:at+len(Reach.OLD_PICKUP)]==Reach.OLD_PICKUP
    s=s[:at]+Reach.NEW_PICKUP+s[at+len(Reach.OLD_PICKUP):]
    packed[2]=Reach.C.Packet.encode(s)
    return blob,labels,parts[:2]+(s,),packed,info


def hoist_units(raw,m,chunks):
    F=Reach.L.F;parent=Reach.recover_parent(raw)
    blob,labels,parts,packed,info=hoisted_plan(parent)
    assert len(blob)==len(chunks[3])and parts[1:]==chunks[1:3]
    changed={i for i,(a,b)in enumerate(zip(chunks[0],parts[0]))if a!=b}
    assert changed and changed<=set(range(0x6fc,0x71b))|set(range(Reach.Projection.CODE-0xa000,Reach.Projection.CODE-0xa000+32))
    def load(old):
        new=N.fork(old);new.ram[1][:len(blob)]=blob
        for i in changed:new.ram[3][i]=parts[0][i]
        return new
    scenes=[('opening',N.fork(m))]
    for name,field,value in (
        ('foreign','SelectedCharacter',37),('engine','GameEngineSubroutine',7),
        ('world','WorldNumber',1),('level','LevelNumber',1),('timer','TimerControl',1),
        ('pause','GamePauseStatus',1),('area','AreaAddrsLOffset',4),('water','AreaType',0),
        ('offscreen','Player_Y_HighPos',2)):
        q=N.fork(m);N.put(q,**{field:value});scenes.append((name,q))
    for name,offset in(('unready',0xab),('dead',0x6cf)):
        q=N.fork(m);q.ram[2][offset]=0;scenes.append((name,q))
    for camera in(720,721,752,753,934):
        q=N.fork(m);N.put(q,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8)
        for i in range(6):F.slot(q,'Enemy_Flag',0,i)
        scenes.append(('camera'+str(camera),q))
    for name,make in(('fresh',Reach.Sweep.fixture),('held',Reach.Sweep.held_fixture)):
        q=make(m);F.slot(q,'Enemy_BoundBoxCtrl',6);scenes.append((name,q))
    rows=[]
    for name,scene in scenes:
        for flags in(0x20,0x21,0x71,0xf1):
            a=N.fork(scene);b=load(scene)
            qa=F.private(a,0xb3d1,p=flags);qb=F.private(b,0xb3d1,p=flags)
            assert qa['regs']==qb['regs']and a.rawtags==b.rawtags and a.chr_latches==b.chr_latches,(name,flags)
            native_diff=[i for i,(x,y)in enumerate(zip(a[:0x800],b[:0x800]))if x!=y]
            assert all(0x17b<=i<=0x1e0 for i in native_diff),(name,native_diff)
            for bank in range(len(a.ram)):
                skip=set(range(len(blob)))if bank==1 else changed if bank==3 else set()
                assert all(x==y or i in skip for i,(x,y)in enumerate(zip(a.ram[bank],b.ram[bank]))),(name,bank)
            rows.append(dict(scene=name,input_P=flags,old=qa['cycles'],new=qb['cycles'],saved=qa['cycles']-qb['cycles']))
    extracted=Reach.C.extract(raw)
    remaining=len(Reach.C.Packet.PAGES)*1024-extracted[3]
    delta=sum(map(len,packed))-sum(r[2]for r in extracted[1])
    return dict(paired_Import_calls=len(rows),rows=rows,raw1_bytes=len(blob),raw1_SHA256=H(blob),
        current_packed_lengths=[r[2]for r in extracted[1]],proposed_packed_lengths=list(map(len,packed)),
        current_carrier_spare=remaining,proposed_spare_with_same_loader=remaining-delta,
        equal_raw_size=True,AXYPSP_native_private_state_maps_CHR_equal=True,
        dead_stack_only_excluded=True,no_image_composed=True,full_linked_or_ISR_or_native_not_claimed=True)


def cold(raw):
    assert H(raw)==PIN
    parent=Reach.recover_parent(raw)
    assert H(parent)==P.PIN
    prior=P.authentication(parent)
    chunks,_,cookie,_=Reach.C.extract(raw)
    assert chunks[1]==P.Prince.Packet.extract(parent)[1][1]
    def auth(image):assert image==raw;return prior
    function=P.Prince.clone(P.Prince.cold,dict(authenticate=auth,COOKIE=cookie.hex()))
    return function(raw),chunks


class Trace(P.D.Trace):
    def __init__(self,m,raw1):
        super().__init__(m)
        self.far=Counter();self.maps=Counter();self.private=Counter()
        signature=bytes.fromhex('ad0260c926')
        assert raw1.count(signature)==1
        self.eligible=0xa000+raw1.index(signature)

    def run(self,c,stop):
        original=c.step;m=self.m;common=W.address(m.bundle,'FarCallCommon')
        def step():
            pc=c.pc;tag=m.rawtags[(pc-0x8000)//8192]if pc>=0x8000 else -1
            if pc==common:
                dest=m[0x16c]+256*m[0x16d]
                self.far[(m.rawtags[1],m.rawtags[2],c.a,dest,c.a==m.rawtags[1])]+=1
            if tag==1 and pc in(0xa000,self.eligible):self.private[(tag,pc)]+=1
            if tag in(2,3)and pc in(0xb36e,0xc312,0xbde2,0xb310):self.private[(tag,pc)]+=1
            opcode=m[pc]
            if opcode in(0x8d,0x8e,0x8c):
                target=m[(pc+1)&65535]+256*m[(pc+2)&65535]
                if target in(0x5115,0x5116):
                    value={0x8d:c.a,0x8e:c.x,0x8c:c.y}[opcode]
                    current=m.rawtags[1 if target==0x5115 else 2]
                    self.maps[(tag,pc,target,current,value,current==value)]+=1
            return original()
        c.step=step
        try:return super().run(c,stop)
        finally:c.step=original


def installed_profile(raw):
    """Profile either verified November 23 pipe build with ordinary controls."""
    import check_prince_pipe_controls_1123 as Pipe

    assert H(raw) in (Pipe.Reverse.CANDIDATE, Pipe.CapSupport.CANDIDATE)
    cookie = Pipe.authenticate(raw)['cookie']
    load = P.Prince.clone(P.Prince.cold, dict(authenticate=Pipe.authenticate, COOKIE=cookie))
    model = load(raw)
    private = Pipe.packet(raw)[0][3]
    for _ in range(4):
        B.main_step(model, 0)
    phases = {}
    for name, pad, count in (('standing', 0, 8), ('walking', 1, 32)):
        trace, rows = Trace(model, private), []
        for _ in range(count):
            assert not any(B.flags(model))
            main, nmi = B.main_step(model, pad, trace)
            assert not any(B.flags(model)) and model.ram[2][0x6cf] == 5
            assert N.get(model, 'NumberofLives') == 2
            rows.append(dict(main_cycles=main, NMI_cycles=nmi, x=B.position(model)))
        profile = trace.summary(rows)
        phases[name] = dict(updates=count, first=rows[0], last=rows[-1],
                            mean_main_cycles=profile['mean_main_cycles'],
                            mean_logical_nmi_cycles=profile['mean_logical_NMI_cycles'],
                            hot_regions=profile['hot_regions'][:16], far_calls=profile['hot_FarCallCommon'][:20],
                            mapper_writes_per_update=sum(trace.maps.values()) / count)
    assert phases['walking']['last']['x'] > phases['standing']['last']['x']
    receipt = dict(ROM=H(raw), phases=phases)
    canonical = json.dumps(receipt, sort_keys=True, separators=(',', ':'))
    print('PRINCE CURRENT TRANSPORT ' + json.dumps(dict(receipt, receipt_SHA256=H(canonical.encode())),
                                                    separators=(',', ':')), flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--hoist',action='store_true')
    mode.add_argument('--installed',action='store_true')
    args=parser.parse_args()
    raw=P.D.Old.ROM.read_bytes()
    if args.installed:
        installed_profile(raw)
        return
    assert H(raw)==PIN
    def deny(*a,**k):raise AssertionError('Transport profile attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):
        m,chunks=cold(raw)
        for _ in range(4):B.main_step(m,0)
        if args.hoist:
            result=hoist_units(raw,m,chunks)
            digest=H(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
            print('PRINCE_HOIST_COMPONENT '+json.dumps(dict(passed=True,ROM=PIN,result=result,SHA256=digest,outputs=0),separators=(',',':')),flush=True)
            return
        phases={}
        for name,pad in(('standing',0),('walking',1)):
            warm=0
            if pad:
                start=B.position(m)
                while B.position(m)<=start:
                    B.main_step(m,pad);warm+=1;assert warm<=96
            trace=Trace(m,chunks[3]);rows=[]
            for i in range(8):
                assert not any(B.flags(m))
                x=B.position(m);cycles,nmi=B.main_step(m,pad,trace)
                s=P.grounded(m,False)
                assert not any(B.flags(m))and N.get(m,'NumberofLives')==2 and m.ram[2][0x6cf]==5
                rows.append(dict(update=i,x_before=x,x_after=B.position(m),main_cycles=cycles,NMI_cycles=nmi,source=s))
            profile=trace.summary(rows)
            profile['hot_instructions']=profile['hot_instructions'][:12]
            profile['hot_regions']=profile['hot_regions'][:16]
            profile['hot_FarCallCommon']=profile['hot_FarCallCommon'][:14]
            profile.update(warmup=warm,private_entries=[dict(bank=k[0],PC=hex(k[1]),per_Main=v/8)for k,v in trace.private.items()],
                mapper_writes=[dict(bank=k[0],PC=hex(k[1]),register=hex(k[2]),before=k[3],after=k[4],redundant=k[5],per_Main=v/8)
                    for k,v in trace.maps.most_common()],
                FarCall_contexts=[dict(A=k[0],C=k[1],requested=k[2],target=hex(k[3]),same_A=k[4],per_Main=v/8)
                    for k,v in trace.far.most_common()])
            phases[name]=profile
            print('PRINCE_TRANSPORT_PHASE '+json.dumps(dict(phase=name,profile=profile),separators=(',',':')),flush=True)
    result=dict(passed=True,ROM=PIN,parent=P.PIN,phases=phases,
                all_ordinary_returns=True,strict_State0_sample=False,normal_logical_NMI=True,
                DMA_stalls_or_native_cadence_qualified=False,outputs=0)
    digest=H(json.dumps(result,sort_keys=True,separators=(',',':')).encode())
    print('PRINCE_TRANSPORT_RECEIPT '+json.dumps(dict(passed=True,SHA256=digest,ROM=PIN,outputs=0),separators=(',',':')),flush=True)


if __name__=='__main__':main()
