"""Small source linker for the existing selected Thomas kernel/carrier grant."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
W=R/'build/thomas-natural-host-1031-v6'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


def build(parent,out,cache,lift,*,extra_refs,adaptation,boundary=None):
    assert not(out/'source-stage.json').exists();out.mkdir(exist_ok=True)
    cc=R/'tools/Windows/cc65/bin'
    def run(name,cmd):
        cmd=list(map(str,cmd));guard=validate(cmd,out,cwd=R)
        for q in guard['outputs']:Path(q['path']).parent.mkdir(parents=True,exist_ok=True)
        q=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        save(out/(name+'.json'),dict(command=cmd,guard=guard,returncode=q.returncode,stderr=q.stderr))
        assert q.returncode==0,q.stderr
    def asm(n):run(n+'-build',[cc/'ca65.exe',out/(n+'.s'),'-I',out,'-I',W/'source','-g','-o',out/(n+'.o'),'--create-full-dep',out/(n+'.dep')])
    for n,text in [('cache',cache),('lift',lift)]:
        (out/(n+'.s')).write_text(text,encoding='utf-8');asm(n)
    if boundary is not None:
        (out/'boundary.s').write_text(boundary,encoding='utf-8');asm('boundary')
    outputs={};count=0
    def redirect(m):
        nonlocal count
        if m[1]in['','%O']:return m[0]
        count+=1;p=out/'sideoutputs'/(f'{count:03d}-'+Path(m[1]).name);outputs[Path(m[1]).name]=p
        return 'file="'+p.as_posix()+'"'
    (out/'candidate.cfg').write_text(re.sub(r'file\s*=\s*"([^"\r\n]*)"',redirect,(parent/'candidate.cfg').read_text()))
    link=json.loads((parent/'final-link.json').read_text())['command'][:]
    for n in ['cache','lift']:link[link.index(str(parent/(n+'.o')))]=str(out/(n+'.o'))
    if boundary is not None:
        old=next(p for p in link if Path(p).name=='boundary.o')
        link[link.index(old)]=str(out/'boundary.o')
    for flag,n in [('-C','candidate.cfg'),('-Ln','candidate.lbl'),('-o','candidate.nes')]:link[link.index(flag)+1]=str(out/n)
    link[link.index('--ld-args')+1]='--dbgfile,'+str(out/'candidate.dbg')
    run('provisional-link',link)
    b=scoped_load(out/'candidate.nes');used=address(b,'ThAllKernelEnd')-0xa000
    assert used<=6144,('Six-page kernel capacity',used)
    kp=next(p for n,p in outputs.items()if n.endswith('kernel.bin'));sp=next(p for n,p in outputs.items()if n.endswith('state.bin'))
    kernel,state=kp.read_bytes(),sp.read_bytes()
    assert state[0x850:0x85e]==bytes(14),'Detached frame occupies only the old zero boundary gap'
    assert state[0x860:0x86c]==bytes(12),'Melee save occupies only the old zero boundary gap'
    (out/'cookie.bin').write_bytes(bytes([167,10,64,1])+hashlib.sha256(kernel+state).digest()[:12])
    (out/'carrier.chr').write_bytes(kernel[:6144]+state[0x1000:0x1800]+(parent/'carrier.chr').read_bytes()[8192:])
    for n in ['resident','carrier']:
        (out/(n+'.s')).write_text((parent/(n+'.s')).read_text());asm(n)
        link[link.index(str(parent/(n+'.o')))]=str(out/(n+'.o'))
    run('final-link',link);assert kp.read_bytes()==kernel and sp.read_bytes()==state
    a,z=(parent/'candidate.nes').read_bytes(),(out/'candidate.nes').read_bytes()
    changed=[i for i,(x,y)in enumerate(zip(a,z))if x!=y and i<1048592]
    assert all(16+85*8192+0x133a<=i<16+85*8192+0x1900 for i in changed)
    assert a[1048592:1048592+426*1024]==z[1048592:1048592+426*1024]
    assert a[1048592+434*1024:]==z[1048592+434*1024:]
    refs={Path(__file__),parent/'source-stage.json',parent/'final-link.json',parent/'cache.s',parent/'lift.s',parent/'carrier.chr',*extra_refs}
    refs|={Path(p)for p in link if p.endswith('.o')};refs|={p for p in out.rglob('*')if p.is_file()}
    q=dict(passed=True,source=True,native=False,installed=False,candidate=sha(out/'candidate.nes'),parent=sha(parent/'candidate.nes'),
           kernel_bytes=used,grant_bytes=6144,adaptation=adaptation,limits=['Source link only; real Main, carry and vector checks pending','Not composed into installed74-character f476'],
           bindings={str(p.resolve()):sha(p)for p in refs})
    save(out/'source-stage.json',q);print(json.dumps({k:q[k]for k in ['passed','candidate','kernel_bytes']}))
