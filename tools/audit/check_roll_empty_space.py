"""Check compiled Roll broad phases against native probes/contact execution.

Authored CPU cases cover page/viewport seams, every terrain row, excluded
actors and wrapped native enemy boxes. A possible solid always hands back to
the original block routine. A skipped enemy test must also miss in the real
native enemy loop/collision core. No native damage or reward is stubbed into
a passing outcome: execution stops at the actual contact/handoff labels.
"""
from pathlib import Path
import argparse,functools,hashlib,itertools,json,re
from check_roll_renderer import Memory,NesMPU


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
 rom=args.rom.resolve();raw=rom.read_bytes();fields={kind:[]for kind in('seg','sym','scope')}
 for line in rom.with_suffix('.dbg').read_text().splitlines():
  kind,_,tail=line.partition('\t')
  if kind not in fields:continue
  fields[kind].append({k:(v.strip('"')if v.startswith('"')else int(v,0)if re.fullmatch(r'(?:0x[0-9A-Fa-f]+|\d+)',v)else v)for k,v in re.findall(r'(\w+)=("[^"]*"|[^,]+)',tail)})
 segments={z['id']:z for z in fields['seg']};scopes={z['id']:z for z in fields['scope']}
 labels={m[2]:int(m[1],16)for line in rom.with_suffix('.lbl').read_text().splitlines()if(m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
 @functools.lru_cache(None)
 def symbol(name,scope=None):
  choices=[z for z in fields['sym']if z['name']==name and'val'in z and(scope is None or scopes.get(z.get('scope'),{}).get('name')==scope)]
  if scope is None:choices=[z for z in choices if z.get('type')!='imp']
  assert len(choices)==1,(name,scope,choices)
  return choices[0]
 @functools.lru_cache(None)
 def address(name,scope=None):return symbol(name,scope)['val']
 @functools.lru_cache(None)
 def bank(name,scope=None):return(segments[symbol(name,scope)['seg']]['ooffs']-16)//8192
 @functools.lru_cache(None)
 def native_byte(name,index):
  sym=symbol(name,'MegaManWeapons');seg=segments[sym['seg']]
  return raw[seg['ooffs']+sym['val']-seg['start']+index]
 def signed(v):return(v+128)%256-128
 for n in('RlEnemyEnvelope',):labels[n]=address(n)
 base=bytearray(65536)
 for s in segments.values():
  if s['name']=='SMCCODE':base[s['start']:s['start']+s['size']]=raw[s['ooffs']:s['ooffs']+s['size']]
 stop=0x5b00;sp=0xd9
 def seed(kind,facing,x,page,y):
  memory=bytearray(base)
  for n,v in(('SelectedCharacter',9),('RlVariant',1),('MmSlot',0),('MmBulletType',kind),('MmBulletDir',facing),('MmBulletX',x),('MmBulletPage',page),('MmBulletY',y)):
   memory[labels[n]]=v
  memory[0x101+sp]=(stop-1)&255;memory[0x102+sp]=(stop-1)>>8
  return memory
 def execute(memory,name,scope=None,handoffs=()):
  target=address(name,scope);a_bank=bank(name,scope);memory=bytearray(memory);memory[labels['CurrentBank']]=a_bank|128;memory[labels['CurrentBankC']]=121|128
  bus=Memory(raw,memory,{0x8000:bank('GetBlockBufferAddr'),0xa000:a_bank,0xc000:121,0xe000:bank('FarCallCommon')})
  cpu=NesMPU(memory=bus);cpu.pc=target;cpu.sp=sp;cpu.x=0;cpu.p=0x24
  for _ in range(12000):
   if cpu.pc==stop:return'clear',bus
   if any(cpu.pc==pc and bus.banks[cpu.pc&0xe000]==bnk for pc,bnk in handoffs):return'handoff',bus
   cpu.step()
  raise AssertionError(('Unbounded broad phase',name,hex(cpu.pc)))
 block_handoff=[(address('Blocks','MegaManWeapons'),bank('Blocks','MegaManWeapons'))]
 enemy_handoff=[(address('Enemies','MegaManWeapons'),bank('Enemies','MegaManWeapons'))]
 contact=[(address('EnemyHit','MegaManWeapons'),bank('EnemyHit','MegaManWeapons'))]
 terrain_checks=terrain_clear=enemy_checks=enemy_clear=0
 for kind,facing,x,page,y,pattern in itertools.product((1,3),(1,2),(0,4,8,15,16,127,247,255),(0,1,254,255),range(256),range(3)):
  memory=seed(kind,facing,x,page,y);tiles=[0,0x23,0x26,0xc2,0xc3]
  for i in range(416):memory[labels['Block_Buffer_1']+i]=0 if pattern==0 else tiles[i%5]if pattern==1 else(0x51 if i%7==0 else tiles[i%5])
  expected=False
  for horizontal,vertical in itertools.product(('ShotRight','ShotLeft'),('ShotTop','ShotBottom')):
   xx=(page*256+x+signed(native_byte(horizontal,kind-1))*(1 if facing==1 else-1))&65535
   yy=(y+signed(native_byte(vertical,kind-1)))&255
   if 32<=yy<240:
    column=((xx>>8)&1)*208+(xx&255)//16;row=(yy&240)-32
    expected|=memory[labels['Block_Buffer_1']+column+row]not in tiles
  outcome,bus=execute(memory,'RlBlocks',handoffs=block_handoff)
  assert not expected or outcome=='handoff',('Broad phase skipped solid',kind,facing,x,page,y,pattern)
  assert bus.data[labels['MmBulletType']]==kind
  assert bus.data[labels['Block_Buffer_1']:labels['Block_Buffer_1']+416]==memory[labels['Block_Buffer_1']:labels['Block_Buffer_1']+416]
  assert not any(a in(labels['Square1SoundQueue'],labels['Square2SoundQueue'])for a,v in bus.writes)
  terrain_checks+=1;terrain_clear+=outcome=='clear'
 for kind,facing,x,shot_y,enemy_x,enemy_y,actor_case in itertools.product((1,3),(1,2),(0,128,255),(0,31,32,96,176,224,233,239,248,255),(0,128,248),(0,96,176,224,231,232,248,255),range(5)):
  memory=seed(kind,facing,x,0,shot_y)
  for n,v in(('Enemy_Flag',1),('Enemy_ID',6),('Enemy_State',0),('Enemy_X_Position',enemy_x),('Enemy_Y_Position',enemy_y),('EnemyOffscrBitsMasked',0)):
   memory[labels[n]]=v
  if actor_case==1:memory[labels['Enemy_State']]=2 # Squashed Goomba.
  elif actor_case==2:memory[labels['Enemy_Flag']]=128 # Native duplicate.
  elif actor_case==3:memory[labels['EnemyOffscrBitsMasked']]=1
  elif actor_case==4:memory[labels['Enemy_ID']]=0x2d # Native Bowser kind.
  outcome,bus=execute(memory,'RlEnemies',handoffs=enemy_handoff)
  if outcome=='clear':
   original,_=execute(memory,'Enemies','MegaManWeapons',contact)
   assert original=='clear',('Broad phase skipped actual native contact',kind,facing,x,shot_y,enemy_x,enemy_y,actor_case)
   enemy_clear+=1
  else:assert bus.data[labels['RlEnemyEnvelope']]==0,'Refresh the envelope after a native contact path'
  assert bus.data[labels['MmBulletType']]==kind
  enemy_checks+=1
 report=dict(passed=True,rom_sha256=hashlib.sha256(raw).hexdigest(),terrain_cases=terrain_checks,terrain_empty_returns=terrain_clear,enemy_cases=enemy_checks,enemy_native_misses_proved=enemy_clear,scope=__doc__)
 out=args.output.resolve();out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))


if __name__=='__main__':main()
