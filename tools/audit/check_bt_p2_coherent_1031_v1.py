"""Narrow same-span P2 caller guard proof on genuine final CF/BT source."""
from pathlib import Path
import argparse,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import battletoads_current_loader_controls_v1 as L
import battletoads_native_adapter_controls_v1 as T
H=L.H;address=L.address
from verify_native_relocation import NesMPU
J=R/'build/bt-cf-coherent-source-1031-v1/joint';P=R/'build/bt-lives-body-source-v7/joint';O=R/'build/bt-cf-coherent-controls-1031-v1'
SHA='e538d2b809b1dac9b70a0a1b23a1b33b3d361297b25fac0b556d8eae5c7721ed'

def bound():
 q=json.loads((J.parent/'source-stage.json').read_text());assert q['candidate']==L.sha(J/'candidate.nes')==SHA
 for n,h in q['bindings'].items():assert L.sha(n)==h,n

def helper():
 b=H.C.qualified(J/'candidate.nes');m=L.make(b);start=address(b,'BtStatusPlayerCount')
 assert start==address(b,'CrossoverPatchStatusName')+18
 m.raw_page(1,131);H.put(m,CurrentBank=131);count=0;cycles=[]
 for raw,x,flag in itertools.product(range(256),[1,255],range(64)):
  H.put(m,SelectedCharacter=raw,NumberOfPlayers=1);m.writes.clear();c=NesMPU(memory=m,pc=start);c.a=85;c.x=x;c.y=37;c.p=L.flags(flag);c.sp=224;c.stPushWord(0x5aff)
  for _ in range(24):
   if c.pc==0x5b00:break
   m.pc=c.pc;c.step()
  else:raise AssertionError('helper bound')
  a=0 if raw==33 and x==255 else 1;p=(L.flags(flag)&125)|(2 if a==0 else 0)
  assert(c.a,c.x,c.y,c.p,c.sp)==(a,x,37,p,224),(raw,x,flag,c.a,c.p)
  assert all(0x100<=a<0x200 for a,v in m.writes),'helper changed application/mapper/state'
  count+=1;cycles.append(c.processorCycles)
 return dict(passed=True,all256raw_all64flags_twoXcases=count,incomingA_dead=True,X_Y_SP_exact=True,foreign_native_LDA_AXYP_exact=True,
   only_Selected33_XFF_returns0=True,no_state_or_mapper_write=True,CPU_range=[min(cycles),max(cycles)],helper_bytes=21)

def callers():
 bs=[H.C.qualified(p/'candidate.nes')for p in[P,J]];count=0;witness=[]
 for variant in [0,1]:
  seeds=[T.seed(b,0,variant)for b in bs]
  for message,flag in itertools.product(range(5),range(64)):
   pair=[]
   for s in seeds:
    m=L.fork(s);H.put(m,CurrentPlayer=1,NumberOfPlayers=1,VRAM_Buffer1_Offset=0,WorldNumber=0,LevelNumber=0)
    c,_=L.call(m,'WriteGameText',a=message,x=91,y=37,p=L.flags(flag));at=address(m.bundle,'VRAM_Buffer1')
    pair.append((m,c,bytes(m[at:at+84])))
   (a,c,old),(m,z,new)=pair
   if message==0:
    at=address(m.bundle,'BtStatusNames')&8191;expected=bytes(m.ram[3][at+variant*7:at+variant*7+7])
    assert new[11:18]==expected and old[11:16]!=new[11:16]
    assert new[:11]==old[:11]and new[18:]==old[18:]
    assert(z.a,z.x,z.y,z.sp)==(0,255,40,224)
    if flag==0:witness.append(dict(variant=variant,retained_wrong_old_name=list(old[11:18]),correct_source_name=list(new[11:18]),old_AXYP=[c.a,c.x,c.y,c.p],new_AXYP=[z.a,z.x,z.y,z.p]))
   else:
    assert old==new and(c.a,c.x,c.y,c.p,c.sp)==(z.a,z.x,z.y,z.p,z.sp),('original nonA0 semantics',variant,message,flag)
   assert a.rawtags==m.rawtags and [bytes(x)for x in a.ram[:3]]==[bytes(x)for x in m.ram[:3]]
   count+=1
 # Real foreign text consumers, including current CF-ready and every high family.
 raws=[0,1,2,5,8,9,13,14,15,17,18,19,20,21,22,24,25,26,27,28,29,30,31,32]
 seeds=[L.make(b,OperMode=0)for b in bs];foreign=0
 for raw,player,message,flag in itertools.product(raws,[0,1],range(5),[0,63]):
  pair=[]
  for s in seeds:
   m=L.fork(s);H.put(m,SelectedCharacter=raw,CurrentPlayer=player,NumberOfPlayers=1,VRAM_Buffer1_Offset=0,FmAlts=0,RdVariant=0)
   c,_=L.call(m,'WriteGameText',a=message,x=91,y=37,p=L.flags(flag));at=address(m.bundle,'VRAM_Buffer1')
   pair.append(((c.a,c.x,c.y,c.p,c.sp),bytes(m[at:at+84]),m.rawtags[:]))
  assert pair[0]==pair[1],('actual foreign WriteGameText changed',raw,player,message,flag,pair[0][0],pair[1][0]);foreign+=1
 return dict(passed=True,actual_BT_P2_WriteGameText_pairs=count,bothvariants_all64flags_all5messages=True,
   foreign_native_WriteGameText_pairs=foreign,actual24foreignraws_bothplayers_5messages_extremeflags=True,
   original_all_nonA0_packet_AXYP_SP_maps_exact=True,only_old_P2_LUIGI_overwrite_removed=witness,
   genuine_caller_contract='Only A0 header reaches CheckPlayerName with XFF. Its original caller WriteTopStatusLine immediately tails IncSubtask; returned X/A/Y are dead there. All other message continuations retain exact native outputs.')

