"""Source-partition current85 menu padding/unused ship tail; reproduce every byte."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
J=R/'build/doki-current-component-1101-v1';O=R/'build/karnov-host-resource-base-1101-v1'
EXPECTED='f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
write=lambda p,t:p.write_text(t,encoding='utf-8',newline='\n')


def main():
    assert not(O/'source-stage.json').exists();O.mkdir(exist_ok=True)
    assert sha(J/'candidate.nes')==EXPECTED
    parent=scoped_load(J/'candidate.nes');inventory=json.loads((R/'build/karnov-current-resource-audit-1101-v1/inventory.json').read_text());assert inventory['candidate']==EXPECTED
    for p,h in inventory['bindings'].items():assert sha(p)==h,p
    # Genuine linked49-entry body table reaches at most393 with its paired
    # page. World394, ZeldaII395 and Parodius HUD396..398 remain untouched.
    at=location(parent,'VvBodyChr');body=parent['raw'][at:at+49];assert {256+x for x in body}=={380,382,384,386,388,390,392}
    selected=set(256+x+d for x in body for d in [0,1]);assert max(selected)==393
    for name,first,last in [('Z2_UI_CHR',395,396),('PN_HUD_CHR',396,399)]:
        s=next(v for v in parent['segs'].values()if v['name']=='"'+name+'"');lo=int(s['ooffs'],0);assert lo==1048592+first*1024 and int(s['size'],0)==(last-first)*1024
    assert all(not inventory['pages'][p]['owners']and inventory['pages'][p]['zero']for p in range(399,412))
    source=R/'build/hogan-thomas-current/src/cf_menu_body.inc';t=source.read_text();old='.res $b22-$0d-(FmCfHelperEnd-FmCfHelperStart),$ff'
    assert t.count(old)==1
    t=t.replace(old,'''KrResidentBegin:
.export KrResidentBegin,KrResidentLimit
; Source-only new private lease inside real menu FF padding. No code yet.
.res $b22-$0d-(FmCfHelperEnd-FmCfHelperStart),$ff
KrResidentLimit:
''')
    write(O/'cf_menu_body.inc',t);write(O/'entrypoint.s',(J/'menu/entrypoint.s').read_text())
    # ca65 searches an included file's own folder before -I. Its exact caller
    # must be local too, or it silently resolves the old sibling helper.
    select_source=source.with_name('character_select.s');write(O/'character_select.s',select_source.read_text())
    cfg=(J/'candidate.cfg').read_text();old='VIC_CHR_MEM: start=$5f000, size=$8000, type=ro, fill=yes, file=%O, fillval=$00;';assert cfg.count(old)==1
    cfg=cfg.replace(old,'''VIC_CHR_MEM: start=$5f000, size=$4c00, type=ro, fill=yes, file=%O, fillval=$00;
KRN_KERNEL_MEM: start=$63c00,size=$2000,type=ro,fill=yes,file=%O,fillval=$00;
KRN_BODY_MEM: start=$65c00,size=$1400,type=ro,fill=yes,file=%O,fillval=$00;''')
    cfg+='\nSEGMENTS { KR_KERNEL_IMAGE:load=KRN_KERNEL_MEM,type=ro,optional=yes; KR_BODY_CHR:load=KRN_BODY_MEM,type=ro,optional=yes; }\n'
    number=0
    def target(m):
        nonlocal number
        if m[1]in ['', '%O']:return m[0]
        number+=1;return 'file="'+(O/'sideoutputs'/f'{number:03d}.bin').as_posix()+'"'
    cfg=re.sub(r'file\s*=\s*"([^"\r\n]*)"',target,cfg);write(O/'candidate.cfg',cfg)
    build=json.loads((J/'graphics-main-build.json').read_text())['command'][:]
    for option,name in [('-o','main.o'),('--create-full-dep','main.dep')]:build[build.index(option)+1]=str(O/name)
    build[-1]=str(O/'entrypoint.s');build[1:1]=['-I',str(O)]
    link=json.loads((J/'graphics-link.json').read_text())['command'][:];old=str(J/'main.o');assert link.count(old)==1;link[link.index(old)]=str(O/'main.o')
    for option,name in [('-C','candidate.cfg'),('-o','candidate.nes'),('-Ln','candidate.lbl'),('-m','candidate.map')]:link[link.index(option)+1]=str(O/name)
    link[link.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate.dbg')
    for tag,command in [('main-build',build),('link',link)]:
        guard=validate(command,O,cwd=R)
        for item in guard['outputs']:Path(item['path']).parent.mkdir(parents=True,exist_ok=True)
        q=subprocess.run(command,cwd=R,capture_output=True,text=True);save(O/(tag+'.json'),dict(command=command,guard=guard,returncode=q.returncode,stderr=q.stderr));assert q.returncode==0,q.stderr
    p=O/'candidate.dbg';keep={'version','info','file','lib','mod','seg','scope','sym'};p.write_bytes(b''.join(l for l in p.read_bytes().splitlines(keepends=True)if l.split(b'\t',1)[0].decode('ascii')in keep));prepare(R,O/'candidate.nes')
    assert(O/'candidate.nes').read_bytes()==(J/'candidate.nes').read_bytes()
    b=scoped_load(O/'candidate.nes');changed=[n for n,s in parent['syms'].items()if n not in b['syms']or s['val']!=b['syms'][n]['val']];assert not changed,changed[:20]
    lo,hi=address(b,'KrResidentBegin'),address(b,'KrResidentLimit');assert hi==0xbfb0 and hi-lo>=2400
    assert parent['raw'][16+29*8192+lo-0xa000:16+29*8192+hi-0xa000]==bytes([255])*(hi-lo)
    refs=[Path(__file__),source,select_source,J/'candidate.nes',J/'candidate.dbg',J/'candidate.cfg',J/'graphics-main-build.json',J/'graphics-link.json',R/'build/karnov-current-resource-audit-1101-v1/inventory.json',R/'tools/prepare_cv3_dmc_mirror.py',O/'cf_menu_body.inc',O/'character_select.s',O/'entrypoint.s',O/'candidate.cfg',O/'candidate.nes',O/'candidate.dbg',O/'main-build.json',O/'link.json']
    save(O/'baseline-controls.json',dict(passed=True,source=True,native=False,installed=False,all_ROM_bytes_exact=True,all_existing_symbols_exact=True,candidate=EXPECTED,resident=dict(bank=29,A_view=[lo,hi],bytes=hi-lo,source='Actual residual CF helper FF padding; fixed Rush reset and all old endpoints unchanged.'),CHR_kernel=[399,407],CHR_body=[407,412],CHR_pages=13,ship_body_superset=sorted(selected),retained_world_and_UI=[394,395,396,397,398],conditional_RAM_plan='No allocation/execution here. Future selected C2 kernel/RAM3 state requires full cookie/epoch/readiness/IRQ/foreign-owner qualification.',not_free='PRG125 is a post-link fixed-E/DMC mirror, not free despite linker gaps. No writes permitted there.',next='Build Karnov owned kernel/callbacks/loader and36-service host gates. Original projectile update, actual controls/options, native health/pickups/music and host gameplay remain required before admission.',bindings={str(p.resolve()):sha(p)for p in refs}))
    print(json.dumps(dict(passed=True,all_ROM_bytes_exact=True,all_symbols_exact=True,resident=[29,hex(lo),hex(hi),hi-lo],CHR_kernel=[399,407],CHR_body=[407,412],installed=False)))


if __name__=='__main__':main()
