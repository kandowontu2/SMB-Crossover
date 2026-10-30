"""Assemble actual source chunk/native-render transport in owned FF RAM3."""
from pathlib import Path
import argparse,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_ff_ram3_kernel_v1 import sha,write
from prepare_ff_current_component_v2 import qualified
from finalize_ff_current_component_v3 import dependencies
from ff_host_combat_controls_v1 import bundle
from check_tmnt_render_oa import address,location
P=R/'build/final-fantasy-host-pickups-v3'
O=R/'build/final-fantasy-host-render-v5'
SOURCE=R/'tools/reference/final_fantasy_host_render_v3.s'


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=O)
    O=parser.parse_args().out.resolve()
    assert not O.exists()
    hp=R/'build/final-fantasy-host-pickups-qualified-v1/handoff.json'
    assert sha(hp)=='db2e2d4fb28a7082836cc2611eb851107f2b8f36aa6a5c58728df55e7a99386d'
    h=json.loads(hp.read_text());assert h['passed']
    for p,d in h['bindings'].items():assert sha(p)==d,p
    b=qualified(R/'build/final-fantasy-current-component-v2/linked/candidate.nes')
    O.mkdir()
    names=['component','publisher','combat','terrain','pickups','render','cull','host-definitions']
    for n in names[:5]:(O/(n+'.s')).write_bytes((P/(n+'.s')).read_bytes())
    # Original ART label visibility only; every compiled original byte checked.
    with (O/'component.s').open('a')as f:
        f.write('\n.export FfEntryRecord,FfRecordLo,FfRecordHi\n.export FfEnemyBit,FfRectH,FfRectPage,FfRectW\n')
    (O/'ff-host-health.inc').write_bytes((P/'ff-host-health.inc').read_bytes())
    (O/'render.s').write_bytes(SOURCE.read_bytes())
    import ff_host_pickups_controls_v2 as T
    original=T.C.bundle(P);m=T.setup(original)
    T.put(m,PlayerOutlinesOff=0,FfSlot=1)
    rows=[]
    for entry in range(144,158):
        chunks=[]
        for chunk in range(8):
            T.put(m,FfSlot=1)
            cpu,_,_=T.run(m,'FfRenderChunk',a=entry,x=chunk,y=1)
            if not cpu.p&1:break
            count=T.get(m,'FfRenderBuffer')
            off=T.get(m,'FfRenderYOffset')+256*T.get(m,'FfRenderYOffset',1)
            if off&32768:off-=65536
            values=[]
            for i in range(0,count,4):
                y=T.get(m,'FfRenderBuffer',i+3)
                values.append(off+(y-256 if y&128 else y))
            lo,hi=(min(values),max(values))if values else(0,0)
            assert -256<=lo<=hi<=256,(entry,chunk,lo,hi)
            chunks.append(dict(chunk=chunk,min_Y=lo,max_Y=hi,source_record_count=count//4))
        assert 1<=len(chunks)<=8
        rows.append(dict(entry=entry,chunks=chunks))
    table=['.segment "FF_HOST_CULL_TABLES"','.export FfCullCount,FfCullLo,FfCullHi',
           'FfCullCount:.byte '+','.join(str(len(row['chunks']))for row in rows),
           'FfCullLo:.byte '+','.join('<FfCull'+str(row['entry'])for row in rows),
           'FfCullHi:.byte '+','.join('>FfCull'+str(row['entry'])for row in rows)]
    for row in rows:
        table+=['FfCull'+str(row['entry'])+':']
        for chunk in row['chunks']:
            table+=['.word $%04x,$%04x'%(chunk['min_Y']&65535,chunk['max_Y']&65535)]
    write(O/'cull.s','\n'.join(table)+'\n')
    cullbytes=42+4*sum(len(row['chunks'])for row in rows)
    write(O/'cull-source-proof.json',json.dumps(dict(passed=True,source_image_sha256=sha(P/'ram3.bin'),
        generated_by_actual_original_FfRenderChunk=True,entries=14,chunks=sum(len(row['chunks'])for row in rows),
        bytes=cullbytes,source_bounds_with_signed_OAM_adjustment=rows),indent=2)+'\n')
    imports={}
    for n in names[:-1]:
        for line in (O/(n+'.s')).read_text().splitlines():
            m=re.fullmatch(r'\.import(zp)? (.+)',line)
            if not m:continue
            for item in m[2].split(','):
                item=item.strip()
                if item.startswith('Ff'):continue
                suffix='zp'if m[1]else''
                assert imports.get(item,suffix)==suffix,item
                imports[item]=suffix
    definitions=[]
    for n,suffix in sorted(imports.items()):
        s=b['syms'][n]
        assert (s['addrsize']=='zeropage')==(suffix=='zp'),(n,s['addrsize'],suffix)
        definitions+=['.export'+suffix+' '+n,n+'='+s['val'].replace('0x','$')]
    physical=(location(b,'MetaspriteRenderLoop')-16)//8192
    assert physical==4
    definitions+=['.exportzp FfNativeRendererBank',f'FfNativeRendererBank=${physical|128:02x}']
    write(O/'host-definitions.s','; Genuine actual host exports, not a flat near-call fixture.\n'+'\n'.join(definitions)+'\n')
    cfg=(P/'kernel.cfg').read_text().replace(P.as_posix(),O.as_posix())
    cfg=cfg.replace('FINAL_FANTASY_CORE:load=RAM3','FF_HOST_RENDER:load=RAM3,type=ro,start=$a300;\nFF_HOST_CULL_TABLES:load=RAM3,type=ro,start=$a800;\nFINAL_FANTASY_CORE:load=RAM3')
    write(O/'kernel.cfg',cfg)
    ca=R/'tools/Windows/cc65/bin/ca65.exe';logs=[]
    commands=[[str(ca),'-g','--cpu','6502x','-I',str(O),'-I',str(R/'src'),'--bin-include-dir',str(R),'--create-full-dep',str(O/(n+'.d')),'-o',str(O/(n+'.o')),str(O/(n+'.s'))]for n in names]
    commands+=[[str(ca.with_name('ld65.exe')),'-C',str(O/'kernel.cfg'),'--dbgfile',str(O/'kernel.dbg'),'-Ln',str(O/'kernel.lbl'),'-m',str(O/'kernel.map'),'-o',str(O/'unused-output.bin'),*[str(O/(n+'.o'))for n in names]]]
    for command in commands:
        q=subprocess.run(command,cwd=R,capture_output=True,text=True)
        logs.append(dict(command=command,returncode=q.returncode,stdout=q.stdout,stderr=q.stderr))
        write(O/'compile-log.json',json.dumps(logs,indent=2)+'\n');assert q.returncode==0,q.stderr
    z=bundle(O);start=address(z,'FfHostRenderBegin');end=address(z,'FfHostRenderEnd')
    assert start==0xa300 and end<=0xa800
    old,new=(P/'ram3.bin').read_bytes(),(O/'ram3.bin').read_bytes()
    assert all(a==v for i,(a,v)in enumerate(zip(old,new))if not (0x300<=i<end-0xa000 or 0x800<=i<0x800+cullbytes))
    for n in ['art.bin','art.chr']:assert (O/n).read_bytes()==(P/n).read_bytes()
    bindings={**h['bindings'],str(hp):sha(hp),str(SOURCE):sha(SOURCE),str(Path(__file__).resolve()):sha(__file__)}
    for n in names:
        for p in dependencies(O/(n+'.d')):bindings[str(p.resolve())]=sha(p)
    bindings.update({str(p.resolve()):sha(p)for p in O.iterdir()if p.is_file()})
    proof=dict(passed=True,status='OFFLINE_ACTUAL_FF_FULL_CHUNK_DRAW_CPU_PENDING',
               image_sha256=sha(O/'ram3.bin'),host_render_bytes=end-start,cull_metadata_bytes=cullbytes,
               start=f'{start:04X}',end=f'{end:04X}',native_renderer_bank=physical|128,
               extra_address_storage_bytes=0,
               new_adapter_fields='Existing FF projectile record bytes2/3 become per-draw chunk/part cursors, reset by genuine allocation.',
               native=False,cart_hooks=False,bindings=bindings)
    write(O/'build-proof.json',json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items()if k!='bindings'}))
