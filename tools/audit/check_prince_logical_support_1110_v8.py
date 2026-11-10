"""Source-only logical careful support, derivative of frozen5174; zero files."""
import argparse
import contextlib
import io
import json
import re
import struct
import sys
from unittest.mock import patch
import check_prince_wall_sweep_1110_v6 as V
import check_prince_wait_pose_route_1110_v3 as Route

Q,C,N,I,F=V.Q,V.C,V.N,V.I,V.F
SOURCE=V.R/'tools/reference/prince_logical_support_1110_v8.s'
PIN='a9c08e84041ed0d86e806d84261febd63008a7686cdf9f1a17915f6f340ad0d8'


def code():
    text=SOURCE.read_text()
    sections=dict(re.findall(r'\.segment "([A-Z_]+)"\s*([\s\S]*?)(?=\.segment|$)',text))
    projection,labels=V.assemble(sections['PROJECTION'],0xbd4b)
    support,slab=V.assemble(sections['SUPPORT'],0xd6d1,labels)
    assert labels['LogicalSupport']==0xbd82,(len(projection),labels)
    assert len(projection)==87 and len(support)==133,(len(projection),len(support))
    previous=C.read(C.OUT/'proof.json')['layout']['entries']
    assert previous['PreviousHigh']+1==0xd4a6 and previous['PreviousSole']+1==0xd4b1
    return projection,support,dict(labels,**slab)


def apply(m):
    projection,support,labels=code()
    old=(V.R/'build/prince-actor-1101-v1/host-render-v11.bin').read_bytes()
    assert bytes(m.ram[3][0x1d4b:0x1da2])==old[0xbd4b-0xbbc1:0xbda2-0xbbc1]
    frozen,_=V.assemble((V.R/'tools/reference/prince_careful_support_1110_v5.s').read_text(),0xd6d1)
    assert len(frozen)==132 and bytes(m.ram[2][0x16d1:0x1756])==frozen+b'\0'
    m.ram[3][0x1d4b:0x1da2]=projection.ljust(87,b'\xea')
    m.ram[2][0x16d1:0x1756]=support
    assert all(len(bank)==8192 for bank in m.ram)
    return labels


def proposal():
    frozen=V.proposal();_,previous,old_chunks,old_layout,program,packet,rows=frozen
    projection,support,labels=code()
    runtime,metadata,state=map(bytearray,old_chunks)
    original=(V.R/'build/prince-actor-1101-v1/host-render-v11.bin').read_bytes()
    assert runtime[0x1d4b:0x1da2]==original[0xbd4b-0xbbc1:0xbda2-0xbbc1]
    old_support,_=V.assemble((V.R/'tools/reference/prince_careful_support_1110_v5.s').read_text(),0xd6d1)
    at=0xd6d1-0xc800
    assert metadata[at:at+133]==old_support+b'\0'
    runtime[0x1d4b:0x1da2]=projection
    metadata[at:at+133]=support
    chunks=tuple(map(bytes,(runtime,metadata,state)))
    assert list(map(len,chunks))==[8159,6112,1607] and chunks[2]==old_chunks[2]
    assert chunks[0][:0x1d4b]==old_chunks[0][:0x1d4b] and chunks[0][0x1da2:]==old_chunks[0][0x1da2:]
    assert chunks[1][:at]==old_chunks[1][:at] and chunks[1][at+133:]==old_chunks[1][at+133:]
    encode=Q.P.Q.M.CODEC.encode;packed=list(map(encode,chunks));pages=old_layout['carrier_pages']
    payload_old=b''.join(previous['raw'][Q.CHR+p*1024:Q.CHR+(p+1)*1024] for p in pages)
    loader_at=31072+254;loader=bytearray(payload_old[loader_at:loader_at+446])
    config=lambda sizes:struct.pack('<12H',0xc500,0xa000,sizes[0],len(chunks[0]),
        0xe100-sizes[1],0xc800,sizes[1],len(chunks[1]),0xc300,0xc100,sizes[2],len(chunks[2]))
    assert loader[392:416]==config(old_layout['packed_bytes'])
    assert payload_old[loader_at+446:old_layout['payload_bytes']]==b''.join(map(encode,old_chunks))
    loader[392:416]=config(list(map(len,packed)))
    payload=payload_old[:loader_at]+bytes(loader)+b''.join(packed)
    assert len(payload)<=45*1024
    cookie=bytes([0xa7,38,2])+Q.sha256(b''.join(chunks)+payload).digest()[:13]
    image=bytearray(previous['raw']);cookie_at=Q.Sonic.C.off(65,0xab9f)
    for index,page in enumerate(pages):
        image[Q.CHR+page*1024:Q.CHR+(page+1)*1024]=payload[index*1024:(index+1)*1024].ljust(1024,b'\xff')
    image[cookie_at:cookie_at+16]=cookie
    assert image[:cookie_at]+image[cookie_at+16:Q.CHR]==previous['raw'][:cookie_at]+previous['raw'][cookie_at+16:Q.CHR]
    assert len(image)==len(previous['raw'])
    assert Q.digest(image)==PIN,'Frozen logical-sole packet changed; use a new derivative'
    layout=dict(old_layout,derivative_parent_in_memory_SHA256=V.PIN,
        in_memory_SHA256=Q.digest(image),Prince_cookie=cookie.hex(),packed_bytes=list(map(len,packed)),
        payload_bytes=len(payload),spare=45*1024-len(payload),new_page_payload_bytes=len(payload)-44*1024,
        metadata_input=0xe100-len(packed[1]),payload_SHA256=Q.digest(payload),stream_SHA256=list(map(Q.digest,chunks)),
        page329_new_SHA256=Q.digest(bytes(image[Q.CHR+329*1024:Q.CHR+330*1024])),
        source=dict(logical_worker=[0xd6d1,0xd756],factored_projection=[0xbd4b,0xbd82],
            logical_predicate=[0xbd82,0xbda2],previous_high_operand=0xd4a6,previous_sole_operand=0xd4b1,
            source_SHA256=Q.digest(SOURCE.read_bytes()),no_new_allocation=True))
    return previous,C.Start.W.bundle(bytes(image)),chunks,layout,program,packet,rows


