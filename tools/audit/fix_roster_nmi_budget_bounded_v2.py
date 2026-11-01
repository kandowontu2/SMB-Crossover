"""Preserve the accepted seven-byte length at the queue validator's advance."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from prepare_cv3_dmc_mirror import prepare
from prepare_contra_force_p1_coherent_cart_v2 import native_abi
P=R/'build/ready76-menu-fixed';O=R/'build/ready76-menu-fixed-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')


def main():
    assert not(O/'source-stage.json').exists();O.mkdir(exist_ok=True)
    assert sha(P/'candidate.nes')=='2b84f1656d0cd111018d84b9ec642b789a3ff93a578f0b4cfc7e8400fde5f3ba'
    parent=json.loads((P/'source-stage.json').read_text())
    for p,h in parent['bindings'].items():assert sha(p)==h,p
    source=P/'menu_vram_budget.s';text=source.read_text()
    old=''' cmp #1                       ; only11/7 or19/7, both within sprite colors
 jne Invalid
 beq Advance'''
    new=''' cmp #1                       ; only11/7 or19/7, both within sprite colors
 jne Invalid
 lda #7                       ; Advance consumes A as the command length
 bne Advance'''
    assert text.count(old)==1;text=text.replace(old,new,1)
    (O/'menu_vram_budget.s').write_text(text,encoding='utf-8',newline='\n')
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
    link=json.loads((P/'final-link.json').read_text())['command'][:];link[link.index(str(P/'main.o'))]=str(O/'main.o')
    for flag,name in [('-C','candidate.cfg'),('-o','candidate.nes'),('-Ln','candidate.lbl'),('-m','candidate.map')]:
        if flag in link:link[link.index(flag)+1]=str(O/name)
    link[link.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate.dbg');run('final-link',link)
    path=O/'candidate.dbg';data=path.read_bytes();keep={'version','info','file','lib','mod','seg','scope','sym'}
    path.write_bytes(b''.join(s for s in data.splitlines(keepends=True)if s.split(b'\t',1)[0].decode('ascii')in keep))
    save(O/'debug-format.json',dict(full_bytes=len(data),full_sha256=hashlib.sha256(data).hexdigest(),compact_bytes=path.stat().st_size,compact_sha256=sha(path)))
    prepare(R,O/'candidate.nes')
    before,after=[scoped_load(p/'candidate.nes')for p in[P,O]]
    changes=[i for i,(a,z)in enumerate(zip(before['raw'],after['raw']))if a!=z]
    assert changes and all(16+0x42*8192<=i<16+0x43*8192 for i in changes)
    assert native_abi(before)==native_abi(after)
    for name in ['kernel.bin','state.bin','final-a1.bin','final-c2.bin','final-a3.bin']:
        old=next(p for p in(P/'sideoutputs').iterdir()if p.name.endswith(name));current=next(p for n,p in outputs.items()if n.endswith(name))
        assert old.read_bytes()==current.read_bytes(),name
    refs={Path(__file__),source,P/'source-stage.json',P/'main-build.json',P/'final-link.json'}
    dep=(O/'main.dep').read_text().split(':\t',1)[1].split('\n',1)[0]
    refs|={Path(x.replace('\\ ',' '))for x in re.split(r'(?<!\\)\s+',dep)if x}
    refs|={Path(p)for p in link if p.endswith('.o')};refs|={p for p in O.rglob('*')if p.is_file()}
    save(O/'source-stage.json',dict(passed=True,source=True,native=False,installed=False,candidate=sha(O/'candidate.nes'),parent=sha(P/'candidate.nes'),gameplay_parent='d1c4973cf69702ba02d83706aadda72a2a63a6f0cec6018ec5fa63735ff75393',private_playable=76,
        changed_native_bytes=len(changes),only_PRG_bank=66,all_CHR_and_selected_images_exact=True,
        defect='The first draft returned the masked palette offset as the packet length. Restore accepted length7 before the existing advance. Preserve the source-negative result and verify actual packet semantics before native execution.',
        bindings={str(p.resolve()):sha(p)for p in refs}))
    print(json.dumps(dict(candidate=sha(O/'candidate.nes'),changed_bytes=len(changes),only_PRG_bank=66)))


if __name__=='__main__':main()
