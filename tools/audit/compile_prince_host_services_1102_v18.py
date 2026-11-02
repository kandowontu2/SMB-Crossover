"""Native ingress successor: explicit player slot; constructor resets events."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import compile_prince_host_lifecycle_1102_v12 as L
from private_build_outputs_v1 import validate
O=L.O


def main():
 src=O/'host-services-v17.s';text=src.read_text()
 changes={'PpNativeInit:\n jsr PpHostInit\n':'PpNativeInit:\n lda #0\n sta PpReady\n jsr PpHostInit\n',' sta PpDead\n lda #$a7':' sta PpDead\n sta $c0ad\n sta $c0ae\n sta $c0af\n lda #$a7',' jsr PpHostUpdate\n':' ldx #0                 ; original F158 consumes X=actor slot\n jsr PpHostUpdate\n'}
 for a,b in changes.items():assert text.count(a)==1,a;text=text.replace(a,b)
 asm=O/'host-services-v18.s';asm.write_text(text);cfg=O/'host-services-v18.cfg';cfg.write_text('MEMORY{M:start=$db9a,size=$198,file=%O;}SEGMENTS{SERVICES:load=M,type=ro,define=yes;}')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe','-g',asm,'-o',O/'host-services-v18.o'],[cc/'ld65.exe','-C',cfg,O/'host-services-v18.o','-o',O/'host-services-v18.bin','-Ln',O/'host-services-v18.lbl']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 lab=L.P.T.labels(O/'host-services-v18.lbl');end=lab['PpNativeServicesEnd']
 q=dict(measured=True,base_ROM_SHA256=L.PIN,code_half_open=[0xdb9a,end],bytes=end-0xdb9a,remaining_tail_bytes=0xdd32-end,constructor_clears_local_ready_epoch_death_events=True,explicit_original_actor_slot_X_zero=True,source_code_bytes_unchanged=True,host_ROM_created=False,bindings={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),src,O/'host-services-v17.bin',O/'host-services-v18.bin',R/'docs/qa/allocations/prince-executable-state-1102-v15.json']})
 (O/'host-services-layout-v18.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
