"""Emit guarded Karnov loader/kernel inside the proven current85 resource lease.

No gameplay ingress or menu admission changes. All old labels and other ROM
bytes must remain exact. Run only through the bounded runner, --resume on O.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from prepare_cv3_dmc_mirror import prepare
O=R/'build/karnov-host-resource-base-1101-v1'
J=R/'build/doki-current-component-1101-v1'
A=R/'build/karnov-original-source-1101-v1/source'
W=R/'build/karnov-original-weapons-1101-v1/source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
write=lambda p,t:p.write_text(t,encoding='utf-8',newline='\n')

def run(tag,command):
    guard=validate(command,O,cwd=R)
    for item in guard['outputs']:Path(item['path']).parent.mkdir(parents=True,exist_ok=True)
    p=subprocess.run(command,cwd=R,capture_output=True,text=True)
    save(O/(tag+'.json'),dict(command=command,guard=guard,returncode=p.returncode,stderr=p.stderr))
    assert p.returncode==0,p.stderr

def main():
    assert not(O/'source-stage.json').exists()
    base=json.loads((O/'baseline-controls.json').read_text());assert base['passed']
    refs=[Path(__file__),R/'tools/reference/karnov_cache_kernel_1101_v1.s',R/'tools/reference/karnov_cache_resident_1101_v1.inc',*[A/n for n in ['portable_dispatch.inc','portable_actor.inc']],*[W/n for n in ['portable_weapon.inc','portable_clear.inc']]]
    cookie=bytes([167,7,1,1])+hashlib.sha256(b''.join(p.read_bytes()for p in refs)).digest()[:12]
    (O/'kr-cookie.bin').write_bytes(cookie)
    write(O/'kr-kernel.s',(refs[1]).read_text());write(O/'kr-resident.inc',refs[2].read_text())
    # Recreate this one exact helper from the pinned source, replacing real pad.
    t=(R/'build/hogan-thomas-current/src/cf_menu_body.inc').read_text()
    old='.res $b22-$0d-(FmCfHelperEnd-FmCfHelperStart),$ff';assert t.count(old)==1
    t=t.replace(old,'''KrResidentBegin:
.export KrResidentBegin,KrResidentLimit
.include "kr-resident.inc"
.assert KrResidentEnd<= $bfb0,lderror,"Karnov resident exceeds real menu padding"
.res $b22-$0d-(FmCfHelperEnd-FmCfHelperStart)-(KrResidentEnd-KrResidentBegin),$ff
KrResidentLimit:
''')
    write(O/'cf_menu_body.inc',t)
    build=json.loads((O/'main-build.json').read_text())['command'][:]
    for opt in ['-I','--bin-include-dir']:build[1:1]=[opt,str(O)]
    run('cache-main-build',build)
    cc=R/'tools/Windows/cc65/bin/ca65.exe'
    command=[str(cc),'-g','-I',str(A),'-I',str(W),'--bin-include-dir',str(O),'-o',str(O/'kr-kernel.o'),str(O/'kr-kernel.s')]
    run('cache-kernel-build',command)
    cfg=(O/'candidate.cfg').read_text()
    if 'KR_RAM3_MEM:'not in cfg:
        cfg=cfg.replace('MEMORY {','MEMORY {\nKR_RAM3_MEM:start=$a000,size=$2000,type=ro,bank=3,fill=yes,fillval=$ff,file="'+(O/'kr-kernel.bin').as_posix()+'";',1)
        cfg+='\nSEGMENTS { KR_KERNEL:load=KR_RAM3_MEM,type=ro; }\n'
        write(O/'candidate.cfg',cfg)
    link=json.loads((O/'link.json').read_text())['command'][:]
    if str(O/'kr-kernel.o')not in link:link.append(str(O/'kr-kernel.o'))
    # First link resolves real imported R0, produces the RAM image; second emits
    # it as source-owned CHR bytes. No binary patching or opaque ROM restore.
    run('cache-first-link',link)
    image=(O/'kr-kernel.bin').read_bytes();assert len(image)==8192 and image[0x1fe0:0x1ff0]==cookie
    write(O/'kr-images.s','.segment "KR_KERNEL_IMAGE"\n.incbin "kr-kernel.bin"\n.segment "KR_BODY_CHR"\n.incbin "body.chr"\n')
    command=[str(cc),'-g','--bin-include-dir',str(O),'--bin-include-dir',str(R/'build/karnov-original-art-1101-v1'),'-o',str(O/'kr-images.o'),str(O/'kr-images.s')]
    run('cache-images-build',command);link.append(str(O/'kr-images.o'));run('cache-final-link',link)
    assert(O/'kr-kernel.bin').read_bytes()==image
    dbg=O/'candidate.dbg';keep={'version','info','file','lib','mod','seg','scope','sym'}
    dbg.write_bytes(b''.join(l for l in dbg.read_bytes().splitlines(keepends=True)if l.split(b'\t',1)[0].decode('ascii')in keep));prepare(R,O/'candidate.nes')
    old=scoped_load(J/'candidate.nes');new=scoped_load(O/'candidate.nes')
    # New repeats renumber assembler-only anonymous loop scopes; added farcall
    # expansions increment the compile-time counter. Neither is a runtime ABI.
    changed=[n for n,s in old['syms'].items()if (n not in new['syms']or s['val']!=new['syms'][n]['val'])and '$anon-SCOPE-'not in n and n!='_FARCALL_COUNT']
    assert not changed,changed[:20]
    lo,hi=[address(new,n)for n in ['KrResidentBegin','KrResidentLimit']];assert hi==0xbfb0
    allowed=[(16+29*8192+lo-0xa000,16+29*8192+hi-0xa000),(1048592+399*1024,1048592+412*1024)]
    delta=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b]
    assert delta and all(any(a<=i<b for a,b in allowed)for i in delta)
    assert address(new,'R0')==3 and address(new,'KrPointer')==3 and address(new,'KrState')==0xc000
    refs += [J/'candidate.nes',J/'candidate.dbg',O/'cf_menu_body.inc',O/'kr-kernel.s',O/'kr-resident.inc',O/'kr-cookie.bin',O/'kr-kernel.bin',O/'candidate.cfg',O/'candidate.nes',O/'candidate.dbg',O/'cache-final-link.json',R/'build/karnov-original-art-1101-v1/body.chr']
    save(O/'cache-assembly.json',dict(passed=True,source_CPU=False,native=False,installed=False,menu_admitted=False,ROM_sha256=sha(O/'candidate.nes'),cookie=cookie.hex(),resident_bytes=address(new,'KrResidentEnd')-lo,kernel_bytes=address(new,'KrKernelEnd')-0xa000,state='conditional RAM2 C000; kernel RAM3 A000',scratch=[3,4],no_NMI_owned_ZP=True,all_existing_runtime_symbols_exact=True,changed_bytes=len(delta),allowed_ROM_ranges=allowed,bindings={str(p.resolve()):sha(p)for p in refs}))
    print(json.dumps(dict(passed=True,candidate=sha(O/'candidate.nes'),resident_bytes=address(new,'KrResidentEnd')-lo,kernel_bytes=address(new,'KrKernelEnd')-0xa000,changed_bytes=len(delta),menu_admitted=False)))

if __name__=='__main__':main()
