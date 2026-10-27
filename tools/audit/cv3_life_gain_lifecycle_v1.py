"""Supplement: actual seven-INC Main ordering and real PlayerLoseLife owner."""
from pathlib import Path
import hashlib,itertools,json
from cv3_life_gain_controls_v1 import P,N,OLD,NEW,fresh,clone,stats,run,regs,live,bus
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
R=Path(__file__).resolve().parents[2];B=R/'build'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert sha(P)==OLD and sha(N)==NEW;old,new=scoped_load(P),scoped_load(N);out=B/'cv3_life_gain_watch_lifecycle.json';assert not out.exists()
 gain=[];death=[];contexts=[]
 for v,mode,initial in itertools.product([1,2,3],[0,1],[0,127,249,250,254,255]):
  q=fresh(new,['','grant','sypha','alucard'][v],mode);q.put(NumberofLives=initial,Cv3LastLife=initial,CoinTally=99)
  # Boundary-only current save records, matching preexisting earned state.
  for n,z in [('Cv3Health',47),('Cv3Hearts',31),('Cv3Subweapon',2),('Cv3Power',2)]:q.set(n,z,v-1)
  q.set('Block_Buffer_1',194,9*16+4)
  for i in range(6):q.set('FloateyNum_Control',11,i);q.set('FloateyNum_Timer',43,i)
  before=stats(q,v);_,writes=q.invoke('GameLoop');life=[z for z in writes if z['address']==address(new,'NumberofLives')]
  assert len(life)==7 and [z['value']for z in life]==[(initial+i)&255 for i in range(1,8)]
  assert life[0]['bank']==3 and all(z['bank']==126 for z in life[1:])
  assert q.get('CoinTally')==0 and stats(q,v)==before and q.get('Cv3LastLife')==q.get('NumberofLives')==(initial+7)&255
  # A following complete Main must retain the acknowledged state again.
  q.invoke('GameLoop');assert stats(q,v)==before and q.get('Cv3LastLife')==(initial+7)&255
  gain.append(dict(variant=v,mode=mode,initial=initial,final=q.get('NumberofLives'),actual_life_writers=life,fields_unchanged=before))
 for v,mode,initial in itertools.product([1,2,3],[0,1],[0,1,2,127,128,255]):
  qs=[fresh(b,['','grant','sypha','alucard'][v],mode)for b in[old,new]]
  for q in qs:
   q.put(NumberofLives=initial,Cv3LastLife=initial)
   for n,z in [('Cv3Health',47),('Cv3Hearts',31),('Cv3Subweapon',2),('Cv3Power',2)]:q.set(n,z,v-1)
  cs=[run(q,'PlayerLoseLife')[0]for q in qs]
  assert regs(cs[0])==regs(cs[1])and live(qs[0])==live(qs[1])and bus(qs[0])==bus(qs[1])and cs[0].processorCycles==cs[1].processorCycles
  for q in qs:assert q.get('NumberofLives')==(initial-1)&255
  writes=[(at,value)for at,value in qs[1].m.writes if at==address(new,'NumberofLives')];assert writes==[(address(new,'NumberofLives'),(initial-1)&255)]
  cs=[run(q,'Cv3Ensure')[0]for q in qs];assert regs(cs[0])==regs(cs[1])and live(qs[0])==live(qs[1])and bus(qs[0])==bus(qs[1]);assert stats(qs[1],v)==[64,10,0,0]
  at=location(new,'PlayerLoseLife');life=address(new,'NumberofLives');opcode=bytes([0xce,life&255,life>>8]);hits=[i for i in range(40)if new['raw'][at+i:at+i+3]==opcode];assert len(hits)==1
  death.append(dict(variant=v,mode=mode,initial=initial,final=qs[1].get('NumberofLives'),actual_PlayerLoseLife_DEC_opcode=list(opcode),actual_DEC_pc=address(new,'PlayerLoseLife')+hits[0],actual_DEC_bank=(at-16)//8192,original_reset_exact=True,Ensure_extra_cycles=cs[1].processorCycles-cs[0].processorCycles))
 for v,mode,kind in itertools.product([1,2,3],[0,1],['cold-ready','variant-switch','area','world','area-world']):
  qs=[fresh(b,['','grant','sypha','alucard'][v],mode)for b in[old,new]]
  for q in qs:
   if kind=='cold-ready':q.set('Cv3Ready',0,v-1)
   elif kind=='variant-switch':q.set('Cv3ActiveVariant',v%3+1)
   else:
    if'area'in kind:q.set('AreaPointer',195)
    if'world'in kind:q.set('WorldNumber',1)
   q.put(Cv3AttackAge=17,Cv3JumpActive=1)
  cs=[run(q,'Cv3Ensure')[0]for q in qs];assert regs(cs[0])==regs(cs[1])and live(qs[0])==live(qs[1])and bus(qs[0])==bus(qs[1])and cs[0].processorCycles==cs[1].processorCycles
  contexts.append(dict(variant=v,mode=mode,kind=kind,exact=True))
 at=location(new,'Cv3LifeChanged');size=int(new['syms']['Cv3LifeChanged']['size'],0);assert size==21 and address(new,'Cv3LifeChanged')==0xbc4f
 assert all(x==255 for x in old['raw'][at:at+size]);assert location(old,'Cv3Ensure::Life')==location(new,'Cv3Ensure::Life')
 z=dict(passed=True,native_run=False,source_CPU_only=True,candidate_sha256=NEW,actual_full_Main_seven_INC_cases=gain,actual_death_owner_cases=death,unchanged_lifecycle_contexts=contexts,helper=dict(bank_decimal=82,bank_hex='52',start='BC4F',end='BC63',bytes=size,formerly_unallocated_FF=True),scope='Actual complete Main collects a coin and processes six pending genuine native popup slots in one update; initial tally/popup/record snapshots are boundary inputs, not earned/no-seed native evidence. Real PlayerLoseLife DEC followed by unchanged Ensure resets across both modes/all3variants, including00->FF. Cold, variant, area/world controls exact. Source CPU only.',bindings={str(p):sha(p)for p in[Path(__file__),P,P.with_suffix('.dbg'),N,N.with_suffix('.dbg'),B/'cv3_life_gain_watch_controls.json',R/'src/game.s',R/'src/player.s',R/'src/screen_render.s',R/'src/cv3_core.s']})
 out.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(dict(passed=True,path=str(out),sha256=sha(out),full_Main=len(gain),deaths=len(death),contexts=len(contexts))))
if __name__=='__main__':main()
