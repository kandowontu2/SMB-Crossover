"""New private body backing/cookie over the exact granted current83 image."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import measure_prince_body_owner_1103_v178 as B
import measure_prince_lzdict_1102_v9 as D
import build_storage_guard_v1 as G
V,O=B.V,B.O
PARENT=R/'build/combined-owner-auth-root-1103-v116/combined-auth-private.nes'
PARENT_SHA='80d3ae95894f5ddb430c3e753dd95f3fc2eca6a87d8e1afdb4b8ce8376ec795a'
CURRENT=R/'build/bub-menu-candidate-1102-v2'


def images():
    return (O/'body-runtime.bin').read_bytes(),(O/'body-metadata.bin').read_bytes(),V.M.B.images()[2]


def image():
    q=json.loads((O/'body-manifest-v180.json').read_text())
    assert B.sha(PARENT)==q['parent_SHA256']==PARENT_SHA
    for name,digest in q['bindings'].items():assert B.sha(R/name)==digest,name
    base,_=V.M.image();raw=bytearray(PARENT.read_bytes())
    for row in q['patches']:
        at=row['file_offset'];old=bytes.fromhex(row['old_hex']);new=bytes.fromhex(row['new_hex'])
        assert raw[at:at+len(old)]==old
        raw[at:at+len(new)]=new
    assert B.digest(raw)==q['expected_memory_only_SHA256']
    return dict(base,raw=bytes(raw)),q


def main():
    G.preflight(private_root=O,reserved_bytes=400000,reserved_files=9,fresh=True)
    assert json.loads((O/'renderer-CPU-v179.json').read_text())['passed']
    raw=PARENT.read_bytes();assert B.digest(raw)==PARENT_SHA
    grant=R/'docs/qa/allocations/combined-owner-auth-1103-v116.json'
    assert json.loads(grant.read_text())['expected_candidate_SHA256']==PARENT_SHA
    chunks=images();packed=[D.encode(data)for data in chunks]
    text=(V.O/'cold-worker-v158.s').read_text();rows=[]
    for name,data,encoded in zip(['Runtime','Metadata','State'],chunks,packed):
        start=0xc500 if name=='Runtime'else 0xc300 if name=='State'else 0xe100-len(encoded)
        for suffix,value in [('Input',start),('Packed',len(encoded)),('Bytes',len(data))]:
            text,n=re.subn(r'(?m)^'+name+suffix+r'=\$[0-9a-f]+$',name+suffix+f'=${value:04x}',text);assert n==1
        rows.append(dict(name=name,uncompressed_bytes=len(data),compressed_bytes=len(encoded),source_start=start,SHA256=B.digest(data)))
    (O/'body-worker.s').write_text(text)
    cfg='MEMORY{B:start=$d25e,size=$100,file=%O;W:start=$c100,size=$200,file=%O;}SEGMENTS{BOOT:load=B,type=ro;WORKER:load=W,type=ro;}'
    (O/'body-worker.cfg').write_text(cfg)
    cc=R/'tools/Windows/cc65/bin'
    for command in [[cc/'ca65.exe',O/'body-worker.s','-o',O/'body-worker.o'],[cc/'ld65.exe','-C',O/'body-worker.cfg',O/'body-worker.o','-o',O/'body-worker.bin','-Ln',O/'body-worker.lbl']]:
        run=subprocess.run(list(map(str,command)),capture_output=True,text=True);assert run.returncode==0,run.stderr
    (O/'body-worker.o').unlink()
    worker=(O/'body-worker.bin').read_bytes();assert len(worker)==444
    art=(V.O/'prince-body-8x16.chr').read_bytes();decoder=(V.O/'cold-decoder-v25.bin').read_bytes()
    payload=art+decoder+worker+b''.join(packed);assert len(payload)<=45056
    (O/'body-pool.bin').write_bytes(payload)
    previous=json.loads((V.O/'backdrop-manifest-v159.json').read_text())
    oldcookie=bytes.fromhex(previous['Prince_cookie'])
    cookie=bytes([0xa7,38,2])+hashlib.sha256(b''.join(chunks)+payload).digest()[:13]
    labels=json.loads((CURRENT/'combined-auth-v83-measurement.json').read_text())['labels']
    address=labels['PrCookie'];cookie_at=16+65*8192+address-0xa000
    assert raw[cookie_at:cookie_at+16]==oldcookie
    # Actual current source names this exact resident data table; no manager
    # or selector instruction, table pointer, cold address or ABI is replaced.
    own=(CURRENT/'combined-auth-v83.s').read_text()
    declared=own.split('PrCookie:\n',1)[1].splitlines()[0]
    assert bytes(int(x.strip().removeprefix('$'),16)for x in declared.removeprefix('.byte ').split(','))==oldcookie
    out=bytearray(raw);patches=[]
    def put(at,data,**fields):
        old=raw[at:at+len(data)];out[at:at+len(data)]=data
        patches.append(dict(file_offset=at,bytes=len(data),old_hex=old.hex(),new_hex=data.hex(),old_SHA256=B.digest(old),new_SHA256=B.digest(data),**fields))
    put(cookie_at,cookie,physical_PRG=65,CPU_half_open=[address,address+16],role='Only current83 Prince cookie data; all shared instructions/pointers exact')
    carriers=sorted([r for r in previous['patches']if 'physical_CHR'in r],key=lambda r:r['source_offset'])
    assert len(carriers)==44
    for index,row in enumerate(carriers):
        at=row['file_offset'];old=bytes.fromhex(row['new_hex'])
        assert raw[at:at+len(old)]==old,'Current116 Prince carrier unchanged since159'
        data=payload[index*1024:(index+1)*1024]
        if data:put(at,data,physical_CHR=row['physical_CHR'],source_offset=index*1024,role='Existing44 Prince carriers; unchanged source art, new source-owned descriptor repair')
    allowed=set()
    for row in patches:allowed.update(range(row['file_offset'],row['file_offset']+row['bytes']))
    changed=[i for i,(a,z)in enumerate(zip(raw,out))if a!=z]
    assert all(i in allowed for i in changed)
    # Original source art is retained exactly at the scattered granted pages.
    for index in range(len(art)):
        row=carriers[index//1024];assert out[row['file_offset']+index%1024]==art[index]
    q=dict(measured=True,qualified=False,source_backed_fullcold_pending=True,ROM_written=False,
           parent_ROM=str(PARENT.relative_to(R)),parent_SHA256=PARENT_SHA,
           expected_memory_only_SHA256=B.digest(out),Prince_cookie=cookie.hex(),old_Prince_cookie=oldcookie.hex(),
           Bub_cookie='a72701f3691d419fd9ae7473840ce393',patches=patches,images=rows,
           physical_pages=44,payload_bytes=len(payload),physical_spare=45056-len(payload),runtime_bytes=len(chunks[0]),metadata_bytes=len(chunks[1]),state_bytes=len(chunks[2]),
           cookie_CPU=address,current_shared_instructions_all_exact=True,all_out_of_patch_bytes_exact=True,
           original_art_bytes_exact=len(art),total_changed_bytes=len(changed),
           required='Root private source/lifetime review, actual fullcold/current-owner/foreign/retire/headers/Fresh and newpath IRQ/genuineFF/nested qualification, then root native probe. No ROM/install/admission claim.',
           bindings={str(p.relative_to(R)):B.sha(p)for p in [Path(__file__),Path(B.__file__),O/'measurement.json',O/'renderer-CPU-v179.json',O/'body-runtime.bin',O/'body-metadata.bin',O/'body-worker.s',O/'body-worker.cfg',O/'body-worker.bin',O/'body-worker.lbl',O/'body-pool.bin',V.O/'backdrop-manifest-v159.json',V.O/'native-state-v153.bin',V.O/'native-audio-v157.s',CURRENT/'combined-auth-v83.s',CURRENT/'combined-auth-v83.bin',CURRENT/'combined-auth-v83-extra.bin',CURRENT/'combined-auth-v83-selector.s',CURRENT/'combined-auth-v83-selector.bin',CURRENT/'combined-auth-v90-composition.json',grant]})
    (O/'body-manifest-v180.json').write_text(json.dumps(q,indent=2)+'\n')
    assert image()[0]['raw']==out
    print(json.dumps({k:v for k,v in q.items()if k not in ['bindings','patches']}))


if __name__=='__main__':main()
