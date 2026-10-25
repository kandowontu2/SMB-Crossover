"""Authenticate original SMB3 hammer lifetime through consecutive full updates.

Executes original PRG007_A361 (motion, sprite preparation, contact loop and hit
handler), then original Bowser_HandleIfDead on every update. No emulation traps.
This isolated RAM arena does not claim original complete-game/PPU behavior.
"""
from pathlib import Path
import argparse,hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/audit'))
from verify_native_relocation import NesMPU


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 a.output.mkdir(parents=True,exist_ok=False)
 auth=ROOT/'build/verification/smb3-mario-candidate-agent/auth-source'
 rom=Path('C:/NES/Super Mario Bros. 3 (USA) (Rev 1).nes').read_bytes()
 assert hashlib.sha256(rom).hexdigest()=='1ddc4b429490e298c05fa70389034107c0cb50f671c7c1baaa3f228224afc2e9'
 assert rom[16:]==(auth/'smb3.nes').read_bytes()[16:]
 sy={n:int(v,16)for n,v in re.findall(r'^(\w+)\s*=\s*\$([0-9A-Fa-f]+)',(auth/'smb3.fns').read_text(),re.M)}
 src=(auth/'smb3.asm').read_text();normal=int(re.search(r'^OBJSTATE_NORMAL\s*=\s*(\d+)',src,re.M).group(1))
 rows=[]
 for facing in [1,2]:
  m=[0]*65536
  def page(base,bank):m[base:base+8192]=rom[16+bank*8192:16+(bank+1)*8192]
  for base,bank in [(0x8000,30),(0xa000,7),(0xc000,0),(0xe000,31)]:page(base,bank)
  for i in range(1,5):m[sy['Objects_SprHVis']+i]=255
  values=dict(PlayerProj_ID=2,PlayerProj_X=80 if facing==1 else 96,
              PlayerProj_Y=96,PlayerProj_YHi=0,PlayerProj_XVel=16 if facing==1 else 240,
              PlayerProj_YVel=253,PlayerProj_XVelFrac=0,PlayerProj_Cnt=0,
              Player_Suit=6,Objects_SprHVis=0,Objects_SprVVis=0,
              Objects_State=normal,Level_ObjectID=24,Objects_SpriteY=80,
              Objects_SpriteX=80,Objects_HitCount=34,SlotIndexBackup=0)
  for n,v in values.items():m[sy[n]]=v
  calls=[]
  def call(name,bank):
   page(0xa000,bank);c=NesMPU(memory=m,pc=sy[name]);c.x,c.y,c.p,c.sp=0,0,0x30,0xfd;c.stPushWord(0x5aff)
   writes={};seen=[]
   for _ in range(60000):
    if c.pc==0x5b00:return c.processorCycles,writes,seen
    if c.pc in [sy['PlayerProj_HitEnemies'],sy['PlayerProj_HitObject']]:seen.append(f'{c.pc:04X}')
    pc=c.pc;op=m[pc]
    target=None
    if op in [0x85,0x86,0x84]:target=m[(pc+1)&65535]
    elif op in [0x95,0x96,0x94]:target=(m[(pc+1)&65535]+(c.y if op==0x96 else c.x))&255
    elif op in [0x8d,0x8e,0x8c,0x9d,0x99]:
     target=m[(pc+1)&65535]+256*m[(pc+2)&65535]
     target=(target+(c.x if op==0x9d else c.y if op==0x99 else 0))&65535
    c.step()
    if target is not None:writes[f'{target:04X}']=m[target]
   raise AssertionError((name,'timeout',hex(c.pc)))
  for update in range(1,5):
   prior=m[sy['Objects_HitCount']]
   cycles,writes,seen=call('PRG007_A361',7)
   assert seen.count(f'{sy["PlayerProj_HitObject"]:04X}')==1
   assert m[sy['Objects_HitCount']]==prior-1
   assert m[sy['PlayerProj_ID']]==2,'Source hammer remains active after actual contact'
   assert m[sy['Objects_State']]==normal,'No hurt/dead state blocks next source contact'
   after_projectile=m.copy()
   owner_cycles,owner_writes,_=call('Bowser_HandleIfDead',1)
   assert m[sy['PlayerProj_ID']]==2 and m[sy['Objects_HitCount']]==34-update
   assert m[sy['Objects_State']]==normal
   assert all(m[sy[n]]==0 for n in ['Objects_Timer','Objects_Timer2','Objects_Timer3']),'Original contact/death owner introduces no boss hurt timer'
   record={n:m[sy[n]]for n in ['PlayerProj_ID','PlayerProj_X','PlayerProj_Y','PlayerProj_Cnt','Objects_HitCount','Objects_State','Objects_Timer','Objects_Timer2','Objects_Timer3']}
   calls.append(dict(update=update,state=record,source_projectile_cycles=cycles,
                     source_boss_death_owner_cycles=owner_cycles,
                     source_contact_PCs=seen,written_addresses=writes,
                     boss_owner_writes=owner_writes))
  rows.append(dict(facing=facing,consecutive_original_updates=calls))
 report=dict(passed=True,original_ROM_sha256=hashlib.sha256(rom).hexdigest(),
             driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             original_symbols_sha256=hashlib.sha256((auth/'smb3.fns').read_bytes()).hexdigest(),
             authenticated_original_payload_exact=True,actual_original_updates=8,
             cases=rows,declared_traps=[],source_hammer_persists=True,
             source_hammer_applies_one_hit_per_overlapping_update=True,
             source_bowser_damage_state_and_timers_unchanged=True,
             source_boss_balance='Original begins at34; zero-counter next hit kills, hence35 total. This is separate from SMB1 native5HP.',
             scope='Actual original complete projectile motion/draw/contact path plus actual Bowser death-state owner, four consecutive overlapping updates per facing. No CPU entry/return substitution or contact trap. Not full source boss AI/PPU/game-frame integration.')
 (a.output/'proof.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='cases'},indent=2))


if __name__=='__main__':main()
