"""Source-only Prince full-world export witness and native side sweep.

The candidate exists only in memory. Frozen v1/103B/44B packets are inputs.
"""
import argparse
import contextlib
import io
import json
import re
import sys
import struct
from unittest.mock import patch
from py65.assembler import Assembler
import check_prince_careful_support_1110_v5 as Careful

Q,C,N,I,F=Careful.Q,Careful.C,Careful.N,Careful.I,Careful.F
R=Q.R
ORIGIN,BOUND=0xd56a,0xd622
PIN='51740230ca394e6c516a0fd65ff5f37defe4c1158c8f90c94d619a61f2bf49d5'


def trace_stop():
    import check_prince_wait_pose_route_1110_v3 as Route
    result=Careful.proposal();native=N.NesMPU;sample=F.sample
    target=None;tick=-1;writes=[];queries=[];native_writes=[];walls=[]
    wall_pc=I.address(result[1],'SamusStopAtWallBanked')
    wall_bank=((I.location(result[1],'SamusStopAtWallBanked')-16)//8192)|128
    def observer(m,epoch):
        nonlocal target,tick
        target,tick=m,epoch
        return sample(m,epoch)
    class Trace(native):
        def step(self):
            if self.memory is not target or not 407<=tick<=437:return super().step()
            m=target;old=int.from_bytes(m.ram[2][0x60f:0x611],'little');pc=self.pc
            tag=m.rawtags[(pc-0x8000)//8192] if pc>=0x8000 else -1
            old_native=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
            if (tag,pc)==(wall_bank,wall_pc):walls.append(dict(tick=tick,side=m[3],X=old_native,
                speed=N.get(m,'Player_X_Speed'),action=m.ram[2][0x616],frame=m.ram[2][0x617]))
            if (tag,pc) in ((3,0xbde2),(3,0xbde5),(2,0xc40b),(3,0xb310)):
                queries.append(dict(tick=tick,bank=tag,pc=pc,X=old,
                    native=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc'),
                    action=m.ram[2][0x616],frame=m.ram[2][0x617],mode=m.ram[2][0x618],
                    raw=int.from_bytes(m.ram[2][0x78:0x7a],'little'),Y=self.y,
                    point=list(m.ram[3][0x1369:0x136d])))
            r=super().step();new=int.from_bytes(m.ram[2][0x60f:0x611],'little')
            new_native=N.get(m,'Player_X_Position')+256*N.get(m,'Player_PageLoc')
            if new_native!=old_native:native_writes.append(dict(tick=tick,bank=tag,pc=pc,old=old_native,new=new_native))
            if new!=old:writes.append(dict(tick=tick,bank=tag,pc=pc,old=old,new=new,
                action=m.ram[2][0x616],frame=m.ram[2][0x617],mode=m.ram[2][0x618]))
            return r
    with patch.object(Q,'proposal',lambda:result),patch.object(F,'sample',observer),\
         patch.object(N,'NesMPU',Trace),patch.object(sys,'argv',[Route.__file__,'--park','careful']):
        with contextlib.redirect_stdout(io.StringIO()) as buffer:Route.main()
    route=json.loads(buffer.getvalue().split('WAIT_POSE_ROUTE ',1)[1])
    print('STOP_CAUSE '+json.dumps(dict(writes=writes,queries=[q for q in queries if q['pc']!=0xb310],
        native_writes=native_writes,native_wall_entries=walls,
        native_points=list({tuple(q['point']):q for q in queries if q['pc']==0xb310}.values()),
        route={k:route[k] for k in ('in_memory_SHA256','outcome','actual_fourth_cap','events','HP_debits','terminal')}),
        separators=(',',':')),flush=True)


def assemble(text,origin,symbols=None):
    lines=[line.split(';',1)[0].strip() for line in text.splitlines()]
    labels={line[:-1]:origin for line in lines if line.endswith(':')}
    labels.update(symbols or {})
    asm=Assembler(N.NesMPU(memory=[0]*65536))
    for _ in range(3):
        code=bytearray()
        for line in lines:
            if not line or line.startswith('.'):continue
            if line.endswith(':'):labels[line[:-1]]=origin+len(code);continue
            line=re.sub(r'\b([A-Za-z_][A-Za-z_0-9]*)\b',
                lambda m:f'${labels[m[1]]:04x}' if m[1] in labels else m[0],line)
            line=re.sub(r'#(\d+)\b',lambda m:f'#${int(m[1]):02x}',line)
            if _==2 and line[:3].upper() in ('BCC','BCS','BEQ','BNE','BMI','BPL','BVC','BVS'):
                target=int(line.split('$')[1],16)
                delta=target-(origin+len(code)+2)
                assert -128<=delta<=127,('Out-of-range source branch',line,hex(origin+len(code)),delta)
            code.extend(asm.assemble(line,pc=origin+len(code)))
    return bytes(code),labels


def code(bundle):
    names=('GameEngineSubroutine','Player_X_Position','Player_PageLoc','Player_Y_Position',
           'Player_X_Scroll','Player_X_Speed','MTileAttribute','ChkForNonSolids','BlockBufferAddr','Player_Y_Speed',
           'ScreenLeft_X_Pos','ScreenLeft_PageLoc','Player_OffscreenBits','JumpspringAnimCtrl')
    names+=('FrameCounter','GamePauseStatus')
    symbols={n:I.address(bundle,n) for n in names}
    text=(R/'tools/reference/prince_native_wall_sweep_1110_v6.s').read_text()
    sections=dict(re.findall(r'\.segment "([A-Z_]+)"\s*([\s\S]*?)(?=\.segment|$)',text))
    positions={'BOUNDS':0xdfcc,'ENTRY':0xdfdb,'CORE':0xd552,'PROBE_HEAD':0xb353,'PROBE_TAIL':0xd660}
    symbols.update({name:at for section,at in positions.items() for name in
        re.findall(r'(?m)^([A-Za-z_][A-Za-z_0-9]*):',sections[section])})
    symbols.update(StepLow=ORIGIN,StepHigh=ORIGIN,SubtractEdge=ORIGIN,EndLow=ORIGIN,EndHigh=ORIGIN,PointReturn=0xb352)
    for _ in range(4):
        blocks={};labels={}
        for section,at in positions.items():
            block,lab=assemble(sections[section],at,symbols)
            blocks[section]=block
            labels.update({n:lab[n] for n in re.findall(r'(?m)^([A-Za-z_][A-Za-z_0-9]*):',sections[section])})
        symbols.update(labels)
        symbols.update({n:labels[n+'Op']+1 for n in ('StepLow','StepHigh','SubtractEdge','EndLow','EndHigh')})
    export,_=assemble((R/'tools/reference/prince_export_world_witness_1110_v6.s').read_text(),0xc386,symbols)
    return blocks,positions,symbols,export


def compact(bundle):
    symbols={n:I.address(bundle,n) for n in ('BlockBufferAddr','Block_Buffer_1','MTileAttribute','GameEngineSubroutine','Player_Y_Speed')}
    point_text=(R/'tools/reference/prince_point_read_compact_1110_v6.s').read_text()
    symbols['ReadLow']=0xb310
    for _ in range(3):
        point,plab=assemble(point_text,0xb310,symbols)
        symbols['ReadLow']=plab['Read']+1
    admission_text=(R/'tools/reference/prince_floor_admission_compact_1110_v6.s').read_text()
    admission,alab=assemble(admission_text,0xd53e,symbols)
    return point,plab,admission,alab


def camera(bundle,old=False):
    names=('ScrollLock','SideCollisionTimer','Platform_X_Scroll','Player_X_Scroll','Player_X_Position',
        'ScreenLeft_X_Pos','Player_PageLoc','ScreenLeft_PageLoc','Player_Pos_ForScroll')
    symbols={n:I.address(bundle,n) for n in names}
    if old:
        text=(R/'tools/reference/prince_camera_framing_1110.s').read_text()
        aliases={'PlayerX':'Player_X_Position','PlayerPage':'Player_PageLoc','ScreenLeftX':'ScreenLeft_X_Pos',
            'ScreenLeftPage':'ScreenLeft_PageLoc','PlatformScroll':'Platform_X_Scroll','PlayerScroll':'Player_X_Scroll',
            'PlayerPositionForScroll':'Player_Pos_ForScroll'}
        symbols.update({n:symbols[v] for n,v in aliases.items()})
        symbols.update(NativeVerticalExport=0xbd42,FollowX=120,MaxScroll=5)
        text='\n'.join(line for line in text.splitlines() if '=' not in line)
    else:text=(R/'tools/reference/prince_camera_compact_1110_v6.s').read_text()
    return assemble(text,0xd622,symbols)


def apply(seed):
    blocks,positions,labels,export=code(seed.bundle)
    point,plab,admission,alab=compact(seed.bundle)
    assert len(point)==67 and len(admission)==20 and len(export)==42
    assert {n:len(b) for n,b in blocks.items()}==dict(BOUNDS=15,ENTRY=5,CORE=207,PROBE_HEAD=19,PROBE_TAIL=18)
    old_camera,_=camera(seed.bundle,old=True);new_camera,_=camera(seed.bundle)
    assert len(old_camera)==67 and len(new_camera)==62
    assert bytes(seed.ram[2][0x1622:0x1665])==old_camera
    assert bytes(seed.ram[2][0x1665:0x1672])==bytes([255])*13
    old,_=Careful.assemble(seed.bundle,old=True)
    with patch.object(Careful,'ORIGIN',Careful.OLD):careful,_=Careful.assemble(seed.bundle)
    assert len(careful)==132 and len(old)==128
    funding=C.read(R/'build/prince-run-support-funded-1110/proof.json')['layout']
    assert funding['support_half_open']==[0xd6d1,0xd751] and funding['execution_spare']==5
    assert bytes(seed.ram[2][0x16d1:0x1751])==old and bytes(seed.ram[2][0x1751:0x1756])==bytes(5)
    assert bytes(seed.ram[3][0x6f6:0x6f9])==bytes.fromhex('20d1d6')
    assert bytes(seed.ram[2][0x153e:0x156a])==Q.admission_code(seed.bundle)
    assert bytes(seed.ram[2][0x156a:0x1622])==bytes([255])*184
    assert bytes(seed.ram[3][0x1d3e:0x1d42])==bytes.fromhex('4c3ed5ea')
    before=[bytes(b) for b in seed.ram]
    seed.ram[2][0x16d1:0x1755]=careful
    seed.ram[2][0x153e:0x1622]=bytes([255])*(0x1622-0x153e)
    seed.ram[2][0x153e:0x153e+len(admission)]=admission
    seed.ram[3][0x1310:0x1369]=point+blocks['PROBE_HEAD']+bytes([255])*3
    seed.ram[2][0x386:0x3b0]=export
    seed.ram[2][0x1622:0x1672]=new_camera+bytes([255])*18
    for name in ('BOUNDS','ENTRY','CORE','PROBE_TAIL'):
        at=positions[name]-0xc000;seed.ram[2][at:at+len(blocks[name])]=blocks[name]
    seed.ram[3][0x1d3e:0x1d42]=bytes.fromhex('4cdbdfea')
    assert bytes(seed.ram[2][0x14d7:0x153e])==before[2][0x14d7:0x153e]
    assert bytes(seed.ram[2][0x1672:0x16d1])==before[2][0x1672:0x16d1]
    assert bytes(seed.ram[2][0x1755:0x1fcc])==before[2][0x1755:0x1fcc]
    assert bytes(seed.ram[2][0x1fe0:])==before[2][0x1fe0:]
    return seed,dict(blocks={n:[positions[n],positions[n]+len(b)] for n,b in blocks.items()},
        careful=[0xd6d1,0xd755],remaining_official_tail=[0xd755,0xd756],
        floor_private=[0xd53e,0xd552],point=[0xb310,0xb353],
        camera=[0xd622,0xd660],old_camera_bytes=67,new_camera_bytes=62,
        horizontal_export=[0xc386,0xc3b0],source_labels=labels,
        frozen103_exact=True,original_motor_actor_health_art_unchanged=True)


def proposal():
    parent,previous,old_chunks,old_layout,program,packet,rows=Q.proposal()
    assert old_layout['in_memory_SHA256']==Careful.PARENT
    seed,_=Q.P.Q.C.C.cold(previous,38);original_export=bytes(seed.ram[2][0x386:0x3b0])
    changed,source=apply(seed)
    runtime=bytearray(old_chunks[0]);runtime[0x1310:0x1369]=changed.ram[3][0x1310:0x1369]
    runtime[0x1d3e:0x1d42]=changed.ram[3][0x1d3e:0x1d42]
    state=bytearray(old_chunks[2]);at=0xc386-0xc0b0
    assert state[at:at+42]==original_export,'Source state-to-live export map differs'
    state[at:at+42]=changed.ram[2][0x386:0x3b0]
    chunks=(bytes(runtime),bytes(changed.ram[2][0x800:0x1fe0]),bytes(state))
    assert list(map(len,chunks))==[8159,6112,1607]
    encode=Q.P.Q.M.CODEC.encode;packed=list(map(encode,chunks));pages=old_layout['carrier_pages']
    payload_old=b''.join(previous['raw'][Q.CHR+p*1024:Q.CHR+(p+1)*1024] for p in pages)
    decoder_end=31072+254;loader=bytearray(payload_old[decoder_end:decoder_end+446]);cfg=392
    config=lambda parts,sizes:struct.pack('<12H',0xc500,0xa000,sizes[0],len(parts[0]),
        0xe100-sizes[1],0xc800,sizes[1],len(parts[1]),0xc300,0xc100,sizes[2],len(parts[2]))
    assert loader[cfg:cfg+24]==config(old_chunks,old_layout['packed_bytes'])
    assert payload_old[decoder_end+446:old_layout['payload_bytes']]==b''.join(map(encode,old_chunks))
    loader[cfg:cfg+24]=config(chunks,list(map(len,packed)))
    payload=payload_old[:decoder_end]+bytes(loader)+b''.join(packed)
    assert len(payload)<=45*1024 and loader[:97]==payload_old[decoder_end:decoder_end+97]
    cookie=bytes([0xa7,38,2])+Q.sha256(b''.join(chunks)+payload).digest()[:13]
    image=bytearray(parent['raw']);cookie_at=Q.Sonic.C.off(65,0xab9f)
    for index,page in enumerate(pages):
        image[Q.CHR+page*1024:Q.CHR+(page+1)*1024]=payload[index*1024:(index+1)*1024].ljust(1024,b'\xff')
    image[cookie_at:cookie_at+16]=cookie
    assert all(image[Q.CHR+p*1024:Q.CHR+(p+1)*1024]==parent['raw'][Q.CHR+p*1024:Q.CHR+(p+1)*1024] for p in range(321,329))
    assert image[:cookie_at]+image[cookie_at+16:Q.CHR]==parent['raw'][:cookie_at]+parent['raw'][cookie_at+16:Q.CHR]
    layout=dict(old_layout,derivative_parent_in_memory_SHA256=Careful.PARENT,
        in_memory_SHA256=Q.digest(image),Prince_cookie=cookie.hex(),packed_bytes=list(map(len,packed)),
        payload_bytes=len(payload),spare=45*1024-len(payload),new_page_payload_bytes=len(payload)-44*1024,
        metadata_input=0xe100-len(packed[1]),payload_SHA256=Q.digest(payload),stream_SHA256=list(map(Q.digest,chunks)),
        page329_new_SHA256=Q.digest(bytes(image[Q.CHR+329*1024:Q.CHR+330*1024])),
        decoded_bytes=list(map(len,chunks)),metadata_extension=[0xdfcc,0xdfe0],header_boundary=0xdfe0,
        admission_bytes=20,frozen_admission_input_bytes=44,full_world_witness_retained_after_sweep=True,
        source=source)
    assert layout['in_memory_SHA256']==PIN,'Frozen source packet changed; use a new derivative'
    return parent,C.Start.W.bundle(bytes(image)),chunks,layout,program,packet,rows


def opening():
    old=Q.proposal()[1];new=proposal()[1]
    rows=[];models=[]
    for bundle in (old,new):
        cold,_=Q.P.Q.C.C.cold(bundle,38)
        env,m,labels=Q.P.Q.first8(bundle,cold)
        C.Seam.terrain(m,lambda x,y:0x54 if y>=208 else 0)
        models.append((env,m,labels))
    for tick in range(75):
        samples=[C.Recovery.sample(m,tick) for _,m,_ in models]
        keys=('x','y','hp','action','frame','mode','native_state','foot')
        a,b=[{k:s[k] for k in keys} for s in samples]
        if a!=b or tick<12:rows.append(dict(tick=tick,old=a,new=b,
            witness=list(models[1][1].ram[2][0xa7:0xa9])))
        for env,m,labels in models:C.Route.controls(env,m,labels,1)
    print('WALL_OPENING '+json.dumps(rows,separators=(',',':')),flush=True)


def point_smoke():
    _,trial,_,_,_,_,_=Q.proposal();old,_=Q.P.Q.C.C.cold(trial,38)
    new=Q.Sonic.slim_fork(old);apply(new)
    rows=[]
    for x,y in ((40,184),(40,208),(255,208),(256,208),(511,208),(512,208),(900,208),(912,184)):
        result=[]
        for m in (old,new):
            C.Seam.terrain(m,lambda x,y:0x54 if y>=208 else 0)
            m.ram[3][0x1369:0x136d]=x.to_bytes(2,'little')+y.to_bytes(2,'little')
            regs=I.invoke(m,3,0xb310,(83,71,109,0x61))['regs']
            result.append(dict(regs=regs,query=list(m.ram[3][0x1369:0x136e]),
                buffer=[m[I.address(trial,'Block_Buffer_1')+((x&255)>>4)+(0xd0 if x>>8&1 else 0)+((y&240)-32)]],
                reader=bytes(m.ram[3][0x1310:0x1369]).hex()))
        rows.append(dict(x=x,y=y,old=result[0],new=result[1]))
    print('POINT_SMOKE '+json.dumps(rows,separators=(',',':')),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit',action='store_true')
    parser.add_argument('--trace-stop',action='store_true')
    parser.add_argument('--fit',action='store_true')
    parser.add_argument('--candidate',action='store_true')
    parser.add_argument('--route',action='store_true')
    parser.add_argument('--opening',action='store_true')
    parser.add_argument('--point-smoke',action='store_true')
    parser.add_argument('--approach',choices=('run','careful'),default='run')
    args=parser.parse_args()
    if args.trace_stop:return trace_stop()
    if args.opening:return opening()
    if args.point_smoke:return point_smoke()
    if args.candidate or args.route:
        result=proposal();_,trial,chunks,layout,program,_,_=result
        seed,cold=Q.actual_cold(trial,chunks,layout,program)
        print('WALL_CANDIDATE '+json.dumps(dict(layout=layout,cold=cold),separators=(',',':')),flush=True)
        if args.route:
            import check_prince_wait_pose_route_1110_v3 as Route
            with patch.object(Q,'proposal',lambda:result),patch.object(sys,'argv',[Route.__file__,'--park','careful','--approach',args.approach]):Route.main()
        return
    _,trial,chunks,layout,program,_,_=Q.proposal()
    seed,cold=Q.actual_cold(trial,chunks,layout,program)
    if args.fit:
        blocks,positions,labels,export=code(trial)
        point,plab,admission,alab=compact(trial)
        print('WALL_FIT '+json.dumps(dict(worker_bytes=sum(map(len,blocks.values())),labels=labels,
            blocks={n:dict(at=positions[n],size=len(b),hex=b.hex()) for n,b in blocks.items()},
            compact_point_bytes=len(point),compact_point_labels=plab,
            compact_admission_bytes=len(admission),compact_admission_labels=alab,
            export_bytes=len(export),export=export.hex()),separators=(',',':')),flush=True)
    if args.audit:
        attrs=I.address(trial,'MTileAttribute')
        print('WALL_AUDIT '+json.dumps(dict(
            layout=layout,cold=cold,
            export_horizontal=bytes(seed.ram[2][0x386:0x386+41]).hex(),
            old_tail=bytes(seed.ram[2][0x1751:0x1756]).hex(),
            declared_historical_padding={hex(a):bytes(seed.ram[bank][a-base:b-base]).hex() for bank,base,a,b in
                ((2,0xc000,0xc0f8,0xc100),(2,0xc000,0xc352,0xc360),(2,0xc000,0xc491,0xc4b1),
                 (2,0xc000,0xc7f3,0xc800),(2,0xc000,0xdac2,0xdac6),(2,0xc000,0xdfcc,0xdfe0),
                 (3,0xa000,0xb3ef,0xb400))},
            worker_end=bytes(seed.ram[2][0x1756:0x1766]).hex(),
            service_table_tail=bytes(seed.ram[2][0x1ac2:0x1add]).hex(),
            tile_attributes={hex(i):seed[attrs+i] for i in (0,0x10,0x12,0x14,0x1c,0x1f,0x23,0x24,0x25,0x26,0x54,0x5f,0x60,0x67,0x68,0x6b,0x6c,0x6d,0xc2,0xc3,0xc5)},
            relevant_symbols={n:[I.address(trial,n),((I.location(trial,n)-16)//8192)|128] for n in
                ('SamusStopAtWall','SamusStopAtWallBanked','CrossoverSourceSideProbe','PlayerBGCollision','MTileAttribute')},
            outputs_written=0),separators=(',',':')),flush=True)


if __name__=='__main__':main()
