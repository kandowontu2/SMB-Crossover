"""Source-link Hogan onto current f476 without copying old build/source trees."""
from pathlib import Path
import hashlib,json,re,subprocess,sys

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_contra_force_p1_coherent_cart_v2 import native_abi

P=R/'build/contra-force-projectile-contact-1031-v3'
W=R/'build/wwf-hogan-natural-source-v15'
A=R/'build/contra-force-world-roles-1031-v2/joint/candidate.nes'
O=R/'build/hogan-current'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p,q):p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def once(s,a,z):assert s.count(a)==1,(a,s.count(a));return s.replace(a,z,1)


def main():
    assert not(O/'source-stage.json').exists(),'Qualified source is immutable'
    pins={A:'a12661c1ddad2e15a8ce0589e86b5510703fd390e6346a982b14a6be0b742e3c',
          P/'joint/candidate.nes':'f4767d595a25bf64355b1e2cea86be7a93046f1cf139a4d9b0544e35f9ed4182',
          W/'joint/candidate.nes':'99b9026588e772e93cdc95e845ab3617ff4376260ad0a111b68c3d92925cbd27'}
    for p,h in pins.items():assert sha(p)==h,p
    O.mkdir(exist_ok=True);refs={Path(__file__),*pins}
    # Selective recovery of two exact include inputs into this task, without
    # rehydrating their old trees or copying immutable reference directories.
    missing=[]
    for recipe in ['union','ff-palette','bt-router']:
        depfile=W/'joint'/(recipe+'.dep')
        line=depfile.read_text().split(':\t',1)[1].split('\n',1)[0]
        for token in re.split(r'(?<!\\)\s+',line):
            if token:
                p=Path(token.replace('\\ ',' '))
                if not p.exists():missing.append(p)
    if missing:
        import zipfile
        with zipfile.ZipFile(R/'build/_recovery/legacy-sources-2026-10-31.zip')as z:
            index={q['path']:q for q in json.loads(z.read('index.json'))}
            for p in set(missing):
                q=index[p.relative_to(R/'build').as_posix()]
                data=z.read('objects/'+q['sha256']);assert hashlib.sha256(data).hexdigest()==q['sha256']
                target=O/'inputs'/p.name
                if target.exists():assert target.read_bytes()==data
                else:target.parent.mkdir(exist_ok=True);target.write_bytes(data)
    current=json.loads((P/'final-link.json').read_text())['command']
    donor=json.loads((W/'final-link.json').read_text())['command']
    main_parent=R/'build/bt-p2-cf-menu-source-1031-v2'
    mc=json.loads((main_parent/'main-build.json').read_text())['command']
    entry=next(Path(x)for x in mc if x.endswith('.s'))
    original=entry.read_text();modified=(W/'joint/host-main/entrypoint.s').read_text()
    assert modified.startswith(original)
    # These are zero-byte exports/imports appended to the current actual entry.
    trailer=modified[len(original):]
    assert all(not s.strip()or s.startswith(('.export ','.import '))for s in trailer.splitlines())
    write(O/'entrypoint.s',original+trailer)
    dep=(main_parent/'joint/main.dep').read_text().split(':\t',1)[1].split('\n',1)[0]
    deps=[Path(x.replace('\\ ',' '))for x in re.split(r'(?<!\\)\s+',dep)if x]
    refs.update(deps)
    changes={}
    # Graft only the reviewed small files that differ in the current Main's
    # actual include closure. No old Main object or whole tree is substituted.
    for name in ['character_select.s','full_roster_menu.s','full_roster_menu_art.inc',
                 'new_roster_dispatch.s','screen_render.s','cf_menu_body.inc']:
        matches=[p for p in deps if p.name==name];assert len(matches)==1,(name,matches)
        old=matches[0];new=W/'joint/host-main/src'/name
        before,after=old.read_text(),new.read_text()
        assert before!=after,name
        write(O/'src'/name,after)
        refs.update([old,new]);changes[name]=dict(actual_current_source=str(old),current_sha256=sha(old),grafted_sha256=sha(new))
    def run(name,cmd):
        guard=validate(cmd,O,cwd=R)
        for item in guard['outputs']:Path(item['path']).parent.mkdir(parents=True,exist_ok=True)
        z=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        save(O/(name+'.json'),dict(command=cmd,guard=guard,returncode=z.returncode,stderr=z.stderr))
        assert z.returncode==0,(name,z.stderr)
    mc=mc[:];mc[1:1]=['-I',str(O),'-I',str(O/'src')]
    mc[mc.index(str(entry))]=str(O/'entrypoint.s')
    for flag,n in [('-o','main.o'),('--create-full-dep','main.dep'),('--create-dep','main.dep'),('-l','main.lst')]:
        if flag in mc:mc[mc.index(flag)+1]=str(O/n)
    if not(O/'main.o').exists():run('main-build',mc)
    else:
        previous=json.loads((O/'main-build.json').read_text())
        assert previous['returncode']==0 and previous['command']==mc,'Resume only the unchanged compiled Main'
    replace={str(main_parent/'joint/main.o'):str(O/'main.o')}
    for name,obj,parentobj in [('union-build','union','build/bt-ready-menu-1031-v2/joint/union.o'),
                               ('bt-router-build','bt-router','build/bt-jmp-row-cold-source-v1/joint/bt/router.o'),
                               ('shared59-build','ff-palette','build/contra-force-p1-coherent-cart-v2/joint/ff-palette.o')]:
        cmd=json.loads((W/(name+'.json')).read_text())['command'][:]
        cmd[1:1]=['-I',str(O/'inputs')]
        source=next(Path(x)for x in cmd if x.endswith('.s'))
        # Recompile the exact reviewed small source; read-only include inputs
        # are shared with its existing producer rather than copied.
        for flag,n in [('-o',obj+'.o'),('--create-full-dep',obj+'.dep'),('--create-dep',obj+'.dep'),('-l',obj+'.lst')]:
            if flag in cmd:cmd[cmd.index(flag)+1]=str(O/n)
        run(name,cmd);replace[str(R/parentobj)]=str(O/(obj+'.o'));refs.add(source)
    # Add only WWF's granted memory/segments to the current actual layout.
    cfg=(P/'joint/candidate.cfg').read_text()
    wc=(W/'joint/candidate.cfg').read_text()
    wm,ws=wc.split('SEGMENTS {',1)
    memory=dict(re.findall(r'\b(WF_\w+)\s*:([^;]*);',wm))
    segments=dict(re.findall(r'\b(WF_\w+)\s*:([^;]*);',ws))
    assert len(memory)==8 and len(segments)==30
    cfg=once(cfg,'X5_NEW_60: start=$a000, size=$2000','X5_NEW_60: start=$a000, size=$936')
    pos=cfg.index(';',cfg.index('X5_NEW_60:'))+1
    cfg=cfg[:pos]+'\n'+''.join(n+':'+memory[n]+';\n'for n in ['WF_RESIDENT_A','WF_RESIDENT_C'])+cfg[pos:]
    cfg=once(cfg,'M3_CHR_MEM: start=$83000,size=$14000,type=ro,fill=yes,file=%O,fillval=$00;',
        'M3_CHR_MEM:start=$83000,size=$5800,type=ro,fill=yes,file=%O,fillval=$00;\n'+
        'WF_BODY_MEM:'+memory['WF_BODY_MEM']+';\nM3_WWF_UNALLOCATED:start=$8cc00,size=$a400,type=ro,file=%O,fill=yes,fillval=0;')
    cfg=once(cfg,'TMNT_CHR_MEM: start=$97000,size=$10000,type=ro,fill=yes,file=%O,fillval=$00;',
        'TMNT_CHR_MEM:start=$97000,size=$6400,type=ro,fill=yes,file=%O,fillval=$00;\n'+
        'WF_TEMPLATE_MEM:'+memory['WF_TEMPLATE_MEM']+';\nWF_METADATA_MEM:'+memory['WF_METADATA_MEM']+';\n'+
        'TMNT_WWF_UNALLOCATED:start=$a3c00,size=$3400,type=ro,file=%O,fill=yes,fillval=0;')
    cfg=once(cfg,'MEMORY {','MEMORY {\n'+''.join(n+':'+memory[n]+';\n'for n in ['WF_A1_MEM','WF_C2_MEM','WF_A3_MEM']))
    cfg=once(cfg,'SEGMENTS {','SEGMENTS {\n'+''.join(n+':'+body+';\n'for n,body in segments.items()))
    sidecount=0
    def redirect(m):
        nonlocal sidecount
        if m[1]in['','%O']:return m[0]
        sidecount+=1
        return 'file="'+(O/'sideoutputs'/(f'{sidecount:03d}-'+Path(m[1]).name)).as_posix()+'"'
    cfg=re.sub(r'file\s*=\s*"([^"\r\n]*)"',redirect,cfg)
    write(O/'candidate.cfg',cfg)
    cmd=[replace.get(x,x)for x in current]
    assert all(old in current for old in replace)
    for flag,n in [('-C','candidate.cfg'),('-o','candidate.nes'),('-Ln','candidate.lbl'),('-m','candidate.map')]:
        if flag in cmd:cmd[cmd.index(flag)+1]=str(O/n)
    cmd[cmd.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate.dbg')
    own=[x for x in donor if x.endswith('.o')and Path(x).is_relative_to(W/'joint')and Path(x).name not in ['main.o','union.o','bt-router.o','ff-palette.o']]
    assert len(own)==16
    cmd+=own
    run('final-link',cmd);prepare(R,O/'candidate.nes')
    # Strong whole-cartridge composition oracle: the independent CF delta and
    # Hogan delta from a126 must be disjoint and both present byte for byte.
    base=A.read_bytes();cf=(P/'joint/candidate.nes').read_bytes();wf=(W/'joint/candidate.nes').read_bytes()
    expected=bytearray(wf);cf_delta=0
    for i,(a,z)in enumerate(zip(base,cf)):
        if a!=z:
            assert wf[i]==a,('Overlapping CF/WWF grant',hex(i))
            expected[i]=z;cf_delta+=1
    actual=(O/'candidate.nes').read_bytes()
    assert len(base)==len(actual)==len(expected)and actual==expected,'Source link is not the exact disjoint composition'
    old=scoped_load(P/'joint/candidate.nes');new=scoped_load(O/'candidate.nes')
    imports=native_abi(new)
    for n in ['GameLoop','MenuResolveCharacter','InitScreen','FmPending','HuEntryBase','GmOnlyCommon','BtRouter','FwNativeDrawAll']:
        assert address(old,n)==address(new,n)and location(old,n)==location(new,n),n
    # Bind actual present source/link dependencies, without recursively growing
    # a graph of previous proof receipts or copying their generated outputs.
    deps2=(O/'main.dep').read_text().split(':\t',1)[1].split('\n',1)[0]
    refs.update(Path(x.replace('\\ ',' '))for x in re.split(r'(?<!\\)\s+',deps2)if x)
    refs.update(Path(x)for x in cmd if x.endswith('.o'))
    refs.update([P/'final-link.json',W/'final-link.json',P/'joint/candidate.cfg',W/'joint/candidate.cfg',
                 R/'tools/audit/private_build_outputs_v1.py',R/'tools/audit/build_storage_guard_v1.py'])
    refs.update(p for p in O.rglob('*')if p.is_file())
    report=dict(passed=True,source=True,native=False,installed=False,candidate=sha(O/'candidate.nes'),
                parent=pins[P/'joint/candidate.nes'],Hogan_component=pins[W/'joint/candidate.nes'],
                exact_disjoint_whole_cartridge_composition=True,preserved_CF_changed_bytes=cf_delta,
                public_native_imports_checked=len(imports),reviewed_source_grafts=changes,
                private_playable=75,roster_identities=86,source_only=True,
                limits=['Hogan and source branches require exact new-ROM native qualification before install.','Other five WWF characters, advanced wrestling/endurance/audio and full1-1/powerup coverage remain incomplete.','Campaign6f9f is a separate uninstalled component, not included in this composition.'],
                bindings={str(p.resolve()):sha(p)for p in refs})
    save(O/'source-stage.json',report)
    print(json.dumps({k:report[k]for k in ['passed','candidate','preserved_CF_changed_bytes','public_native_imports_checked']}))


if __name__=='__main__':main()
