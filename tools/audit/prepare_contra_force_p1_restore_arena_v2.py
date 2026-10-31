"""Link67B source worker to a synthetic arena view only; never a cartridge."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
O=R/'build/contra-force-p1-restore-arena-v2';P=R/'build/contra-force-p1-cart-v2';S=R/'tools/reference/contra_force_p1_native_restore_proposal_v2.s'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();d=json.loads((P/'source-stage.json').read_text())
 for p,h in d['bindings'].items():assert sha(p)==h,p
 b=qualified(P/'joint/candidate.nes');imports=['SmFreezeLastBlue','SmFreezePalettePending','FarCallCommon','SafecallA_SMC','FarcallJmpTarget_SMC'];a=''
 for n in imports:a+='.export '+n+'\n'+n+'=$%04x\n'%address(b,n)
 a+='.export FwMuxNativeSelect,BtServiceVeneers\n.segment "BOUND_FF"\nFwMuxNativeSelect:\n.segment "BOUND_SHARED"\nBtServiceVeneers:\n'
 (O/'bound-imports.s').write_text(a)
 (O/'arena.cfg').write_text('MEMORY { ARENA: start=$A000,size=$2000,file=%O,fill=yes,fillval=$FF,bank=91; FF: start=$BEB6,size=0,file="",bank=93; SHARED: start=$B020,size=0,file="",bank=87; } SEGMENTS { CF_P1_ROM_RESTORE_PROPOSAL: load=ARENA,type=ro; BOUND_FF: load=FF,type=ro; BOUND_SHARED: load=SHARED,type=ro; }')
 ca=R/'tools/Windows/cc65/bin/ca65.exe';logs=[]
 def run(cmd):
  g=validate(cmd,O,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);logs.append(dict(command=cmd,guard=g,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));assert z.returncode==0,z.stderr
 for name,source in [('worker',S),('imports',O/'bound-imports.s')]:run([str(ca),'--cpu','6502x','-g','--create-full-dep',str(O/(name+'.dep')),'-o',str(O/(name+'.o')),str(source)])
 run([str(ca.with_name('ld65.exe')),'-C',str(O/'arena.cfg'),'-o',str(O/'worker.bin'),'-Ln',str(O/'worker.lbl'),'--dbgfile',str(O/'worker.dbg'),'-m',str(O/'worker.map'),str(O/'worker.o'),str(O/'imports.o')])
 (O/'commands.json').write_text(json.dumps(logs,indent=2)+'\n');image=(O/'worker.bin').read_bytes();assert len(image)==8192 and all(x==255 for x in image[67:])
 q=dict(source=True,native=False,actual_cartridge=False,resource_adopted=False,worker_bytes=67,synthetic_only_bank=91,synthetic_PC=40960,actual_bound_native_select_PC=address(b,'Retire')+37,scope='CPU arena overlays ONLY a synthetic fetchview for67B. No NES/shared source/image/installed table is changed. Physical91 A000 is a fixture placeholder, not requested or allocated.',bindings={str(p.resolve()):sha(p)for p in[Path(__file__),S,P/'source-stage.json',P/'joint/candidate.nes',*[p for p in O.iterdir()if p.is_file()]]})
 p=O/'proof.json';p.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(path=str(p),sha256=sha(p))),flush=True)
if __name__=='__main__':main()