def run_trace(result,changed=True):
    sample=F.sample;target=None;tick=-1;rows=[];writes=[];native=N.NesMPU;fixture=None
    def observer(m,epoch):
        nonlocal target,tick
        if target is not m:
            target=m
            if changed:apply(m)
        tick=epoch
        return sample(m,epoch)
    def state(m):
        word=lambda at:int.from_bytes(m.ram[2][at:at+2],'little')
        return dict(native_x=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
            native_y=N.get(m,'Player_Y_Position'),native_ground=N.get(m,'Player_State'),
            foot=word(0x84),oldfoot=word(0x86),previous_sole=m.ram[2][0x14b1],
            previous_high=m.ram[2][0x14a6],delta=m.ram[2][0x88],baseline=word(0x9b),
            offset=word(0x99),roomrows=m.ram[2][0x82],row=m.ram[2][0x7c],
            currentrow=m.ram[2][0x83],phase_call=m.ram[2][0x2c],
            action=m.ram[2][0x616],frame=m.ram[2][0x617],mode=m.ram[2][0x618])
    class Trace(native):
        def step(self):
            nonlocal fixture
            m=self.memory;pc=self.pc
            if m is target and 608<=tick<=810:
                tag=m.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1
                if tag==2 and pc==0xd6d1 and tick==622:fixture=Q.Sonic.slim_fork(m)
                if tag==2 and pc==0xd46e and tick in (622,626):rows.append(dict(tick=tick,kind='accepted capture',A=self.a,**state(m)))
                if tag==2 and pc==0xd6d4:rows.append(dict(tick=tick,kind='after-worldtile',A=self.a,**state(m)))
                if tag==3 and pc==0xa34d and self.y==0:rows.append(dict(tick=tick,kind='set-action',A=self.a,**state(m)))
                if tag==3 and pc==0xbd82:rows.append(dict(tick=tick,kind='logical',A=self.a,**state(m)))
                old=bytes(m.ram[2][0x84:0x89]);r=super().step()
                new=bytes(m.ram[2][0x84:0x89])
                if new[2:]!=old[2:]:writes.append(dict(tick=tick,bank=tag,pc=pc,before=old.hex(),after=new.hex()))
                return r
            return super().step()
    with patch.object(Q,'proposal',lambda:result),patch.object(F,'sample',observer),patch.object(N,'NesMPU',Trace),\
         patch.object(sys,'argv',[Route.__file__,'--park','careful','--approach','careful']):
        with contextlib.redirect_stdout(io.StringIO()) as output:Route.main()
    route=json.loads(output.getvalue().split('WAIT_POSE_ROUTE ',1)[1])
    return dict(changed=changed,rows=rows,writes=writes,route=route,outputs_written=0),fixture


def geometry(result):
    seed,_=Q.P.Q.C.C.cold(result[1],38)
    new=Q.Sonic.slim_fork(seed);apply(new)
    total=0
    for packed in range(256):
        for header in (0,64,128,192):
            for actor_y in (0,1,28,65,127,191,255):
                output=[]
                for m in (seed,new):
                    # Test input bytes only; no ROM/candidate allocation.
                    m.ram[2][0x800]=packed
                    m.ram[3][0x1cf5:0x1cf7]=(0xc800).to_bytes(2,'little')
                    m.ram[3][0x1da2]=header
                    m.ram[2][0x611]=actor_y
                    regs=I.invoke(m,3,0xbd4b,(83,71,0,0x61))['regs']
                    values=[m.ram[2][at] for at in (0x88,0x4bc,0x4c3,0x6f1,0x70f)]
                    output.append((regs,values))
                assert output[0]==output[1],(packed,header,actor_y,output)
                total+=1
    return dict(actual_6502_pairs=total,packed_geometry_bytes=256,header_widths=4,
        actor_Y_boundaries=7,registers_flags_geometry_exact=True,
        retired_codec_scratch='BDA3 WidthHigh is no longer read or written')


