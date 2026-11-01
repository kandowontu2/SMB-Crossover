"""Add only the four prelisted native platforms to the private Thomas source."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
P=R/'build/thomas-adapter';O=R/'build/thomas-pipe-lifts';W=R/'build/thomas-natural-host-1031-v6'
PLAN=R/'docs/qa/checkpoints/2026-10-31/thomas-camera-source-v1/pipe-assists-before-changes.json'
SOURCE=R/'tools/reference/thomas_pipe_lifts_v1.s'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


def main():
    assert not(O/'source-stage.json').exists();O.mkdir(exist_ok=True)
    assert sha(P/'candidate.nes')=='b1725ec3e25cbfd321e435249a996b2d0bec901c35e1f57664a0e75cf42d8972'
    plan=json.loads(PLAN.read_text());assert not plan['changes_applied']
    assert [x['platform_X']for x in plan['additions']]==[400,560,688,864]
    cache=(P/'cache.s').read_text()
    def once(s,a,z):assert s.count(a)==1;return s.replace(a,z,1)
    cache='.import ThLiftTick,ThLiftReset\n'+cache
    cache=once(cache,'ThNaturalPublishContext:\n','ThNaturalPublishContext:\n jsr ThLiftReset\n')
    cache=once(cache,' sta PlayerSize\nThNaturalMoveDone:',' sta PlayerSize\n jsr ThLiftTick\nThNaturalMoveDone:')
    (O/'cache.s').write_text(cache,encoding='utf-8')
    (O/'lift.s').write_text(SOURCE.read_text(),encoding='utf-8')
    cc=R/'tools/Windows/cc65/bin'
    def run(name,cmd):
        cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R)
        for q in guard['outputs']:Path(q['path']).parent.mkdir(parents=True,exist_ok=True)
        q=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        save(O/(name+'.json'),dict(command=cmd,guard=guard,returncode=q.returncode,stderr=q.stderr))
        assert q.returncode==0,q.stderr
    def asm(n):run(n+'-build',[cc/'ca65.exe',O/(n+'.s'),'-I',O,'-I',W/'source','-g','-o',O/(n+'.o'),'--create-full-dep',O/(n+'.dep')])
    asm('cache');asm('lift')
    outputs={};count=0
    def redirect(m):
        nonlocal count
        if m[1]in['','%O']:return m[0]
        count+=1;p=O/'sideoutputs'/(f'{count:03d}-'+Path(m[1]).name);outputs[Path(m[1]).name]=p
        return 'file="'+p.as_posix()+'"'
    (O/'candidate.cfg').write_text(re.sub(r'file\s*=\s*"([^"\r\n]*)"',redirect,(P/'candidate.cfg').read_text()))
    link=json.loads((P/'final-link.json').read_text())['command'][:]
    link[link.index(str(P/'cache.o'))]=str(O/'cache.o')
    link.insert(link.index(str(P/'boundary.o')),str(O/'lift.o'))
    for flag,n in [('-C','candidate.cfg'),('-Ln','candidate.lbl'),('-o','candidate.nes')]:link[link.index(flag)+1]=str(O/n)
    link[link.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate.dbg')
    run('provisional-link',link)
    b=scoped_load(O/'candidate.nes');used=address(b,'ThAllKernelEnd')-0xa000
    assert used<=6144,('Six-page kernel capacity',used)
    kernel_path=next(p for n,p in outputs.items()if n.endswith('kernel.bin'))
    state_path=next(p for n,p in outputs.items()if n.endswith('state.bin'))
    kernel=kernel_path.read_bytes();state=state_path.read_bytes()
    assert state[0x838:0x83a]==bytes(2),'New state is in the original zero boundary gap'
    (O/'cookie.bin').write_bytes(bytes([167,10,64,1])+hashlib.sha256(kernel+state).digest()[:12])
    body=(P/'carrier.chr').read_bytes()[8192:]
    (O/'carrier.chr').write_bytes(kernel[:6144]+state[0x1000:0x1800]+body)
    for n in ['resident','carrier']:
        (O/(n+'.s')).write_text((P/(n+'.s')).read_text())
        asm(n);link[link.index(str(P/(n+'.o')))]=str(O/(n+'.o'))
    run('final-link',link)
    assert kernel_path.read_bytes()==kernel and state_path.read_bytes()==state
    a,z=(P/'candidate.nes').read_bytes(),(O/'candidate.nes').read_bytes()
    changed=[i for i,(x,y)in enumerate(zip(a,z))if x!=y and i<1048592]
    assert all(16+85*8192+0x133a<=i<16+85*8192+0x1900 for i in changed)
    assert a[1048592:1048592+426*1024]==z[1048592:1048592+426*1024]
    assert a[1048592+434*1024:]==z[1048592+434*1024:]
    refs={Path(__file__),SOURCE,PLAN,P/'source-stage.json',P/'final-link.json',P/'cache.s',P/'carrier.chr'}
    refs|={Path(p)for p in link if p.endswith('.o')}
    refs|={p for p in O.rglob('*')if p.is_file()}
    q=dict(passed=True,source=True,native=False,installed=False,candidate=sha(O/'candidate.nes'),parent=sha(P/'candidate.nes'),
           kernel_bytes=used,grant_bytes=6144,new_selected_state=['C838 lift seen bits','C839 saved native ObjectOffset'],
           adaptation='Four prelisted Thomas-only1-1 actors, type25 via genuine native InitEnemyObject and existing vertical AI/support/carry/rendering. Existing actors take priority. Source jump/physics and level tiles unchanged.',
           limits=['Source link only; source route/support/vector and native validation pending','Private parent; not the installed74-character f476 build'],
           bindings={str(p.resolve()):sha(p)for p in refs})
    save(O/'source-stage.json',q);print(json.dumps({k:q[k]for k in ['passed','candidate','kernel_bytes']}))


if __name__=='__main__':main()
