"""Assemble authentic Tank policy/pickup leaves and compare actual donor CPU."""
from pathlib import Path
import hashlib,itertools,json,re,subprocess,sys,zipfile
from py65.devices.mpu6502 import MPU
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_mario_tank_source_1101_v1 import O,COMMIT,donor,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
S=O/'source';B=O/'author-build';CC=R/'tools/Windows/cc65/bin';REF=R/'tools/reference/mario_tank_rules_1101_v1.inc'
def bundle(path):
 b=scoped_load(path)
 # Unlike the host's deduplicated debug, original ca65 exports/imports repeat
 # names. Always retain the actual value-bearing definition for plain RAM ABI.
 for line in path.with_suffix('.dbg').read_text().splitlines():
  if not line.startswith('sym\t')or'val='not in line:continue
  q=dict(re.findall(r'(\w+)=("[^"\n]*"|[^,\n]+)',line));b['syms'][q['name'].strip('"')]=q
 return b
def main():
 orig=bundle(B/'donor-source.nes');image,identity=donor();assert orig['raw']==image
 names=['PlayerStatus','GameEngineSubroutine','RemovedTile','StarInvincibleTimer','FrameCounter','ObjectOffset','PowerUpType','Enemy_SprAttrib','R2']
 aliases=dict(MtCheckClimb='CheckForClimbMTiles',MtGetPlayerColors='GetPlayerColors',MtSetPRout='SetPRout')
 bind='\n'.join('.export'+('zp'if int(orig['syms'][n]['val'],0)<256 else'')+' '+n+'\n'+n+'=$'+format(address(orig,n),'x')for n in names)+'\n'
 bind+='\n'.join('.export '+n+'\n'+n+'=$'+format(address(orig,v),'x')for n,v in aliases.items())+'\n'
 (O/'rule-bindings.s').write_text(bind);(O/'rules.s').write_text('.setcpu "6502"\n.include "'+REF.name+'"\n');(O/'rules.cfg').write_text('MEMORY { C:start=$c000,size=$1000,type=ro,file=%O; }\nSEGMENTS { MT_RULES:load=C,type=ro; }\n')
 commands=[]
 def run(cmd):
  guard=validate(cmd,O,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);commands.append(dict(command=cmd,guard=guard,returncode=p.returncode,stderr=p.stderr));assert not p.returncode,p.stderr
 for name in['rule-bindings','rules']:run([str(CC/'ca65.exe'),'-g','-I',str(REF.parent),'-o',str(O/(name+'.o')),str(O/(name+'.s'))])
 run([str(CC/'ld65.exe'),'-C',str(O/'rules.cfg'),'-o',str(O/'rules.bin'),'--dbgfile',str(O/'rules.dbg'),'-Ln',str(O/'rules.lbl'),str(O/'rules.o'),str(O/'rule-bindings.o')])
 (O/'rules-assembly.json').write_text(json.dumps(commands,indent=2)+'\n');new=bundle(O/'rules.bin')
 base=[0]*65536
 for addr,bank in[(0x8000,6),(0xa000,0),(0xc000,5),(0xe000,7)]:base[addr:addr+8192]=image[16+bank*8192:16+(bank+1)*8192]
 code=(O/'rules.bin').read_bytes();base[0xc000:0xc000+len(code)]=code
 def put(m,**fields):
  for n,v in fields.items():m[address(orig,n)]=v
 class Tracked(list):
  def __init__(self):super().__init__(base);self.changed=set()
  def __setitem__(self,i,v):
   assert isinstance(i,int);self.changed.add(i);super().__setitem__(i,v)
 measured={}
 def execute(name,*,a=0,x=5,y=7,p=0x31,values=None,stop=None):
  m=Tracked();put(m,**(values or{}));c=MPU(memory=m,pc=address(new,name)if name.startswith('Mt')else address(orig,name));c.a=a;c.x=x;c.y=y;c.p=p;c.sp=224;c.stPushWord(0x5aff)
  if not name.startswith('Mt')and 0xa000<=c.pc<0xc000:
   bank=(location(orig,name)-16)//8192
   list.__setitem__(m,slice(0xa000,0xc000),image[16+bank*8192:16+(bank+1)*8192])
  low=c.sp
  for _ in range(5000):
   if c.pc==((stop if isinstance(stop,int)else address(orig,stop))if stop else 0x5b00):break
   assert m[c.pc]!=0,(name,hex(c.pc));c.step();low=min(low,c.sp)
  else:raise AssertionError(('Bounded leaf',name,hex(c.pc)))
  if not stop:assert c.sp==224
  q=measured.setdefault(name,dict(calls=0,max_cycles=0,max_stack_bytes_including_JSR=0));q['calls']+=1;q['max_cycles']=max(q['max_cycles'],c.processorCycles);q['max_stack_bytes_including_JSR']=max(q['max_stack_bytes_including_JSR'],224-low)
  state=(c.a,c.x,c.y,c.p&~16);changed={i:m[i]for i in m.changed if i<0x8000 and m[i]!=base[i]and not 0x100<=i<0x200}
  return state,changed,m
 def pair(before,after,**kw):
  x=execute(before,**kw);y=execute(after,**kw);assert x[:2]==y[:2],(before,after,kw,x[:2],y[:2]);return y
 def boundary(name,stops,*,a=0,p=0x31,values=None):
  # Run the real released program until its named policy exits. Source
  # CheckForSpeedrunMode intentionally discards a JSR return; trapping before
  # effects/native continuation avoids pretending that is a safe host ABI.
  m=Tracked();put(m,**(values or{}));c=MPU(memory=m,pc=address(orig,name));c.a=a;c.x=5;c.y=7;c.p=p;c.sp=224;c.stPushWord(0x5aff)
  exits={address(orig,label):action for label,action in stops.items()};exits[0x5b00]=2
  for _ in range(128):
   if c.pc in exits:return exits[c.pc]
   assert m[c.pc]!=0,(name,hex(c.pc));c.step()
  raise AssertionError(('Bounded original policy',name,hex(c.pc)))
 exact_tile=image[location(orig,'TileChecks'):location(orig,'DoSpeedrunModeStuff')]
 assert code[:len(exact_tile)]==exact_tile
 tile_cases=0;protected=[]
 for value,p in itertools.product(range(256),[0x30,0x31,0x70,0x71,0xb0,0xb1,0xf0,0xf1]):
  result=pair('TileChecks','MtTileChecks',a=value,p=p);tile_cases+=1
  if p==0x30 and result[0][3]&1:protected.append(value)
 # Compare adapted action against actual original selector, trapping only its
 # declared destructive/native boundaries before their effects execute.
 action_cases=0
 for tile,status,engine,removed in itertools.product(range(256),range(3),[7,8],[0,1]):
  values=dict(PlayerStatus=status,GameEngineSubroutine=engine,RemovedTile=removed)
  want=boundary('CheckForSpeedrunMode',dict(GoToCheckSideMTilesJmp=1,GoToCheckSideMTilesPlaJmp=0,CheckSideMTiles=0,DoSpeedrunModeStuff=3),a=tile,values=values)
  assert want==(1 if tile in protected else 0 if status!=2 or engine!=8 else 2 if removed else 3)
  result=execute('MtCellAction',a=tile,values=values)[0];assert result[0]==want and bool(result[3]&1)==(want==3);action_cases+=1
 contact_cases=0
 for status,star,p in itertools.product(range(3),range(256),[0x30,0x31,0x70,0xf1]):
  values=dict(PlayerStatus=status,StarInvincibleTimer=star)
  want=boundary('EColl',dict(ShellOrBlockDefeat=1,HandlePECollisions=0),p=p,values=values)
  result=execute('MtContactPolicy',p=p,values=values)[0]
  assert bool(result[3]&1)==bool(want)==(status==2 or star!=0);contact_cases+=1
 injury_cases=0
 for status,p in itertools.product(range(256),[0x30,0x31,0x70,0x71,0xb0,0xb1,0xf0,0xf1]):
  before=execute('ForceInjury',p=p,values=dict(PlayerStatus=status),stop=address(orig,'ForceInjury')+5)
  after=execute('MtInjuryBlocked',p=p,values=dict(PlayerStatus=status))
  assert before[:2]==after[:2];injury_cases+=1
 pickup_cases=0
 for kind,frame,attr,p in itertools.product(range(4),range(256),[0,32,64,128,224,255],[0x30,0x71]):
  values=dict(PowerUpType=kind,FrameCounter=frame,ObjectOffset=5)
  # Source caller provides the existing enemy attribute field at native slot5.
  base[address(orig,'Enemy_SprAttrib')+5]=attr
  before=execute('DrawPowerUp',p=p,values=values,stop='DrawPowerUp::SkipPaletteCycle')
  after=execute('MtPickupCycle',p=p,values=values)
  assert before[:2]==after[:2],(kind,frame,attr,p,before[:2],after[:2]);pickup_cases+=1
 base[address(orig,'Enemy_SprAttrib')+5]=0
 upgrade_cases=0
 for status,player,area,offset,p in itertools.product(range(3),range(2),range(4),[0,32],[0x30,0x71,0xf1]):
  pair('Shroom_Flower_PUp','MtCollectUpgrade',p=p,values=dict(PlayerStatus=status,CurrentPlayer=player,AreaType=area,BackgroundColorCtrl=0,VRAM_Buffer1_Offset=offset,ObjectOffset=5));upgrade_cases+=1
 # User-requested worn-boot palette helper is explicitly an adaptation.
 glow_cases=0
 for status,frame,attr in itertools.product(range(3),range(16),[0,1,2,3,32,64,128,255]):
  result=execute('MtWearBootsFlash',a=attr,values=dict(PlayerStatus=status,FrameCounter=frame))[0]
  expected=attr if status!=2 else(attr&224)|((frame>>1)&3)
  assert result[0]==expected;glow_cases+=1
 # The donor uses the same native movement code with and without boots.
 # This compares actual source CPU outputs; it does not assume the initial
 # author's imported base is byte-identical to some later SMB1Base version.
 physics_cases=0
 for state,swim,lr,ab,speed in itertools.product(range(4),range(2),range(4),[0,64,128,192],[0,8,9,15,16,24,25,27,28,32,33,40,255]):
  values=dict(Player_State=state,SwimmingFlag=swim,Left_Right_Buttons=lr,A_B_Buttons=ab,PreviousA_B_Buttons=0,Player_XSpeedAbsolute=speed,Player_CollisionBits=3,Player_Y_Speed=252,Player_Y_HighPos=1,Player_Y_Position=128,AreaType=1,GameEngineSubroutine=8,Player_MovingDir=1,PlayerFacingDir=1)
  one=execute('PlayerPhysicsSub',values=dict(values,PlayerStatus=1));two=execute('PlayerPhysicsSub',values=dict(values,PlayerStatus=2))
  one[1].pop(address(orig,'PlayerStatus'),None);two[1].pop(address(orig,'PlayerStatus'),None)
  assert one[:2]==two[:2],('Boot physics',values,one[:2],two[:2]);physics_cases+=1
 # Original asset lives in misc1KB bank at8x16 pair56/58 (tile79/7B).
 bank=address(orig,'CHR_MISC');at=16+65536+bank*1024+0x380;boots=image[at:at+64]
 assert boots==(S/'chr/sprites_misc.chr').read_bytes()[0x380:0x3c0]
 (O/'boots-pickup.chr').write_bytes(boots)
 report=dict(passed=True,donor_sha256=identity['donor_sha256'],source_commit=COMMIT,rules_bytes=len(code),new_RAM_allocated=False,caller_admits_identity=True,
  exact_original_TileChecks_bytes=len(exact_tile),tile_AXYP_RAM_cases=tile_cases,cell_policy_cases=action_cases,contact_policy_cases=contact_cases,pickup_palette_AXYP_RAM_cases=pickup_cases,upgrade_AXYP_RAM_cases=upgrade_cases,worn_flash_adaptation_cases=glow_cases,
  injury_prefix_AXYP_RAM_cases=injury_cases,
  same_native_physics_status1_vs2_AXYP_RAM_cases=physics_cases,
  measured_leaf_bounds=measured,measured_bounds_scope='Observed over stated aggregate inputs, including direct donor callback execution. Not actual host Main/ISR reserve, universal worst case, code placement or scratch ownership qualification.',
  policy_oracles='Actual reproduced donor CPU: CheckForSpeedrunMode to named native/destructive exits; EColl to ShellOrBlockDefeat/HandlePECollisions. Explicit returning cell ABI and contact carry result compared to original controlflow.',
  source_pickup_palette_period_frames=2,source_pickup_palette_cycle=[0,1,2,3],status_enum=dict(small=0,big=1,boots=2),protected_metatiles=protected,
  pickup_CHR=dict(physical_bank=bank,offset=0x380,bytes=64,sha256=sha(boots),left_pair=[0x38,0x39],right_pair=[0x3a,0x3b]),
  hooks=dict(side='PlayerBGCollision two side probes -> CheckForSpeedrunMode; returning MtCellAction replaces unsafe TXS caller discard.',head='PlayerHeadCollision/BrickShatter: no vertical bounce for Tank; source clears the cell and runs native debris/SFX/50point owner.',enemy='EColl routes native ShellOrBlockDefeat for Tank, preserving actual prechecks and native defeat/score/SFX.',injury='ForceInjury ignores status2 for Tank; timer/pits still retain native death ownership.',upgrade='Native mushroom growth0->1, next mushroom/flower1->2; source pickup erase/1000/SFX remains outer owner.',pickup='PowerUpType1 uses authentic LightningBoots icon and source2-frame palette cycle; source rise is1px per4 frames, as native flower.'),
  integration_limits=['No roster/Main/O edits or native qualification. Returning cell-policy ABI is an explicit adaptation; actual terrain/effect/queue mapping is still an integration job.','Worn-boot-only flash helper is the user-requested adaptation; masked boot art/OAM layer and palette budget still need integration. Donor source does not contain that separate worn-boot effect.','No movement speed/jump constants were substituted: source native PlayerMovementSubs/PlayerPhysicsSub/ImposeFriction/MovePlayerHorizontally remain intact; ordinary boots status2 still passes the original native fireball eligibility check.','Do not copy donor RemovedTile79A or brick arrays into host memory blindly. The component imports caller-owned fields and callbacks; no RAM/CHR/code placement lease is granted.'],
  bindings={str(REF.relative_to(R)):sha(REF.read_bytes()),str(Path(__file__).relative_to(R)):sha(Path(__file__).read_bytes()),'author_ROM':sha(image),'component':sha(code)})
 (O/'rules-CPU-controls.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k not in['hooks','integration_limits','bindings','protected_metatiles']}))
if __name__=='__main__':main()
