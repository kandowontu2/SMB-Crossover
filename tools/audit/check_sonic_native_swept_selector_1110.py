"""Stdout actual6502 native-buffer swept selection/contact qualification."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/reference'))
import sonic_sms_native_swept_selector_1110 as B
import check_sonic_native_shape_contact_1110 as Prior
from verify_native_relocation import NesMPU

ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
PIN='96e09ab1b67a7c75b89d49219e8e529582b9a05b7dd82dd3cd570fdb239212bd'
STOP=0x5b00
FROZEN={
 'tools/reference/sonic_sms_native_sweep_witness_1110.py':'03b737cd008af3996860a2a0d34b99db02df1de85f846e003640e201e104f5ce',
 'tools/reference/sonic_sms_native_shape_contact_1110.py':'ceea5507300f07bbe1da0339a109af90067ac1b37c8a0f92d6b2488c8ec9c602',
 'tools/reference/sonic_sms_native_point_read_1110.py':'fc135d40cb35d115d4854db00b29943b57ee9a454b7cff58f65e2a2e6ddf8eff'}


class Memory(Prior.Memory):
 def __init__(self,p,attributes):
  view=dict(p,core=p['shape']['core'])
  super().__init__(view,attributes)
  self.selector=p
  for block in(p['shape'],p['witness']):
   start=block['code_half_open'][0]
   list.__setitem__(self,slice(start,start+len(block['image'])),block['image'])
 def reset(self,state):
  assert len(state)==256,'Full private-state fixture required'
  super().reset(state)
  assert len(self)==65536


def invoke(m,pc,*,flags=0x21):
 c=NesMPU(memory=m,pc=pc);c.a,c.x,c.y,c.p,c.sp=85,73,109,flags,224
 m.active=True
 try:
  c.stPushWord(STOP-1);low=c.sp
  for _ in range(4000):
   if c.pc==STOP:break
   assert 0xa000<=c.pc<0xbfe0,('Escape',hex(c.pc))
   assert m[c.pc],('BRK',hex(c.pc));low=min(low,c.sp);c.step()
  else:raise AssertionError(('Instruction bound',hex(c.pc)))
 finally:m.active=False
 assert c.sp==224 and not m.fixture_reads
 m.minimum_SP=min(m.minimum_SP,low)
 return c.a,bool(c.p&1),c.processorCycles,low,(c.a,c.x,c.y,c.p&0xef,c.sp)


def put24(m,at,value):
 for i in range(3):m[at+i]=(value>>(8*i))&255
def word(m,at):return m[at]|m[at+1]<<8


def full_state(post):
 state=bytearray(Prior.STATE_CANARY);state[:0xb4]=post;state[0xb4]=1
 return state


def pointer(x,y):return 0x300+((x>>8)&1)*208+((y-32)//16)*16+((x>>4)&15)


def setup(m,axis,negative,height,page,phase,fraction,velocity_fraction,*,flags=0xc4,leading_base=None):
 p=m.selector;edge=0 if negative else(24 if axis==0 else height)
 leading=(page*256+80+phase)if axis==0 else((96 if leading_base is None else leading_base)+phase)
 coordinate=leading-edge
 velocity=(0xfff000 if negative else 0x1000)|velocity_fraction
 state=Prior.base_state(height=height,x=((coordinate if axis==0 else page*256+64)<<8)|fraction,
  y=((coordinate if axis==1 else 96)<<8)|(fraction^255),
  vx=velocity if axis==0 else 0,vy=velocity if axis==1 else 0,flags=flags)
 m.reset(state);m.setup_domain(page)
 list.__setitem__(m,slice(0x300,0x4a0),bytes(416))
 capture=p['witness']['symbols']['SonicSweepCapture'];invoke(m,capture)
 invoke(m,p['shape']['core']['symbols']['PositionStep'])
 old=word(m,p['witness']['fields']['OldXLo']+3*axis)
 new=word(m,0xc071+3*axis)
 start=(old+edge)&0xfff0;end=(new+edge)&0xfff0
 cells=list(range(start,end+(-16 if negative else 16),-16 if negative else 16))
 orth=(word(m,0xc074)+height//2)if axis==0 else(word(m,0xc071)+12)
 return dict(axis=axis,negative=negative,edge=edge,cells=cells,orth=orth,
             post=bytes(m[0xc000:0xc0b4]),fraction=bytes((m[0xc070],m[0xc073])))


def classify(tile,attribute,axis):
 if attribute&2:return 7,None
 if tile in(0x23,0xc2,0xc3)or not attribute&1:return 0,False
 if tile in(0x5f,0x60,0x67,0x68)or axis==0 and tile in(0x1c,0x6b):return 7,None
 return 0,True


def oracle(m,q):
 host=m.selector['point']['host'];phase=m[host['AreaParserTaskNum']]
 if m[host['ColumnSets']]!=255:return 2,[],None
 if phase>=8:return 3,[],None
 col,page=m[host['CurrentColumnPos']],m[host['CurrentPageLoc']]
 if col>=16 or m[host['BlockBufferColumnPos']]!=(page&1)*16+col:return 4,[],None
 first=m[host['ScreenLeftPage']]*16+(m[host['ScreenLeftX']]>>4)
 end=page*16+col+int(phase in(1,2,3,5,6,7))
 if not 1<=end-first<=32:return 5,[],None
 reads=[]
 for cell in q['cells']:
  x,y=(cell,q['orth'])if q['axis']==0 else(q['orth'],cell)
  if not 32<=y<240:return 1,reads,None
  if not first<=x//16<end:return 6,reads,None
  at=pointer(x,y);tile=m[at];attr=m[0xef36+tile];reads.append(at)
  status,solid=classify(tile,attr,q['axis'])
  if status:return status,reads,None
  if solid:
   if cell<q['edge']:return 10,reads,None
   return 0,reads,cell
 return 0,reads,None


def case(m,reference,q):
 p=m.selector;status,reads,hit=oracle(m,q)
 post=bytes(m[0xc000:0xc0b4])
 m.buffer_reads=[];m.attribute_reads=[];m.writes=[]
 out=invoke(m,p['symbols']['SonicSweptHorizontal'if q['axis']==0 else'SonicSweptVertical'])
 assert out[:2]==(status,status==0),(q,status,out)
 assert m[p['shape']['context']['Status']]==status
 assert m.buffer_reads==reads,(q,reads,m.buffer_reads)
 assert len(m.attribute_reads)==len(reads)
 if status:
  assert bytes(m[0xc000:0xc0b4])==post,('Unavailable actor/core write',q,status)
  assert not any(at<0xc0b4 and at>=0xc000 for at,value in m.writes)
  assert m[p['shape']['context']['Kind']]==0
  return status,out[2],hit
 state=full_state(post);axis=q['axis'];negative=q['negative'];edge=q['edge']
 if hit is not None:
  value=hit-edge;state[0x71+3*axis:0x73+3*axis]=value.to_bytes(2,'little')
  shape=(hit&16)+(16 if negative else 0)
 else:shape=128
 state[0x80:0x83]=bytes((shape,edge,0));state[0x30]&=0xbf if axis==0 else 0x7f
 reference.reset(state)
 invoke(reference,p['shape']['core']['symbols']['HorizontalContact'if axis==0 else'VerticalContact'])
 assert bytes(m[0xc000:0xc0b4])==bytes(reference[0xc000:0xc0b4]),('Original contact mismatch',q,hit)
 assert bytes((m[0xc070],m[0xc073]))==q['fraction'],'Lost source fraction'
 kind=0 if hit is None else axis*2+int(negative)+1
 assert m[p['shape']['context']['Kind']]==kind
 if hit is not None:
  boundary=hit+(16 if negative else 0)
  assert word(m,0xc071+3*axis)==boundary-edge
  velocity=0xc020+64*axis
  assert bytes(m[velocity:velocity+3])==bytes(3)
  if axis==1 and not negative:assert m[0xc030]&128,'Skipped actual ContactGround'
 return status,out[2],hit


def geometry(p,attributes):
 m,reference=Memory(p,attributes),Memory(p,attributes);count=0;probes=Counter();cost=[];earliest=Counter()
 for axis in(0,1):
  for negative in(False,True):
   for height in(24,32):
    for page in(0,1):
     for phase in range(16):
      for fraction in(0,1,127,255):
       for vf in(0,1,127,255):
        for choice in(-1,0,1,2):
         q=setup(m,axis,negative,height,page,phase,fraction,vf,flags=count&255)
         if choice>=len(q['cells']):continue
         if choice>=0:
          cell=q['cells'][choice];x,y=(cell,q['orth'])if axis==0 else(q['orth'],cell)
          m[pointer(x,y)]=0x54
         status,cycles,hit=case(m,reference,q)
         assert status==0
         probes[len(m.buffer_reads)]+=1;cost.append(cycles);earliest[choice]+=1;count+=1
  print(json.dumps(dict(phase='geometry',axis=axis,cases=count)),flush=True)
 return dict(cases=count,queries=dict(probes),selected_index=dict(earliest),
             cycles=[min(cost),max(cost)],minimum_SP=m.minimum_SP)


def tiles(p,attributes):
 m,reference=Memory(p,attributes),Memory(p,attributes);count=0;statuses=Counter();stops=Counter()
 for axis in(0,1):
  for negative in(False,True):
   for height in(24,32):
    for page in(0,1):
     for tile in range(256):
      for choice in(0,1,2):
       q=setup(m,axis,negative,height,page,15,255,255,flags=(tile*37)&255)
       if choice>=len(q['cells']):continue
       cell=q['cells'][choice];x,y=(cell,q['orth'])if axis==0 else(q['orth'],cell)
       m[pointer(x,y)]=tile
       status,_,hit=case(m,reference,q)
       statuses[status]+=1;stops[len(m.buffer_reads)]+=1;count+=1
 return dict(cases=count,statuses=dict(statuses),queries=dict(stops),all256_actual_attributes=True)


def failures(p,attributes):
 m,reference=Memory(p,attributes),Memory(p,attributes);host=p['point']['host'];counts=Counter()
 for axis in(0,1):
  for label,changes in(
   ('initial',{host['ColumnSets']:0}),('phase',{host['AreaParserTaskNum']:8}),
   ('cursor',{host['BlockBufferColumnPos']:255}),('capacity',{host['ScreenLeftPage']:8}),
   ('distant_alias',{host['ScreenLeftPage']:8,host['CurrentPageLoc']:9}),
  ):
   q=setup(m,axis,False,32,0,15,255,255)
   for at,value in changes.items():m[at]=value
   status,_,_=case(m,reference,q);assert status;counts[label]+=1
  q=setup(m,axis,False,32,0,15,255,255)
  # Actual left-column interval excludes the first cell, despite ring aliases.
  m[host['ScreenLeftX']]=128
  status,_,_=case(m,reference,q);assert status;counts['left_exclusion']+=1
  # An empty starting cell followed by unsupported data may not publish an
  # empty contact/clear flags before returning unavailable.
  q=setup(m,axis,False,32,0,15,255,255)
  cell=q['cells'][1];x,y=(cell,q['orth'])if axis==0 else(q['orth'],cell)
  m[pointer(x,y)]=0x67
  status,_,_=case(m,reference,q);assert status==7;counts['late_unsupported_atomic']+=1
  q=setup(m,axis,False,32,0,15,255,255,leading_base=209 if axis else None)
  if axis==0:
   m[host['CurrentPageLoc']]=0;m[host['CurrentColumnPos']]=6;m[host['BlockBufferColumnPos']]=6
  status,_,_=case(m,reference,q);assert status,(axis,q);counts['late_OOB_atomic']+=1
 return dict(cases=sum(counts.values()),counts=dict(counts),no_actor_or_core_writes=True)


def legacy(p,attributes):
 old,new=Memory(p,attributes),Memory(p,attributes);count=0;cost=[]
 for axis in(0,1):
  for tileflag in range(256):
   for phase in range(32):
    for negative in(False,True):
     height=24 if (tileflag+phase)&1 else 32
     edge=0 if negative else(24 if axis==0 else height)
     state=Prior.base_state(mode=0,height=height,
      x=((0x1e0+phase-edge if axis==0 else 128+(tileflag&31)-12)<<8)|(tileflag^phase),
      y=((0x1e0+phase-edge if axis==1 else 128+(tileflag&31)-height//2)<<8)|phase,
      vx=-0x181 if negative and axis==0 else 0x181,
      vy=-0x181 if negative and axis==1 else 0x181,flags=(tileflag*37)&255)
     state[0x82]=tileflag
     old.reset(state);new.reset(state)
     f=(0x21,0x60,0xad)[tileflag%3]
     a=invoke(old,p['shape']['entrypoints']['SonicShapeHorizontal'if axis==0 else'SonicShapeVertical'],flags=f)
     b=invoke(new,p['symbols']['SonicSweptHorizontal'if axis==0 else'SonicSweptVertical'],flags=f)
     assert a[4]==b[4]and bytes(old[0xc000:0xc100])==bytes(new[0xc000:0xc100])
     assert [old[x]for x in p['shape']['core']['SMC_operands']]==[new[x]for x in p['shape']['core']['SMC_operands']]
     assert not old.buffer_reads and not new.buffer_reads
     cost.append(b[2]-a[2]);count+=1
 return dict(cases=count,full256_state_AXYP_SP_SMC_exact=True,additional_cycles=[min(cost),max(cost)])


def corners(p,attributes):
 count=0;controls=0
 for page in(0,1):
  for height in(24,32):
   for left in(False,True):
    for up in(False,True):
     for frac in(0,255):
      ordered,wrong=Memory(p,attributes),Memory(p,attributes)
      oldx=page*256+(96 if left else 71);oldy=156 if up else 95
      vx=(0xfff000 if left else 0x1000)|frac
      vy=(0xfff000 if up else 0x1000)|frac
      state=Prior.base_state(height=height,x=oldx<<8|frac,y=oldy<<8|frac,vx=vx,vy=vy,flags=0)
      for m in(ordered,wrong):
       m.reset(state);m.setup_domain(page)
       list.__setitem__(m,slice(0x300,0x4a0),bytes(416))
       invoke(m,p['witness']['symbols']['SonicSweepCapture'])
       invoke(m,p['shape']['core']['symbols']['PositionStep'])
      postx,posty=word(ordered,0xc071),word(ordered,0xc074)
      fraction=bytes((ordered[0xc070],ordered[0xc073]))
      clippedx=page*256+(96 if left else 72)
      wallx=page*256+(80 if left else 96)
      wally=(posty+height//2)&0xfff0
      groundy=128 if up else (posty+height)&0xfff0
      assert wally!=groundy
      for m in(ordered,wrong):
       m[pointer(wallx,wally)]=0x54
       m[pointer(clippedx+12,groundy)]=0x54
      for axis in(0,1):
       out=invoke(ordered,p['symbols']['SonicSweptHorizontal'if axis==0 else'SonicSweptVertical']);assert out[1]
      for axis in(1,0):
       out=invoke(wrong,p['symbols']['SonicSweptHorizontal'if axis==0 else'SonicSweptVertical']);assert out[1]
      expectedy=groundy+16 if up else groundy-height
      assert word(ordered,0xc071)==clippedx and word(ordered,0xc074)==expectedy
      assert ordered[0xc030]==(0x40 if up else 0xc0)
      assert bytes((ordered[0xc070],ordered[0xc073]))==fraction
      assert (word(wrong,0xc071),word(wrong,0xc074))!=(clippedx,expectedy),'Swapped order not detected'
      count+=1;controls+=1
 return dict(cases=count,swapped_order_negatives=controls,real_ground_flag_and_fractions=True)


def shortcut_controls(p,attributes):
 count=0
 for axis in(0,1):
  m,reference,endpoint=Memory(p,attributes),Memory(p,attributes),Memory(p,attributes)
  q=setup(m,axis,False,32,0,15,255 if axis==0 else 0,255,flags=0)
  assert len(q['cells'])==3
  middle=q['cells'][1];x,y=(middle,q['orth'])if axis==0 else(q['orth'],middle)
  at=pointer(x,y);m[at]=0x54
  assert case(m,reference,q)[0]==0
  endpoint.reset(full_state(q['post']));endpoint.setup_domain(0);endpoint[at]=0x54
  out=invoke(endpoint,p['shape']['entrypoints']['SonicShapeHorizontal'if axis==0 else'SonicShapeVertical'])
  assert out[1] and endpoint[p['shape']['context']['Kind']]==0
  assert word(endpoint,0xc071+3*axis)!=word(m,0xc071+3*axis),'Endpoint-only shortcut did not fail'
  count+=1
  if axis==1:
   bad=Memory(p,attributes);state=full_state(q['post'])
   final=Prior.stateword(state,0x74)+32
   state[0x80:0x83]=bytes(((middle-(final&0xffe0))&255,32,0));state[0x30]&=0x7f
   assert state[0x80]&128
   bad.reset(state);invoke(bad,p['shape']['core']['symbols']['VerticalContact'])
   assert word(bad,0xc074)==word(m,0xc074)
   assert not bad[0xc030]&128 and m[0xc030]&128,'Negative offset did not expose ground-bit bypass'
   count+=1
 return dict(endpoint_only_failures=2,negative_offset_floor_flag_failure=1,cases=count)


def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
 args=ap.parse_args();assert args.output.resolve().is_relative_to(R/'build')and not args.output.exists()
 for path,digest in FROZEN.items():assert sha256((R/path).read_bytes()).hexdigest()==digest,path
 raw=ROM.read_bytes();assert sha256(raw).hexdigest()==PIN
 for bank,pc,data in(
  (126,0x9d83,'c9c2f006c9c3f0021860'),
  (126,0x9eca,'c95ff002c96060'),(126,0x9eea,'c967f005c96818d0013860'),
  (126,0x9c77,'c88c0601a5bdc920901dc9e4b0302097e4f014c91cf010c96bf00ca8b936'),
  (9,0xbf21,'9db805209fbfa405a9239109a9108d8107')):
  data=bytes.fromhex(data);at=16+bank*8192+(pc&8191)
  assert raw[at:at+len(data)]==data,(bank,hex(pc))
 attrs=raw[16+127*8192+0xf36:16+127*8192+0xf36+256]
 assert attrs[0]&3==0 and attrs[0x54]&3==1
 p=B.build()
 report=dict(passed=True,files_written=0,ROM_written=False,current_SHA256=PIN,
  selector_bytes=len(p['image']),selector_SHA256=p['image_SHA256'],code=p['code_half_open'],
  context=p['context_half_open'],requires_eighth_carrier=p['requires_eighth_carrier'],over_seven_rows=p['over_seven_rows'],
  geometry=geometry(p,attrs),tiles=tiles(p,attrs),failures=failures(p,attrs),
  legacy=legacy(p,attrs),corners=corners(p,attrs),shortcut_negatives=shortcut_controls(p,attrs),
  no_native_hook_or_RAM_grant=True,scope='Actual6502 native-buffer sweep and unchanged contacts only; frame bridge/lifecycle/native gameplay/art not yet implemented.')
 for path,digest in FROZEN.items():assert sha256((R/path).read_bytes()).hexdigest()==digest,path
 assert not args.output.exists();print(json.dumps(report,sort_keys=True),flush=True)


if __name__=='__main__':main()
