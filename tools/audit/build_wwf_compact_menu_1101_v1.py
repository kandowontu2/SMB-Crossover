"""Exact current85 derivative: fit six authentic WWF menu previews in32px."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from prepare_cv3_dmc_mirror import prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
J=R/'build/doki-current-component-1101-v1';O=R/'build/menu-wwf-compact-1101-v1'
P=R/'build/hogan-thomas-current/src/character_select.s'
EXPECTED='f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
write=lambda p,s:p.write_text(s,encoding='utf-8',newline='\n')
def once(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)

def main():
    assert sha(J/'candidate.nes')==EXPECTED
    O.mkdir(exist_ok=True);assert not(O/'source-stage.json').exists()
    source=P.read_text();write(O/'character_select.s',source)
    write(O/'entrypoint.s',(J/'menu/entrypoint.s').read_text())
    cfg=(J/'candidate.cfg').read_text();number=0
    def destination(m):
        nonlocal number
        if m[1]in ['', '%O']:return m[0]
        number+=1;return 'file="'+(O/'sideoutputs'/(f'{number:03d}-'+Path(m[1]).name)).as_posix()+'"'
    write(O/'candidate.cfg',re.sub(r'file\s*=\s*"([^"\r\n]*)"',destination,cfg))
    build=json.loads((J/'graphics-main-build.json').read_text())['command'][:]
    build[1:1]=['-I',str(O)]
    for flag,name in [('-o','main.o'),('-l','main.lst'),('--create-dep','main.dep'),('--create-full-dep','main.dep')]:
        if flag in build:build[build.index(flag)+1]=str(O/name)
    build[-1]=str(O/'entrypoint.s')
    link=json.loads((J/'graphics-link.json').read_text())['command'][:]
    assert link.count(str(J/'main.o'))==1;link[link.index(str(J/'main.o'))]=str(O/'main.o')
    for flag,name in [('-C','candidate.cfg'),('-o','candidate.nes'),('-Ln','candidate.lbl'),('-m','candidate.map')]:link[link.index(flag)+1]=str(O/name)
    link[link.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate.dbg')
    def run(tag,cmd):
        guard=validate(cmd,O,cwd=R)
        for p in guard['outputs']:Path(p['path']).parent.mkdir(parents=True,exist_ok=True)
        q=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        save(O/(tag+'.json'),dict(command=cmd,output_guard=guard,returncode=q.returncode,stdout=q.stdout,stderr=q.stderr));assert q.returncode==0,q.stderr
    def compiled(tag):
        run(tag+'-main-build',build);run(tag+'-link',link)
        dbg=O/'candidate.dbg';keep={'version','info','file','lib','mod','seg','scope','sym'}
        dbg.write_bytes(b''.join(l for l in dbg.read_bytes().splitlines(keepends=True)if l.split(b'\t',1)[0].decode('ascii')in keep))
        prepare(R,O/'candidate.nes')
    compiled('baseline')
    assert(O/'candidate.nes').read_bytes()==(J/'candidate.nes').read_bytes(),'Exact source reproduction differs'
    save(O/'baseline-reproduction.json',dict(passed=True,ROM_sha256=EXPECTED,source_inputs_not_copied=True))
    source=once(source,'  farcall FmPending\n  bcs FmPendingPreview\n  cpx #30','  farcall FmPending\n  bcs FmPendingPreview\n  cpx #28\n  beq FmPendingGenericPreview\n  cpx #30')
    original='  ldx CrossoverMenuIndex\n  lda PreviewX,x\n  sta Player_X_Position'
    funded='''  ldx CrossoverMenuIndex
.if ::ENABLE_MMC5_EXPANDED
WfCompactX:
  txa
  and #$10
  bne WfCompactDefaultX
  lda PreviewX,x
  bne WfCompactHaveX
WfCompactDefaultX:
  lda #120
WfCompactHaveX:
.else
  lda PreviewX,x
.endif
  sta Player_X_Position'''
    source=once(source,original,funded)
    source=once(source,'  .repeat 13\n  .byte 120\n  .endrepeat\n','  ; Indices16..31 use the exact120px default above.\n')
    write(O/'character_select.s',source);compiled('compact')
    old,new=[scoped_load(p/'candidate.nes')for p in [J,O]]
    changed=[n for n,s in old['syms'].items()if(n not in new['syms']or s['val']!=new['syms'][n]['val'])and '$anon-SCOPE-'not in n]
    local={n for n in changed if n.startswith('DrawSelectionPreview::')}
    assert set(changed)<=local|{n.split('::')[-1]for n in local},changed[:30]
    for n in ['CrossoverMenuInput','MenuResolveCharacter','QueueSelection','DrawSelectionPreview','QueueVariantHint','QueueSelectName','QueueCursor','FmPending','FmResolve','FmStartFlags']:
        assert address(old,n)==address(new,n),(n,'Public menu address moved')
    lo=location(old,'DrawSelectionPreview');hi=location(old,'QueueVariantHint')
    assert hi-lo==234 and address(new,'DrawSelectionPreview::PreviewX')==0xabac
    delta=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b]
    assert delta and all(lo<=i<hi for i in delta),(len(delta),lo,hi)
    deps=[]
    for text in re.split(r'(?<!\\)\s+',(O/'main.dep').read_text().splitlines()[0].split(':\t',1)[1]):
        if text:
            p=Path(text.replace('\\ ',' '))
            if p.is_file():deps.append(p)
    inputs=[p for p in map(Path,link)if p.suffix=='.o'and p!=O/'main.o']
    refs=[Path(__file__).resolve(),P,J/'candidate.nes',J/'candidate.dbg',J/'graphics-main-build.json',J/'graphics-link.json',O/'entrypoint.s',O/'character_select.s',O/'candidate.cfg',O/'candidate.nes',O/'candidate.dbg',O/'compact-main-build.json',O/'compact-link.json']
    save(O/'assembly-stage.json',dict(passed=True,source_only=True,native=False,installed=False,playable=85,total_identities=90,parent_ROM=EXPECTED,ROM_sha256=sha(O/'candidate.nes'),changed_bytes=len(delta),allowed_ROM_range=[lo,hi],unchanged_public_entries=True,moved_internal_symbols=changed,funding='4B WWF route +9B X fallback -13B redundant constant tail; original234B DrawSelectionPreview footprint exact, no new stack/RAM.',input_objects={str(p):sha(p)for p in inputs},main_source_inputs={str(p):sha(p)for p in deps},bindings={str(p):sha(p)for p in refs}))
    print(json.dumps(dict(passed=True,candidate=sha(O/'candidate.nes'),changed_bytes=len(delta),allowed_ROM_range=[lo,hi],ready=85,native=False)))

if __name__=='__main__':main()
