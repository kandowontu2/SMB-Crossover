"""Sparse private single-owner CV3 stopwatch repair; no native or install."""
from pathlib import Path
import difflib,hashlib,json,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from prepare_cv3_dmc_mirror import prepare
from check_tmnt_audio_fallback_oc import qualified
R=Path(__file__).resolve().parents[2];B=R/'build';P='cv3_watch_single_owner';SHA='ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
def main():
 parent=B/'mega_proto_body_palette_9ea.nes';assert sha(parent)==SHA
 out=B/(P+'.nes');resume='--resume-linked'in sys.argv;assert resume==out.exists()
 src=R/'src/cv3_combat.s';raw=src.read_bytes();old=b'.proc Cv3FreezeTick\r\n lda AvStopwatch\r\n beq :+\r\n dec AvStopwatch\r\n: ldx #5'
 assert raw.count(old)==1,'Original raw CRLF source contract'
 new=b'.proc Cv3FreezeTick\r\n ; Shared RemainingWeapons::AdvanceFreeze is the sole stopwatch owner.\r\n ; Preserve all later PCs and the independent CV3 frozen-enemy loop.\r\n jmp FrozenActors\r\n .res 5,$ea ; unreachable former second stopwatch decrement\r\nFrozenActors: ldx #5'
 leaf=B/(P+'_combat.s');leaf.write_bytes(raw.replace(old,new))
 aggregate=B/(P+'_cv3.s');ar=(R/'src/cv3.s').read_bytes();assert ar.count(b'.include "cv3_combat.s"')==1;aggregate.write_bytes(ar.replace(b'.include "cv3_combat.s"',b'.include "'+leaf.name.encode()+b'"'))
 entry=B/(P+'_entrypoint.s');er=(R/'src/entrypoint.s').read_bytes();assert er.count(b'.include "cv3.s"')==1;entry.write_bytes(er.replace(b'.include "cv3.s"',b'.include "'+aggregate.name.encode()+b'"'))
 original=json.loads((B/'mega_proto_body_palette_9ea_build.json').read_text())['command'];command=[];i=0
 while i<len(original):
  arg=original[i]
  if arg in ['-m','-Ln','-o']:
   command.extend([arg,str(out.with_suffix({'-m':'.map','-Ln':'.lbl','-o':'.nes'}[arg]))]);i+=2;continue
  if arg=='--ld-args':command.extend([arg,'--dbgfile,'+str(out.with_suffix('.dbg'))]);i+=2;continue
  command.append(str(entry)if i==len(original)-1 else arg);i+=1
 if resume:
  assert sha(out)=='d5fcaa70247652577db78a08d7c5f153feb77924a8c2ee2dd4e8d879e9426987'
  put(B/(P+'_setup-negative.json'),dict(passed=False,stage='Initial linked image before mandatory postlink clone producer',linked_sha256=sha(out),unexpected_changes={'bank125':7686,'intended_bank84':8},cause='Builder omitted the existing deterministic fixed-E clone postlink producer; no game instructions tested and no native launched. Preserved here before completing the same unbound working candidate.'))
 else:
  run=subprocess.run(command,cwd=R,capture_output=True,text=True);out.with_suffix('.build.log').write_text(run.stdout+run.stderr);assert run.returncode==0,run.stdout+run.stderr
 producer=prepare(R,out)
 before,after=parent.read_bytes(),out.read_bytes();delta=[i for i,(a,b)in enumerate(zip(before,after))if a!=b]
 assert len(before)==len(after)and {(i-16)//8192 for i in delta}=={84}and len(delta)<=8
 qo,qn=qualified(parent),qualified(out);moved={str(k):[v,qn.get(k)]for k,v in qo.items()if qn.get(k)!=v and not any('LOCAL-MACRO_SYMBOL-'in s for s in k)};assert not moved,moved
 patch=B/(P+'_implementation.patch');patch.write_text(''.join(difflib.unified_diff(raw.decode().splitlines(True),leaf.read_bytes().decode().splitlines(True),fromfile='src/cv3_combat.s',tofile='src/cv3_combat.s')),newline='')
 assert src.read_bytes()==raw
 receipt=B/(P+'_build.json');put(receipt,dict(passed=True,source_only=True,native_run=False,parent_sha256=SHA,candidate_sha256=sha(out),changed_bytes=len(delta),changed_bank=84,changed_offsets=delta,all_existing_qualified_public_labels_exact=True,new_genuine_loop_label='Cv3FreezeTick::FrozenActors',source_overlay={str(src):str(leaf)},command=command,ordinary_builds='Pending source-controls closure; include is expanded-only and ordinary binaries must be freshly verified before handoff.',bindings={str(p):sha(p)for p in [Path(__file__),src,R/'src/cv3.s',R/'src/entrypoint.s',leaf,aggregate,entry,patch,parent,parent.with_suffix('.dbg'),out,out.with_suffix('.dbg'),out.with_suffix('.lbl'),out.with_suffix('.map'),out.with_suffix('.cv3-mirror.json'),R/'tools/prepare_cv3_dmc_mirror.py']}))
 print(json.dumps(dict(passed=True,candidate_sha256=sha(out),changed_bytes=len(delta),receipt=str(receipt),sha256=sha(receipt))))
if __name__=='__main__':main()
