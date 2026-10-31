"""Actual physical Thomas helper ABI and unchanged host vector seams; no preload."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as L
import ff_wram_host_controls_v7 as H
import ff_host_pickups_vectors_v2 as V
from check_tmnt_render_oa import address
from verify_native_relocation import NesMPU
P=R/'build/thomas-physical-host-1031-v7';O=R/'build/thomas-physical-vectors-1031-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
old_pending=V.pending_store
def pending(m,c,slot,op):
 if old_pending(m,c,slot,op):return True
 # The resident remains A85 while C changes. Only exact source-emitted
 # STX shadow / STX hardware adjacency is an additional live seam here.
 shadow=address(m.bundle,'CurrentBankC')
 return slot==2 and m.rawtags[1]==0xd5 and bytes(m[c.pc-3:c.pc+3])==bytes([0x8e,shadow&255,shadow>>8,0x8e,0x16,0x51])
V.pending_store=pending
def main():
 assert not O.exists();O.mkdir(parents=True);q=dict(passed=False,native=False,no_RAM_preload=True)
 try:
  stage=json.loads((P/'source-stage.json').read_text())
  for p,h in stage['bindings'].items():assert sha(p)==h,p
  b=H.C.qualified(P/'candidate.nes')
  def make(**kw):return L.make(b,SelectedCharacter=10,FmAlts=64,CurrentPlayer=0,Player_Rel_XPos=120,Player_Rel_YPos=160,**kw)
  seed=make();L.call(seed,'ThLoad');L.call(seed,'ThServiceVeneers',slot=0)
  def direct(m,name,p=48,hook=None):
   m.raw_page(1,0xd5);H.put(m,CurrentBank=0xd5);c=NesMPU(memory=m,pc=address(b,name));c.a,c.x,c.y,c.p,c.sp=0x59,7,0x83,p,0xc0;c.stPushWord(0x5aff)
   return H.finish(m,c,hook)
  pairs=0
  for name,valid in itertools.product(['ThCheckCode','ThCheck','ThRetire','ThColors','ThColdPortrait'],[False,True]):
   for flags in range(64):
    m=L.fork(seed);H.put(m,CurrentOAMOffset=0)
    if not valid:m.ram[2][0x1fe3]^=1
    p=L.flags(flags);c,_=direct(m,name,p)
    expected=(p&254)|int(valid)if name in['ThCheckCode','ThCheck']else p
    assert(c.a,c.x,c.y,c.p,c.sp)==(0x59,7,0x83,expected,0xc0),(name,valid,flags,c.a,c.x,c.y,c.p,c.sp,expected)
    pairs+=1
  print('Thomas direct full64flag helpers PASS',pairs,flush=True)
  failures=[]
  for name,locked,corrupt in [('locked',True,None),('verify',False,(3,17))]:
   m=make();m.protection=[0,0]if locked else[2,1];m.corrupt_at=corrupt;c,_=L.call(m,'ThLoad')
   assert not c.p&1 and not(m.ram[2][0x1fe0]==167 and m.ram[3][0x1fe0]==167),name
   failures.append(name)
  vectors=[]
  for name in ['ThLoad','ThCheck','ThRetire','ThColdPortrait']:
   origin=make()if name=='ThLoad'else L.fork(seed);trace=[]
   def collect(m,c,n):
    if m.rawtags[1]==0xd5:trace.append((n,c.pc,c.p))
   baseline=L.fork(origin);direct(baseline,name,hook=collect)
   first={}
   for n,pc,p in trace:first.setdefault(pc,(n,p))
   unique=list(first.items());selected=unique[::max(1,len(unique)//12)]
   # Include all true mapper shadow/hardware boundaries in the resident.
   for pc,(n,p)in unique:
    if bytes(baseline[pc:pc+3])in[b'\x8d\x16\x51',b'\x8e\x16\x51']:selected.append((pc,(n,p)))
   selected=dict(selected)
   for kind,lag,pause in [('NMI',255,0),('NMI',255,1),('IRQ',255,0)]:
    for pc,(cut,p)in selected.items():
     if kind=='IRQ'and p&4:continue
     m=L.fork(origin);H.put(m,NmiDisable=lag,GamePauseStatus=pause);hit=[]
     def hook(m,c,n):
      if n==cut:hit.append(V.interrupt(m,c,kind))
     c,_=direct(m,name,p=48,hook=hook)
     assert len(hit)==1
     assert m.ram[2:]==baseline.ram[2:] and bytes(m[3:11])==bytes(baseline[3:11]),(name,kind,pc,'resumed payload/scratch differs')
     vectors.append(dict(name=name,PC=f'{pc:04X}',lag=lag,pause=pause,**hit[0]))
   print('Thomas actual resident vectors PASS',name,len(vectors),flush=True)
  q.update(passed=True,direct_full64flags_helper_pairs=pairs,failed_copy_cases=failures,actual_host_vectors=len(vectors),vectors=vectors,
   limits=['Actual a126 vectors and new physically loaded payload; no shared ingress/natural Main or native raster claim','IRQ correctly deferred while source cold-copy SEI is active; NMI remains actual lag-vector enabled'])
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p):sha(p)for p in[Path(__file__),Path(L.__file__),Path(H.__file__),Path(V.__file__),R/'tools/audit/verify_native_relocation.py',P/'source-stage.json',P/'candidate.nes',P/'candidate.dbg',P/'candidate.lbl']}
 dump(O/'controls.json',q);print(json.dumps({k:v for k,v in q.items()if k not in['bindings','vectors','traceback']}));assert q['passed'],q.get('error')
if __name__=='__main__':main()
