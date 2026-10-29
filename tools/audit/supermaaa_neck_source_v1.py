"""Bounded author-source/actual-ROM neck audit. No native or integration edits."""
from pathlib import Path
import hashlib,itertools,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
from verify_native_relocation import NesMPU
from py65.disassembler import Disassembler
S=R/'build/source-acquisition/super-maaa-author-2026-10-29/source'
O=R/'build/supermaaa-neck-audit-v1'
ROM=Path('C:/NES/the stash/super_maaaaaaaaaaaaaaaaaaaaaaaa..nes')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
COMMANDS=[]

class OriginalMemory(bytearray):
 # These bounded source arenas make no mapper/PPU/controller accesses.
 # Fail instead of silently treating an unmodeled hardware access as RAM.
 def __getitem__(self,key):
  if isinstance(key,int):assert not 0x800<=key<0x8000,('unmodeled original bus read',hex(key))
  return super().__getitem__(key)
 def __setitem__(self,key,value):
  if isinstance(key,int):assert 0<=key<0x800,('unmodeled original bus write',hex(key),value)
  return super().__setitem__(key,value)

def execute(args):
 p=subprocess.run(args,cwd=R,capture_output=True,text=True);assert not p.returncode,(args,p.stdout,p.stderr)
 COMMANDS.append(args)

def labels(path):
 return{m[2]:int(m[1],16)for line in path.read_text().splitlines()if(m:=re.fullmatch(r'al ([\da-fA-F]+) \.(\S+)',line))}

def asm(name,text,start=0xe000,defines=None):
 p=O/(name+'.s');p.write_text('.include "common.inc"\n.segment "PROBE"\n'+text)
 cfg=O/(name+'.cfg');cfg.write_text('MEMORY { ZP:start=$0000,size=$100,type=rw,file=""; SP:start=$0100,size=$100,type=rw,file=""; OAM:start=$0200,size=$100,type=rw,file=""; RAM:start=$0300,size=$500,type=rw,file=""; OUT:start=$'+f'{start:04x}'+',size=$2000,type=ro,file=%O; }\nSEGMENTS { ZEROPAGE:load=ZP,type=zp; STACK:load=SP,type=bss; OAM:load=OAM,type=bss; BSS:load=RAM,type=bss; PROBE:load=OUT,type=ro; }\n')
 args=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-I',str(S/'inc'),'-o',str(O/(name+'.o'))]
 for n,v in(defines or{}).items():args+=['-D',f'{n}={v}']
 execute(args+[str(p)])
 execute([str(R/'tools/Windows/cc65/bin/ld65.exe'),'-C',str(cfg),'-o',str(O/(name+'.bin')),'-Ln',str(O/(name+'.lbl')),str(O/'memory.o'),str(O/(name+'.o'))])
 return(O/(name+'.bin')).read_bytes(),labels(O/(name+'.lbl'))

class Cpu(NesMPU):
 # py65 omits undocumented AXS. This is the exact source's sole $CB #$FC,
 # an unsigned (A&X)-immediate with A unchanged and C/N/Z from the result.
 def step(self):
  if self.memory[self.pc]==0xcb:
   value=(self.a&self.x)-self.memory[(self.pc+1)&65535]
   self.x=value&255;self.p=(self.p&~(self.CARRY|self.NEGATIVE|self.ZERO))|(self.CARRY if value>=0 else 0)|(self.NEGATIVE if self.x&128 else 0)|(self.ZERO if self.x==0 else 0)
   self.pc=(self.pc+2)&65535;self.processorCycles+=2
   return self
  return super().step()

def memory(raw,bank=1):
 m=bytearray(65536)
 for k,at in[(6,0x8000),(bank,0xa000),(3,0xc000),(7,0xe000)]:m[at:at+8192]=raw[16+k*8192:16+(k+1)*8192]
 return OriginalMemory(m)

def run(m,pc,stop=0x5b00,a=0):
 c=Cpu(memory=m,pc=pc);c.a=a;c.sp=253;c.p=0x30;c.stPushWord(stop-1);trace=[];mn=253
 for _ in range(20000):
  if c.pc==stop:return c,trace,mn
  mn=min(mn,c.sp);assert m[c.pc]not in[0,255],('invalid original opcode',hex(c.pc));trace.append(c.pc);c.step()
 raise AssertionError(('bound',hex(c.pc)))

