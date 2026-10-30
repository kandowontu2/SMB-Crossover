"""Link exact FF terrain consumers into the private RAM3 image; no cart hooks."""
from pathlib import Path
import argparse,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_ff_ram3_kernel_v1 import sha,write
from prepare_ff_current_component_v2 import qualified
from finalize_ff_current_component_v3 import dependencies
from ff_host_combat_controls_v1 import bundle
from check_tmnt_render_oa import address
P=R/'build/final-fantasy-host-combat-v2'
O=R/'build/final-fantasy-host-terrain-v3'
SOURCE=R/'tools/reference/final_fantasy_host_terrain_v2.s'


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=O)
    O=parser.parse_args().out.resolve()
    assert not O.exists()
    hp=R/'build/final-fantasy-host-combat-qualified-v3/handoff.json'
    assert sha(hp)=='6773102feabdb2983d06b4b61fce4c6a62b1cba3865c21092c18b2f77bb1c2b6'
    h=json.loads(hp.read_text());assert h['passed']
    for p,d in h['bindings'].items():assert sha(p)==d,p
    b=qualified(R/'build/final-fantasy-current-component-v2/linked/candidate.nes')
    O.mkdir()
    names=['component','publisher','combat','terrain','host-definitions']
    for name in ['component','publisher','combat']:(O/(name+'.s')).write_bytes((P/(name+'.s')).read_bytes())
    (O/'ff-host-health.inc').write_bytes((P/'ff-host-health.inc').read_bytes())
    (O/'terrain.s').write_bytes(SOURCE.read_bytes())
    imports={}
    for name in names[:-1]:
        for line in (O/(name+'.s')).read_text().splitlines():
            m=re.fullmatch(r'\.import(zp)? (.+)',line)
            if not m:continue
            for n in m[2].split(','):
                n=n.strip()
                if n.startswith('Ff'):continue
                suffix='zp'if m[1]else''
                assert imports.get(n,suffix)==suffix,n
                imports[n]=suffix
    definitions=[]
    for n,suffix in sorted(imports.items()):
        s=b['syms'][n]
        assert (s['addrsize']=='zeropage')==(suffix=='zp'),(n,s['addrsize'],suffix)
        definitions+=['.export'+suffix+' '+n,n+'='+s['val'].replace('0x','$')]
    write(O/'host-definitions.s','; Actual current host ABI, offline image only.\n'+'\n'.join(definitions)+'\n')
    cfg=(P/'kernel.cfg').read_text().replace(P.as_posix(),O.as_posix())
    cfg=cfg.replace('FINAL_FANTASY_ART:load=ART','FF_HOST_TERRAIN:load=RAM3,type=ro,start=$b900;\nFINAL_FANTASY_ART:load=ART')
    write(O/'kernel.cfg',cfg)
    ca=R/'tools/Windows/cc65/bin/ca65.exe';logs=[]
    commands=[[str(ca),'-g','--cpu','6502x','-I',str(O),'-I',str(R/'src'),'--bin-include-dir',str(R),'--create-full-dep',str(O/(n+'.d')),'-o',str(O/(n+'.o')),str(O/(n+'.s'))]for n in names]
    commands+=[[str(ca.with_name('ld65.exe')),'-C',str(O/'kernel.cfg'),'--dbgfile',str(O/'kernel.dbg'),'-Ln',str(O/'kernel.lbl'),'-m',str(O/'kernel.map'),'-o',str(O/'unused-output.bin'),*[str(O/(n+'.o'))for n in names]]]
    for command in commands:
        q=subprocess.run(command,cwd=R,capture_output=True,text=True)
        logs.append(dict(command=command,returncode=q.returncode,stdout=q.stdout,stderr=q.stderr))
        write(O/'compile-log.json',json.dumps(logs,indent=2)+'\n');assert q.returncode==0,q.stderr
    z=bundle(O);size=address(z,'FfHostTerrainEnd')-address(z,'FfHostTerrainBegin')
    assert address(z,'FfHostTerrainBegin')==0xb900 and address(z,'FfHostTerrainEnd')<=0xbfe0
    old,new=(P/'ram3.bin').read_bytes(),(O/'ram3.bin').read_bytes()
    assert all(a==v for i,(a,v)in enumerate(zip(old,new))if not 0x1900<=i<0x1900+size)
    assert (O/'art.bin').read_bytes()==(P/'art.bin').read_bytes()
    assert (O/'art.chr').read_bytes()==(P/'art.chr').read_bytes()
    negative=R/'build/final-fantasy-host-terrain-nativebg-v1/controls.json'
    assert not json.loads(negative.read_text())['passed']
    bindings={str(negative):sha(negative),str(R/'tools/reference/final_fantasy_host_terrain_v1.s'):sha(R/'tools/reference/final_fantasy_host_terrain_v1.s'),**h['bindings'],str(hp):sha(hp),str(SOURCE):sha(SOURCE),str(Path(__file__).resolve()):sha(__file__)}
    for n in names:
        for p in dependencies(O/(n+'.d')):bindings[str(p.resolve())]=sha(p)
    bindings.update({str(p.resolve()):sha(p)for p in O.iterdir()if p.is_file()})
    proof=dict(passed=True,status='OFFLINE_SOURCE_LINKED_TERRAIN_CPU_PENDING',image_sha256=sha(O/'ram3.bin'),host_terrain_bytes=size,start='B900',end=hex(address(z,'FfHostTerrainEnd')),host_imports=len(imports),extra_RAM_bytes=0,scratch='First8 existing FfRenderBuffer bytes only before actual source renderer rewrites full descriptor.',native=False,cart_hook=False,bindings=bindings)
    write(O/'build-proof.json',json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items()if k!='bindings'}))
