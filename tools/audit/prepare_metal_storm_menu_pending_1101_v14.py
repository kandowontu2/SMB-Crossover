"""Fund a Metal-specific playable check without changing cold portrait dispatch."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
O=R/'build/metal-storm-menu-1101-v14';P=R/'build/metal-storm-lifecycle-1101-v13'
REF=R/'tools/reference/metal_storm_menu_pending_1101_v14.inc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    s=json.loads((P/'scene-assembly.json').read_text());assert sha(P/'candidate.nes')==s['ROM_sha256']
    O.mkdir(exist_ok=True);b=qualified(P/'candidate.nes');raw=bytearray(b['raw'])
    at=location(b,'FmStartFlags');pc=address(b,'FmStartFlags');old=bytes(raw[at:at+28])
    assert old[:3]==bytes.fromhex('8d6a01') and old[18:]==b'\xea'*10
    src=f'.segment "CODE"\n.org ${pc+15:04x}\nFmPending=${address(b,"FmPending"):04x}\n'+REF.read_text()
    (O/'helper.s').write_text(src)
    (O/'helper.cfg').write_text(f'MEMORY {{ H:start=${pc+15:04x},size=13,file=%O; }} SEGMENTS {{ CODE:load=H,type=ro; }}\n')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'helper.s','-o',O/'helper.o'],[cc/'ld65.exe','-C',O/'helper.cfg',O/'helper.o','-o',O/'helper.bin']]:
        cmd=list(map(str,cmd));validate(cmd,O,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);assert p.returncode==0,p.stderr
    helper=(O/'helper.bin').read_bytes();assert len(helper)==13
    raw[at:at+28]=old[3:18]+helper
    (O/'candidate.nes').write_bytes(raw)
    for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((P/('candidate'+suffix)).read_bytes())
    q=dict(passed=True,installed=False,helper_wired=False,menu_admitted=False,base_ROM_sha256=sha(P/'candidate.nes'),ROM_sha256=sha(O/'candidate.nes'),
           helper_PC=pc+15,helper_bank=(at-16)//8192,patch=dict(offset=at,old=old.hex(),new=bytes(raw[at:at+28]).hex()),
           scope='Only Start incoming-A save removed; helper occupies former padding. Pending/portrait callers remain unchanged until lifecycle resolution is complete.',
           bindings={str(p):sha(p) for p in [Path(__file__),REF,P/'candidate.nes',O/'helper.s',O/'candidate.nes']})
    (O/'menu-assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items() if k not in ['patch','bindings']}))
if __name__=='__main__':main()
