"""Recover only the current S2 compilation unit and fund Doki's source branches."""
from pathlib import Path
import hashlib,json,re,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from prepare_cv3_dmc_mirror import prepare
P=R/'build/wwf-roster-native-1101-v1';O=R/'build/doki-current-component-1101-v1';S=O/'src'
EXPECTED='429b9f3c3fb551ec023d997f9e83515a2c68f1447a2d4a7cad43c029ff5ee3e2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
write=lambda p,s:p.write_text(s,encoding='utf-8',newline='\n')


def main():
    assert not(O/'source-stage.json').exists();O.mkdir(exist_ok=True);S.mkdir(exist_ok=True)
    assert sha(P/'candidate.nes')==EXPECTED
    parent=scoped_load(P/'candidate.nes');records={k:{}for k in ['sym','scope','mod','file']}
    for line in(P/'candidate.dbg').read_text().splitlines():
        k=line.split('\t',1)[0]
        if k in records:
            q=dict(re.findall(r'(\w+)=("[^"\n]*"|[^,\n]+)',line));records[k][q['id']]=q
    symbol=next(q for q in records['sym'].values()if q.get('name')=='"S2NativeStart"'and 'val'in q)
    module=records['scope'][symbol['scope']]['mod'];inputs=[];basenames=set()
    with zipfile.ZipFile(R/'build/_recovery/legacy-sources-2026-10-31.zip')as z:
        idx={q['path']:q for q in json.loads(z.read('index.json'))}
        for q in records['file'].values():
            if module not in q.get('mod','').split('+'):continue
            path=Path(q['name'].strip('"'))
            if not path.is_relative_to(R/'build'):continue
            key=path.relative_to(R/'build').as_posix()
            if path.is_file():data=path.read_bytes()
            else:
                row=idx[key];data=z.read('objects/'+row['sha256']);assert hashlib.sha256(data).hexdigest()==row['sha256']
            assert len(data)==int(q['size']) and path.name not in basenames
            basenames.add(path.name);target=S/path.name;target.write_bytes(data)
            inputs.append(dict(original=str(path),source=str(target),sha256=sha(target),bytes=len(data)))
    assert len(inputs)==24,len(inputs)
    save(O/'exact-source-inputs.json',dict(parent=EXPECTED,files=inputs,scope='Only current S2 module dependencies, recovered individually. No recursive historical tree.'))
    flags=json.loads((P/'main-build.json').read_text())['command'];defines=[]
    for i,x in enumerate(flags):
        if x=='-D':defines+=['-D',flags[i+1]]
    def run(tag,cmd):
        cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R)
        for q in guard['outputs']:Path(q['path']).parent.mkdir(parents=True,exist_ok=True)
        result=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        save(O/(tag+'.json'),dict(command=cmd,guard=guard,returncode=result.returncode,stderr=result.stderr));assert result.returncode==0,result.stderr
    def assemble():
        run('component-build',[R/'tools/Windows/cc65/bin/ca65.exe','-U','-g','-I',S,'-I',R,*defines,S/'component.s','-o',O/'component.o','-l',O/'component.lst'])
    cfg=(P/'candidate.cfg').read_text();number=0
    def destination(m):
        nonlocal number
        if m[1]in ['', '%O']:return m[0]
        number+=1;return 'file="'+(O/'sideoutputs'/(f'{number:03d}-'+Path(m[1]).name)).as_posix()+'"'
    write(O/'candidate.cfg',re.sub(r'file\s*=\s*"([^"\r\n]*)"',destination,cfg))
    link=json.loads((P/'final-link.json').read_text())['command'][:]
    old=str(R/'build/coherent62-lives-fixes-v1/joint/component.o');assert link.count(old)==1;link[link.index(old)]=str(O/'component.o')
    for flag,name in [('-C','candidate.cfg'),('-o','candidate.nes'),('-Ln','candidate.lbl'),('-m','candidate.map')]:link[link.index(flag)+1]=str(O/name)
    link[link.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate.dbg')
    def linked():
        run('link',link);p=O/'candidate.dbg';keep={'version','info','file','lib','mod','seg','scope','sym'}
        p.write_bytes(b''.join(l for l in p.read_bytes().splitlines(keepends=True)if l.split(b'\t',1)[0].decode('ascii')in keep));prepare(R,O/'candidate.nes')
        return scoped_load(O/'candidate.nes')
    assemble();linked();assert (O/'candidate.nes').read_bytes()==(P/'candidate.nes').read_bytes(),'Current source reproduction differs'
    save(O/'baseline-reproduction.json',dict(passed=True,ROM=EXPECTED,current_compilation_unit_payload_exact=True,restored_files=len(inputs)))
    native=S/'smb2_roster_native.inc';text=native.read_text();rounds=[]
    for iteration in range(12):
        b=scoped_load(O/'candidate.nes');edits=[]
        def relax(m):
            label,condition,target=m.groups()
            if label not in b['syms']or target not in b['syms']:return m[0]
            # Both endpoints must remain genuine instructions in this same
            # original native-code block; never shorten cross-bank helpers.
            pc=address(b,label);dest=address(b,target)
            if not(address(b,'S2NativeStart')<=pc<address(b,'S2NativeEnd')and address(b,'S2NativeStart')<=dest<address(b,'S2NativeEnd')):return m[0]
            if -128<=dest-(pc+2)<=127:
                edits.append(dict(label=label,target=target,old_pc=pc,old_target=dest));return label+': b'+condition+' '+target
            return m[0]
        new=re.sub(r'^(S2N[0-9A-F]+): j(cc|cs|eq|ne|pl|mi|vc|vs) (\w+)',relax,text,flags=re.M)
        if not edits:break
        text=new;write(native,text);assemble();b=linked();rounds.append(dict(round=iteration,branches=len(edits),native_bytes=address(b,'S2NativeEnd')-address(b,'S2NativeStart')))
    else:raise AssertionError('Branch relaxation bound')
    b=scoped_load(O/'candidate.nes')
    for name in ['S2NativeStart','S2NativeEnd','S2ComponentStart','S2ComponentEnd','S2HudCoreEnd']:assert name in b['syms']
    assert address(b,'S2NativeStart')==address(parent,'S2NativeStart')==0xa640
    saved=address(parent,'S2NativeEnd')-address(b,'S2NativeEnd');assert saved>50,saved
    # All changes stay in this module's original source-owned segments. Other
    # code may change only through actual imported S2 symbol relocations.
    refs={Path(__file__),P/'candidate.nes',P/'candidate.dbg',O/'candidate.nes',O/'candidate.dbg',O/'candidate.cfg',O/'baseline-reproduction.json',O/'exact-source-inputs.json',*[p for p in S.iterdir()if p.is_file()]}
    save(O/'assembly-controls.json',dict(passed=True,source=True,native=False,installed=False,parent=EXPECTED,candidate=sha(O/'candidate.nes'),baseline_payload_exact=True,rounds=rounds,source_bytes_freed=saved,core_end=address(b,'S2HudCoreEnd'),
        scope='Exact current S2 source reproduction, then genuine6502 relative-branch relaxation. Doki-specific behavior, complete differential CPU and native checks are not yet qualified; no new admission or nightly replacement.',bindings={str(p.resolve()):sha(p)for p in refs}))
    print(json.dumps(dict(passed=True,parent=EXPECTED,candidate=sha(O/'candidate.nes'),source_bytes_freed=saved,rounds=rounds,native=False,installed=False)))


if __name__=='__main__':main()
