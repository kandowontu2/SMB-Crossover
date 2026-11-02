"""Public Arthur policy and full-cookie differential verification."""
import itertools,json
import prepare_arthur_auth_fast_1101_v2 as P
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

def main():
 seeds=[]
 for rom in [P.BASE,P.O/'candidate.nes']:
  b=scoped_load(rom);m=M.fresh(b)
  sig=bytes(b['raw'][location(b,'ArCacheSignature'):location(b,'ArCacheSignature')+16])
  m.ram[2][0x1fe0:0x1ff0]=sig
  M.put(m,SelectedCharacter=32,OperMode=1,GameEngineSubroutine=8,ArHostReady=167,FamilyMainCommit=1)
  seeds.append(m)
 names=['HuVisible','HuBody','HuAdder','HuBox','HuUi','HuWeaponTail']
 cases=0;savings=[]
 for name,a,p,bad in itertools.product(names,[0,85,255],[0x20,0x21,0x60,0xa1],[-1,*range(16)]):
  pair=[]
  for seed in seeds:
   m=M.fork(seed)
   if bad>=0:m.ram[2][0x1fe0+bad]^=1
   z=M.invoke(m,name,a=a,x=19,y=73,p=p);pair.append((m,z))
  (old,z),(new,w)=pair
  assert all(z[k]==w[k] for k in ['A','X','Y','P']),(name,a,p,bad,z,w)
  for lo,hi in [(0,256),(512,2048)]:assert old[lo:hi]==new[lo:hi],(name,bad,'native')
  assert old.ram==new.ram,(name,bad,'WRAM')
  assert old.rawtags==new.rawtags,(name,bad,'mapper')
  if bad<0:savings.append(dict(name=name,old=z['CPU'],new=w['CPU'],saved=z['CPU']-w['CPU']))
  cases+=1
 # Direct original public predicates cover every possible byte mismatch and
 # both constructor bypass/decline paths as well as ordinary cache checks.
 auth_cases=0
 for name,y,p,bad,value in itertools.product(['ArGenCheckForeground','ArGenCookieOnly'],[0,9,15,18,35],[0x20,0x61,0xa1],[-1,*range(16)],[1,128,255]):
  pair=[]
  for seed in seeds:
   m=M.fork(seed);M.put(m,CurrentBankC=198);m[0x5116]=198
   if bad>=0:m.ram[2][0x1fe0+bad]^=value
   z=M.invoke(m,name,a=85,x=19,y=y,p=p);pair.append((m,z))
  (old,z),(new,w)=pair
  assert all(z[k]==w[k] for k in ['A','X','Y','P']),(name,y,p,bad,value,z,w)
  assert old.rawtags==new.rawtags and old.ram==new.ram
  for lo,hi in [(0,256),(512,2048)]:assert old[lo:hi]==new[lo:hi]
  auth_cases+=1
 q=dict(passed=True,public_policy_cases=cases,auth_cases=auth_cases,ROM_sha256=P.sha(P.O/'candidate.nes'),valid_policy_costs=savings[:12],saved_cycle_range=[min(x['saved'] for x in savings),max(x['saved'] for x in savings)],scope='Final AXYP/nonstack nativeRAM/all WRAM/mapping exact. Intentional dropped scratch self-writes are not ordered-store parity. Native and interrupt-cut verification pending.')
 (P.O/'CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
if __name__=='__main__':main()
