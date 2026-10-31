"""Execute new selector/fallback via genuine B020/scene native caller frames."""
from pathlib import Path
import hashlib,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import cf_cold_warm_retirement_controls_v1 as V
T,C=V.T,V.C
from check_tmnt_render_oa import address,location
P=R/'build/cf-cold-warm-palette-source-v1/joint';J=R/'build/cf-preload-name-source-v1/joint';O=R/'build/cf-preload-name-caller-controls-v2'
sha=V.sha;FLAGS=[v for v in range(256)if v&0x30==0x30]

def scene_seed(root,raw,var,form,warm):
 V.select(root);m=T.Bus();V.blank(m,raw,var,form)
 T.put(m,NumberofLives=2,PlayerStatus=0,CurrentPlayer=0,GameEngineSubroutine=8,Player_X_Position=120,Player_PageLoc=0,Player_Y_Position=176,Player_Y_HighPos=1,Player_State=0)
 if warm:V.V.call(m,'BwScene')
 m.writes.clear();m.ram_writes.clear();return m

def result(m,z):
 app=bytes(m[i]for i in range(0x8000)if not(0x100<=i<0x1e1 or 0x2000<=i<0x5c00))
 writes=[(a,v)for a,v in m.writes if a<0x8000 and not(0x100<=a<0x1e1 or 0x2000<=a<0x5c00)]
 return(z['AXYP'],app,[bytes(x)for x in m.ram],m.rawtags[:],T.smc(m),bytes(m[0x1e1:0x200]),writes)

def main():
 O.mkdir(exist_ok=False);q=dict(passed=False,native=False,CF_BT_pending=True,scene=[],name=[])
 try:
  identities=[(27,0,0),(27,0,8)]+[(31,v,0)for v in range(4)]
  # Warm paths cover every architectural flag. Actual full verified cold
  # copies cover the eight established loader flag edges for each identity.
  for raw,var,form in identities:
   for warm,flags in[(1,FLAGS),(0,[0x30,0x31,0x38,0x3d,0x70,0x79,0xb0,0xf9])]:
    seeds={root:scene_seed(root,raw,var,form,warm)for root in[P,J]}
    for p in flags:
     pair=[];cost=[]
     for root in[P,J]:
      V.select(root);m=C.clone(seeds[root]);z=V.V.call(m,'BwScene',p=p);pair.append(result(m,z));cost.append(z['CPU'])
     assert pair[0]==pair[1],('whole native scene actual emitted selector',raw,var,form,warm,p,[i for i in range(7)if pair[0][i]!=pair[1][i]])
     q['scene'].append(dict(raw=raw,variant=var,form=form,warm=warm,flags=p,oldCPU=cost[0],newCPU=cost[1]))
   print('actual scene flags PASS',raw,var,form,flush=True)
  V.select(J)
  for raw,var,p in itertools.product([31,33],range(4),FLAGS):
   base=T.Bus();T.put(base,SelectedCharacter=raw,CrossoverMenuIndex=30 if raw==31 else 23,FmGroups=var<<3,FmAlts=0,OperMode=0,FamilyMainCommit=1,VRAM_Buffer1_Offset=0)
   base.ram[2][0x1fe0]=0;base.ram[3][0x1fe0]=0
   pair=[]
   for routed in[False,True]:
    m=C.clone(base);m.writes.clear();m.ram_writes.clear();name='BtServiceVeneers'if routed else'FmQueueName';pc=address(T.B,name)+(54 if routed else 0);bank=(location(T.B,name)-16)//8192|128
    c=C.start(m,pc,bank,a=0x55,x=7,y=91,p=p);seen=[]
    def watch(cpu,step):
     if cpu.pc==address(T.B,'FmQueueName')and m.rawtags[1]==(location(T.B,'FmQueueName')-16)//8192|128:seen.append(step)
     if cpu.pc>=0x8000:assert m.rawtags[(cpu.pc-0x8000)//8192]>=128,('unready name executed guest',raw,var,hex(cpu.pc))
    z=T.finish(m,c,watch);r=result(m,z)
    if routed:
     shadow=address(T.B,'CurrentBankC');prefix=[(shadow,2 if raw==31 else 3),(shadow,base.rawtags[2])]
     assert r[6][:2]==prefix,(raw,r[6][:3]);r=(*r[:6],r[6][2:])
    assert len(seen)==1 and not m.ram_writes
    pair.append(r)
   assert pair[0]==pair[1],('actual invalid18 FmQueueName queue/caller',raw,var,p,[i for i in range(7)if pair[0][i]!=pair[1][i]])
   q['name'].append([raw,var,p])
  delta=[r['newCPU']-r['oldCPU']for r in q['scene']]
  q.update(passed=True,actual_whole_scene_pairs=len(q['scene']),warm_all64flags_and_cold8flags_each6identities=True,actual_unready_name18_native_pairs=len(q['name']),full_returned_AXYP_SP_application_orderedwrites_4WRAM_rawmaps_33SMC_liveupperpage1_exact=True,scene_CPU_delta=[min(delta),max(delta)],scope='Actual emitted31Bselector/19Bfallback, source stage38a6. CurrentBW/CF cold+warm retain actualnativecallback, invalid31/33name18 executes genuine ROM FmQueueName exactlyonce, exact twoCshadow authprefix then original orderednativequeuewrites, noA2/A3. CF/BTpending; no native/readiness.')
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 files=[Path(__file__),R/'tools/audit/cf_preload_name_caller_controls_v1.py',R/'build/cf-preload-name-caller-controls-v1/controls.json',Path(V.__file__),Path(C.__file__),Path(T.__file__),J/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',P/'candidate.nes',P/'candidate.dbg',J/'cf-stream.bin',J/'cf-cookie.bin',J/'bowser/router.s',J/'bowser/cold.s']
 q['bindings']={str(p.resolve()):sha(p)for p in files};(O/'controls.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k not in['scene','name','bindings']}));assert q['passed']
if __name__=='__main__':main()
