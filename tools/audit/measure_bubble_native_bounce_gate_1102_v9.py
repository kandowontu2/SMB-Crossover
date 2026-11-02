"""Memory-only owner39 stomp routing; exact old path for every foreign raw ID."""
import itertools,json
from pathlib import Path
import measure_bubble_native_bounce_router_1102_v9 as B
P=B.P;R=B.R;O=B.O;N=B.N;address=B.address


def same(a,b,z,zz):
 differences=[]
 if[z[n]for n in['A','X','Y','P']]!=[zz[n]for n in['A','X','Y','P']]:differences.append(dict(kind='AXYP',old=z,new=zz))
 if a.rawtags!=b.rawtags:differences.append(dict(kind='maps',old=a.rawtags,new=b.rawtags))
 if bytes(a[0x15a:0x17b])!=bytes(b[0x15a:0x17b]):differences.append(dict(kind='SMC',old=bytes(a[0x15a:0x17b]).hex(),new=bytes(b[0x15a:0x17b]).hex()))
 # Bypass emulated register reads on BOTH sides. In particular b[$2007]
 # would consume buffered PPU data while supposedly observing memory.
 ramdiff=[(hex(i),x,y)for i,(x,y)in enumerate(zip(list.__getitem__(a,slice(0,32768)),list.__getitem__(b,slice(0,32768))))if x!=y and not 0x100<=i<0x200]
 if ramdiff:differences.append(dict(kind='native_state',first=ramdiff[:12]))
 for i in range(4):
  if a.ram[i]!=b.ram[i]:differences.append(dict(kind='private_RAM'+str(i),first=[(hex(j),x,b.ram[i][j])for j,x in enumerate(a.ram[i])if x!=b.ram[i][j]][:12]))
 return differences


def bundles():
 old=P.scoped_load(P.ROM);raw=B.ROM.read_bytes();assert P.sha(raw)==B.PIN;old['raw']=raw
 at=16+124*8192+0x4b0;gate=16+124*8192+0xd6
 assert raw[at:at+11]==bytes.fromhex('088d6a019848a00c4c2aa2')
 assert raw[gate:gate+10]==bytes([255])*10
 # Every typed original caller enters through FarCallCommon, which has
 # already published this same A in SafecallA_SMC+1. The old repeated store
 # is replaced with SelectedCharacter's load and the discriminator below.
 thunk=bytes.fromhex('089848a00cad02604cd6a0')
 classifier=bytes.fromhex('c927d0034c79a14c90a1')
 after=bytearray(raw);after[at:at+11]=thunk;after[gate:gate+10]=classifier
 new=dict(old);new['raw']=bytes(after)
 patches=[dict(offset=a,old=raw[a:a+len(v)].hex(),new=v.hex(),role=role)for a,v,role in[(at,thunk,'Original source stomp thunk; same saved P/Y and already-published A'),(gate,classifier,'Owner39-only discriminator; other IDs rejoin original A190 chain')]]
 return old,new,patches


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
 out=dict(passed=not negative and not rejects,ROM_written=False,shared_mutation=False,base_ROM_SHA256=B.PIN,proposed_patches=patches,fixed_MegaManBounceVelocity_unchanged=True,foreign_raw_direct_cases=cases,negative=negative,unqualified_or_invalid_seed_cases=rejects[:16],unqualified_case_count=len(rejects),scope='Memory-only differential. The10B navigation tail remains a requested lease; passing arbitrary raw fixtures still requires exact caller/table/indirect closure, legal active profiles and IRQ/NMI proof before composition.')
 (O/'native-bounce-owner-gate-measurement-v9.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))


if __name__=='__main__':main()
