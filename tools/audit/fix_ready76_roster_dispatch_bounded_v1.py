"""Restore Hogan's rare-owner classification in the combined Thomas dispatcher."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from prepare_cv3_dmc_mirror import prepare
from prepare_contra_force_p1_coherent_cart_v2 import native_abi
P=R/'build/hogan-thomas-current';O=R/'build/ready76-visible'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')


def main():
    assert not(O/'source-stage.json').exists();O.mkdir(exist_ok=True)
    assert sha(P/'candidate.nes')=='0322bb935149a493665d025b0ed8b5e46e5d5e439312df5dd18d5a9a7dfe80df'
    source=P/'src/new_roster_dispatch.s';text=source.read_text()
    old=''' cmp #28
 beq GmOnlyHigh
 cmp #22
 beq GmOnlyHigh
 cmp #31
 bcs GmOnlyHigh
 ; Exactly24or28 after clearing their sole differing bit. Every other
 ; highID stays on its genuine old direct legacy table, avoiding recursion.
 and #$fc
 cmp #24
 beq GmOnlyHigh'''
    new=''' cmp #22
 beq GmOnlyHigh
 cmp #31
 bcs GmOnlyHigh
 cmp #24
 bcc GmOnlyLegacy
 cmp #30
 bcc GmOnlyHigh
 .res 2,$ea'''
    assert text.count(old)==1;text=text.replace(old,new,1)
    (O/'new_roster_dispatch.s').write_text(text,encoding='utf-8',newline='\n')
    def run(name,cmd):
        cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R)
        for item in guard['outputs']:Path(item['path']).parent.mkdir(parents=True,exist_ok=True)
        result=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        save(O/(name+'.json'),dict(command=cmd,guard=guard,returncode=result.returncode,stderr=result.stderr));assert result.returncode==0,result.stderr
    cmd=json.loads((P/'main-build.json').read_text())['command'][:];cmd[1:1]=['-I',str(O)]
    for flag,name in [('-o','main.o'),('-l','main.lst'),('--create-full-dep','main.dep')]:
        if flag in cmd:cmd[cmd.index(flag)+1]=str(O/name)
    run('main-build',cmd)
    outputs={};count=0
    def redirect(m):
        nonlocal count
        if m[1]in['','%O']:return m[0]
        count+=1;p=O/'sideoutputs'/(f'{count:03d}-'+Path(m[1]).name);outputs[Path(m[1]).name]=p
        return 'file="'+p.as_posix()+'"'
    (O/'candidate.cfg').write_text(re.sub(r'file\s*=\s*"([^"\r\n]*)"',redirect,(P/'candidate.cfg').read_text()))
    link=json.loads((P/'final-link.json').read_text())['command'][:]
    link[link.index(str(P/'main.o'))]=str(O/'main.o')
    for flag,name in [('-C','candidate.cfg'),('-o','candidate.nes'),('-Ln','candidate.lbl'),('-m','candidate.map')]:
        if flag in link:link[link.index(flag)+1]=str(O/name)
    link[link.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate.dbg')
    run('final-link',link)
    path=O/'candidate.dbg';data=path.read_bytes();keep={'version','info','file','lib','mod','seg','scope','sym'}
    path.write_bytes(b''.join(s for s in data.splitlines(keepends=True)if s.split(b'\t',1)[0].decode('ascii')in keep))
    save(O/'debug-format.json',dict(full_bytes=len(data),full_sha256=hashlib.sha256(data).hexdigest(),compact_bytes=path.stat().st_size,compact_sha256=sha(path)))
    prepare(R,O/'candidate.nes')
    before,after=[scoped_load(p/'candidate.nes')for p in [P,O]]
    at=location(before,'GmOnlyCompareStart')+12
    changes=[i for i,(a,z)in enumerate(zip(before['raw'],after['raw']))if a!=z]
    assert changes and all(at<=i<at+18 for i in changes),[hex(i)for i in changes]
    assert native_abi(before)==native_abi(after)
    # No selected code/data relocation changed, so both existing cache images
    # and their cookies remain valid byte for byte; assert the real link files.
    for name in ['kernel.bin','state.bin','final-a1.bin','final-c2.bin','final-a3.bin']:
        old=next(p for p in(P/'sideoutputs').iterdir()if p.name.endswith(name))
        current=next(p for n,p in outputs.items()if n.endswith(name))
        assert old.read_bytes()==current.read_bytes(),name
    for name in ['GmOnlyCommon','HuResolve','ThSceneInit','WfScene','GameLoop']:
        assert address(before,name)==address(after,name),name
    refs={Path(__file__),source,P/'source-stage.json',P/'main-build.json',P/'final-link.json'}
    dep=(O/'main.dep').read_text().split(':\t',1)[1].split('\n',1)[0]
    refs|={Path(x.replace('\\ ',' '))for x in re.split(r'(?<!\\)\s+',dep)if x}
    refs|={Path(p)for p in link if p.endswith('.o')};refs|={p for p in O.rglob('*')if p.is_file()}
    save(O/'source-stage.json',dict(passed=True,source=True,native=False,installed=False,candidate=sha(O/'candidate.nes'),parent=sha(P/'candidate.nes'),private_playable=76,
        changed_native_bytes=len(changes),changed_native_span=[at,at+18],all_CHR_and_both_selected_images_exact=True,
        defect='The older Thomas classifier routed29 to the legacy portrait/prepare rows, leaving the admitted Hogan preview blank. Restore the current24..29 rare-owner range while retaining the authenticated Thomas special branch.',
        bindings={str(p.resolve()):sha(p)for p in refs}))
    print(json.dumps(dict(candidate=sha(O/'candidate.nes'),native_changed_bytes=len(changes),cache_images_exact=True)))


if __name__=='__main__':main()