def matrix(fixture):
    assert fixture is not None
    cases=[]
    def one(name,change,expected=False):
        base=Q.Sonic.slim_fork(fixture);change(base)
        a,b=(Q.Sonic.slim_fork(base) for _ in range(2))
        frozen,_=V.assemble((V.R/'tools/reference/prince_careful_support_1110_v5.s').read_text(),0xd6d1)
        a.ram[2][0x16d1:0x1756]=frozen+b'\0'
        actor=bytes(base.ram[2][0x606:0x800]);feet=bytes(base.ram[2][0x86:0x88])
        outputs=[I.invoke(m,3,0xd6d1,(83,71,109,0x61))['regs'] for m in (a,b)]
        if expected:assert outputs[0][0]==0 and outputs[1][0]==1,(name,outputs)
        else:assert outputs[0]==outputs[1],(name,outputs)
        assert outputs[0][1:3]==outputs[1][1:3] and outputs[0][4:]==outputs[1][4:],(name,outputs)
        for m in (a,b):
            assert bytes(m.ram[2][0x606:0x800])==actor and bytes(m.ram[2][0x86:0x88])==feet,name
        cases.append(dict(name=name,old_A=outputs[0][0],new_A=outputs[1][0],surface=b.ram[2][0x7f]))
    one('actual622 unchanged actor/previous sole',lambda m:None,True)
    for prior in (146,148):one('previous physical sole '+str(prior),lambda m,p=prior:m.ram[2].__setitem__(0x14b1,p))
    one('previous page nonzero',lambda m:m.ram[2].__setitem__(0x14a6,1))
    one('physical sole moved since prior Main',lambda m:m.ram[2].__setitem__(0x611,66))
    one('source foot page nonzero',lambda m:m.ram[2].__setitem__(0x8a,1))
    for state in (1,2,3):one('native air '+str(state),lambda m,s=state:N.put(m,Player_State=s))
    for high in (0,2):one('native Y page '+str(high),lambda m,h=high:N.put(m,Player_Y_HighPos=h))
    for y in (111,113,224):one('native anchor mismatch '+str(y),lambda m,y=y:N.put(m,Player_Y_Position=y))
    one('opposite leading foot',lambda m:m.ram[2].__setitem__(0x615,0))
    for action in (1,2,3,4,7,17,24,49):one('not careful '+str(action),lambda m,a=action:m.ram[2].__setitem__(0x616,a))
    for mode in (0,2,3,4,5,6,7,8,15):one('scripted mode '+str(mode),lambda m,v=mode:m.ram[2].__setitem__(0x618,v))
    for room in (1,255):one('different source row '+str(room),lambda m,v=room:m.ram[2].__setitem__(0x82,v))
    for kind in ('gap','covered','shaft','wall'):
        def alter(m,kind=kind):
            for x in (912,928):
                at=I.address(m.bundle,'Block_Buffer_2' if x>>8&1 else 'Block_Buffer_1')+((x&255)>>4)
                for y in (128,144,160,176,192):
                    if kind=='gap':m[at+((y-32)&240)]=0
                    elif y==128 and kind=='covered':m[at+96]=0x54
                    elif y==144 and kind in ('shaft','wall'):m[at+112]=0x14 if kind=='shaft' else 0x54
        one('actual native '+kind,alter)
    return dict(cases=cases,source_actor_health_and_terrain_OldFoot_exact=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trace',action='store_true')
    parser.add_argument('--old',action='store_true')
    parser.add_argument('--geometry',action='store_true')
    parser.add_argument('--matrix',action='store_true')
    parser.add_argument('--candidate',action='store_true')
    args=parser.parse_args()
    projection,support,labels=code()
    print('LOGICAL_FIT '+json.dumps(dict(projection_bytes=len(projection),support_bytes=len(support),labels=labels)),flush=True)
    result=V.proposal() if args.trace or args.geometry or args.matrix else None
    if args.geometry:print('LOGICAL_GEOMETRY '+json.dumps(geometry(result)),flush=True)
    if args.trace or args.matrix:
        trace,fixture=run_trace(result,not args.old)
        route=trace['route']
        trace['route']={k:route[k] for k in ('outcome','actual_fourth_cap','maximum_X','events','HP_debits','terminal','pads')}
        if args.trace:print('LOGICAL_TRACE '+json.dumps(trace,separators=(',',':')),flush=True)
        if args.matrix:print('LOGICAL_MATRIX '+json.dumps(matrix(fixture),separators=(',',':')),flush=True)
    if args.candidate:
        candidate=proposal();seed,cold=Q.actual_cold(candidate[1],candidate[2],candidate[3],candidate[4])
        print('LOGICAL_CANDIDATE '+json.dumps(dict(layout=candidate[3],cold=cold),separators=(',',':')),flush=True)


if __name__=='__main__':main()
