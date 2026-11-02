"""Private native BlockBuffer producer versus independent original DK probes."""
import collections,json,re
from pathlib import Path
import prepare_dkjr_native_world_1102_v3 as P
R=P.R;O=P.O;D=P.P.D


def main():
 # Reuse the frozen donor test, writing only distinct v3 outputs.
 src=(R/'tools/audit/check_dkjr_native_source_1102_v2.py').read_text()
 for old,new in [('component.lbl','native-world-v3.lbl'),('component.bin','native-world-v3.bin'),('component.s','native-world-v3.s'),('layout.json','native-world-v3-source-layout.json'),('CPU.json','native-world-v3-source-CPU.json')]:src=src.replace(old,new)
 env={'__name__':'dkjr_v3_source_regression','__file__':__file__};exec(compile(src,__file__,'exec'),env);env['main']()
 lab={n:int(a,16)for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'native-world-v3.lbl').read_text(),re.M)}
 blob=(O/'native-world-v3.bin').read_bytes();layout=json.loads((O/'native-world-v3-layout.json').read_text());raw=P.CURRENT.read_bytes();assert P.P.sha(raw)==P.PIN
 native=layout['native_bindings'];attrs=raw[layout['native_MTileAttribute_file_offset']:][:256]
 active,_=D.active();seed=bytes(active.memory[:2048]);cohorts=collections.Counter();cycles=[];records=[];minimum_sp=255
 class Flat(list):pass
 def call(m,entry,regs=(0x57,7,9,0x20)):
  nonlocal minimum_sp
  c=D.T.NesMPU(memory=m,pc=entry);c.a,c.x,c.y,c.p=regs;c.sp=0xfd;c.stPushWord(0x5ffe)
  for _ in range(50000):
   if c.pc==0x5fff:break
   minimum_sp=min(minimum_sp,c.sp);assert m[c.pc]!=0,('BRK',hex(c.pc));c.step()
  else:raise AssertionError(('Bound',hex(c.pc)))
  return c,(c.a,c.x,c.y,c.p,c.sp)
 donor_raw=D.donor();control_cases=0
 m=Flat([0]*65536);m[0xa000:0xa000+len(blob)]=blob
 q=D.Bus(donor_raw)
 for rawpad in range(256):
  for previous in[0,0x81,0x82,0xff]:
   for port in[0,1]:
    r=bytearray(seed);r[0x14+2*port]=previous;r[0x15+2*port]=previous
    m[0xc000:0xc800]=r;q[:2048]=r
    c,got=call(m,lab['DkjrNormalizePad'],(rawpad,port,9,0x20));d=D.T.NesMPU(memory=q,pc=0);z=D.T.run(d,0xf23e,rawpad,port,9,0x20)
    assert bytes(q[:256])+bytes(q[0x200:0x800])==bytes(m[0xc000:0xc100])+bytes(m[0xc200:0xc800]),('source controller',rawpad,previous,port)
    assert z[:3]==got[:3]and z[3]&0xef==got[3]&0xef and z[4]==got[4],('source controller registers',z,got)
    if port==0:
     expected=bytes(m[0xc000:0xc800]);m[0xc000:0xc800]=r;m[native['SavedJoypadBits']]=rawpad;before=bytes(m[:0x100]);call(m,lab['DkjrNativeControls'])
     assert bytes(m[0xc000:0xc800])==expected and bytes(m[:0x100])==before
    control_cases+=1
 local_service_cases=0
 for entry,fields in[(0xcec9,[{0x2e:v}for v in range(256)]),(0xec17,[{0x3a:a,0x3b:b,0x231:tile}for a in[0,1,255]for b in[0,1,255]for tile in[0,0xa0,0xa4]])]:
  for fields_case in fields:
   r=bytearray(seed)
   for pc,value in fields_case.items():r[pc]=value
   m[0xc000:0xc800]=r;q[:2048]=r
   _,got=call(m,lab['D_%04x'%entry],(0x57,7,9,0xf1));d=D.T.NesMPU(memory=q,pc=0);z=D.T.run(d,entry,0x57,7,9,0xf1)
   assert bytes(q[:256])+bytes(q[0x200:0x800])==bytes(m[0xc000:0xc100])+bytes(m[0xc200:0xc800]),('local source service',hex(entry),fields_case)
   assert z[:3]==got[:3]and z[3]&0xef==got[3]&0xef and z[4]==got[4],('local source service registers',entry,z,got)
   local_service_cases+=1
 coordinate_cases=0;accepted=0;rejected=0
 player_fields=[native[n]for n in['Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos']]
 for camera in[0,1,15,127,248,255,256,511,65520]:
  for relative in[0,7,8,16,147,231,232,255]:
   for y in[0,32,176,224,225]:
    for high in[0,1,2]:
     m[0xc000:0xc800]=seed;m[native['ScreenLeft_X_Pos']]=camera&255;m[native['ScreenLeft_PageLoc']]=camera>>8
     world=(camera+relative)&65535
     for pc,value in zip(player_fields,[world&255,world>>8,y,high]):m[pc]=value
     before=bytes(m[:0x800]);c,z=call(m,lab['DkjrNativeImportAnchor'],(0x57,7,9,0xf1));legal=high==1 and y<=224 and 8<=relative<=231
     assert bool(z[3]&1)==legal,('anchor admission',camera,relative,y,high,z)
     expected=bytearray(seed)
     if legal:
      dx=relative-8-seed[0x213];dy=y+15-seed[0x210]
      for i in range(0,32,4):expected[0x210+i]=(seed[0x210+i]+dy)&255;expected[0x213+i]=(seed[0x213+i]+dx)&255
      accepted+=1
     else:rejected+=1
     assert bytes(m[0xc000:0xc800])==expected,('anchor source body/state',camera,relative,y,high)
     assert bytes(m[:0x100])+bytes(m[0x200:0x800])==before[:0x100]+before[0x200:],('anchor native mutation',camera)
     if legal:
      # Native camera can advance after a source update. Publication uses
      # the actual CURRENT camera exactly once, including page carry.
      current_camera=(camera+9)&65535;m[native['ScreenLeft_X_Pos']]=current_camera&255;m[native['ScreenLeft_PageLoc']]=current_camera>>8
      _,z=call(m,lab['DkjrNativePublishAnchor']);assert z[3]&1
      got=[m[p]for p in player_fields];world=(current_camera+relative)&65535
      assert got==[world&255,world>>8,y,1],('anchor publication',camera,relative,y,got)
      assert bytes(m[0xc000:0xc800])==expected
     coordinate_cases+=1
 for top in[32,64,96,144,160,176,208,224]:
  m[0xc000:0xc800]=seed;m[0xc043]=top;call(m,lab['DkjrLand']);source_y=m[0xc210];assert source_y==top-17
  _,z=call(m,lab['DkjrNativePublishAnchor']);assert z[3]&1 and m[native['Player_Y_Position']]==top-32
  coordinate_cases+=1
 for x,y in[(224,191),(255,191),(32,0),(32,14)]:
  m[0xc213]=x;m[0xc210]=y;before=bytes(m[:0x800]);_,z=call(m,lab['DkjrNativePublishAnchor']);assert not z[3]&1 and bytes(m[:0x100])+bytes(m[0x200:0x800])==before[:0x100]+before[0x200:];coordinate_cases+=1
 def oracle(m,camera,bounds,kind):
  left,top,right,bottom=bounds
  if kind==3:top=(bottom+1)&255;bottom=(bottom+2)&255
  if (right-left)&255>=33 or (bottom-top)&255>=17:return bytes([255])
  if top>=240 or bottom<32:return bytes([255])
  rows=range(max(top,32)&240,(min(bottom,239)&240)+1,16);out=[]
  for y in rows:
   for world in range((camera+left)&~15,((camera+right)&~15)+1,16):
    v=m[(0x300 if (world>>8)&1==0 else 0x3d0)+(y-32)+((world>>4)&15)]
    solid=attrs[v]&3==1
    if not(v==0x26 if kind<2 else solid):continue
    sx=world-camera
    if kind<2:
     sx+=8
     if not 0<=sx<255:continue
     l=r=sx
    else:
     if sx+15<0 or sx>=255:continue
     l=max(0,sx);r=min(255,sx+15)
    out.extend([l,y,r,y+15])
  def append(rect):
   l,t,r,b=rect
   if r>=left and right>=l and b>=top and bottom>=t:out.extend(rect)
  if kind<2:
   n=m[native['Vine_FlagOffset']];slot=5
   flag=m[native['Enemy_Flag']+slot]
   sx=m[native['Enemy_X_Position']+slot]+256*m[native['Enemy_PageLoc']+slot]-camera+8
   t=max(32,m[native['Enemy_Y_Position']+slot]);b=min(239,m[native['Vine_Start_Y_Position']])
   if n in[1,2] and 5 in m[native['Vine_ObjOffset']:native['Vine_ObjOffset']+n] and 8<=m[native['Vine_Height']]<=[48,96][n-1] and 0<flag<128 and m[native['Enemy_ID']+slot]==0x2f and m[native['Enemy_Y_HighPos']+slot]==1 and 0<=sx<255 and t<=b:append([sx,t,sx,b])
  elif kind>=3:
   for slot in range(5,-1,-1):
    flag=m[native['Enemy_Flag']+slot];ident=m[native['Enemy_ID']+slot];state=m[native['Enemy_State']+slot]
    if not(0<flag<128 and 0x24<=ident<0x2d and (ident>=0x2b or state<128)and m[native['Enemy_Y_HighPos']+slot]==1):continue
    l,t,r,b=m[native['BoundingBox_UL_Corner']+4*(slot+1):][:4]
    if l==255 or r<l:continue
    ys=[t]
    if ident>=0x2b:
     y=m[native['Enemy_Y_Position']+slot]
     second=state if m[native['AreaPointer']]==0x62 and m[native['WorldNumber']]in[1,4]else(y+128)&255
     ys=[y,second]
    for y in ys:
     if 32<=y<240:append([l,y,r,y])
  assert len(out)<=60,('Oracle capacity',bounds,kind,len(out))
  return bytes(out+[255])
 def case(camera,bounds,kind,stage,flags,world,cohort,objects=None):
  m=Flat([0]*65536);m[0xa000:0xa000+len(blob)]=blob;m[0xe000:]=raw[16+127*8192:16+128*8192];m[0xc000:0xc800]=seed
  m[native['ScreenLeft_X_Pos']]=camera&255;m[native['ScreenLeft_PageLoc']]=camera>>8
  # Fill actual native circular two-page BlockBuffer addresses.
  for page in range(camera>>8,(camera>>8)+2):
   for y in range(32,240,16):
    for x in range(16):m[(0x300 if page&1==0 else 0x3d0)+(y-32)+x]=world(page*256+x*16,y)
  for pc,value in(objects or{}).items():m[pc]=value
  expected=oracle(m,camera,bounds,kind);which=1 if kind<2 else 2 if kind==2 else 0
  geometry=[bytes([255])for _ in range(3)];geometry[which]=expected
  r=bytearray(seed);r[0x4a]=stage;r[0x3e:0x42]=bytes(bounds)
  for base,data in zip([0x700,0x740,0x780],geometry):r[base:base+len(data)]=data
  m[0xc000:0xc800]=r;call(m,lab['DkjrNativeWorldEnable']);assert m[0xc8da]==1
  before=bytes(m[:0x800]);c,got=call(m,lab['D_%04x'%[0xe893,0xe897,0xe89b,0xe89f,0xe8a3][kind]],(0x57,7,9,flags))
  assert bytes(m[:0x100])+bytes(m[0x200:0x800])==before[:0x100]+before[0x200:],('Native low RAM write',cohort)
  base=[0xc800,0xc840,0xc880][which];assert bytes(m[base:base+len(expected)])==expected,(cohort,camera,bounds,kind,expected,list(m[base:base+64]))
  assert m[0xc8ef]==0,(cohort,camera,bounds,kind,'producer error')
  q=D.Bus();q[:2048]=r
  for table,base,data in zip([0xc440,0xc448,0xc450],[0x700,0x740,0x780],geometry):
   for i in range(4):list.__setitem__(q,table+2*i,base&255);list.__setitem__(q,table+2*i+1,base>>8)
  d=D.T.NesMPU(memory=q,pc=0);entry=[0xe893,0xe897,0xe89b,0xe89f,0xe8a3][kind];z=D.T.run(d,entry,0x57,7,9,flags,limit=50000)
  diff=[(i,q[i],m[0xc000+i])for i in list(range(256))+list(range(0x200,0x800))if q[i]!=m[0xc000+i]]
  assert not diff,(cohort,camera,bounds,kind,diff[:8]);assert z[:3]==got[:3]and z[3]&0xef==got[3]&0xef and z[4]==got[4],(cohort,z,got)
  cohorts[cohort]+=1;cycles.append(c.processorCycles);records.append((len(expected)-1)//4)
 def world(x,y):
  if y>=208 and not 320<=x<368:return 0x54
  if 96<=x<128 and y>=176:return 0x51
  if 192<=x<224 and y>=160:return 0x52
  if 256<=x<288 and y>=144:return 0x53
  if x in[64,400] and 48<=y<208:return 0x26
  if x in[80,416] and 48<=y<208:return 0x24 if x==80 else 0x25
  return 0
 for camera in[0,1,7,8,15,16,63,95,127,191,240,248,255,256,257,319,511,512,767]:
  for x,y in[(0,16),(0,48),(7,80),(16,159),(48,191),(64,191),(96,159),(127,127),(208,191),(223,223),(224,224),(248,191)]:
   bounds=[x,y,min(254,x+24),min(239,y+15)]
   for kind in range(5):
    for flags in[0x20,0xf1]:case(camera,bounds,kind,1+camera%4,flags,world,'camera-pipe-pit-vine-boundaries')
 # Solid ceilings and one-tile head/side/foot contacts, native metatile flags.
 for tile in[0,0x10,0x24,0x25,0x26,0x51,0x61,0xc0,0xff]:
  for kind in range(5):
   for xy in[(16,64),(31,80),(32,95),(40,96)]:case(15,[xy[0],xy[1],xy[0]+16,xy[1]+15],kind,2,0x20,lambda x,y,t=tile:t if x==48 and y==80 else 0,'native-metatile-classification')
 for camera in[0,1,15,248,255,256,511]:
  for grown in[0,7,8,16,31,32,48,96,97]:
   for count in[0,1,2,3]:
    for flag in[0,1,0x85]:
     x=camera+48;obj={native['Vine_FlagOffset']:count,native['Vine_Height']:grown,native['Vine_ObjOffset']:5,native['Vine_ObjOffset']+1:1,native['Enemy_Flag']+5:flag,native['Enemy_ID']+5:0x2f,native['Enemy_Y_HighPos']+5:1,native['Enemy_X_Position']+5:x&255,native['Enemy_PageLoc']+5:x>>8,native['Enemy_Y_Position']+5:208-grown,native['Vine_Start_Y_Position']:208}
     for kind in[0,1]:case(camera,[40,184,64,199],kind,3,0x20,lambda x,y:0,'actual-growing-vine-policy',obj)
 for relative in[-9,-8,-7,0,8,247,248,255,256]:
  for root_list in[[5,1],[1,5],[1,2]]:
   x=256+relative;obj={native['Vine_FlagOffset']:2,native['Vine_Height']:48,native['Vine_ObjOffset']:root_list[0],native['Vine_ObjOffset']+1:root_list[1],native['Enemy_Flag']+5:1,native['Enemy_ID']+5:0x2f,native['Enemy_Y_HighPos']+5:1,native['Enemy_X_Position']+5:x&255,native['Enemy_PageLoc']+5:x>>8,native['Enemy_Y_Position']+5:160,native['Vine_Start_Y_Position']:208}
   for xx in[0,224]:
    for kind in[0,1]:case(256,[xx,176,min(254,xx+30),191],kind,2,0xf1,lambda x,y:0,'growing-vine-root-list-and-viewport',obj)
 for ident in range(0x23,0x2e):
  for flag in[0,1,0x81]:
   for state in[0,0x40,0x80,0xff]:
    for high in[0,1,2]:
     for kind in[2,3,4]:
      obj={native['Enemy_Flag']+2:flag,native['Enemy_ID']+2:ident,native['Enemy_State']+2:state,native['Enemy_Y_HighPos']+2:high,native['Enemy_Y_Position']+2:208}
      for off,value in enumerate([32,208,80,216]):obj[native['BoundingBox_UL_Corner']+12+off]=value
      case(255,[40,191,64,206],kind,1,0x20,lambda x,y:0,'published-native-platform-admission',obj)
 for area,worldno in[(0,0),(0x62,0),(0x62,1),(0x62,4),(0x62,7)]:
  for first,second in[(80,128),(96,144),(160,208),(224,32)]:
   for body_y in[15,31,63,79,95,127,143,159,191,207,223]:
    obj={native['AreaPointer']:area,native['WorldNumber']:worldno,native['Enemy_Flag']:1,native['Enemy_ID']:0x2b,native['Enemy_State']:second,native['Enemy_Y_HighPos']:1,native['Enemy_Y_Position']:first}
    # Deliberately leave second/oldY in the published box, as the actual
    # native collision loop can. Both support planes must remain correct.
    for off,value in enumerate([32,second,56,(second+8)&255]):obj[native['BoundingBox_UL_Corner']+4+off]=value
    for kind in[3,4]:case(256,[40,body_y,56,body_y+15],kind,4,0xf1,lambda x,y:0,'actual-small-platform-two-plane-policy',obj)
 for rect in[[0,32,254,40],[255,208,255,216],[80,208,32,216],[0,31,254,39],[0,239,254,247],[0,240,254,248],[0,255,254,7]]:
  obj={native['Enemy_Flag']+4:1,native['Enemy_ID']+4:0x28,native['Enemy_State']+4:0x40,native['Enemy_Y_HighPos']+4:1}
  for off,value in enumerate(rect):obj[native['BoundingBox_UL_Corner']+20+off]=value
  for yy in[15,16,191,222,223]:
   for kind in[2,3,4]:case(511,[0,yy,24,yy+15],kind,1,0x20,lambda x,y:0,'platform-clipping-and-top-plane-only',obj)
 q=dict(passed=True,native=False,ROM_written=False,component_SHA256=P.P.sha(blob),native_base_SHA256=P.PIN,source_regression=json.loads((O/'native-world-v3-source-CPU.json').read_text())['CPU_cases'],controller_original_and_native_cases=control_cases,local_source_service_cases=local_service_cases,coordinate_cases=coordinate_cases,coordinate_imports=dict(accepted=accepted,rejected_before_source_mutation=rejected,source_x_equals_native_screen_x_minus=8,source_OAM_y_equals_native_anchor_y_plus=15,original_Land_support_minus=17,native_landed_anchor_support_minus=32),native_query_cases=sum(cohorts.values()),cohorts=dict(cohorts),maximum_emitted_rectangles=max(records),CPU_cycles_per_query=dict(minimum=min(cycles),maximum=max(cycles),mean=sum(cycles)//len(cycles)),minimum_SP=minimum_sp,host_low_RAM_preserved=True,original_nonstack_RAM_AXYP_SP_parity=True,bindings={p.relative_to(R).as_posix():P.P.sha(p.read_bytes())for p in[Path(__file__),Path(P.__file__),O/'native-world-v3.bin',O/'native-world-v3.s',O/'native-world-v3-layout.json']},scope='Actual current native circular BlockBuffers and fixed native MTileAttribute feed independent donor E893/E897/E89B/E89F/E8A3; native SavedJoypadBits feeds exact original controller F23E..F266. Declared CPU terrain/coordinate fixtures plus malformed/offscreen rejection controls; no native Main, owner, remaining services, mapper/IRQ or Mesen claim.')
 (O/'native-world-v3-CPU.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
