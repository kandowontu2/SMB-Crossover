"""Relink late lifts against the latest Thomas graphics/palette source."""
import hashlib, json, re, subprocess
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

P=R/'build/thomas-platform-chr'
O=R/'build/thomas-current-lifts-1102-v2'
W=R/'build/thomas-natural-host-1031-v6'

def main():
    O.mkdir(exist_ok=True)
    assert not (O/'source-stage.json').exists()
    old=(P/'candidate.nes').read_bytes()
    current=(R/'build/bub-menu-candidate-1102-v2/combined-event.nes').read_bytes()
    start=1048592+426*1024
    assert current[start:start+14336]==old[start:start+14336]
    # The historical zero tail now belongs to other components. This source
    # stage is not a whole-carrier replacement for the current ROM.
    compiler=R/'tools/Windows/cc65/bin'
    def run(tag,cmd):
        cmd=list(map(str,cmd)); guard=validate(cmd,O,cwd=R)
        for item in guard['outputs']: Path(item['path']).parent.mkdir(parents=True,exist_ok=True)
        q=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        (O/(tag+'.json')).write_text(json.dumps(dict(command=cmd,returncode=q.returncode,stderr=q.stderr),indent=2))
        assert q.returncode==0,q.stderr
    def asm(name):
        run(name+'-build',[compiler/'ca65.exe',O/(name+'.s'),'-I',O,'-I',P,'-I',W/'source','-g','-o',O/(name+'.o')])
    (O/'lift.s').write_text((R/'build/thomas-late-lifts-1102-v1/lift.s').read_text())
    asm('lift')
    outputs=[]
    def redirect(m):
        if m[1] in ['', '%O']: return m[0]
        dest=O/'sideoutputs'/(str(len(outputs))+'-'+Path(m[1]).name)
        outputs.append(dest)
        return 'file="'+dest.as_posix()+'"'
    (O/'candidate.cfg').write_text(re.sub(r'file\s*=\s*"([^"\r\n]*)"',redirect,(P/'candidate.cfg').read_text()))
    link=json.loads((P/'final-link.json').read_text())['command'][:]
    old_lift=next(p for p in link if Path(p).name=='lift.o')
    link[link.index(old_lift)]=str(O/'lift.o')
    for flag,name in [('-C','candidate.cfg'),('-o','candidate.nes'),('-Ln','candidate.lbl')]: link[link.index(flag)+1]=str(O/name)
    link[link.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate.dbg')
    def linked(tag):
        run(tag,link)
        path=O/'candidate.dbg'
        keep={b'version',b'info',b'file',b'lib',b'mod',b'seg',b'scope',b'sym'}
        path.write_bytes(b''.join(s for s in path.read_bytes().splitlines(keepends=True) if s.split(b'\t',1)[0] in keep))
    linked('provisional-link')
    kernel=next(p for p in outputs if p.name.endswith('kernel.bin')).read_bytes()
    state=next(p for p in outputs if p.name.endswith('state.bin')).read_bytes()
    assert address(scoped_load(O/'candidate.nes'),'ThAllKernelEnd')-0xa000==6144
    carrier=bytearray((P/'carrier.chr').read_bytes());carrier[:6144]=kernel[:6144]
    (O/'carrier.chr').write_bytes(carrier)
    (O/'cookie.bin').write_bytes(bytes([167,10,64,1])+hashlib.sha256(kernel+state).digest()[:12])
    (O/'native-background-colors.bin').write_bytes((P/'native-background-colors.bin').read_bytes())
    for name in ['resident','carrier']:
        (O/(name+'.s')).write_text((P/(name+'.s')).read_text())
        asm(name)
        link[link.index(str(P/(name+'.o')))]=str(O/(name+'.o'))
    linked('final-link')
    new=(O/'candidate.nes').read_bytes();bundle=scoped_load(O/'candidate.nes')
    cookie=location(bundle,'ThCookie')
    changes=[i for i,(a,b) in enumerate(zip(old,new)) if a!=b]
    assert all(start<=i<start+6144 or cookie+4<=i<cookie+16 for i in changes)
    assert new[start+6144:start+16384]==old[start+6144:start+16384]
    q=dict(passed=True,source=True,native=False,installed=False,candidate=sha(O/'candidate.nes'),parent=sha(P/'candidate.nes'),kernel_bytes=6144,changed_bytes=len(changes),cookie_offset=cookie,
           scope='Latest graphics/metadata/palette retained. Only six-page kernel and its cookie change. Current composition, full caller ABI/interrupts and crossings remain unqualified.',
           bindings={str(p):sha(p) for p in [Path(__file__),O/'lift.s',P/'final-link.json',P/'candidate.nes',O/'candidate.nes',O/'candidate.dbg']})
    (O/'source-stage.json').write_text(json.dumps(q,indent=2)+'\n'); print(json.dumps({k:v for k,v in q.items() if k!='bindings'}))

if __name__=='__main__': main()
