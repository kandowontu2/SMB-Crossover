"""Measure owned51B factoring and actual caller's private X/Y independence."""
from pathlib import Path
import hashlib,itertools,json,subprocess,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import cf_cold_warm_retirement_controls_v1 as V
from private_build_outputs_v1 import validate
T,C=V.T,V.C;J=V.J;O=R/'build/cf-name-fallback-factor-proposal-v1'
S=R/'tools/reference/cf_name_fallback_factor_proposal_v1.s';sha=V.sha

def context(raw,var,form):
 V.select(J);m=T.Bus();V.blank(m,raw,var,form);T.put(m,NumberofLives=2,PlayerStatus=0,CurrentPlayer=0,GameEngineSubroutine=8,Player_X_Position=120,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0)
 return m

def finish(m,project=False,p=0x30):
 c=C.start(m,T.address(T.B,'BwScene'),(T.location(T.B,'BwScene')-16)//8192|128,a=0x57,x=0xa9,y=0x63,p=p);projected=[]
 target='CfLoadIfCold'if T.get(m,'SelectedCharacter')==31 else'BwLoad'
 high=T.address(T.B,target)>>8;bank=(T.location(T.B,target)-16)//8192|128
 def hook(cpu,step):
  if cpu.pc==T.address(T.B,'BwCfSceneLoad')and m.rawtags[1]==0xc3:
   if project:cpu.x,cpu.y=high,bank
   projected.append(dict(step=step,original_native_AXYP_still_on_outer_stack=True,X=cpu.x,Y=cpu.y))
 z=T.finish(m,c,hook)
 return z,projected

def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,native=False,proposal_only=True,host_source_unchanged=True,rows=[])
 try:
  assert sha(J/'candidate.nes')=='8f0a925be0f1845952583a28dac7b54dd716c35539cfd65a13df37a7f9cdb310'
  cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-o',str(O/'measured.o'),str(S)];guard=validate(cmd,O,cwd=R);z=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
  (O/'build.json').write_text(json.dumps(dict(command=cmd,output_guard=guard,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n');assert z.returncode==0,z.stderr
  dump=subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-segments',str(O/'measured.o')],capture_output=True,text=True,check=True).stdout;(O/'segments.txt').write_text(dump)
  # Assembler asserts31+19; the real original owned51B has room for1EA.
  assert '31'in dump and '19'in dump
  for raw,var,form,warm,p in itertools.product([27,31],range(4),[0,8],[0,1],[0x30,0x79]):
   if raw==27 and var or raw==31 and form:continue
   base=context(raw,var,form)
   if warm:finish(base)
   pairs=[]
   for project in[False,True]:
    m=C.clone(base);m.writes.clear();m.ram_writes.clear();z,at=finish(m,project,p)
    app=bytes(m[i]for i in range(0x8000)if not(0x100<=i<0x1e1 or 0x2000<=i<0x5c00))
    writes=[(a,v)for a,v in m.writes if a<0x8000 and not(0x100<=a<0x1e1 or 0x2000<=a<0x5c00)]
    pairs.append((z['AXYP'],app,[bytes(x)for x in m.ram],m.rawtags[:],T.smc(m),bytes(m[0x1e1:0x200]),writes,z['CPU'],at))
   assert pairs[0][:7]==pairs[1][:7],('actual outer Scene private argument use',raw,var,form,warm,p,[i for i in range(7)if pairs[0][i]!=pairs[1][i]])
   q['rows'].append(dict(raw=raw,variant=var,form=form,warm=warm,flags=p,CPU=pairs[0][7],projected_call=pairs[1][8]))
  assert all(len(r['projected_call'])==1 for r in q['rows'])
  q.update(passed=True,compiled_fallback=19,compiled_selector=31,old_owned=51,padding_left=1,actual_outer_BwScene_argument_projection_pairs=len(q['rows']),full_returned_AXYP_SP_application_orderedwrites_4WRAM_rawmaps_33SMC_live_upperpage1_exact=True,
   ABI='Only the private load-selector may use X/Y as target high/rawbank. Actual BwScene saves nativeAXYP before it; CF returnsC0 and directly restores saved nativeAXYP, BW actual constructor ignores incomingXY except preserving them before same outer restore. This finite fixture changes only CPU X/Y at retained private helper entry to measured metadata values; no host ROM opcode/source is patched.',
   scope='Compiled size and real retained-caller argument independence only. New31B selector/19B fallback is not linked/adopted. After review, actual source-repack successor still needs allflags/branch/fullcallback/new vector tests. Preload name18 becomes genuine FmQueueName;15/19 existing native targets unchanged. No new span/state/P1/readiness.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):sha(p)for p in[Path(__file__),S,O/'measured.o',O/'build.json',O/'segments.txt',Path(V.__file__),J/'candidate.nes',J/'candidate.dbg',J/'bowser/router.s',J/'bowser/cold.s',R/'build/cf-cold-warm-source-v3/handoff.json']if p.exists()}
 (O/'proposal.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['rows','bindings']}));assert q['passed']
if __name__=='__main__':main()
