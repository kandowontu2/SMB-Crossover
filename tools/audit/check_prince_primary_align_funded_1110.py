"""Fund the typed alignment repair by sharing two identical Prince pose packets."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import tempfile
from unittest.mock import patch

import check_prince_primary_align_lifetime_1110 as Life
import check_prince_run_support_funding_1110 as Pack


R, Route, N, I, Check = Life.R,Life.Route,Life.N,Life.I,Life.Check
P = Pack.P
ROOT = Life.ROOT
GRID = 0xc800
DECODER = 0xd68f
DROP = {52158:51097,52354:52340}


def share(data):
    tags = [int.from_bytes(data[i:i+2],'little') for i in range(0,478,2)]
    rows = sorted(set(tags)-{0xffff},key=lambda n:n&0x3fff)
    records = {tag:data[tag&0x3fff:end] for tag,end in zip(rows,
               [tag&0x3fff for tag in rows[1:]]+[len(data)],strict=True)}
    for drop,keep in DROP.items():
        assert drop>>14==keep>>14 and records[drop]==records[keep]
    packed,remap = bytearray(b'\xff'*478),{}
    for tag in rows:
        if tag in DROP:
            continue
        remap[tag] = (tag&0xc000)|len(packed)
        packed.extend(records[tag])
    for frame,tag in enumerate(tags):
        if tag!=0xffff:
            packed[2*frame:2*frame+2] = remap[DROP.get(tag,tag)].to_bytes(2,'little')
    assert len(data)-len(packed)==29
    assert all(Pack.geometry(data,f)==Pack.geometry(packed,f) for f in range(239))
    return bytes(packed),[dict(removed=d,retained=k,bytes=len(records[d])) for d,k in DROP.items()]


def assemble(out,name,source,cfg):
    with tempfile.TemporaryDirectory(dir=out) as temp:
        return P.assemble(Path(temp),name,source,cfg)


def compose(out,base,seed):
    prior_rt,_,state = P.Q.source_images()
    previous = bytearray(seed.ram[3][:len(prior_rt)])
    assert previous[0x1fa3:0x1fd8]==(P.V.O/'native-live-v149.bin').read_bytes()
    previous[0x1fa3:0x1fd8] = prior_rt[0x1fa3:0x1fd8]
    assert P.live(previous)==bytes(seed.ram[3][:len(previous)])
    meta = bytes(seed.ram[2][0x800:0x1fcc])
    original_grid,_ = P.pack(Pack.POSE.read_bytes())
    decoded,_ = Pack.pack(original_grid)
    assert len(decoded)==DECODER-GRID and meta[:len(decoded)]==decoded
    shared,duplicate_records = share(decoded)
    start = GRID+len(shared)
    worker,entries = assemble(out,'primary',Check.ASM.read_text(),P.one_segment(start,DECODER-start))
    assert start==0xd672 and len(worker)==29 and start+len(worker)==DECODER
    fixed_meta = shared+worker+meta[len(decoded):]
    assert len(fixed_meta)==len(meta) and fixed_meta[DECODER-GRID:]==meta[DECODER-GRID:]
    updated = bytearray(previous)
    for pc,name in ((Check.FIRST,'PpSavePrimaryAlign'),(Check.SECOND,'PpRestorePrimaryAlign')):
        off = pc-0xa000
        assert updated[off:off+3]==b'\x20\x0b\xc4'
        updated[off+1:off+3] = entries[name].to_bytes(2,'little')
    encode = P.Q.M.CODEC.encode
    old_chunks = (bytes(previous),meta,state)
    new_chunks = (bytes(updated),fixed_meta,state)
    old = [encode(data) for data in old_chunks]
    new = [encode(data) for data in new_chunks]
    assert [len(data) for data in old]==[6383,5544,1232]
    read = Check.Pair.Second.First.Pit.Current.read
    pages = sorted((p for p in read(P.OLD)['patches'] if 'physical_CHR' in p),key=lambda p:p['source_offset'])
    assert len(pages)==44 and len({p['file_offset'] for p in pages})==44
    raw = base['raw']
    existing = b''.join(raw[p['file_offset']:p['file_offset']+1024] for p in pages)
    decoder_end = 31072+len((P.V.O/'cold-decoder-v25.bin').read_bytes())
    loader_end = decoder_end+444
    assert existing[loader_end:loader_end+sum(map(len,old))]==b''.join(old)
    previous_cookie = bytes([0xa7,38,2])+sha256(b''.join(old_chunks)+existing[:44929]).digest()[:13]
    assert raw[P.COOKIE:P.COOKIE+16]==previous_cookie
    asm = Pack.LOADER.read_text(encoding='utf-8')
    for name,data in zip(('Runtime','Metadata','State'),new,strict=True):
        origin = 0xc500 if name=='Runtime' else 0xc300 if name=='State' else 0xe100-len(data)
        for suffix,val in [('Input',origin),('Packed',len(data))]:
            asm,hits = re.subn(rf'(?m)^{name}{suffix}=\$[0-9a-f]+$',f'{name}{suffix}=${val:04x}',asm)
            assert hits==1
    loader,_ = assemble(out,'loader',asm,Pack.CONFIG.read_text())
    assert len(loader)==444 and 0xe100-len(new[1])>=0xc300
    payload = existing[:decoder_end]+loader+b''.join(new)
    assert len(payload)<=len(existing)
    cookie = bytes([0xa7,38,2])+sha256(b''.join(new_chunks)+payload).digest()[:13]
    image = bytearray(raw)
    patches = []

    def add(at,data,role):
        before = raw[at:at+len(data)]
        if before==data:
            return
        assert image[at:at+len(data)]==before
        image[at:at+len(data)] = data
        patches.append(dict(offset=at,preimage=before.hex(),replacement=data.hex(),role=role))

    add(P.COOKIE,cookie,'Existing authenticated raw38 cookie')
    for i,page in enumerate(pages):
        data = payload[i*1024:(i+1)*1024]
        if data:
            add(page['file_offset'],data,f'Existing Prince physical CHR {page["physical_CHR"]}')
    result = bytes(image)
    assert Pack.Current.apply(raw,patches)==result
    layout = dict(duplicate_records=duplicate_records,worker_half_open=[start,DECODER],entries=entries,
                  packed_bytes=[len(data) for data in new],payload_bytes=len(payload),pool_spare=len(existing)-len(payload),
                  decoder_address_unchanged=DECODER,decoder_and_existing_code_exact=True)
    return result,new_chunks,cookie,patches,layout


def linked_fixtures(seed, linked, snap, proof):
    invoke = I.invoke
    outcomes, interrupt_fixtures = [],[]
    for row in proof['cases']:
        recorded = None

        def mapped(m,*args):
            nonlocal recorded
            assert recorded is None
            m.ram[3][:] = linked.ram[3]
            m.ram[2][0x800:] = linked.ram[2][0x800:]
            recorded = N.fork(m)
            return invoke(m,*args)

        with patch.object(I,'invoke',mapped):
            result,_ = Check.host(seed,snap,row['local_x'],row['facing'],row['alternate'],row['origin'],
                                  row['wall'],row['back_floor'])
        assert result['actor']==row['after']['actor'] and result['return_regs']==row['after']['return_regs']
        outcomes.append(dict(name=row['name'],actor=result['actor'],return_regs=result['return_regs']))
        if row['name'] in ('right authentic coordinates','left alternate low-byte wrap','right original solid-back control'):
            interrupt_fixtures.append((row['name'],recorded))
    return outcomes,interrupt_fixtures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    out = parser.parse_args().output.resolve()
    report = out/'funded.json'
    assert out==ROOT and not report.exists()
    read = Check.Pair.Second.First.Pit.Current.read
    assert sha256((out/'proof.json').read_bytes()).hexdigest()==Life.PROOF_SHA
    assert sha256((out/'lifetime.json').read_bytes()).hexdigest()=='fd44851f7ad05e25768332807a8aefe6e17f5fd7d46bfa2f9ae74bf348ad67ac'
    template,_,_ = Check.Pair.Second.First.Pit.Current.current()
    base = dict(template,raw=Route.ROM.read_bytes())
    assert sha256(base['raw']).hexdigest()==Route.PIN
    seed,_ = P.Q.C.C.cold(base,38)
    image,chunks,cookie,patches,layout = compose(out,base,seed)
    print('Exact carrier space',layout,flush=True)
    linked,cold = P.Q.C.C.cold(dict(base,raw=image),38)
    assert bytes(linked.ram[3][:len(chunks[0])])==P.live(chunks[0])
    assert bytes(linked.ram[2][0x800:0x800+len(chunks[1])])==chunks[1]
    assert all(bytes(linked.ram[k][0x1fe0:0x1ff0])==cookie for k in (2,3))
    warm = []
    for row in (15,36):
        differences = []
        for start in (seed,linked):
            m = N.fork(start)
            assert I.invoke(m,193,0xb08c+3*row)['regs'][3]&1
            before,after = start.ram[2],m.ram[2]
            differences.append([(i,before[i],after[i]) for i in range(0x800,0x1fcc) if before[i]!=after[i]])
        assert differences[0]==differences[1],differences
        a,b = [x-0xc000 for x in layout['worker_half_open']]
        assert m.ram[2][a:b]==linked.ram[2][a:b]
        warm.append(dict(row=row,unchanged_metadata_write_set=differences[0]))
    art = P.test_pose(seed,linked)
    print('All 408 native pose and OAM/CHR comparisons passed.',flush=True)
    snap = read(Check.WRITER)['retained_D17A_inputs']['190']
    cases,fixtures = linked_fixtures(seed,linked,snap,read(out/'proof.json'))
    vectors = []
    for name,m in fixtures:
        q = Life.stress(name,m,lambda q:I.invoke(q,3,Check.ENTRY,tuple(snap['registers'][:4]))['regs'],
                        [(2,*layout['worker_half_open']),(3,Check.FIRST,Check.SECOND+4),(2,0xc40b,0xc491)])
        print(name,q['cuts'],flush=True)
        vectors.append(q)
    refs = (Path(__file__),out/'proof.json',out/'lifetime.json',Path(Life.__file__),Path(Check.__file__),
            Route.ROM,Check.ASM,Pack.POSE,Pack.LOADER,Pack.CONFIG,P.OLD,Path(Pack.__file__))
    proof = dict(passed=True,ROM_written=False,Mesen_run=False,parent_SHA256=Route.PIN,
                 expected_memory_only_SHA256=sha256(image).hexdigest(),Prince_cookie=cookie.hex(),patches=patches,
                 layout=layout,actual_cold_CPU=cold['CPU'],warm_rows=warm,poses=art,linked_cases=cases,real_vectors=vectors,
                 scope='Two byte-identical pose packets share backing. Existing decoder and worker addresses are pinned. '
                       'Exact cold-backed original D17A restores the saved primary horizontal context on both sides. '
                       'Native wall-height policy remains unchanged. No ROM artifact or publication.',
                 bindings={p.relative_to(R).as_posix():sha256(p.read_bytes()).hexdigest() for p in refs})
    report.write_text(json.dumps(proof,separators=(',',':'))+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
