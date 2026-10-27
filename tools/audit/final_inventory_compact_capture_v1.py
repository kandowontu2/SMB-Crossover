"""Lossless streamed NESPPU01 reader and I/O-only native source adapter."""
from pathlib import Path
import csv,hashlib,json,struct

WIDTH,HEIGHT=256,240
FRAME_BYTES=WIDTH*HEIGHT*4
MAGIC=b'NESPPU01'+struct.pack('<HHI',WIDTH,HEIGHT,32)
HEADER=struct.Struct('<BBHIIII')
MAX_CONTAINER=1_500_000_000
MAX_RECORDS=25_000
MODULE=Path(__file__).with_suffix('.lua')

def word_fnv(raw):
    assert len(raw)%4==0
    value=2166136261
    for (word,)in struct.iter_unpack('<I',raw):value=((value^word)*16777619)&0xffffffff
    return value

def decode(mode,payload,previous,expected):
    assert mode in[0,1,2]
    if mode==0:raw=payload
    else:
        out=[];i=0;size=0
        while i<len(payload):
            control=payload[i];i+=1;count=(control&127)+1
            length=4 if control&128 else count*4
            assert i+length<=len(payload),'Truncated RLE token'
            part=payload[i:i+length];i+=length
            if control&128:part*=count
            size+=len(part);assert size<=expected,'Oversized RLE payload';out.append(part)
        raw=b''.join(out)
        if mode==2:
            assert previous is not None and len(previous)==len(raw),'Missing XOR predecessor'
            raw=bytes(a^b for a,b in zip(raw,previous))
    assert len(raw)==expected,'Decoded frame length'
    return raw

def records(container):
    """Stream decoded records; retain only one previous image, never PNG trees."""
    container=Path(container);assert container.stat().st_size<=MAX_CONTAINER
    with container.open('rb')as f:
        assert f.read(16)==MAGIC,'Wrong container header'
        ordinal=0;previous=None
        while header:=f.read(HEADER.size):
            assert len(header)==HEADER.size,'Partial record header'
            kind,mode,reserved,sequence,meta_bytes,payload_bytes,checksum=HEADER.unpack(header)
            assert kind in[1,2,3]and reserved==0 and sequence==ordinal+1 and sequence<=MAX_RECORDS
            assert 0<meta_bytes<=65536 and payload_bytes<=FRAME_BYTES
            at=f.tell()-HEADER.size;meta_raw=f.read(meta_bytes);payload=f.read(payload_bytes)
            assert len(meta_raw)==meta_bytes and len(payload)==payload_bytes,'Partial record payload'
            meta=json.loads(meta_raw);expected=meta['decoded_bytes']
            assert expected==FRAME_BYTES if kind!=3 else 0<expected<=1024
            assert kind!=3 or mode==0
            raw=decode(mode,payload,previous,expected);assert word_fnv(raw)==checksum,'Source-buffer word checksum differs'
            if kind!=3:previous=raw
            ordinal=sequence
            yield dict(type='record',record=sequence,offset=at,bytes=f.tell()-at,kind=kind,mode=mode,name=meta['name'],decoded_bytes=len(raw),stamp=meta['stamp'],full_ordinal=meta['full_ordinal'],word_fnv1a32=checksum),raw

def verify(container,index,full_index=None):
    """Validate encoded bytes, all indices/aliases and optional native PPU CSV."""
    rows=[json.loads(s)for s in Path(index).open(encoding='utf-8')]
    expected=[q for q in rows if q['type']=='record'];actual=[];hashes={};names={};full=[];stream=hashlib.sha256();decoded=0
    for q,raw in records(container):
        actual.append(q);hashes[q['record']]=hashlib.sha256(raw).hexdigest();names[q['name']]=q['record']
        if q['kind']==1:full.append(q);stream.update(raw);decoded+=len(raw)
    assert actual==expected,'Container/index physical records differ'
    assert[q['full_ordinal']for q in full]==list(range(1,len(full)+1))
    kinds={q['record']:q['kind']for q in actual};by_id={q['record']:q for q in actual};last_full=None;seen=set();aliases=0
    for q in rows:
        if q['type']=='record':
            seen.add(q['record']);names[q['name']]=q['record']
            if q['kind']==1:last_full=q['record']
        else:
            assert q['type']=='alias'and q['record']in seen and q['record']==last_full and kinds[q['record']]==1
            assert q['decoded_bytes']==FRAME_BYTES and q['stamp']==by_id[q['record']]['stamp']
            aliases+=1;names[q['name']]=q['record']
    if full_index is not None:
        csv_rows=list(csv.DictReader(Path(full_index).open(newline='')));assert len(csv_rows)==len(full)
        assert[int(q['ordinal'])for q in csv_rows]==list(range(1,len(full)+1))
        for p,q in zip(csv_rows,full):
            for key,current in [('ppu_frame','ppu_frame'),('scanline','scanline'),('dot','dot'),('cpu_cycle','cpu_cycle')]:assert int(p[key])==q['stamp'][current]
    named=[q for q in rows if q.get('name','').endswith('.argb')and q['name']not in['actual-ppu.argb','first-failure.argb']]
    return dict(passed=True,format='NESPPU01',full_frames=len(full),decoded_full_bytes=decoded,decoded_full_sha256=stream.hexdigest(),physical_records=len(actual),named_aliases=aliases,named_capture_index=named,virtual_names=names,record_sha256=hashes,container_bytes=Path(container).stat().st_size,container_sha256=hashlib.sha256(Path(container).read_bytes()).hexdigest(),index_sha256=hashlib.sha256(Path(index).read_bytes()).hexdigest(),screenshots_created=0,per_frame_files=0)

