"""Measure an explicit native stomp-event route, memory only, never a ROM."""
import json,itertools
from pathlib import Path
import check_bubble_bobble_native_cold_fix_1102_v8 as Q
import check_bub_menu_art_1102_v1 as UI
P=Q.P;R=Q.R;O=Q.O;N=Q.V7.N;address=Q.V7.address;location=UI.location
ROM=R/'build/bub-menu-candidate-1102-v2/combined-cold-fixed.nes';PIN='5a8a04c3deabafc2222e594bdcefd4a445afecb5c1ab4c1753e66acc4a883d29'


def bundles():
 b=P.scoped_load(P.ROM);raw=ROM.read_bytes();assert P.sha(raw)==PIN;b['raw']=raw;pc=address(b,'MegaManBounceVelocity');at=location(b,'MegaManBounceVelocity');target=address(b,'HuBounceOnly');bank=((location(b,'HuBounceOnly')-16)//8192)|128
 assert raw[at:at+21]==bytes.fromhex('088d6a01a9b08d6c01a9a48d6d01a9fc205a012860')
 after=bytearray(raw);patches=[]
 for i,v,role in[(5,target&255,'targetlow'),(10,target>>8,'targethigh'),(15,bank,'targetbank')]:patches.append(dict(offset=at+i,old=raw[at+i],new=v,role=role));after[at+i]=v
 new=dict(b);new['raw']=bytes(after);return b,new,patches


def same(a,b,z,zz):
 differences=[]
 if[z[n]for n in['A','X','Y','P']]!=[zz[n]for n in['A','X','Y','P']]:differences.append(dict(kind='AXYP',old=z,new=zz))
 if a.rawtags!=b.rawtags:differences.append(dict(kind='maps',old=a.rawtags,new=b.rawtags))
 if bytes(a[0x15a:0x17b])!=bytes(b[0x15a:0x17b]):differences.append(dict(kind='SMC',old=bytes(a[0x15a:0x17b]).hex(),new=bytes(b[0x15a:0x17b]).hex()))
 ramdiff=[(hex(i),x,b[i])for i,x in enumerate(list.__getitem__(a,slice(0,32768)))if x!=b[i]and not 0x100<=i<0x200]
 if ramdiff:differences.append(dict(kind='native_state',first=ramdiff[:12]))
 for i in range(4):
  if a.ram[i]!=b.ram[i]:differences.append(dict(kind='private_RAM'+str(i),first=[(hex(j),x,b.ram[i][j])for j,x in enumerate(a.ram[i])if x!=b.ram[i][j]][:12]))
 return differences


def main():
 old,new,patches=bundles();seeds=[N.fresh(b)for b in[old,new]];negative=[];cases=0;rejects=[]
 for raw,velocity,flags in itertools.product([i for i in range(256)if i!=39],[0,252,253],[0x30,0xf1]):
  pair=[]
  for seed in seeds:
   m=N.fork(seed);N.put(m,SelectedCharacter=raw,Player_Y_Speed=velocity,OperMode=1,GameEngineSubroutine=8,NmiDisable=1)
   try:z=N.invoke(m,'MegaManBounceVelocity',a=velocity,x=0,y=0,p=flags)
   except AssertionError as e:pair.append((m,None,str(e)));continue
   pair.append((m,z,None))
  a,z,e=pair[0];b,zz,ee=pair[1]
  if e or ee:
   rejects.append(dict(raw=raw,velocity=velocity,flags=flags,old=e,new=ee));continue
  diff=same(a,b,z,zz)
  if diff and len(negative)<16:negative.append(dict(raw=raw,velocity=velocity,flags=flags,differences=diff))
  cases+=1
  if negative:break
 out=dict(passed=not negative and not rejects,ROM_written=False,shared_mutation=False,base_ROM_SHA256=PIN,proposed_fixed_patch=patches,foreign_raw_direct_cases=cases,negative=negative,unqualified_or_invalid_seed_cases=rejects[:16],unqualified_case_count=len(rejects),scope='First memory-only full ABI/state/SMC/map differential of native existing bounce vs direct HuBounce event route. Arbitrary raw fixtures are not active cold owners; a passing result still needs legal91menu profiles/authenticated owners and interrupt closure before any grant.')
 (O/'native-bounce-only-router-measurement-v9.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))


if __name__=='__main__':main()