def vectors():
 b=H.C.qualified(J/'candidate.nes');seed=T.seed(b,0,1);H.put(seed,CurrentPlayer=1,NumberOfPlayers=1,OperMode=0,NmiDisable=255,GuestAudioCharacter=22,Square1SoundQueue=4,Square2SoundQueue=8)
 rows=[]
 for raw in [0,33]:
  initial=L.fork(seed);H.put(initial,SelectedCharacter=raw);cuts=[];seen=set();m=L.fork(initial)
  def trace(mm,c,i):
   if mm.rawtags[1]==131 and address(b,'BtStatusPlayerCount')<=c.pc<address(b,'BtStatusPlayerCount')+21 and c.pc not in seen:
    seen.add(c.pc);cuts.append((i,c.pc,bool(c.p&4)))
  H.finish(m,H.start(m,'WriteGameText',a=0,p=48),trace);assert cuts
  for step,pc,masked in cuts:
   for kind in ['NMI']+([]if masked else['IRQ']):
    m=L.fork(initial);proof=[]
    def inject(mm,c,i):
     if i==step:assert c.pc==pc;proof.append(L.V.interrupt(mm,c,kind))
    c,lo=H.finish(m,H.start(m,'WriteGameText',a=0,p=48),inject);assert len(proof)==1
    rows.append(dict(raw=raw,PC=pc,**proof[0]))
 return dict(passed=True,cases=len(rows),all_reached_near_helper_PC_cuts=True,real_lag_NMI_legal_IRQ=True,all33SMC_livepage1_AXYP_SP_rawmaps_exact=True,rows=rows)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',choices=['helper','callers','vectors'],required=True);a=ap.parse_args();O.mkdir(exist_ok=True)
 out=O/(a.check+'-controls.json');assert not out.exists();q=dict(passed=False,native=False,candidate=SHA)
 try:bound();q.update(result=globals()[a.check](),passed=True)
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc())
 q['bindings']={str(p.resolve()):L.sha(p)for p in[Path(__file__),Path(L.__file__),Path(T.__file__),J.parent/'source-stage.json',J/'candidate.nes',J/'candidate.dbg',P/'candidate.nes',P/'candidate.dbg']}
 out.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in q.items()if k not in['result','bindings']}),flush=True)
 if q['passed']:print(json.dumps({k:v for k,v in q['result'].items()if k not in['rows','only_old_P2_LUIGI_overwrite_removed']}),flush=True)
 assert q['passed'],q.get('error')
if __name__=='__main__':main()
