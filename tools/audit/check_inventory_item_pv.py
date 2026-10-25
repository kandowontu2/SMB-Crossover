"""Source-table ownership/spending oracles through actual public linked calls."""
from pathlib import Path
import argparse,hashlib,itertools,json
from check_tmnt_render_oa import load,Memory,address,location
from verify_native_relocation import NesMPU
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);b=load(a.rom)
 def values(name,n):pos=location(b,name);return b['raw'][pos:pos+n]
 lo,hi=values('InvBitLo',16),values('InvBitHi',16);assert list(lo)==[(1<<i)&255 for i in range(16)]and list(hi)==[(1<<i)>>8 for i in range(16)]
 pools=values('InvAmmoIndex',192);cases=spends=0
 def run(name,char,variant,mode,item,owned,status=1,balance=0,cost=0,star=0):
  m=Memory(b);bank=(location(b,name)-16)//8192;m.page(1,bank);m[address(b,'CurrentBank')]=bank|128
  seed=dict(SelectedCharacter=char,CrossoverBehaviorVersion=mode,Cv3Variant=variant,Z2Variant=variant,RlVariant=variant,PlayerStatus=status,StarInvincibleTimer=star,InvDirty=254)
  for n,v in seed.items():m[address(b,n)]=v
  m[address(b,'InvOwnedLo')+char]=owned&255;m[address(b,'InvOwnedHi')+char]=owned>>8
  for i in range(192):m[address(b,'InvAmmo')+i]=balance
  m[0x1fe]=255;m[0x1ff]=0x7e;m.writes=[];c=NesMPU(memory=m,pc=address(b,name));c.sp=0xfd;c.a=item;c.x=3;c.y=cost;c.p=0x71
  for _ in range(10000):
   if c.pc==0x7f00:break
   c.step()
  else:raise AssertionError(('Inventory call timeout',name,char,variant,mode,item,hex(c.pc)))
  assert c.sp==255
  return c,m
 def classic(char,v,mode):
  if char==9 and v:return False
  if char==5 and 1<=v<4:return True
  if char==4 and v==1:return True
  return mode==0 and 1<=char<=5
 masks=[0,*[1<<i for i in range(16)],65535,0xaaaa,0x5555,131]
 for char,v,mode,item,owned,status in itertools.product(range(1,12),range(4),range(2),range(16),masks,[0,1]):
  for name in ['InventoryHasRaw','InventoryHas']:
   c,m=run(name,char,v,mode,item,owned,status)
   expected=not classic(char,v,mode)and bool(owned&(1<<item))and(status!=0 or name=='InventoryHasRaw')
   assert bool(c.p&1)==expected,(name,char,v,mode,item,owned,status,c.a,c.p,expected)
   cases+=1
 for char,v,mode,item,balance,cost,star in itertools.product(range(1,12),[0,1],range(2),range(16),[0,1,16,112],[0,1,4,113],[0,1]):
  c,m=run('InventorySpend',char,v,mode,item,65535,balance=balance,cost=cost,star=star);pool=pools[char*16+item]
  modern=not classic(char,v,mode);free=star or pool==255;expected=modern and(free or balance>=cost)
  assert bool(c.p&1)==bool(expected),('spend',char,v,mode,item,balance,cost,star,c.a,c.p,pool)
  for i in range(192):
   want=balance-cost if expected and not free and i==pool else balance
   assert m[address(b,'InvAmmo')+i]==want,('wrong pool',char,v,mode,item,pool,i)
  spends+=1
 q=dict(passed=True,ROM_sha256=hashlib.sha256(b['raw']).hexdigest(),ownership_public_call_cases=cases,spending_cases=spends,
  scope='Independent bit-mask and linked-pool table oracles through real InventoryHas/Raw/Spend,11legacy IDs, four/two alternate values, both modes,16requested IDs, single-bit/mixed ownership, powered/unpowered and affordable/empty/star/free ammo cases. Explicit legal component seeds; physical pickup/use is separate.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q),flush=True)
if __name__=='__main__':main()
