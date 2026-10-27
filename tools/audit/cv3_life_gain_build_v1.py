"""Sparse private CV3 life-gain + stopwatch composition; never install or launch."""
from pathlib import Path
import difflib,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];B=R/'build';sys.path.insert(0,str(R/'tools'))
from prepare_cv3_dmc_mirror import prepare
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_audio_fallback_oc import qualified
P='cv3_life_gain_watch';AB='ab221e81821dd10690ad3a1068d91c9efae6c7406230d9bd7fc4a729fdc433d2';WATCH='9a1b68c0a26ea86ff8c4712af66b8de8cd5ed2de13c74db1bfaf15eb9e2ba333'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8',newline='\n')
HELPER='''; CV3 lives are a byte: native INC grants a life; native DEC loses one.
; Enter only on a changed count, with A=current. Active native gains between
; Ensure calls are bounded to fewer than128 INCs (six popup slots + coins).
; Signed modulo difference supports simultaneous gains and FF->00 rollover;
; native DEC losses, including00->FF, stay negative. Preserve original V/D/I.
; Keep the unchanged-life movement path and every old PC byte-for-byte.
.pushseg
.segment "CV3_GRIP"
.proc Cv3LifeChanged
 php
 sec
 sbc Cv3LastLife
 bmi Loss
 plp
 lda NumberofLives
 sta Cv3LastLife
 jmp Cv3Ensure::CheckArea
Loss:
 plp
 jmp Cv3Ensure::Life
.endproc
.popseg
'''
def main():
 parent=B/'mega_proto_body_palette_9ea.nes';watch=B/'cv3_watch_single_owner.nes';assert sha(parent)==AB and sha(watch)==WATCH
 out=B/(P+'.nes');assert not out.exists(),'Do not overwrite a bound candidate'
 raw=(R/'src/cv3_core.s').read_bytes();old=b'  cmp Cv3LastLife\r\n  jne Life\r\n  lda AreaPointer';new=b'  cmp Cv3LastLife\r\n  jne Cv3LifeChanged\r\nCheckArea:\r\n  lda AreaPointer';assert raw.count(old)==1
 core=B/(P+'_core.s');core.write_bytes(raw.replace(old,new));helper=B/(P+'_helper.s');helper.write_text(HELPER,encoding='utf-8',newline='\n')
 agraw=(R/'src/cv3.s').read_bytes();ag=B/(P+'_cv3.s');ag.write_bytes(agraw.replace(b'.include "cv3_core.s"',b'.include "'+core.name.encode()+b'"').replace(b'.include "cv3_combat.s"',b'.include "cv3_watch_single_owner_combat.s"'))
 eraw=(R/'src/entrypoint.s').read_bytes();assert eraw.count(b'.include "cv3.s"')==1
 tail=b'\r\n.if ::ENABLE_MMC5_EXPANDED\r\n.include "'+helper.name.encode()+b'"\r\n.endif\r\n'
 entry=B/(P+'_entrypoint.s');entry.write_bytes(eraw.replace(b'.include "cv3.s"',b'.include "'+ag.name.encode()+b'"')+tail)
 original=json.loads((B/'cv3_watch_single_owner_build.json').read_text())['command'];command=[];i=0
 while i<len(original):
  arg=original[i]
  if arg in ['-m','-Ln','-o']:
   command.extend([arg,str(out.with_suffix({'-m':'.map','-Ln':'.lbl','-o':'.nes'}[arg]))]);i+=2;continue
  if arg=='--ld-args':command.extend([arg,'--dbgfile,'+str(out.with_suffix('.dbg'))]);i+=2;continue
  command.append(str(entry)if i==len(original)-1 else arg);i+=1
 run=subprocess.run(command,cwd=R,capture_output=True,text=True);out.with_suffix('.build.log').write_text(run.stdout+run.stderr,encoding='utf-8');assert run.returncode==0,run.stdout+run.stderr
 prepare(R,out)
 a,c=parent.read_bytes(),out.read_bytes();assert len(a)==len(c);delta=[i for i,(x,y)in enumerate(zip(a,c))if x!=y];banks={k:sum((i-16)//8192==k for i in delta)for k in sorted({(i-16)//8192 for i in delta})};assert set(banks)=={82,84}and banks[84]==8,banks
 w=watch.read_bytes();assert all(x==y for i,(x,y)in enumerate(zip(w,c))if(i-16)//8192!=82)
 qo,qn=qualified(parent),qualified(out);moved={str(k):[v,qn.get(k)]for k,v in qo.items()if qn.get(k)!=v};assert not moved,moved
 # New code occupies only a genuinely unallocated FF tail in bank82.
 start=16+82*8192+0x1c4f;assert all(x==255 for x in a[start:start+64]);assert all(i in range(start,start+64)or i in range(16+82*8192+0x53,16+82*8192+0x56)for i in delta if(i-16)//8192==82)
 production_entry=eraw+b'\r\n.if ::ENABLE_MMC5_EXPANDED\r\n.include "cv3_life_gain.s"\r\n.endif\r\n'
 patches=[]
 for name,before,after in [('src/cv3_core.s',raw,core.read_bytes()),('src/cv3_combat.s',(R/'src/cv3_combat.s').read_bytes(),(B/'cv3_watch_single_owner_combat.s').read_bytes()),('src/entrypoint.s',eraw,production_entry),('src/cv3_life_gain.s',b'',helper.read_bytes())]:
  patches.append(''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile=name,tofile=name)))
 patch=B/(P+'_implementation.patch');patch.write_text(''.join(patches),encoding='utf-8',newline='')
 receipt=B/(P+'_build.json');put(receipt,dict(passed=True,source_only=True,native_run=False,parent_sha256=AB,watch_parent_sha256=WATCH,candidate_sha256=sha(out),changed_bytes=len(delta),changed_banks=banks,changed_offsets=delta,all_existing_qualified_symbols_exact=True,existing_symbol_count=len(qo),helper_tail='bank82/$52 BC4F onward (verified final extent in controls)',new_RAM=0,source_overlay={'src/cv3_core.s':str(core),'src/cv3_combat.s':str(B/'cv3_watch_single_owner_combat.s'),'src/cv3_life_gain.s':str(helper),'src/entrypoint.s':'Append expanded-only cv3_life_gain.s include; private build include paths differ only.'},command=command,bindings={str(p):sha(p)for p in[Path(__file__),parent,parent.with_suffix('.dbg'),watch,watch.with_suffix('.dbg'),R/'src/cv3_core.s',R/'src/cv3.s',R/'src/entrypoint.s',R/'src/cv3_combat.s',core,helper,ag,entry,patch,B/'cv3_watch_single_owner_combat.s',B/'cv3_watch_single_owner_handoff.json',out,out.with_suffix('.dbg'),out.with_suffix('.lbl'),out.with_suffix('.map'),out.with_suffix('.cv3-mirror.json'),R/'tools/prepare_cv3_dmc_mirror.py']}))
 print(json.dumps(dict(passed=True,candidate_sha256=sha(out),changed_banks=banks,receipt=str(receipt),sha256=sha(receipt))))
if __name__=='__main__':main()
