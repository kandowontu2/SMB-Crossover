"""Fit the real F801 ledge worker by losslessly packing native Prince pose cells."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import re
import subprocess

from verify_native_relocation import NesMPU
import check_prince_pose_reservation_1103_v186 as Q
import check_prince_climb_edge_1108_v1 as EDGE


R, O, V, N, I = Q.R, Q.O, Q.V, Q.N, Q.I
OLD = R/'build/prince-body-current-candidate-root-1103-v186/candidate.json'
SOURCE = R/'tools/reference/prince_grid_compact_1109_v1.s'
PARENTS = {
    '37bb': ('build/mini-busy-pipeline-final-1108/candidate.nes', '37bb9c1a69b993edda540c75cbe256aeac75396d55d34d9daf3d4de86deebeeb'),
    'a08d': ('build/mini-parser-lift-1109/candidate.nes', 'a08d839b187fc6866a3fd3658200c2f26b8e3724b3b4de3b5e7d2a65702598d2'),
}
GRID_END = 0xd8f1
WORKER = 0xd800
COOKIE = 16+65*8192+0xba4
sha = lambda b: hashlib.sha256(b).hexdigest()


def assemble(out, name, source, cfg):
    base = out/name
    s, c, o, b, l = (base.with_suffix(s) for s in ('.s','.cfg','.o','.bin','.lbl'))
    s.write_text(source)
    c.write_text(cfg)
    cc = R/'tools/Windows/cc65/bin'
    for cmd in ((cc/'ca65.exe',s,'-o',o),(cc/'ld65.exe','-C',c,o,'-o',b,'-Ln',l)):
        run=subprocess.run(list(map(str,cmd)),capture_output=True,text=True)
        assert run.returncode==0,run.stderr
    o.unlink()
    c.unlink()
    return b.read_bytes(),Q.M.labels(l)


def one_segment(origin,size,name='CODE'):
    return f'MEMORY{{M:start=${origin:04x},size=${size:04x},file=%O;}}SEGMENTS{{{name}:load=M,type=ro;}}'


def geometry(raw, frame):
    tag=int.from_bytes(raw[2*frame:2*frame+2],'little')
    if tag == 0xffff:
        return None
    at=tag&0x3fff
    header=raw[at]
    n, pages=header&15,(header>>4)&3
    prefix=bytes(raw[at:at+2+pages])
    at += 2+pages
    if not tag&0x8000:
        return prefix, bytes(raw[at:at+3*n])
    bx,by=raw[at:at+2]
    at+=2
    if tag&0x4000:
        records=[]
        for index in range(0,n,2):
            pair=raw[at]
            at+=1
            for shift in (4,0) if index+1<n else (4,):
                low=(pair>>shift)&15
                tile=raw[at]
                at+=1
                coord=((low&12)<<2)|(low&3)|((tile&1)<<2)
                records.append((coord,tile&0xfe))
    else:
        records=list(zip(raw[at:at+2*n:2],raw[at+1:at+2*n:2]))
    return prefix,bytes(value for coord,tile in records
                        for value in ((by+8*(coord&15))&255,tile,(bx+8*(coord>>4))&255))


def pack(old):
    tags=[int.from_bytes(old[i:i+2],'little') for i in range(0,478,2)]
    rows=sorted(set(tags)-{0xffff},key=lambda t:t&0x7fff)
    new=bytearray([255])*478
    remap={}
    selected=parts=0
    for tag,limit in zip(rows,rows[1:]+[len(old)]):
        start,end=tag&0x7fff,limit&0x7fff
        packet=old[start:end]
        n,pages=packet[0]&15,(packet[0]>>4)&3
        dest=len(new)|(tag&0x8000)
        if tag&0x8000:
            prefix=4+pages
            cells=packet[prefix::2]
            tiles=packet[prefix+1::2]
            assert len(cells)==len(tiles)==n
            if all((c>>4)<4 and (c&15)<8 for c in cells):
                assert all(t&1==0 for t in tiles)
                selected+=1
                parts+=n
                dest|=0x4000
                pair=bytearray()
                for i in range(0,n,2):
                    group=cells[i:i+2]
                    low=[((c>>4)<<2)|(c&3) for c in group]
                    pair.append((low[0]<<4)|(low[1] if len(low)==2 else 0))
                    pair.extend(tiles[i+j]|((c>>2)&1) for j,c in enumerate(group))
                packet=packet[:prefix]+pair
        remap[tag]=dest
        new.extend(packet)
    for f,tag in enumerate(tags):
        if tag!=0xffff:
            new[2*f:2*f+2]=remap[tag].to_bytes(2,'little')
    assert (selected,parts,len(old)-len(new))==(162,904,411)
    assert all(geometry(old,f)==geometry(new,f) for f in range(239))
    return bytes(new),dict(compact_packets=selected,compact_parts=parts,raw_reclaimed=411,all_indexed_geometry_equal=True)


def call(data, base, pc, old, new):
    at=pc-base
    assert data[at:at+3]==bytes([0x20])+old.to_bytes(2,'little'),hex(pc)
    data[at+1:at+3]=new.to_bytes(2,'little')


def find(data,base,start,end,needle):
    entries=[base+i for i in range(start-base,end-base) if data[i:i+len(needle)]==needle]
    pc,=entries
    return pc


def images(out):
    runtime,meta,state=Q.source_images()
    plan=json.loads((O/'pose-source.json').read_text())
    assert [sha(x) for x in (runtime,meta,state)]==[row['SHA256'] for row in plan['streams']]
    old_grid=(V.O/'prince-pose-grid-v37.bin').read_bytes()
    assert meta[:len(old_grid)]==old_grid and 0xc800+len(old_grid)==GRID_END
    packed,layout=pack(old_grid)
    compact_at=0xc800+len(packed)
    grid=Q.M.labels(V.O/'pose-grid-helper-v37.lbl')
    draw=plan['labels']
    prefix=''.join(f'{n}=${a:04x}\n' for n,a in (
        ('Byte',draw['Byte']),('ReadProjection',draw['PpReadProjection']),
        ('GridCell',grid['PpGridCell']),('GridFlag',grid['PpGridFlag'])))
    compact,clab=assemble(out,'compact',prefix+SOURCE.read_text(),one_segment(compact_at,WORKER-compact_at))
    worker,wlab=assemble(out,'climb',EDGE.WORKER.read_text(),one_segment(WORKER,GRID_END-WORKER,'CLIMB_EDGE'))
    assert len(worker)==178 and wlab['PpClimbEdgeAlign']==WORKER
    isolated=(R/'build/prince-climb-edge-cpu-1108/worker.bin').read_bytes()
    # The only absolute local jump is CommitPage, relocated $70AC -> $D8AC.
    assert isolated[155:158]==bytes.fromhex('4cac70')
    assert worker==isolated[:157]+bytes([WORKER>>8])+isolated[158:]
    m=bytearray(meta)
    m[:len(old_grid)]=packed+bytes(len(old_grid)-len(packed))
    m[compact_at-0xc800:compact_at-0xc800+len(compact)]=compact
    m[WORKER-0xc800:WORKER-0xc800+len(worker)]=worker
    at=find(m,0xc800,grid['PpGridLookup'],grid['PpGridProjection'],bytes.fromhex('297f1869c8'))-0xc800
    m[at+1]=0x3f
    call(m,0xc800,grid['PpGridProjection'],draw['PpReadProjection'],clab['ResetPair'])
    at=find(m,0xc800,grid['PpGridY'],grid['PpGridX'],bytes([0x20])+draw['Byte'].to_bytes(2,'little'))
    call(m,0xc800,at,draw['Byte'],clab['ReadCell'])
    r=bytearray(runtime)
    at=find(r,0xa000,draw['Parts'],draw['PpGridPartEnd'],bytes([0x20])+draw['Byte'].to_bytes(2,'little'))
    call(r,0xa000,at,draw['Byte'],clab['ReadTile'])
    call(r,0xa000,EDGE.PC,0xc40b,WORKER)
    chunks=(bytes(r),bytes(m),state)
    enc=[Q.M.CODEC.encode(blob) for blob in chunks]
    boot=(O/'pose-worker.s').read_text()
    for name,blob in zip(('Runtime','Metadata','State'),enc):
        src=0xc500 if name=='Runtime' else 0xc300 if name=='State' else 0xe100-len(blob)
        for suffix,value in [('Input',src),('Packed',len(blob))]:
            boot,n=re.subn(rf'(?m)^{name}{suffix}=\$[0-9a-f]+$',f'{name}{suffix}=${value:04x}',boot)
            assert n==1
    loader,_=assemble(out,'cold-loader',boot,(O/'pose-worker.cfg').read_text())
    assert len(loader)==444
    assert 0xe100-len(enc[1])>=0xc300
    original=(O/'pose-pool.bin').read_bytes()
    payload=original[:31072]+(V.O/'cold-decoder-v25.bin').read_bytes()+loader+b''.join(enc)
    assert len(payload)<=44*1024
    cookie=bytes([0xa7,38,2])+hashlib.sha256(b''.join(chunks)+payload).digest()[:13]
    return chunks,payload,cookie,dict(layout,compact_half_open=[compact_at,compact_at+len(compact)],
                worker_half_open=[WORKER,WORKER+len(worker)],compact_labels=clab,
                still_free_before_grid_service=GRID_END-WORKER-len(worker),
                old_pool_bytes=len(original),new_pool_bytes=len(payload),remaining_physical=44*1024-len(payload),
                old_packed_bytes=[row['packed'] for row in plan['streams']],new_packed_bytes=list(map(len,enc)))


def compose(payload,cookie):
    body=json.loads(OLD.read_text())
    assert len(body['patches'])==54
    approved=json.loads((R/'docs/qa/allocations/prince-current-frontend-1103-v105.json').read_text())['approved_exact_patches']
    approved_offsets={row['file_offset'] for row in approved}
    source_rows=sorted((row for row in body['patches'] if 'physical_CHR' in row),key=lambda row:row['source_offset'])
    assert len(source_rows)==44 and all(not 962<=row['physical_CHR']<=968 for row in source_rows)
    current={};prior={};final={};common_rows=None
    for key,(path,pin) in PARENTS.items():
        raw=(R/path).read_bytes()
        assert sha(raw)==pin
        current[key]=raw
        before=bytearray(raw)
        for row in body['patches']:
            at=row['file_offset'];old=bytes.fromhex(row['old_hex']);new=bytes.fromhex(row['new_hex'])
            assert raw[at:at+len(old)]==old,(key,hex(at))
            before[at:at+len(new)]=new
        prior[key]=bytes(before)
        result=bytearray(raw)
        records=[]
        def put(at,new,role):
            old=raw[at:at+len(new)]
            if old==new:return
            assert result[at:at+len(new)]==old
            result[at:at+len(new)]=new
            records.append(dict(offset=at,preimage=old.hex(),replacement=new.hex(),role=role))
        put(COOKIE,cookie,'Existing raw38 cookie data only')
        for row in body['patches']:
            if row['file_offset'] in approved_offsets:
                put(row['file_offset'],bytes.fromhex(row['new_hex']),'Exact previously approved Prince frontend')
        for index,row in enumerate(source_rows):
            data=payload[index*1024:(index+1)*1024]
            if data:put(row['file_offset'],data,f'Existing Prince carrier {row["physical_CHR"]}')
        if common_rows is None:common_rows=records
        assert records==common_rows
        final[key]=bytes(result)
    delta={i for i,(x,y) in enumerate(zip(current['37bb'],current['a08d'])) if x!=y}
    owned={i for p in common_rows for i in range(p['offset'],p['offset']+len(bytes.fromhex(p['preimage'])))}
    assert not delta&owned
    assert all(i in owned or x==y for i,(x,y) in enumerate(zip(current['a08d'],final['a08d'])))
    return prior,final,common_rows,len(delta)


def live(runtime):
    out=bytearray(runtime)
    out[0x1fa3:0x1fd8]=(V.O/'native-live-v149.bin').read_bytes()
    return bytes(out)


def test_pose(before,after):
    art=json.loads((V.O/'source-art.json').read_text())
    lab=json.loads((V.O/'native-labels-v153.json').read_text())
    counts=0
    for pose in art['poses']:
        pair=[N.fork(before),N.fork(after)]
        for m in pair:
            m.raw_page(2,2)
            N.put(m,CurrentBankC=2,CurrentOAMOffset=0,GuestOamRotationActive=1,RgOamRotation=0,
                  Player_Rel_XPos=48,Player_Rel_YPos=176,ScreenLeft_X_Pos=0,ScreenLeft_PageLoc=0)
            m.ram[2][0x617]=pose['source_frame'];m.ram[2][0x615]=pose['source_facing']
            m[0x200:0x300]=bytes([0xf8])*256
            I.invoke(m,3,lab['PpHostProject'],(83,71,109,0x61))
            I.invoke(m,3,0xc383,(83,71,109,0x61))
            m.writes.clear()
        results=[I.invoke(m,3,lab['PpHostDraw'],(83,71,109,0x61)) for m in pair]
        assert results[0]['regs']==results[1]['regs']
        a,b=pair
        assert a.rawtags==b.rawtags and a.chr_latches==b.chr_latches
        assert bytes(a[0x200:0x800])==bytes(b[0x200:0x800]),(pose['source_frame'],pose['source_facing'])
        assert bytes(a[3:11])==bytes(b[3:11]) and bytes(a[0x15a:0x17b])==bytes(b[0x15a:0x17b])
        assert bytes(a.ram[2][0x200:0x235])==bytes(b.ram[2][0x200:0x235])
        n=len(pose['parts_8x16'])
        assert N.get(a,'SmPose')==N.get(b,'SmPose')==4*n
        counts+=n
    assert len(art['poses'])==408 and counts==2578
    return dict(actual_native_poses=408,actual_native_parts=counts,source_native_OAM_CHR_registers_and_source_packet_equal=True)


def test_climb(before,after):
    def run(seed,edge,face,foot,inside,outside,roof):
        m=N.fork(seed)
        m.raw_page(1,3);m.raw_page(2,2)
        put,word=EDGE.put,EDGE.word
        put(m,0xc60f,(edge-15 if face else edge+15)&65535)
        m[0xc615]=face;put(m,0xc084,foot)
        m[0xc616]=24;m[0xc618]=2;m[0xc617]=91;m[0xc611]=128
        put(m,0xc078,413);m[0xc07a]=9;m[0xc4b1]=19
        put(m,0xc07f,208);m[0xc081]=1;put(m,0xc089,77);m[0xc6d1]=5
        m[0x300:0x4a0]=bytes(0x1a0)
        hand=foot-24
        if edge and 32<=hand<240:
            wall=edge if face else edge-1
            open_=edge-1 if face else edge
            m[EDGE.block(wall,hand)]=inside
            m[EDGE.block(open_,hand)]=outside
            if roof and (hand&0xf0)>=48:m[EDGE.block(wall,(hand&0xf0)-1)]=0x54
        c=NesMPU(memory=m,pc=EDGE.PC)
        c.a,c.x,c.y,c.p,c.sp=43,19,24 if face else 58,0x61,240
        for _ in range(1500):
            if c.pc==EDGE.PC+3:break
            c.step()
        else:raise AssertionError(('F801 actual backed call bound',hex(c.pc)))
        return word(m,0xc60f),bytes(m.ram[2][:0x800]),(c.a,c.x,c.y,c.p,c.sp),c.processorCycles
    good=bad=0;peak=0
    for edge,face,foot,inside,outside,roof in itertools.product(
            (0,16,256,448,0xfff0),(0,255),(31,56,203,263),(0,0x54),(0,0x54),(False,True)):
        roof_present=roof and ((foot-24)&0xf0)>=48
        accepted=edge!=0 and foot>=56 and inside and not outside and not roof_present
        a=run(before,edge,face,foot,inside,outside,roof)
        b=run(after,edge,face,foot,inside,outside,roof)
        assert a[2]==b[2]
        if accepted:
            assert b[0]==edge+(-8 if face else 8)
            assert a[1][:0x60f]==b[1][:0x60f] and a[1][0x611:]==b[1][0x611:]
            good+=1
        else:
            assert a[:3]==b[:3],(edge,face,foot,inside,outside,roof,a[0],b[0])
            bad+=1
        peak=max(peak,b[3])
    a=run(before,448,255,203,0x54,0,False)
    b=run(after,448,255,203,0x54,0,False)
    assert (a[0],b[0])==(408,440)
    return dict(actual_backed_positive_edges=good,actual_backed_unchanged_fallbacks=bad,
                actual_source_align_X=[a[0],b[0]],projected_native_climb_exit_center=452,max_CPU=peak)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();args.output.mkdir(exist_ok=True)
    chunks,payload,cookie,layout=images(args.output)
    original,final,patches,delta=compose(payload,cookie)
    print('Funded/rebased Prince',json.dumps(layout),flush=True)
    template,_=Q.M.OLD.image()
    oldbase=dict(template,raw=original['a08d'])
    newbase=dict(template,raw=final['a08d'])
    before,_=Q.C.C.cold(oldbase,38)
    after,cold=Q.C.C.cold(newbase,38)
    runtime,meta,_=chunks
    assert bytes(after.ram[3][:len(runtime)])==live(runtime)
    assert bytes(after.ram[2][0x800:0x800+len(meta)])==meta
    assert all(bytes(after.ram[k][0x1fe0:0x1ff0])==cookie for k in (2,3))
    for row in (15,36):
        reference=N.fork(before)
        old=bytes(reference.ram[2][0x800:0x800+len(meta)])
        old_return=I.invoke(reference,193,0xb08c+3*row)
        m=N.fork(after)
        result=I.invoke(m,193,0xb08c+3*row)
        assert result['regs'][3]&1
        assert result['regs']==old_return['regs']
        deltas=lambda origin,target:[(0xc800+i,a,b) for i,(a,b) in enumerate(zip(origin,target)) if a!=b]
        old_delta=deltas(old,reference.ram[2][0x800:0x800+len(meta)])
        new_delta=deltas(meta,m.ram[2][0x800:0x800+len(meta)])
        assert old_delta==new_delta and all(pc>=GRID_END for pc,_,_ in new_delta),(row,old_delta,new_delta)
    print('Actual current Prince cold and both warm rows retained worker',flush=True)
    poses=test_pose(before,after)
    print('Actual 408/2578 native pose differential',json.dumps(poses),flush=True)
    climb=test_climb(before,after)
    result=dict(passed=True,private_source_only=True,ROM_written=False,
                parent_SHA256=PARENTS['a08d'][1],expected_memory_only_SHA256=sha(final['a08d']),
                supported_parents={key:dict(SHA256=pair[1],expected_memory_only_SHA256=sha(final[key]))
                                   for key,pair in PARENTS.items()},patches=patches,
                parent_delta_bytes_preserved=delta,full_Mini_payload_and_all_nonpatch_bytes_exact=True,
                Prince_cookie=cookie.hex(),layout=layout,pose_differential=poses,climb=climb,
                actual_cold_CPU=cold['CPU'],both_full_headers=True,actual_warm_rows=[15,36],
                scope='Exact existing 44 carriers, old nine frontend spans and raw38 cookie only. '
                      'Only private pose metadata and one original align call are adapted. Current real cold and warm '
                      'overlay backing, original rendering and isolated CPU source ledge projection. '
                      'Native pipe landing and hardware interrupt qualification remain pending.',
                bindings={str(f.relative_to(R)):sha(f.read_bytes()) for f in
                          (Path(__file__),SOURCE,EDGE.WORKER,EDGE.TRACE,OLD,O/'pose-source.json',
                           O/'pose-pool.bin',O/'pose-runtime.bin',O/'pose-metadata.bin',O/'pose-worker.s')})
    (args.output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('passed','expected_memory_only_SHA256','pose_differential','climb')}))


if __name__=='__main__':main()