def main():
 assert not(O/'proof.json').exists()or'--replace-unbound-draft'in sys.argv;O.mkdir(exist_ok=True)
 acquisition=json.loads((S.parent/'acquisition.json').read_text())
 for f in acquisition['files']:assert sha(f['path'])==f['sha256']
 raw=ROM.read_bytes();assert sha(ROM)=='2a415a731495aa6ca3e4e18c9e12abbc382c5dac5daf19f50cfcd0a78d862f27'
 assert raw[16+3*8192:16+6*8192]==bytes([255])*24576
 execute([str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-I',str(S/'inc'),'-o',str(O/'memory.o'),str(S/'src/memory.s')])
 reset=(S/'src/reset.s').read_text();player=(S/'src/player.s').read_text();collision=(S/'src/collision.s').read_text();game=(S/'src/gamecore.s').read_text()
 draw=reset[reset.index('.proc DrawNeck'):reset.index('.endproc',reset.index('.proc DrawNeck'))+len('.endproc')]
 queue=player[player.index('.proc QueueDrawPlayerNeck'):player.index('.endproc',player.index('.proc QueueDrawPlayerNeck'))+len('.endproc')]
 code,L=asm('draw-probe','.export DrawNeck\n'+draw)
 prefix=code[:7];hits=[i for i in range(16,65552)if raw[i:i+len(prefix)]==prefix];assert len(hits)==1,hits
 off=hits[0];native=0xe000+(off-16)%8192;assert(off-16)//8192==7
 code,L=asm('draw-native','.export DrawNeck\n'+draw,native)
 assert raw[off:off+len(code)]==code,('author DrawNeck does not match ROM',hex(native))
 qcode,Q=asm('queue-probe','.export QueueDrawPlayerNeck\n'+queue)
 hits=[i for i in range(16,65552)if raw[i:i+len(qcode)]==qcode];assert len(hits)==1,hits
 qoff=hits[0];qpc=0xa000+(qoff-16)%8192;assert(qoff-16)//8192==1
 # Exact table+block-reader assembly, linked at its actual original base.
 text=collision[collision.index('BlockBuffer_X_Adder:'):collision.index('FireballBGCollision:')]
 bcode,B=asm('block-probe','.export BlockBuffer_X_Adder,BlockBuffer_Y_Adder,BlockBufferColli_Head,BlockBufferColli_Feet,BlockBufferColli_Side\n'+text)
 hits=[i for i in range(16,65552)if raw[i:i+60]==bcode[:60]];assert len(hits)==1,hits
 boff=hits[0];bpc=0x8000+(boff-16)%8192;assert(boff-16)//8192==6
 bcode,B=asm('block-native','.export BlockBuffer_X_Adder,BlockBuffer_Y_Adder,BlockBufferColli_Head,BlockBufferColli_Feet,BlockBufferColli_Side\n'+text,bpc)
 assert raw[boff:boff+len(bcode)]==bcode,('author block reader differs',hex(bpc))
 timer=game[game.index('RunGameTimer:'):game.index('ProcessWhirlpools:')]
 targets=['DigitsMathRoutine','PrintStatusBarNumbers','ForceInjury']
 tcode,T=asm('timer-probe','.export RunGameTimer\n'+timer,defines={n:0 for n in targets})
 d=Disassembler(NesMPU(memory=list(tcode)+[0]*(65536-len(tcode))));at=0;operands=[]
 while at<len(tcode):
  size,_=d.instruction_at(at)
  if tcode[at]in[0x20,0x4c]and tcode[at+1:at+3]==bytes(2):operands.append(at+1)
  at+=size
 assert len(operands)==len(targets)
 mask={i for at in operands for i in[at,at+1]}
 hits=[i for i in range(16,65552-len(tcode))if all(j in mask or raw[i+j]==v for j,v in enumerate(tcode))];assert len(hits)==1,hits
 toff=hits[0];assert(toff-16)//8192==6;tpc=0x8000+(toff-16)%8192
 targets={n:raw[toff+at]+256*raw[toff+at+1]for n,at in zip(targets,operands)}
 tcode,T=asm('timer-native','.export RunGameTimer\n'+timer,tpc,targets)
 assert raw[toff:toff+len(tcode)]==tcode
 body=player[player.index('RenderPlayerSub:'):player.index('PlayerGfxHandler:')]
 rcode,V=asm('body-probe','.export RenderPlayerSub,PlayerGraphicsTable\n'+body,0xa000,{'DrawOneSpriteRow':0})
 hits=[i for i in range(16,65552)if raw[i:i+10]==rcode[:10]];assert len(hits)==1,hits
 roff=hits[0];assert(roff-16)//8192==1;rpc=0xa000+(roff-16)%8192
 call=rcode.index(bytes([0x20,0,0]));rowpc=raw[roff+call+1]+256*raw[roff+call+2]
 rcode,V=asm('body-native','.export RenderPlayerSub,PlayerGraphicsTable\n'+body,rpc,{'DrawOneSpriteRow':rowpc})
 assert raw[roff:roff+len(rcode)]==rcode
 side=collision[collision.index('PlayerSideNeckCheck:'):collision.index('BasePlayerSideCheck:')]+'\nBasePlayerSideCheck:\n'
 defs=dict(BLOCK_BUFFER_ADDER_NECK_OFFSET=28,BlockBufferColli_Side=B['BlockBufferColli_Side'],CheckForCoinMTiles=0,HandleCoinMetatile=0)
 scode,W=asm('side-probe','.export PlayerSideNeckCheck,BasePlayerSideCheck\n'+side,defines=defs)
 hits=[i for i in range(16,65552)if raw[i:i+8]==scode[:8]];assert len(hits)==1,hits
 soff=hits[0];assert(soff-16)//8192==6;spc=0x8000+(soff-16)%8192
 calls=[j for j in range(len(scode)-2)if scode[j]in[0x20,0x4c]and scode[j+1:j+3]==bytes(2)]
 assert len(calls)==2
 for n,j in zip(['CheckForCoinMTiles','HandleCoinMetatile'],calls):defs[n]=raw[soff+j+1]+256*raw[soff+j+2]
 scode,W=asm('side-native','.export PlayerSideNeckCheck,BasePlayerSideCheck\n'+side,spc,defs)
 assert raw[soff:soff+len(scode)]==scode
 rows=[]
 for length,gfx,face,used,body_y in itertools.product([0,1,7,8,15,16,80,159,160],[0,8,16,24,32,80,96,176,184,192,200],[1,2],[0,20,55],[100,200]):
  m=memory(raw);m[L['PlayerNeckLength']]=length;m[L['PlayerGfxOffset']]=gfx;m[L['PlayerFacingDir']]=face
  for j in range(64):m[0x200+j*4]=248
  # Native source player OAM occupies1..8. Populate exact head rows so this
  # arena measures only the genuine neck routine, not a claimed full Main.
  for j in range(1,9):m[0x200+j*4]=body_y+((j-1)//2)*8;m[0x203+j*4]=96+((j-1)%2)*8;m[0x202+j*4]=0x20
  for j in range(used):m[0x200+(9+j)*4]=120
  before=bytes(m[0x200:0x300]);c,tr,mn=run(m,native)
  changed=[j for j in range(9,64)if m[0x200+j*4]!=before[j*4]]
  assert all(before[j*4]>=248 for j in changed)
  assert all(bytes(m[0x200+j*4:0x204+j*4])==before[j*4:j*4+4]for j in range(9,9+used))
  rows.append([length,gfx,face,used,len(changed),body_y,c.processorCycles,mn])
 qrows=[]
 for length,high,y,small,engine,hidden in itertools.product([0,1,160],[0,1,2],[15,239,240,255],[0,1],[8,11],[False,True]):
  m=memory(raw);m[Q['PlayerNeckLength']]=length;m[Q['Player_Y_HighPos']]=high;m[Q['Player_Y_Position']]=y;m[Q['PlayerSize']]=small;m[Q['GameEngineSubroutine']]=engine;m[Q['Player_SprDataOffset']]=4;m[0x208]=248 if hidden else 100
  c,tr,mn=run(m,qpc);qrows.append([length,high,y,small,engine,hidden,m[Q['ShouldDrawNeck']],c.processorCycles])
 brows=[]
 for length,y,entry,index in itertools.product([0,1,8,32,80,160],[16,31,32,64,176,240],['BlockBufferColli_Head','BlockBufferColli_Feet','BlockBufferColli_Side'],[0,7,14]):
  m=memory(raw);m[B['PlayerNeckLength']]=length;m[B['Player_Y_Position']]=y;m[B['Player_X_Position']]=64
  for i in range(416):m[B['Block_Buffer_1']+i]=0xc4
  c=Cpu(memory=m,pc=B[entry]);c.sp=253;c.p=0x30;c.y=index;c.stPushWord(0x5aff)
  for _ in range(2000):
   if c.pc==0x5b00:break
   c.step()
  else:raise AssertionError('block bound')
  assert m[B['PlayerNeckTemp']]==0
  brows.append([length,y,entry,index,c.a,m[2],m[4],c.processorCycles])
 chrraw=raw[65552:];assert chrraw==(S/'chr/lanky_mario.chr').read_bytes()
 source_body_rows=[]
 for frame,face,length in itertools.product(range(26),[1,2],[0,8,80,160]):
  m=memory(raw)
  for n,v in dict(PlayerGfxOffset=frame*8,Player_Rel_XPos=96,Player_Rel_YPos=200,PlayerFacingDir=face,Player_SprDataOffset=4,PlayerNeckLength=length).items():m[V[n]]=v
  for j in range(64):m[0x200+j*4]=248
  c,tr,mn=run(m,rpc,a=4)
  d,dt,dm=run(m,native)
  source_body_rows.append([frame,face,length,c.processorCycles,d.processorCycles,min(mn,dm),bytes(m[0x204:0x224]).hex()])
 side_rows=[]
 for length,tile in itertools.product([0,8,16,80,160],[0,0xc4,0xc2]):
  m=memory(raw)
  for n,v in dict(PlayerNeckLength=length,Player_Y_Position=200,Player_X_Position=96,OperMode=1).items():m[W[n]]=v
  for i in range(416):m[W['Block_Buffer_1']+i]=tile
  c,tr,mn=run(m,spc,stop=W['BasePlayerSideCheck'])
  assert m[W['Player_X_Position']]==96,('neck side must not invent wall push',length,tile)
  side_rows.append([length,tile,c.processorCycles,m[W['CoinTallyFor1Ups']],m[W['VRAM_Buffer1_Offset']],mn])
 # Read authentic26x8 source tile records and exact source head-row offsets.
 # This is a packing proposal only: no new CHR file or page allocation.
 tiles=raw[roff+V['PlayerGraphicsTable']-rpc:roff+V['PlayerGraphicsTable']-rpc+208]
 heads=code[-26:];assert len(tiles)==208 and len(heads)==26
 assert chrraw[252*16:253*16]==bytes(16)
 sets=[];body_parts=[]
 for frame in range(26):
  v=tiles[frame*8:(frame+1)*8];head=heads[frame]//8;pairs={(16,16),(16,252)};parts=0
  for col in range(2):
   pairs.add((v[head*2+col],252));parts+=1;row=0
   while row<4:
    if row==head or v[row*2+col]==252:row+=1;continue
    pairs.add((v[row*2+col],v[(row+1)*2+col]if row+1<4 and row+1!=head else 252));parts+=1;row+=2
  if frame in[5,6,7]:pairs.add((49,252))
  if frame in[17,18,19]:pairs.add((70,252))
  sets.append(pairs);body_parts.append(parts)
 bins=[];members=[]
 for frame,pairs in sorted(enumerate(sets),key=lambda row:-len(row[1])):
  options=[(len(pairs-current),i)for i,current in enumerate(bins)if len(pairs|current)<=32]
  if not options:bins.append(set(pairs));members.append([frame])
  else:_,i=min(options);bins[i]|=pairs;members[i].append(frame)
 assert len(bins)==3 and all(sets[frame]<=bins[i]for i,frames in enumerate(members)for frame in frames)
 packing=dict(proposed_only=True,no_allocations_or_CHR_written=True,all26_source_records_and_kick_tiles=True,shared_window0_body_neck_per_pose=True,both_faces_use_source_Hflip=True,needed_1KB_pages=3,stored_16high_pairs=[len(x)for x in bins],actual_pattern_payload_bytes=sum(len(x)*32 for x in bins),pose_groups=members,maximum_body_parts=max(body_parts),maximum_paired_neck_parts=11,maximum_body_plus_neck_parts=max(body_parts)+11,original_8high_neck_maximum=21)
 trows=[]
 for length,scenario in itertools.product([0,1,159,160],['tick','title','entry','death','below','pending','timeup']):
  m=memory(raw)
  for n,v in dict(OperMode=1,GameEngineSubroutine=8,Player_Y_HighPos=1,GameTimerCtrlTimer=0,PlayerNeckLength=length).items():m[T[n]]=v
  m[T['GameTimerDisplay']]=4
  for n,v in({'title':{'OperMode':0},'entry':{'GameEngineSubroutine':7},'death':{'GameEngineSubroutine':11},'below':{'Player_Y_HighPos':2},'pending':{'GameTimerCtrlTimer':1},'timeup':{'GameTimerDisplay':0}}.get(scenario,{})).items():m[T[n]]=v
  c,tr,mn=run(m,tpc)
  assert m[T['PlayerNeckLength']]==(min(160,length+1)if scenario=='tick'else length)
  if scenario=='tick':assert m[T['GameTimerCtrlTimer']]==24 and list(m[T['GameTimerDisplay']:T['GameTimerDisplay']+3])==[3,9,9]
  trows.append([length,scenario,m[T['PlayerNeckLength']],m[T['GameTimerCtrlTimer']],c.processorCycles,mn])
 refs=[]
 for bank in[0,1,2,6,7]:
  base=0x8000 if bank==6 else 0xe000 if bank==7 else 0xa000
  data=raw[16+bank*8192:16+(bank+1)*8192]
  for at in range(8190):
   if data[at]in[0xad,0x8d,0xed,0x4e]and data[at+1:at+3]==bytes([L['PlayerNeckLength']&255,L['PlayerNeckLength']>>8]):refs.append([bank,hex(base+at),data[at:at+3].hex()])
 proof=dict(passed=True,source_CPU_only=True,native_run=False,source_commit=acquisition['commit'],full_ROM_source_build_NOT_claimed=True,original_ROM=sha(ROM),original_CHR_matches_authored_lanky_mario_exactly=True,actual_routines=dict(DrawNeck=dict(bank=7,PC=hex(native),bytes=len(code),source_assembled_full_bytes_exact=True),QueueDrawPlayerNeck=dict(bank=1,PC=hex(qpc),bytes=len(qcode),source_assembled_full_bytes_exact=True),block_readers=dict(bank=6,PC=hex(bpc),bytes=len(bcode),source_assembled_full_bytes_exact=True),RunGameTimer=dict(bank=6,PC=hex(tpc),bytes=len(tcode),source_assembled_full_bytes_exact=True,actual_original_callees=targets)),original_RAM={n:hex(L[n])for n in['PlayerNeckLength','PlayerNeckTemp','ShouldDrawNeck','PlayerNeckXOffset']},neck_absolute_reference_census=refs,DrawNeck=dict(cases=len(rows),CPU=[min(z[-2]for z in rows),max(z[-2]for z in rows)],minimum_SP=min(z[-1]for z in rows),maximum_emitted_segments=max(z[4]for z in rows),never_overwrites_active_original_slots=True,rows=rows),queue=dict(cases=len(qrows),rows=qrows),block_readers=dict(cases=len(brows),rows=brows),timer=dict(cases=len(trows),rows=trows,includes_real_original_digit_decrement_and_status_command=True,no_source_Button_control=True),commands=COMMANDS,bindings={str(p.resolve()):sha(p)for p in[Path(__file__),ROM,S.parent/'acquisition.json',S/'src/reset.s',S/'src/player.s',S/'src/collision.s',S/'src/gamecore.s',S/'src/memory.s',S/'chr/lanky_mario.chr',R/'tools/audit/verify_native_relocation.py']})
 proof['actual_routines'].update(RenderPlayerSub=dict(bank=1,PC=hex(rpc),bytes=len(rcode),source_assembled_full_bytes_exact=True,actual_DrawOneSpriteRow=hex(rowpc)),PlayerSideNeckCheck=dict(bank=6,PC=hex(spc),end=hex(W['BasePlayerSideCheck']),bytes=len(scode),source_assembled_full_bytes_exact=True,actual_native_callees=defs))
 proof.update(source_body_then_neck=dict(cases=len(source_body_rows),rows=source_body_rows),actual_side_neck=dict(cases=len(side_rows),rows=side_rows,all_native_coin_writers_executed=True,stopped_before_original_body_side_collision=True),packing_proposal=packing,static_bus_validity=dict(all_CPU_arenas_reject_unmodeled_RAM_mirrors_hardware_reads_and_writes=True,no_mapper_writes=True,no_PPU_or_controller_accesses=True))
 (O/'proof.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,actual_routines=proof['actual_routines'],DrawNeck_cases=len(rows),DrawNeck_CPU=proof['DrawNeck']['CPU'],queue_cases=len(qrows),block_cases=len(brows),body_cases=len(source_body_rows),side_rows=side_rows,packing=packing)))
if __name__=='__main__':main()
