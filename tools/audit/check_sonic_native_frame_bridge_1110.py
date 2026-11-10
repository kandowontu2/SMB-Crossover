"""Actual6502 original-prefix/constructor/native-frame transactions, stdout."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
from unittest.mock import patch

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/reference'))
import sonic_sms_native_frame_bridge_1110 as B
import check_sonic_native_swept_selector_1110 as S
import check_sonic_relocated_core_1110 as D

STOP=0x5b00
PIN='96e09ab1b67a7c75b89d49219e8e529582b9a05b7dd82dd3cd570fdb239212bd'


class Memory(S.Memory):
 def __init__(self,p,attributes):
  super().__init__(p['selector'],attributes)
  self.frame=p;self.allow_fixture=False
  start=p['code_half_open'][0]
  list.__setitem__(self,slice(start,start+len(p['image'])),p['image'])
 def __setitem__(self,at,value):
  assert isinstance(at,int)
  if self.active:
   own=0xc000<=at<0xc119 or B.SNAPSHOT<=at<B.SNAPSHOT+0xb8 or B.RECORD<=at<B.RECORD+26
   assert own or 0x17b<=at<=0x1e0 or at in self.frame['selector']['shape']['core']['SMC_operands'],('Frame unowned write',hex(at))
   self.writes.append((at,value&255))
  list.__setitem__(self,at,value&255)


def invoke(m,pc,*,stop=STOP,limit=16000):
 c=S.NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=0,0,0,0x30,224
 c.stPushWord(STOP-1);low=c.sp;m.active=True
 try:
  for _ in range(limit):
   if c.pc==stop:break
   assert 0xa000<=c.pc<0xbfe0,hex(c.pc)
   assert m[c.pc],('Native frame BRK',hex(c.pc))
   low=min(low,c.sp);c.step()
  else:raise AssertionError(('Frame bound',hex(c.pc)))
 finally:m.active=False
 assert not m.fixture_reads,'Native frame read retired fixture world'
 if stop==STOP:assert c.sp==224
 return c,low


def old_after_step(core,*,original=False):
 q=core['original']if original else core
 start=q['symbols']['OrdinaryFrame'];end=q['symbols']['ComposedMotionStep']
 points=[]
 for i,item in enumerate(q['items']):
  pc=q['boundaries'].get(i,-1)
  if start<=pc<end and item.get('op')=='JSR'and item.get('operand')=='PositionStep':points.append(pc+3)
 assert len(points)==1
 return points[0]


class PrefixCPU(D.RealCPU):
 program=None
 attributes=None
 cases=0
 cycles=[]
 minimum=255
 after_step=None
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);self.initial=self.memory.copy();self.checked=False
 def step(self):
  result=super().step()
  p=type(self).program;core=p['selector']['shape']['core']
  if not self.checked and self.pc==type(self).after_step:
   self.checked=True;m=Memory(p,type(self).attributes)
   state=bytearray(self.initial[:256]);state[0xb4]=1
   for ptr in(0x8c,0xae):
    v=state[ptr]|state[ptr+1]<<8
    state[ptr:ptr+2]=D.translate_pointer(core,v).to_bytes(2,'little')
   m.reset(state)
   c,minimum=invoke(m,p['symbols']['SonicNativeOrdinaryFrame'],stop=p['symbols']['NativeFrameAfterPosition'])
   wanted=bytearray(self.memory[:0xb4])
   for ptr in(0x8c,0xae):
    v=wanted[ptr]|wanted[ptr+1]<<8
    wanted[ptr:ptr+2]=D.translate_pointer(core,v).to_bytes(2,'little')
   assert bytes(m[0xc000:0xc0b4])==wanted,('Full original prefix state',type(self).cases,
    [(hex(i),wanted[i],m[0xc000+i])for i in range(0xb4)if wanted[i]!=m[0xc000+i]][:12])
   assert (c.a,c.x,c.y,c.p,c.sp)==(self.a,self.x,self.y,self.p,self.sp),('Original prefix AXYP/SP',type(self).cases)
   assert not m.buffer_reads,'Prefix must precede all native geometry'
   type(self).cases+=1;type(self).cycles.append(c.processorCycles);type(self).minimum=min(type(self).minimum,minimum)
  return result


def prefix_matrix(p,attributes):
 PrefixCPU.program=p;PrefixCPU.attributes=attributes;PrefixCPU.cases=0;PrefixCPU.cycles=[];PrefixCPU.minimum=255
 PrefixCPU.after_step=old_after_step(p['selector']['shape']['core'],original=True)
 with patch.object(D,'DualCPU',PrefixCPU):q=D.replay_frozen(p['selector']['shape']['core'])
 assert PrefixCPU.cases==7297
 return dict(cases=PrefixCPU.cases,episodes=len(q['episodes']),full_original180_state_and_AXYP_SP_exact=True,
  actual_donor_Z80_instructions=q['donor_instructions'],prefix_cycles=[min(PrefixCPU.cycles),max(PrefixCPU.cycles)],
  minimum_SP=PrefixCPU.minimum,scope='Original7297-case/40episode generator and donor Z80 remain intact. New native prefix stops immediately after original PositionStep, before geometry.')


def donor_constructor(rom,tilex,tiley):
 # Execute the actual bank0 constructor bytes, without its level-list caller.
 # Only opcodes in235E..239B are admitted; no arithmetic rewrite is the oracle.
 mem=bytearray(65536);mem[:0x8000]=rom[:0x8000]
 ix,hl,de,bc=0xd3fc,0xc000,26,0x5473
 alt=[0x82b7,0x1549,0x8f21];a=0;sp=0xff00;pc=0x235e
 mem[hl],mem[hl+1]=tilex,tiley;mem[ix:ix+26]=bytes([0x9d])*26
 for _ in range(160):
  op=mem[pc];pc+=1
  if op==0xdd:
   op=mem[pc];pc+=1
   if op==0x77:mem[ix+mem[pc]]=a;pc+=1
   elif op==0x74:mem[ix+mem[pc]]=hl>>8;pc+=1
   elif op==0x75:mem[ix+mem[pc]]=hl&255;pc+=1
   elif op==0xe5:
    sp-=1;mem[sp]=ix>>8;sp-=1;mem[sp]=ix&255
   elif op==0x19:ix=(ix+de)&65535
   else:raise AssertionError(('Ctor DD',hex(pc-2),hex(op)))
  elif op==0x7e:a=mem[hl]
  elif op==0xd9:hl,de,bc,alt=alt[0],alt[1],alt[2],[hl,de,bc]
  elif op==0x6f:hl=(hl&0xff00)|a
  elif op==0x26:hl=(mem[pc]<<8)|(hl&255);pc+=1
  elif op==0x29:hl=(hl*2)&65535
  elif op==0x23:hl=(hl+1)&65535
  elif op==0xe1:hl=mem[sp]|mem[sp+1]<<8;sp+=2
  elif op==0x11:de=mem[pc]|mem[pc+1]<<8;pc+=2
  elif op==0x19:hl=(hl+de)&65535
  elif op==0x06:bc=mem[pc]<<8|(bc&255);pc+=1
  elif op==0xaf:a=0
  elif op==0x77:mem[hl]=a
  elif op==0x10:
   displacement=mem[pc];pc+=1;bc=((bc-0x100)&0xff00)|(bc&255)
   if bc>>8:pc=(pc+(displacement-256 if displacement&128 else displacement))&65535
  elif op==0xc9:
   assert pc==0x239c and ix==0xd416 and hl==0xc002
   return bytes(mem[0xd3fc:0xd416])
  else:raise AssertionError(('Ctor opcode',hex(pc-1),hex(op)))
 raise AssertionError('Original constructor bound')


def constructors(p,attributes):
 rom=D.Frozen.DONOR.read_bytes();assert sha256(rom).hexdigest()==D.Frozen.SMS_PIN
 m=Memory(p,attributes);count=0;cost=[];minimum=255
 allowed=set(B.MAPPED_ZERO)|set(range(0xc070,0xc076))
 for x in range(256):
  for y in range(256):
   state=bytearray((i*31+x+y)&255 for i in range(256));state[0xb4]=1;m.reset(state)
   m[B.TILE_X],m[B.TILE_Y]=x,y
   before=bytes(m[0xc000:0xc100]);expected=donor_constructor(rom,x,y)
   c,low=invoke(m,p['symbols']['SonicOriginalObjectConstructor'])
   assert bytes(m[B.RECORD:B.RECORD+26])==expected
   assert bytes(m[0xc070:0xc076])==expected[1:7]
   assert all(m[a]==0 for a in B.MAPPED_ZERO)
   assert all(m[a]==before[a-0xc000]for a in range(0xc000,0xc100)if a not in allowed)
   count+=1;cost.append(c.processorCycles);minimum=min(minimum,low)
 return dict(cases=count,actual_Z80_constructor_half_open=[0x235e,0x239c],
  full26byte_record_and_mapped_object_fields_exact=True,other_globals_preserved=True,
  cycles=[min(cost),max(cost)],minimum_SP=minimum)


def floor_domain(m,x):
 host=m.frame['selector']['point']['host'];left=max(0,(x-128)//16);end=left+24
 values={'ColumnSets':255,'AreaParserTaskNum':0,'CurrentPageLoc':end//16,'CurrentColumnPos':end&15,
  'BlockBufferColumnPos':end&31,'ScreenLeftPage':left//16,'ScreenLeftX':(left&15)*16}
 for n,v in values.items():m[host[n]]=v
 list.__setitem__(m,slice(0x300,0x4a0),bytes([255])*416)
 for col in range(left,end):
  for row in range(13):m[S.pointer(col*16,32+row*16)]=0x54 if row==11 else 0


def episodes(p,attributes):
 rows=[];minimum=255;cost=[]
 for rolling in(False,True):
  m=Memory(p,attributes);m.reset(bytearray(256));m[0xc0b4]=1;m[B.TILE_X],m[B.TILE_Y]=1,5
  invoke(m,p['symbols']['SonicOriginalObjectConstructor'])
  ground,jumps,heights,xmax=0,0,set(),0
  for tick in range(200):
   if tick<24:pad=0
   elif tick<80:pad=1
   elif tick<100:pad=5 if rolling else 129
   elif tick<140:pad=129 if rolling else 1
   elif tick<180:pad=1
   else:pad=0
   m[0xc0a8],m[0xc092]=pad,tick&255
   floor_domain(m,S.word(m,0xc071))
   c,low=invoke(m,p['symbols']['SonicNativeOrdinaryFrame'])
   assert c.p&1 and m[B.STATUS]==0,('Native floor episode unavailable',rolling,tick,c.a)
   ground+=bool(m[0xc030]&128);jumps+=m[0xc05e]==1;heights.add(m[0xc042]);xmax=max(xmax,S.word(m,0xc071))
   minimum=min(minimum,low);cost.append(c.processorCycles)
   assert m[0xc041]==24 and m[0xc042]in(24,32)
  assert ground>40 and jumps>=1 and xmax>300
  if rolling:assert heights=={24,32}
  rows.append(dict(rolling=rolling,frames=200,grounded=ground,jump_events=jumps,max_x=xmax,
   final_x=S.word(m,0xc071),final_y=S.word(m,0xc074),heights=sorted(heights)))
 return dict(episodes=rows,cycles=[min(cost),max(cost)],minimum_SP=minimum,
  terrain='Explicit native-buffer flat floor fixtures with consistent queryable parser state; not a native stage/parser/controller route')


def rollback(p,attributes):
 count=0
 for kind in('invalid_parser','unsupported_first','unsupported_after_horizontal','vertical_outside'):
  m=Memory(p,attributes);m.reset(bytearray(256));m[0xc0b4]=1;m[B.TILE_X],m[B.TILE_Y]=2,5
  invoke(m,p['symbols']['SonicOriginalObjectConstructor'])
  m[0xc041],m[0xc042],m[0xc0a0],m[0xc0a1],m[0xc0a2]=24,32,255,0,0
  S.put24(m,0xc070,64<<8);S.put24(m,0xc073,(96 if kind!='vertical_outside'else 220)<<8)
  floor_domain(m,64)
  host=p['selector']['point']['host']
  if kind=='invalid_parser':m[host['ColumnSets']]=0
  elif kind=='unsupported_first':m[S.pointer(80,112)]=0x67
  elif kind=='unsupported_after_horizontal':
   m[S.pointer(80,112)]=0x54
   m[S.pointer(64+12,128)]=0x67
  elif kind=='vertical_outside':pass
  actor=bytes(m[0xc000:0xc0b4]);smc=[m[x]for x in p['selector']['shape']['core']['SMC_operands']]
  m.writes=[]
  c,_=invoke(m,p['symbols']['SonicNativeOrdinaryFrame'])
  assert not c.p&1 and m[B.STATUS],('Missing explicit frame failure',kind)
  assert bytes(m[0xc000:0xc0b4])==actor and [m[x]for x in p['selector']['shape']['core']['SMC_operands']]==smc
  if kind=='unsupported_after_horizontal':
   assert any(at==0xc071 and value==56 for at,value in m.writes),'Missing genuine horizontal clip before vertical failure'
  count+=1
 return dict(cases=count,all_original_actor_state_and_four_SMC_bytes_restored=True,
  unavailable_is_not_empty=True,includes_rollback_after_real_horizontal_clip=True)


def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
 args=ap.parse_args();assert args.output.resolve().is_relative_to(R/'build')and not args.output.exists()
 # The nightly can advance while this source-only task runs. Reconstruct the
 # exact already-tested96 parent in memory rather than silently repin it.
 import check_ff_head_corner_1110_v2 as FF
 raw=FF.proposal(S.Prior.ROM.read_bytes())[0]
 assert sha256(raw).hexdigest()==PIN
 attributes=raw[16+127*8192+0xf36:16+127*8192+0xf36+256]
 p=B.build()
 result=dict(passed=True,files_written=0,ROM_written=False,image_bytes=len(p['image']),image_SHA256=p['image_SHA256'],
  code=p['code_half_open'],snapshot=p['snapshot_half_open'],object_record=p['record_half_open'],remaining=p['remaining_before_header'],
  prefix=prefix_matrix(p,attributes),constructor=constructors(p,attributes),native_floor=episodes(p,attributes),rollback=rollback(p,attributes),
  scope='Actual complete ordinary-frame source prefix/motor + native swept contacts and object ctor in RAM. Test-only snapshots/context; no native hooks, lifecycle/clock lease, art/effects/raw43 admission or ROM.')
 print(json.dumps(result,sort_keys=True),flush=True);assert not args.output.exists()


if __name__=='__main__':main()
