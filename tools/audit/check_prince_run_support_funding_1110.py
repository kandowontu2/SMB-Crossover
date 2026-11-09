"""Fit sustained Prince pipe support inside the existing authenticated carrier."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile

import check_prince_run_support_1110 as Run


Current,P,Support,R = Run.Current,Run.P,Run.Support,Run.R
N,I = Support.N,Support.I
SOURCE = R/'tools/reference/prince_mixed_pose_1110.s'
POSE = P.V.O/'prince-pose-grid-v37.bin'
COMPACT_PROOF = R/'build/prince-climb-funded-1109-v1/result.json'
POSITIVE = R/'build/prince-run-support-1110/trajectory.json'
LOADER = Current.SHAFT.with_name('descent-loader.s')
CONFIG = P.O/'pose-worker.cfg'
GRID_BASE,GRID_PROJECT,GRID_X = 0xc800,0xd922,0xd94c


def positions(records):
    y,_,x = zip(*records)
    signed = lambda n:(n^128)-128
    return tuple(map(signed,y)),tuple(map(signed,x))


def grid_parts(records):
    y,x = positions(records)
    if len({a%8 for a in y})!=1 or len({a%8 for a in x})!=1:
        return None
    bx,by = min(x),min(y)
    width,height = (max(x)-bx)//8,(max(y)-by)//8
    if max(width,height)>15:
        return None
    tiles = bytes(r[1] for r in records)
    cells = [((a-bx)//8<<4)|(b-by)//8 for a,b in zip(x,y,strict=True)]
    compact = width<4 and height<8 and all(not t&1 for t in tiles)
    if not compact:
        encoded = bytes(n for pair in zip(cells,tiles,strict=True) for n in pair)
    else:
        encoded = bytearray()
        for start in range(0,len(cells),2):
            part = cells[start:start+2]
            nibs = [((c>>4)<<2)|(c&3) for c in part]
            encoded.append((nibs[0]<<4)|(nibs[1] if len(part)==2 else 0))
            encoded.extend(tiles[start+i]|((c>>2)&1) for i,c in enumerate(part))
    return compact,bytes((bx&255,by&255))+bytes(encoded)


def hybrid(packet,n,prefix):
    records = list(zip(*[packet[prefix+i::3] for i in range(3)],strict=True))
    assert len(records)==n
    options = []
    for k in range(1,n):
        grid = grid_parts(records[k:])
        if grid is None:
            continue
        compact,tail = grid
        marker = k|(0x80 if compact else 0)
        body = packet[:prefix]+bytes([marker])+tail[:2]+packet[prefix:prefix+3*k]+tail[2:]
        options.append((len(body),k,body))
    _,_,packed = min(options)
    assert len(packed)<len(packet)
    return packed


def geometry(packed,frame):
    tag = int.from_bytes(packed[2*frame:2*frame+2],'little')
    if tag&0xc000!=0x4000:
        return P.geometry(packed,frame)
    start = tag&0x3fff
    header = packed[start]
    n,pages = header&15,(header>>4)&3
    end = start+2+pages
    control,bx,by = packed[end:end+3]
    k = control&0x7f
    raw = packed[end+3:end+3+3*k]
    offset = end+3+3*k
    tail = bytearray()
    for i in range(n-k):
        if control&0x80:
            if not i&1:
                pair = packed[offset]
                offset += 1
            low = pair&15 if i&1 else pair>>4
            tile = packed[offset]
            offset += 1
            coord = ((low&12)<<2)|(low&3)|((tile&1)<<2)
            tile &= 0xfe
        else:
            coord,tile = packed[offset:offset+2]
            offset += 2
        tail.extend(((by+8*(coord&15))&255,tile,(bx+8*(coord>>4))&255))
    return packed[start:end],raw+bytes(tail)


def pack(old):
    tags = [int.from_bytes(old[i:i+2],'little') for i in range(0,478,2)]
    records = sorted(set(tags)-{0xffff},key=lambda n:n&0x3fff)
    new,changed,remap = bytearray(b'\xff'*478),[],{}
    for tag,stop in zip(records,records[1:]+[len(old)],strict=True):
        start,end = tag&0x3fff,stop&0x3fff
        packet = old[start:end]
        tag_bits = tag&0xc000
        if tag_bits==0:
            header = packet[0]
            replacement = hybrid(packet,header&15,2+((header>>4)&3))
            changed.append((tag,len(packet)-len(replacement)))
            tag_bits,packet = 0x4000,replacement
        remap[tag] = len(new)|tag_bits
        new.extend(packet)
    for i,tag in enumerate(tags):
        if tag!=0xffff:
            new[2*i:2*i+2] = remap[tag].to_bytes(2,'little')
    assert len(changed)==26 and len(old)-len(new)==sum(n for _,n in changed)==199
    assert all(P.geometry(old,i)==geometry(bytes(new),i) for i in range(239))
    return bytes(new),[tags.index(tag) for tag,_ in changed]


def fit(out,base,seed):
    body,shaft,compact = (Current.read(p) for p in (P.OLD,Current.SHAFT,COMPACT_PROOF))
    original,_,state = P.Q.source_images()
    live = bytearray(seed.ram[3][:len(original)])
    assert live[0x1fa3:0x1fd8]==(P.V.O/'native-live-v149.bin').read_bytes()
    live[0x1fa3:0x1fd8] = original[0x1fa3:0x1fd8]
    meta = bytearray(seed.ram[2][0x800:0x1fcc])
    previous_grid,_ = P.pack(POSE.read_bytes())
    assert meta[:len(previous_grid)]==previous_grid
    packed,hybrid_frames = pack(previous_grid)
    start,end = GRID_BASE+len(packed),GRID_BASE+len(previous_grid)
    layout = compact['layout']
    assert layout['compact_half_open'][0]==end
    helper = P.Q.M.labels(P.V.O/'pose-grid-helper-v37.lbl')
    labels = Current.read(P.O/'pose-source.json')['labels']
    declarations = dict(Byte=labels['Byte'],ResetPair=layout['compact_labels']['ResetPair'],
                        GridFlag=helper['PpGridFlag'],GridBaseX=helper['PpGridBaseX'],GridBaseY=helper['PpGridBaseY'],
                        ExistingGridX=GRID_X+5)
    assert bytes(meta[GRID_X-GRID_BASE:GRID_X-GRID_BASE+8])==bytes.fromhex('2c5fd9100bad62d9')
    assembly = ''.join(f'{name}=${address:04x}\n' for name,address in declarations.items())+SOURCE.read_text(encoding='utf-8')
    encode = P.Q.M.CODEC.encode
    previous = [encode(x) for x in (bytes(live),bytes(meta),state)]
    assert [len(x) for x in previous]==shaft['layout']['packed_bytes']
    def assemble(name,source,config):
        with tempfile.TemporaryDirectory(dir=out) as directory:
            return P.assemble(Path(directory),name,source,config)

    decoder,dlab = assemble('mixed',assembly,P.one_segment(start,end-start,'MIXED_POSE'))
    seam = start+len(decoder)
    worker,wlab = assemble('support',Run.source(),P.one_segment(seam,end-seam))
    assert wlab['PpD297Support']==seam and dlab['MixedPoseEnd']==seam
    assert len(worker)==Current.read(POSITIVE)['worker_bytes']==128
    old = bytes.fromhex('20e2bd')
    Support.V3.V.replace(live,0xa000,Support.CALL,old,b'\x20'+seam.to_bytes(2,'little'))
    meta[:end-GRID_BASE] = (packed+decoder+worker).ljust(end-GRID_BASE,b'\0')
    P.call(meta,GRID_BASE,GRID_PROJECT,declarations['ResetPair'],dlab['ResetMixedPose'])
    Support.V3.V.replace(meta,GRID_BASE,GRID_X,bytes.fromhex('2c5fd9'),b'\x4c'+dlab['ReadMixedX'].to_bytes(2,'little'))
    chunks = bytes(live),bytes(meta),state
    streams = [encode(data) for data in chunks]
    boot = LOADER.read_text(encoding='utf-8')
    for name,data in zip(('Runtime','Metadata','State'),streams,strict=True):
        origin = 0xc500 if name=='Runtime' else 0xc300 if name=='State' else 0xe100-len(data)
        for suffix,n in [('Input',origin),('Packed',len(data))]:
            boot,hits = re.subn(rf'(?m)^{name}{suffix}=\$[0-9a-f]+$',f'{name}{suffix}=${n:04x}',boot)
            assert hits==1
    loader,_ = assemble('loader',boot,CONFIG.read_text(encoding='utf-8'))

    pages = sorted((p for p in body['patches'] if 'physical_CHR' in p),key=lambda p:p['source_offset'])
    assert len(pages)==44 and all(not 962<=p['physical_CHR']<=968 for p in pages)
    old_payload = b''.join(base['raw'][p['file_offset']:p['file_offset']+1024] for p in pages)
    decoder_end = 31072+len((P.V.O/'cold-decoder-v25.bin').read_bytes())
    prior_end = decoder_end+len(loader)
    assert len(loader)==444 and old_payload[prior_end:prior_end+sum(map(len,previous))]==b''.join(previous)
    assert 0xe100-len(streams[1])>=0xc300
    payload = old_payload[:decoder_end]+loader+b''.join(streams)
    assert len(payload)<=44*1024,dict(size=len(payload),packed=list(map(len,streams)))
    cookie = bytes([0xa7,38,2])+hashlib.sha256(b''.join(chunks)+payload).digest()[:13]
    current = Current.BASE.read_bytes()
    final = bytearray(base['raw'])
    scopes = {p['offset']:(len(bytes.fromhex(p['preimage'])),p['role']) for p in shaft['patches']}
    for i,p in enumerate(pages):
        offset = p['file_offset']
        data = payload[i*1024:(i+1)*1024]
        if data:
            final[offset:offset+1024] = data+current[offset+len(data):offset+1024]
            scopes[offset] = (1024,f'Prince physical CHR {p["physical_CHR"]}')
    final[P.COOKIE:P.COOKIE+16] = cookie
    patches = []
    for offset,(length,role) in sorted(scopes.items()):
        old,new = current[offset:offset+length],final[offset:offset+length]
        if old!=new:
            patches.append(dict(offset=offset,preimage=old.hex(),replacement=new.hex(),role=role))
    assert Current.apply(current,patches)==final
    data = dict(hybrid_frames=hybrid_frames,raw_pose_bytes_reclaimed=199,decoder_bytes=len(decoder),
                decoder_half_open=[start,seam],support_half_open=[seam,seam+len(worker)],
                execution_spare=end-seam-len(worker),payload_bytes=len(payload),pool_spare=44*1024-len(payload),
                packed_bytes=list(map(len,streams)))
    return bytes(final),patches,chunks,cookie,data,worker


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    assert out.is_relative_to(R/'build') and out!=R/'build'
    out.mkdir(exist_ok=True)
    path = out/'proof.json'
    assert not path.exists() and Current.read(POSITIVE)['passed']
    base,_,_ = Current.current()
    seed,_ = P.Q.C.C.cold(base,38)
    raw,patches,chunks,cookie,layout,worker = fit(out,base,seed)
    print(json.dumps(layout),flush=True)
    new,cold = P.Q.C.C.cold(dict(base,raw=raw),38)
    assert bytes(new.ram[3][:len(chunks[0])])==P.live(chunks[0])
    assert bytes(new.ram[2][0x800:0x800+len(chunks[1])])==chunks[1]
    assert all(bytes(new.ram[k][0x1fe0:0x1ff0])==cookie for k in (2,3))
    for row in (15,36):
        warm = N.fork(new)
        assert I.invoke(warm,193,0xb08c+3*row)['regs'][3]&1
        a,b = layout['support_half_open']
        assert bytes(warm.ram[2][a-0xc000:b-0xc000])==worker
    pose = P.test_pose(seed,new)
    print('All 408 pose/OAM/CHR comparisons passed.',flush=True)
    original = Support.fixture(seed,mode=1,frame=1)
    patched = Support.fixture(new,mode=1,frame=1)
    a,b = [Support.result(m,Support.TERRAIN) for m in (original,patched)]
    assert a['X']==708 and a['action']==7 and b['X']==731 and b['action']==1 and b['surface']==144
    refs = (Path(__file__),Path(Run.__file__),Path(Current.__file__),SOURCE,POSE,COMPACT_PROOF,POSITIVE,
            LOADER,CONFIG,Current.BASE,Current.SHAFT,P.OLD,Support.ROM)
    proof = dict(passed=True,ROM_written=False,Mesen_run=False,native_pending=True,parent_SHA256=Current.BASE_PIN,
                 previous_private_SHA256=Current.PRINCE_PIN,expected_memory_only_SHA256=P.sha(raw),
                 Prince_cookie=cookie.hex(),patches=patches,layout=layout,cold_CPU=cold['CPU'],warm_rows=[15,36],
                 pose=pose,ordinary_run_support=[a,b],interrupts_pending=True,
                 bindings={str(p.resolve()):P.sha(p.read_bytes()) for p in refs})
    path.write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
    print(proof['expected_memory_only_SHA256'],flush=True)


if __name__=='__main__':
    main()
