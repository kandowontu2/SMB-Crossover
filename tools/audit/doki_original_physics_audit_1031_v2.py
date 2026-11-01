"""Actual local DDP/SMB2U/installed S2 leaf CPU physics lineage, read-only."""
from pathlib import Path
import hashlib,json,re,sys,traceback
from py65.devices.mpu6502 import MPU
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location,Memory as CartMemory
P=R/'build/doki-original-rebuild-1031-v1';S=P/'source';O=R/'build/doki-original-physics-audit-1031-v2'
US=R.parent/'mario in kid icarus/vendor/smb2';INST=R/'build/contra-force-world-chr-publisher-1031-v1/joint/candidate.nes'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 assert not O.exists();O.mkdir();d=dict(passed=False,source_CPU=True,native=False,source_changes=False)
 try:
  # Source reconstruction is intentionally retained as a whole-file negative.
  # All CPU instructions below come from the actual extracted local donor.
  rec=json.loads((P/'reproduction.json').read_text());assert not rec['passed']
  by={q['name']:q for q in rec['disk_files']};original=Path(by['MAIN-PRO']['extracted']).read_bytes();rebuilt=(P/'assembled/main_pro.bin').read_bytes();temp=Path(by['TEMP-PRG']['extracted']).read_bytes()
  values={}
  for line in(P/'assembled/original.dbg').read_text().splitlines():
   if line.startswith('sym\t'):
    z=dict(x.split('=',1)for x in line[4:].split(',')if '='in x)
    if 'val'in z:values.setdefault(z['name'].strip('"'),set()).add(int(z['val'],0))
  def D(n):assert len(values[n])==1,(n,values[n]);return next(iter(values[n]))
  # Entire original player action, jump/gravity, horizontal policy and both
  # Q4 integrators form a single verified original byte slice.
  first,last=D('player_proc_normal'),D('actor_dophysics')+60
  assert original[first-0x6000:last-0x6000]==rebuilt[first-0x6000:last-0x6000]
  d['actual_original_player_slice']=dict(CPU=[first,last],disk_offsets=[by['MAIN-PRO']['data_offset']+first-0x6000,by['MAIN-PRO']['data_offset']+last-0x6000],bytes=last-first,sha256=hashlib.sha256(original[first-0x6000:last-0x6000]).hexdigest(),source_assembled_bytes_exact=True)
  usraw=Path('C:/NES/Super Mario Bros. 2 (USA).nes').read_bytes();assert hashlib.sha256(usraw).hexdigest()=='41300bc4942a8a4f9b53148b404dd5cae3dd708ebdd9b617888d290a51a83e43'
  assert (US/'bin/native.nes').read_bytes()[16:]==usraw[16:]
  UL={}
  for p in(US/'bin').glob('native.nes.*.nl'):
   for line in p.read_text().splitlines():
    m=re.match(r'\$([0-9a-fA-F]+)#([^#]+)#',line)
    if m:UL[m[2]]=int(m[1],16)
  b=qualified(INST);assert sha(INST)=='a4410264ffccc7ce44e3b5ead1da639428cfa0594c94b2f63fa99fb4feab5b38'
  class Flat:
   def __init__(self,kind):
    self.m=bytearray(65536)
    if kind=='DDP':self.m[0x6000:0xe000]=original;self.m[0x6000:0x65ff]=temp
    else:self.m[0x8000:0xc000]=usraw[16:16+16384];self.m[0xc000:]=usraw[16+7*16384:16+8*16384]
   def __getitem__(self,p):return self.m[p]
   def __setitem__(self,p,v):self.m[p]=v&255
  keys=['stats','x','xh','xf','y','yh','yf','vx','vy','held','fresh','charge','holding','quicksand','float','frame','air','duck','timer','state','animation','held_index','obj_type','obj_state','lift_timer']
  DN=['map_player_props_working','pos_x_lo_player','pos_x_hi_player','subpix_x_player','pos_y_lo_player','pos_y_hi_player','subpix_y_player','veloc_x_player','veloc_y_player','joypad_p1h','joypad_p1','timer_player_crouch_jump','player_item_held','player_quicksand_state','timer_player_jump_float','frame_count','player_airborne','player_crouch','timer_player_state','proc_id_player','player_ani_frame','player_item_held_id','obj_id_actor','proc_id_actor','timer_actor_held']
  UN=['CharacterStatsRAM','PlayerXLo','PlayerXHi','PlayerXSubpixel','PlayerYLo','PlayerYHi','PlayerYSubpixel','PlayerXVelocity','PlayerYVelocity','Player1JoypadHeld','Player1JoypadPress','CrouchJumpTimer','HoldingItem','QuicksandDepth','JumpFloatTimer','byte_RAM_10','PlayerInAir','PlayerDucking','PlayerStateTimer','PlayerState','PlayerAnimationFrame','ObjectBeingCarriedIndex','ObjectType','EnemyState','ObjectBeingCarriedTimer']
  HN=['S2Stats','S2X','S2Page','S2XF','S2Y','S2YPage','S2YF','S2VX','S2VY','S2Held','S2Fresh','S2Charge','S2Holding','S2Quicksand','S2Float','S2Clock','S2Air','S2Duck','S2Timer','S2State','S2Animation','S2HeldIndex','S2ObjectType','S2ObjectState','S2ObjectLift']
  configs={
   'DDP':dict(fields=dict(zip(keys,[D(n)for n in DN])),func={n:D(t)for n,t in dict(jump='player_jump_start',gravity='player_gravity_calc',X='actor_dophysics',Y='actor_dophysics_y',action='player_action_start',lift='player_proc_lift').items()}),
   'USA':dict(fields=dict(zip(keys,[UL[n]for n in UN])),func={n:UL[t]for n,t in dict(jump='PlayerStartJump',gravity='PlayerGravity',X='ApplyPlayerPhysics',Y='ApplyPlayerPhysicsY',action='sub_BANK0_8C1A',lift='HandlePlayerState_Lifting').items()}),
   'S2':dict(fields=dict(zip(keys,[address(b,n)for n in HN])),func={n:address(b,t)for n,t in dict(jump='S2N8C99',gravity='S2N8CD9',X='S2N8EA6',Y='S2N8EA4',action='S2N8C1A',lift='S2N8A87').items()})}
  # Resolve aliases from the actual original symbol names, never numeric guesses.
  mapids=[0,1,3,2];hostids=[0,3,1,2];usnames=['Mario','Princess','Luigi','Toad'];names=['Imajin','Lina','Mama','Papa']
  ptr=D('map_player_props_list')-0x6000;offsets=list(temp[ptr:ptr+4]);data=D('map_player_props_data')-0x6000
  stats=[]
  for v,name in enumerate(names):
   dv=list(temp[data+offsets[v]:data+offsets[v]+23]);up=UL[usnames[v]+'Stats'];uv=list(usraw[16+5*16384+up-0x8000:16+5*16384+up-0x8000+23]);hp=location(b,'S2OriginalStats')+hostids[v]*23;hv=list(b['raw'][hp:hp+23]);assert uv==hv
   dif=[dict(offset=i,DDP=a,USA=z)for i,(a,z)in enumerate(zip(dv,uv))if a!=z]
   assert dif==([dict(offset=i,DDP=dv[i],USA=uv[i])for i in range(6,12)]if v==2 else[])
   stats.append(dict(id=v,name=name,US_character=usnames[v],host_variant=hostids[v],Doki_CPU=0x6000+data+offsets[v],donor_offset=by['TEMP-PRG']['data_offset']+data+offsets[v],Doki=dv,USA=uv,installed_S2=hv,differences=dif))
  def make(kind,v):
   if kind=='S2':
    m=CartMemory(b);pc=configs[kind]['func']['jump'];physical=(location(b,'S2N8C99')-16)//8192;m.page((pc-0x8000)//8192,physical)
   else:m=Flat(kind)
   st=stats[v]['Doki'if kind=='DDP'else'USA'];at=configs[kind]['fields']['stats']
   for i,value in enumerate(st):m[at+i]=value
   return m
  def put(m,kind,**fields):
   for n,v in fields.items():m[configs[kind]['fields'][n]]=v
  def get(m,kind,n):return m[configs[kind]['fields'][n]]
  def call(m,kind,n):
   c=MPU(memory=m,pc=configs[kind]['func'][n]);c.sp=253;c.p=0x24;m[0x1fe]=0xfe;m[0x1ff]=0x7f
   for i in range(10000):
    if c.pc==0x7fff:assert c.sp==255;return c
    assert m[c.pc]!=0,('BRK',kind,n,hex(c.pc));c.step()
   raise AssertionError(('CPU bound',kind,n,hex(c.pc)))
  jumps=[]
  for v in range(4):
   for context in range(8):
    for hold in[1,2,8,25,60,180]:
     row=dict(id=v,context_RCI=context,hold=hold,engines={});traces={}
     for kind in configs:
      m=make(kind,v);put(m,kind,y=180,yh=0,vx=8 if context&4 else 0,charge=60 if context&2 else 0,holding=context&1,held=128);c=call(m,kind,'jump');launch=get(m,kind,'vy');trace=[]
      for tick in range(240):
       put(m,kind,held=128 if tick<hold else 0,frame=tick&255)
       if tick:call(m,kind,'gravity')
       call(m,kind,'Y');y=get(m,kind,'y')+256*get(m,kind,'yh');y=y-65536 if y>=32768 else y
       trace.append([tick,y,get(m,kind,'yf'),get(m,kind,'vy'),get(m,kind,'float')])
       if tick>1 and y>=180:break
      traces[kind]=trace;row['engines'][kind]=dict(launch=launch,apex_rise=180-min(r[1]for r in trace),return_updates=len(trace),trace_sha256=hashlib.sha256(json.dumps(trace).encode()).hexdigest())
     assert traces['USA']==traces['S2'],row
     if v!=2:assert traces['DDP']==traces['USA'],row
     jumps.append(row)
  d.update(passed=True,stats=stats,jump_cases=len(jumps),jumps=jumps,source_functions=configs,scope='Actual extracted DV1 instructions, original payload-exact SMB2U and actual mapped installed-a441 S2 pure jump/gravity/Q4 leaves. Declared collisionless from-rest fixtures; not native full-controller/terrain or a playable Doki port. Full disassembly reproduction remains negative for4 unrelated file variants.')
 except Exception as e:d.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  refs=[Path(__file__),P/'reproduction.json',P/'assembled/original.dbg',P/'assembled/original.lbl',P/'assembled/main_pro.bin',Path(by['MAIN-PRO']['extracted']),Path(by['TEMP-PRG']['extracted']),INST,INST.with_suffix('.dbg'),R/'tools/smb2_roster_source_v1.py',US/'src/prg-0-1.asm',S/'src/obj/player/state.s',S/'src/obj/player/state_base.s',S/'data/actor/player_props.s']
  d['bindings']={str(p.resolve()):sha(p)for p in refs};p=O/'audit.json';p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8',newline='\n');print(json.dumps(dict(path=str(p),sha256=sha(p),passed=d['passed'],error=d.get('error'))),flush=True)
if __name__=='__main__':main()
