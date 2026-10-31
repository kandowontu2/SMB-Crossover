"""Genuine source-only SMB3+05b1 graft onto immutable installed Bowser66c663."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
P=R/'build/peach-palette-fix-1030-v1/joint'
S=R/'build/smb3plus-peach-gravity-consumer-1031-v1/joint'
C=R/'build/bowser-playable-jump-v1/joint'
B=R/'build/bowser-current64-v3'
O=R/'build/smb3plus-current66-source-1031-v1';J=O/'joint'
PLAN=R/'build/smb3plus-current66-adoption-plan-1031-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8',newline='\n')
def save(p,q):write(p,json.dumps(q,indent=2)+'\n')
def once(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)


def main():
    assert not O.exists()
    plan=json.loads((PLAN/'plan.json').read_text())
    for n,h in plan['bindings'].items():assert sha(n)==h,n
    for d,h in [(P,plan['common_ancestor']),(S,plan['leaf']),(C,plan['source_base'])]:assert sha(d/'candidate.nes')==h
    shutil.copytree(C,J)
    roots=[C,B/'joint',P,S]
    def rt(s):
        for root in roots:s=s.replace(str(root),str(J)).replace(root.as_posix(),J.as_posix())
        return s
    # Rebind owned source/config paths before any assembler can run. Other
    # immutable source/object dependencies remain original read-only inputs.
    for p in J.rglob('*'):
        if p.is_file()and p.suffix in['.s','.inc','.cfg']:write(p,rt(p.read_text()))
    modules=plan['source_inventory'][:5]
    for item in modules:
        n=item['path'];assert item['current_module_equals_ancestor']
        write(J/n,rt((S/n).read_text()))
    names=J/'src/new_roster_dispatch.s'
    t=names.read_text();t=once(t,'  lda #28\n  clc\n  adc M3Variant\n  jmp NameIndex\n',
        '  jmp MbMenuNameSelect\n  .res 6,$ea\n');write(names,t)
    menu=J/'src/character_select.s';t=menu.read_text()
    t=once(t,'  lda M3Variant\n  eor #1\n  sta M3Variant\n',
        '  inc M3Variant\n  lda M3Variant\n  and #3\n  sta M3Variant\n')
    t=once(t,'  .res 12,$ea\nGbPitNavContinue:',
        '  .res 9,$ea ; Fund the three-byte four-identity Select cycle.\nGbPitNavContinue:');write(menu,t)
    helpers=['smb3plus_body_host.s','smb3plus_kick_host.s','smb3plus_float_state.inc',
             'smb3plus_float_data.s','smb3plus_menu_name.s']
    for n in helpers+['smb3plus-chr.s']:write(J/n,rt((S/n).read_text()))
    for n in['toad-smb3plus-body.chr','peach-smb3plus-body.chr']:shutil.copyfile(S/n,J/n)
    entry=J/'entrypoint.s';t=entry.read_text()
    for n in helpers:
        assert f'.include "{n}"'not in t
        t+='\n.include "'+n+'"\n'
    write(entry,t)
    cfg=J/'private.cfg';t=cfg.read_text();assert 'SMB3PLUS_BODY_CHR:'not in t
    match=re.search(r'^\s*BENJ_MARIO_CHR:[^\n]+\n',t,re.M);assert match
    t=t[:match.end()]+'    SMB3PLUS_BODY_CHR:load=UNALLOCATED_CHR_MEM,type=ro,start=$f2400;\n'+t[match.end():]
    write(cfg,t)
    assert (J/'union.s').read_text()==rt((C/'union.s').read_text()),'Current compressed union must not be replaced'
    logs=[]
    def run(label,cmd):
        proof=validate(cmd,J,cwd=R)
        z=subprocess.run(cmd,cwd=R,text=True,capture_output=True)
        p=O/(label+'.json');save(p,dict(command=cmd,validation=proof,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));logs.append(p)
        assert z.returncode==0,(label,z.stderr)
    for n in['main','union']:
        cmd=[rt(x)for x in json.loads((B/(n+'-build.json')).read_text())['command']]
        cmd[1:1]=['-I',str(J),'-I',str(J/'src'),'--bin-include-dir',str(J)]
        cmd[-1]=str(J/('entrypoint.s'if n=='main'else'union.s'))
        for flag in['-o','--create-full-dep','--create-dep','-l','--listing']:
            if flag in cmd:cmd[cmd.index(flag)+1]=str(J/(n+'.o'if flag=='-o'else n+'.dep'if'dep'in flag else n+'.lst'))
        run(n+'-build',cmd)
    cmd=[rt(x)for x in json.loads((S.parent/'chr-build.json').read_text())['command']]
    run('chr-build',cmd)
    cmd=[rt(x)for x in json.loads((C.parent/'final-link.json').read_text())['command']]
    assert cmd.count(str(J/'main.o'))==1 and cmd.count(str(J/'union.o'))==1
    cmd.append(str(J/'smb3plus-chr.o'));run('final-link',cmd)
    prepare(R,J/'candidate.nes')
    old,leaf,new=[scoped_load(d/'candidate.nes')for d in[C,S,J]]
    base=scoped_load(P/'candidate.nes')
    # Verification oracle only. The cart above came solely from true source
    # assembly/link; no expected bytes are written to any ROM file.
    expected=bytes(y if x!=y else z for x,y,z in zip(base['raw'],leaf['raw'],old['raw']))
    assert new['raw']==expected,'Compiled source differs from exact disjoint composition oracle'
    assert old['raw'][:16]==new['raw'][:16]
    ds={i for i,(x,y)in enumerate(zip(old['raw'],new['raw']))if x!=y}
    assert len(ds)==36451
    ch=16+128*8192
    assert old['raw'][ch:ch+969*1024]==new['raw'][ch:ch+969*1024]
    assert old['raw'][ch+1019*1024:]==new['raw'][ch+1019*1024:]
    for bank in[119,120,125,127]:
        lo=16+bank*8192;assert old['raw'][lo:lo+8192]==new['raw'][lo:lo+8192],bank
    union=next(g for g in old['segs'].values()if g['name']=='"HOST_UNION"')if any(g['name']=='"HOST_UNION"'for g in old['segs'].values())else None
    if union:
        lo=int(union['ooffs'],0);size=int(union['size'],0);assert old['raw'][lo:lo+size]==new['raw'][lo:lo+size]
    # Every externally consumed current export from every actual link object
    # is checked at its resolved address, not inferred from copied label text.
    publics=set();unresolved=set();object_inputs=[]
    oldcmd=json.loads((C.parent/'final-link.json').read_text())['command']
    for name in oldcmd:
        if not name.endswith('.o'):continue
        obj=Path(name);object_inputs.append(dict(path=str(obj),sha256=sha(obj)))
        z=subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-exports',str(obj)],cwd=R,text=True,capture_output=True)
        assert z.returncode==0,(obj,z.stderr)
        for n in re.findall(r'Name:\s+"([^"]+)"',z.stdout):
            if n in old['syms']and'val'in old['syms'][n]:
                assert n in new['syms']and address(old,n)==address(new,n),('Current66 export moved',n)
                publics.add(n)
            else:unresolved.add(n)
    current_M3=[n for n,z in old['syms'].items()if n.startswith('M3')and z.get('type')=='lab']
    allowed_missing={'M3Palette::Pick','M3Palette::Identity'}
    allowed_moved={'M3NoToggle','M3StatusNameDispatch::Names','M3StatusNameDispatch::Loop','M3StatusNameDispatch::Done'}
    for n in current_M3:
        if n in allowed_missing:assert n not in new['syms'];continue
        assert n in new['syms'],n
        if n not in allowed_moved:assert address(old,n)==address(new,n),n
    for n in['bowser.bin','ram3.bin','code.bin','data.bin','ff-cookie.bin','bt/cache.bin','bt/cookie.bin','bowser/cookie.bin']:
        assert sha(C/n)==sha(J/n),('Existing current66 payload/cookie changed',n)
    q=dict(status='PRIVATE_SOURCE_SMB3PLUS_ON_CURRENT66_ORACLE_EXACT_CONTROLS_PENDING',
        source=True,native=False,installed=False,readiness_count_updated=False,
        candidate=sha(J/'candidate.nes'),base=sha(C/'candidate.nes'),leaf=sha(S/'candidate.nes'),
        common_ancestor=sha(P/'candidate.nes'),source_compilation_only=True,binary_overlay=False,
        exact_disjoint_source_oracle=True,changed_bytes=len(ds),
        CHR_outside_969_1019_exact=True,header_fixed_and_DMC_exact=True,
        current66_resolved_object_exports_preserved=len(publics),
        unresolved_non_debug_object_exports=sorted(unresolved),actual_link_objects=object_inputs,
        all_current66_M3_public_PCs_exact=True,original_M3_labels=len(current_M3),
        internal_labels_removed=sorted(allowed_missing),internal_labels_moved=sorted(allowed_moved),
        compressed_current_union_retained=True,existing_current66_cache_images_cookies_exact=True,
        runtime_state='Existing selected17 M3 state5C64..67; no new global lease/common protocol',
        limitations=['Ground pound unfinished','Custom stomp delay unfinished','Special art unfinished','Kick SFX request dropped','No native proof for this composed hash'],
        bindings={str(p.resolve()):sha(p)for p in[Path(__file__),PLAN/'handoff.json',PLAN/'plan.json',
            C.parent/'handoff.json',S.parent/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',
            J/'private.cfg',J/'entrypoint.s',J/'union.s',*[J/x['path']for x in plan['source_inventory'][:7]],
            *[J/n for n in helpers],J/'smb3plus-chr.s',J/'toad-smb3plus-body.chr',J/'peach-smb3plus-body.chr',*logs]})
    save(O/'source-stage.json',q)
    print(json.dumps({k:v for k,v in q.items()if k not in['bindings','actual_link_objects','unresolved_non_debug_object_exports']}))


if __name__=='__main__':main()
