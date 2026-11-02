"""Qualify the one-entry Arthur admission repair before emitting a private ROM."""
from pathlib import Path
import itertools,json,subprocess,zipfile,re
import check_arthur_side_clamp_1101_v8 as C
from private_build_outputs_v1 import validate
P=C.P;M=C.M;O=P.O;R=P.R
SOURCE=R/'tools/reference/arthur_maturity_policy_1102_v12.s'
BASE=O/'candidate.nes'


def point(b,n):return((C.location(b,n)-16)//8192|128,C.address(b,n))


def same(a,za,b,zb,why):
 low=min(za['minimum_SP'],zb['minimum_SP'])
 assert C.result(za)==C.result(zb),(why,'AXYP',za,zb)
 assert C.fields(a,low)==C.fields(b,low),(why,'application',[(hex(k),a[k],b[k])for k in range(0x8000)if a[k]!=b[k]and not 0x101+low<=k<0x1e1][:12])
 assert a.ram==b.ram and a.rawtags==b.rawtags and a.chr_latches==b.chr_latches,(why,'WRAM/cache/mapper/CHR')
 assert a.vram==b.vram and a.ppu_log==b.ppu_log,(why,'PPU/palette')


def main():
 assert P.sha(BASE)=='8be03441c6f5503acb3d001e76fbcc1d82a0fc4967c856c2eda763eba2d09806'
 old=C.scoped_load(BASE);raw=bytearray(old['raw']);slot=C.location(old,'ArOwnServices')+23*3
 assert raw[slot]==0x4c
 # These actual optimized locations are inherited from the source-linked v3
 # component; the whole18B policy prefix and4B local body are checked below.
 ownlabels={}
 for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(R/'build/arthur-camera-1101-v3/camera.lbl').read_text(),re.M):ownlabels[n]=int(a,16)
 set9,set18=ownlabels['ArOwnSet9'],ownlabels['ArOwnSet18']
 visible,noop=ownlabels['ArMergeLocalVisible'],ownlabels['ArMergeLocalNoop']
 off=lambda pc:16+70*8192+pc-0xa000
 assert int.from_bytes(raw[slot+1:slot+3],'little')==set18
 a,b=raw[off(set9):off(set9)+18],raw[off(set18):off(set18)+18]
 assert a[0]==b[0]==8 and a[-4]==b[-4]==0x28 and a[-3]==b[-3]==0x4c
 assert int.from_bytes(a[-2:],'little')==visible and int.from_bytes(b[-2:],'little')==noop
 assert all(a[i]==b[i]for i in range(18)if i not in [2,7,16,17]),'Only draw-target and pure policy branch differ'
 v,n=raw[off(visible):off(visible)+4],raw[off(noop):off(noop)+4]
 assert v[0]==0x38 and n[0]==0x18 and v[1:]==n[1:] and v[1]==0x4c,'The reused body is SEC then the same policy return'
 cc=R/'tools/Windows/cc65/bin'
 s=O/'maturity-entry.s';s.write_text(f'ArOwnSet9=${set9:04x}\n'+SOURCE.read_text())
 cfg=O/'maturity-entry.cfg';cfg.write_text('MEMORY{M:start=$bd45,size=3,file=%O;}SEGMENTS{MATURE:load=M,type=ro;}')
 for cmd in [[cc/'ca65.exe',s,'-o',O/'maturity-entry.o'],[cc/'ld65.exe','-C',cfg,O/'maturity-entry.o','-o',O/'maturity-entry.bin']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 entry=(O/'maturity-entry.bin').read_bytes();assert entry==bytes([0x4c,set9&255,set9>>8]);raw[slot:slot+3]=entry
 new=dict(old);new['raw']=bytes(raw)
 # In-memory oracle retains row23's old transport address, with an exact copy
 # of the already-proven visible policy. It has the same deliberate C=1 and
 # ArDrawPtr target, but never depends on the new table-entry branch.
 expected=dict(old);eraw=bytearray(old['raw']);eraw[off(set18):off(set18)+18]=a;expected['raw']=bytes(eraw)
 bases=[]
 for q in [old,new,expected]:
  m=C.seed(q);M.put(m,SelectedCharacter=32,ArHostReady=167,OperMode_Task=3)
  sig=C.location(q,'ArCacheSignature');m.ram[2][0x1fe0:0x1ff0]=q['raw'][sig:sig+16]
  bases.append(m)
 gate=0;foreign=0
 for state,kind,flag in itertools.product([0,6,16,127,128,129,255],range(4),[0x20,0x31,0x61,0xa9]):
  pair=[]
  for base in bases[1:]:
   m=M.fork(base);m[C.address(m.bundle,'PowerUpType')+5]=kind;m[C.address(m.bundle,'Enemy_State')+5]=state
   z=M.invoke(m,'NrPickupCollision',a=85,x=5,y=73,p=flag);pair.append((m,z));assert z['P']&1
  same(*pair[0],*pair[1],('owned admission',state,kind,flag));gate+=1
 print('Owned admission complete-state parity',gate,flush=True)
 for rawid,flag in itertools.product([i for i in range(39)if i!=32],[0x20,0x31,0x61,0xa9]):
  pair=[]
  for base in bases[:2]:
   m=M.fork(base);M.put(m,SelectedCharacter=rawid);m[C.address(m.bundle,'PowerUpType')+5]=1;m[C.address(m.bundle,'Enemy_State')+5]=128
   z=M.invoke(m,'NrPickupCollision',a=85,x=5,y=73,p=flag);pair.append((m,z))
  same(*pair[0],*pair[1],('foreign admission',rawid,flag));foreign+=1
 print('Foreign admission unchanged',foreign,flush=True)
 # Construct through the real Arthur constructor, not hand-written source state.
 initial=[]
 for q in [old,new,expected]:
  m=C.seed(q);M.put(m,SelectedCharacter=32,ArHostReady=0,OperMode_Task=3,CurrentPlayer=0,NumberofLives=2,OffScr_NumberofLives=4,DisableScreenFlag=1,Mirror_PPUMASK=0)
  M.invoke(m,'HuFresh',x=5)
  assert M.get(m,'ArHostReady')==167 and M.get(m,'ArR_053A')==64,('Actual constructor state',M.get(m,'ArHostReady'),M.get(m,'ArR_053A'))
  initial.append(m)
 print('Actual constructor initialized',flush=True)
 # Exercise every other Arthur public policy through the actual unchanged
 # callback/owner dispatch. Exactly one row may acquire new semantics.
 with zipfile.ZipFile(R/'build/_recovery/legacy-sources-2026-10-31.zip')as z:
  ix={q['path']:q for q in json.loads(z.read('index.json'))}
  item=ix['arthur-physical-clock-v2/joint/union.s'];union=z.read('objects/'+item['sha256']).decode()
 routes=re.findall(r'\.proc (Hu\w+)\n sta SafecallA_SMC\+1\n php\n tya\n pha\n ldy #(\d+)',union)
 assert len(routes)==36 and dict((int(i),n)for n,i in routes)[23]=='HuMature'
 rows=0
 for name,index in routes:
  if int(index)==23:continue
  for flag in [0x20,0x31,0x61,0xa9]:
   pair=[]
   for base in initial[:2]:
    m=M.fork(base);z=M.invoke(m,name,a=0,x=0,y=0,p=flag);pair.append((m,z))
   same(*pair[0],*pair[1],('unchanged owned row',index,name,flag));rows+=1
 print('All35 other owned public rows unchanged',rows,flush=True)
 source_names=[n for n in old['syms']if n.startswith('ArR_')and '::'not in n]
 counts={};cls=M.NesMPU;step=cls.step;active={}
 names=['ArHostCollect','ArHostNativePickup','MarioSourcePowerupCollision','EraseEnemyObject','SetupFloateyNumber']
 points={point(old,n):n for n in names}
 def record(c):
  if c.pc>=0x8000:
   n=points.get((c.memory.rawtags[(c.pc-0x8000)//8192],c.pc))
   if n:active[n]=active.get(n,0)+1
  return step(c)
 cls.step=record;contact=0;immature=0;native=0;earned=0
 try:
  for state,kind,slotid,flag in itertools.product([0,6,16,128,129],range(4),range(6),[0x20,0x61]):
   pair=[];visits=[]
   for base in initial[1:]:
    m=M.fork(base);M.put(m,ObjectOffset=slotid,Player_Y_Position=112,Player_Y_HighPos=1,Player_State=0,FrameCounter=0)
    for name,value in [('PowerUpType',kind),('Enemy_State',state),('Enemy_ID',46),('Enemy_Flag',1),('EnemyOffscrBitsMasked',0),('Enemy_CollisionBits',0)]:m[C.address(m.bundle,name)+slotid]=value
    for index,values in [(0,[99,124,107,140]),((slotid+1)*4,[96,128,108,140])]:m[C.address(m.bundle,'BoundingBox_UL_Corner')+index:C.address(m.bundle,'BoundingBox_UL_Corner')+index+4]=values
    source_before={n:M.get(m,n)for n in source_names};pal=bytes(m.vram[0x3f00:0x3f20]);active.clear()
    z=M.invoke(m,'NrPickupCollision',a=85,x=slotid,y=73,p=flag);assert z['P']&1
    z=M.invoke(m,'RemainingNormalPlayerCollision',a=z['A'],x=z['X'],y=z['Y'],p=z['P']);visits.append(dict(active));pair.append((m,z))
    assert active.get('ArHostCollect')==1,('Actual overlap missed',state,kind,slotid,active)
    if kind<2 and state<128:
     assert active.get('ArHostNativePickup',0)==0 and active.get('EraseEnemyObject',0)==0 and active.get('SetupFloateyNumber',0)==0
     assert {n:M.get(m,n)for n in source_names}==source_before and bytes(m.vram[0x3f00:0x3f20])==pal
     assert M.get(m,'Enemy_Flag',slotid)==1
    elif kind>=2:
     assert active.get('MarioSourcePowerupCollision')==1 and active.get('ArHostNativePickup',0)==0
    else:
     assert active.get('ArHostNativePickup')==1 and active.get('EraseEnemyObject')==1
     assert M.get(m,'Enemy_Flag',slotid)==0
   same(*pair[0],*pair[1],('actual contact',state,kind,slotid,flag));assert visits[0]==visits[1]
   contact+=1;immature+=int(kind<2 and state<128);native+=int(kind>=2);earned+=int(kind<2 and state>=128)
 finally:cls.step=step
 cuts={}
 def cutrecord(c):
  if c.pc>=0x8000 and c.memory.rawtags[(c.pc-0x8000)//8192]==198 and (c.pc==0xbd45 or set9<=c.pc<set9+18 or visible<=c.pc<visible+4 or ownlabels['ArMergePolicyReturn']<=c.pc<ownlabels['ArFastPolicyHigh']):
   cuts.setdefault((c.pc,c.sp),(M.fork(c.memory),C.state(c)))
  return step(c)
 cls.step=cutrecord
 try:M.invoke(M.fork(bases[1]),'NrPickupCollision',a=85,x=5,y=73,p=0x61)
 finally:cls.step=step
 assert cuts
 for kind,(m0,s)in itertools.product(['IRQ','lag-NMI'],cuts.values()):
  m=M.fork(m0);c=cls(memory=m,pc=s[0]);c.pc,c.a,c.x,c.y,c.p,c.sp=s
  before=C.state(c);smc=bytes(m[0x15a:0x17b]);live=bytes(m[0x101+c.sp:0x200]);maps=m.rawtags[:]
  if kind=='IRQ':c.irq()
  else:c.nmi()
  for _ in range(100000):
   if C.state(c)==before:break
   assert m[c.pc]!=0,(kind,hex(before[0]),'BRK');c.step()
  else:raise AssertionError((kind,hex(before[0]),'ISR bound'))
  assert bytes(m[0x15a:0x17b])==smc and bytes(m[0x101+c.sp:0x200])==live and m.rawtags==maps and m.ram==m0.ram
  for n in ['CurrentBank','CurrentBankC','ArDrawPtr','ArTemp','ArTempHi']:assert M.get(m,n)==M.get(m0,n)
 d=dict(passed=True,source_CPU_only=True,native=False,base_sha256=P.sha(BASE),candidate_sha256=__import__('hashlib').sha256(new['raw']).hexdigest(),changed_bytes=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b],Arthur_owned_admission_full_state_cases=gate,other35_Arthur_public_policy_full_state_cases=rows,foreign_actual_NrPickupCollision_parity_cases=foreign,actual_overlapping_contact_cases=contact,immature_kind0_1_no_source_palette_grant_erase_cases=immature,kind2_3_genuine_MarioSource_cases=native,mature_kind0_1_original_Arthur_pickup_cases=earned,unique_owned_policy_interrupt_boundaries=len(cuts),IRQ_lag_NMI_cuts=2*len(cuts),no_new_PRG_CHR_RAM=True,scope='Actual owned policy is pure SEC followed by the existing complete return transport; constructor, all36publicpolicies, full admission and real normal-player bbox contact run actual ROM instructions. Full application/WRAM/source counters/cache/palette/mapper/AXYP parity against an independent in-memory copy of the existing allowed policy at the former transport address. ArHostCollect remains the maturity authority; BBox is unchanged. Native real flower/torch and full1-1 still pending.',bindings={str(p.relative_to(R)):P.sha(p)for p in [Path(__file__),SOURCE,BASE,O/'maturity-entry.bin',R/'build/arthur-camera-1101-v3/camera.lbl']},source_union_archive_object=item['sha256'])
 assert len(d['changed_bytes'])<=2 and all(slot+1<=i<slot+3 for i in d['changed_bytes'])
 (O/'maturity-fix-CPU.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))


if __name__=='__main__':main()