def read_virtual(container,index,name):
    rows=[json.loads(s)for s in Path(index).open(encoding='utf-8')];matches=[q for q in rows if q.get('name')==name];assert matches,name;target=matches[-1]['record']
    for q,raw in records(container):
        if q['record']==target:return raw
    raise AssertionError('Missing indexed virtual capture')

def adapt_script(original):
    """Only prepend the I/O shim; every original callback/body byte remains."""
    prefix='FINAL_ITEM_PROGRESSIVE=';assert original.startswith(prefix)and'FINAL_COMPACT_CAPTURE'not in original
    first,body=original.split('\n',1)
    inserted='''-- BEGIN FINAL_COMPACT_CAPTURE_IO_ONLY_V1
local FINAL_COMPACT_CAPTURE=(function()
'''+MODULE.read_text(encoding='utf-8')+'''
end)().install(OUTPUT,{container_bytes=1500000000,records=25000},function()
 local s=emu.getState();return{ppu_frame=s['ppu.frameCount'],scanline=s['ppu.scanline'],dot=s['ppu.cycle'],cpu_cycle=s['cpu.cycleCount']}
end)
-- END FINAL_COMPACT_CAPTURE_IO_ONLY_V1
'''
    result=first+'\n'+inserted+body
    assert result.replace(inserted,'',1)==original
    assert original.count('emu.addMemoryCallback')==result[len(first)+1+len(inserted):].count('emu.addMemoryCallback')
    return result,inserted

def collect_full_ppu(out):
    out=Path(out);z=json.loads((out/'ppu-capture-native-result.json').read_text());rows=list(csv.DictReader((out/'actual-ppu-index.csv').open(newline='')))
    packed=verify(out/'captures.nesppuv1',out/'captures-index.jsonl',out/'actual-ppu-index.csv')
    assert z['passed']and z['actual_mode_readback']==1 and z['original_done_seen']
    assert z['frames']==len(rows)==packed['full_frames']and z['bytes']==packed['decoded_full_bytes']==len(rows)*FRAME_BYTES
    assert all(int(b['ppu_frame'])>int(a['ppu_frame'])for a,b in zip(rows,rows[1:]))
    assert all(int(q['mode'])==1 for q in rows if int(q['updates'])>0)
    events=[json.loads(s)for s in(out/'events.jsonl').open()]
    captures=[q['data']['name']+'.argb'for q in events if q['kind']=='ppu-frame-captured']
    assert captures==[q['name']for q in packed['named_capture_index']],'Every ordered native named capture must exist in the container index'
    return dict(passed=True,frames=len(rows),bytes=packed['decoded_full_bytes'],raw_sha256=packed['decoded_full_sha256'],index_sha256=hashlib.sha256((out/'actual-ppu-index.csv').read_bytes()).hexdigest(),container=packed)

def adapt_collector(original):
    """Replace only the raw-file reader, retaining every native predicate."""
    anchor='from final_megaproto_common_collector_witness_v1 import ordered_case_witnesses'
    assert original.count(anchor)==1
    begin=original.index(" try:\n  z=json.loads((out/'ppu-capture-native-result.json').read_text())")
    end=original.index(" except Exception as e:errors.append('FullPPU: '+str(e))",begin)
    old=original[begin:end];new=" try:\n  parts['full_actual_PPU']=collect_full_ppu(out)\n"
    added='\nfrom final_inventory_compact_capture_v1 import collect_full_ppu'
    result=original[:begin]+new+original[end:];result=result.replace(anchor,anchor+added)
    assert result.replace(anchor+added,anchor).replace(new,old,1)==original
    return result,dict(old_block=old,new_block=new,added_import=added,all_other_collector_mechanics_launch_predicates_literal=True)
