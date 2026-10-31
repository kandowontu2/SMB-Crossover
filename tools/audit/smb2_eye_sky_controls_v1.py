"""Actual final62 S2 eye/backdrop source consumers; no native or shared edits."""
from pathlib import Path
import collections,copy,hashlib,importlib.util,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location
from smb2_eye_palette_audit_v1 import pixels
O=R/'build/smb2-eye-sky-controls-v1';J=R/'build/smb2-eye-sky-v3/joint';P=R/'build/functional-roster-coherent62-v4/joint'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
s=importlib.util.spec_from_file_location('single_eye_sky_factory',R/'build/smb2-natural-current-audio-v20/controls.py');A=importlib.util.module_from_spec(s);s.loader.exec_module(A);C=A.C;M=A.M
BODIES=[[1,22,39],[6,37,54],[1,48,39],[1,42,54]]
def seed(var,mode=0):
 m=M.fresh(var,mode);old=C.O;C.O=J
 try:b=C.Bus()
 finally:C.O=old
 m.bundle=b.bundle;m.ROM_banks=b.ROM_banks;m.lab=b.lab
 C.invoke(m,'GetAreaPalette');A.interrupt(m,0)
 for n in['MenuResolveCharacter','QueueSelection','DrawSelectionPreview']:C.invoke(m,n)
 A.interrupt(m,0);return m

def actual_parts(m):
 count=m.get('CurrentOAMOffset');assert count==20
 parts=[list(m.ram[0x200+i:0x204+i])for i in range(0,count,4)]
 assert sum(p[2]&3==2 for p in parts)==1 and sum(p[2]&3==0 for p in parts)==4
 return parts

def main():
 assert not O.exists();O.mkdir();q=dict(passed=False,native=False,checks={});ck=q['checks'];last=None
 try:
  assert sha(J/'candidate.nes')=='f0ce3d16fe0130924e6d1afeb541ed1c7cd8fe4bfd06c86621a5713fa73e979c'
  a=scoped_load(P/'candidate.nes');b=scoped_load(J/'candidate.nes');rows=[];maxline=0
  for profile,i in itertools.product(range(8),range(32)):
   recs=[]
   for z in[a,b]:
    raw=z['raw'];rid=raw[location(z,'S2BodyRecord')+profile*32+i];ptr=raw[location(z,'S2ArtLo')+rid]+256*raw[location(z,'S2ArtHi')+rid];at=16+80*8192+ptr-0xc000;recs.append(raw[at:at+21])
   old,eye=pixels(a['raw'],796+profile,recs[0]);new,neweye=pixels(b['raw'],796+profile,recs[1]);assert old.keys()==new.keys() and len(recs[1])==21
   for p in old:
    op,oi,ok=old[p];np,ni,nk=new[p];oc=BODIES[profile//2][oi-1]if op==0 else[48,22,15][oi-1];nc=BODIES[profile//2][ni-1]if np==0 else[22,48,39][ni-1]
    assert(oc,ok)==(nc,nk),(profile,i,p,old[p],new[p],oc,nc)
   counts=collections.Counter()
   for k in range(5):
    y=recs[1][1+k*4+2];y=y-256 if y>=128 else y
    for yy in range(y,y+16):counts[yy]+=1
   maxline=max(maxline,max(counts.values()));rows.append(dict(profile=profile,pose=i,opaque=len(new),visible_eye=sum(v[2]==0 for v in new.values()),body_parts=5,maximum_body_sprites_per_line=max(counts.values())))
  assert maxline<=8;ck['all256_lossless_source_pixel_priority']=dict(cases=256,rows=rows,maximum_body_sprites_per_scanline=maxline,source_eye_NES16_exact=True,no_new_quad_or_world_recolor=True)
  bases=[seed(v)for v in range(4)];rows=[]
  nativebg=[34,34,15,15,15,34,15,15]
  for var,area,ctrl in itertools.product(range(4),range(4),[0,2,4,5,6,7]):
   m=copy.deepcopy(bases[var]);M.put(m,AreaType=area,BackgroundColorCtrl=ctrl,StarInvincibleTimer=0,VRAM_Buffer_AddrCtrl=0,VRAM_Buffer1_Offset=0)
   before=list(m.vram[0x3f15:0x3f20]);C.invoke(m,'GetPlayerColors');at=m.lab['VRAM_Buffer1'];packet=list(m.ram[at:at+8]);want=[63,16,4,nativebg[ctrl or area]]+BODIES[m.get('S2NativeCharacter')]+[0]
   assert packet==want,(var,area,ctrl,packet,want);A.interrupt(m,0)
   assert m.vram[0x3f00]==want[3] and list(m.vram[0x3f11:0x3f14])==want[4:7]
   assert list(m.vram[0x3f15:0x3f20])==before and list(m.vram[0x3f19:0x3f1c])==[22,48,39]
   rows.append(dict(var=var,area=area,BGctrl=ctrl,packet=packet,actual_NMI_BG=m.vram[0x3f00],P1_P2_P3_exact=True))
  ck['actual_scene_queue_normalNMI']=dict(cases=len(rows),rows=rows)
  rows=[]
  for off in range(85):
   m=copy.deepcopy(bases[0]);M.put(m,StarInvincibleTimer=0,VRAM_Buffer_AddrCtrl=0,S2PaletteAck=255,VRAM_Buffer1_Offset=off,AreaType=1,BackgroundColorCtrl=0)
   at=m.lab['VRAM_Buffer1'];m.ram[at:at+86]=bytes([0xa6])*86;before=bytes(m.ram[at:at+86]);z=C.invoke(m,'S2MainPalette');after=bytes(m.ram[at:at+86])
   if off<77:
    assert after[:off]==before[:off] and list(after[off:off+8])==[63,16,4,34,1,22,39,0] and after[off+8:]==before[off+8:]
    assert m.get('VRAM_Buffer1_Offset')==off+7 and m.get('S2PaletteAck')==0
   else:assert after==before and m.get('S2PaletteAck')==255 and m.get('VRAM_Buffer1_Offset')==off
   rows.append(dict(offset=off,accepted=off<77,CPU=z['CPU']))
  ck['all85_queue_offsets_and_canaries']=dict(cases=85,rows=rows)
  rejects=[]
  for name,value in [('StarInvincibleTimer',1),('VRAM_Buffer_AddrCtrl',1),('S2PaletteAck',0)]:
   m=copy.deepcopy(bases[0]);M.put(m,StarInvincibleTimer=0,VRAM_Buffer_AddrCtrl=0,S2PaletteAck=255,VRAM_Buffer1_Offset=0);m.set(name,value);at=m.lab['VRAM_Buffer1'];before=bytes(m.ram[at:at+84]);C.invoke(m,'S2MainPalette');assert bytes(m.ram[at:at+84])==before;rejects.append(name)
  ck['unchanged_native_star_published_and_ack_guards']=rejects
  rows=[]
  for var,mode in itertools.product(range(4),range(2)):
   m=seed(var,mode);case=dict(var=var,mode=mode,selected_parts=actual_parts(m));rows.append(case);assert m.vram[0x3f00]==34
   M.put(m,SavedJoypad1Bits=16,SavedJoypad2Bits=0);C.invoke(m,'GameMenuRoutine');C.invoke(m,'PauseRoutine',A=0);pending=False;seen=False
   for age in range(1500):
    A.interrupt(m,0)
    if pending:
     assert m.vram[0x3f00]==15 and list(m.vram[0x3f19:0x3f1c])==[22,48,39]
     case['lives_BG']=m.vram[0x3f00];case['lives_parts']=actual_parts(m);seen=True;pending=False
    z=C.invoke(m,'GameLoop')
    pending=any(pc==m.lab['DisplayIntermediate']and tags[(pc-32768)//8192]==m.bank('DisplayIntermediate')|128 for tags,pc in z['trace']if pc>=32768)
    if m.get('OperMode_Task')==3 and m.get('GameEngineSubroutine')==8:break
   else:raise AssertionError('cold entrance bound')
   assert seen;A.interrupt(m,0);assert m.get('AreaType')==1 and m.get('BackgroundColorCtrl')==0 and m.vram[0x3f00]==34
   case.update(actual_cold_Main=age+1,entered_BG=m.vram[0x3f00],Main=[])
   for tick in range(8):
    A.interrupt(m,1 if tick>2 else 0);z=C.invoke(m,'GameLoop');assert m.vram[0x3f00]==34 and m.get('S2Ready')==178;case['Main'].append(dict(CPU=z['CPU'],X=m.get('Player_X_Position'),Y=m.get('Player_Y_Position'),BG=m.vram[0x3f00]))
  ck['actual_8cold_selected_lives_entrance_64Main']=rows
  # Every emitted instruction in the new helper/header/loop is cut by the
  # genuine IRQ or lag-NMI while the foreground packet is not yet committed.
  m=copy.deepcopy(bases[0]);M.put(m,S2PaletteAck=255,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,StarInvincibleTimer=0)
  z=C.invoke(m,'S2MainPalette');ranges=[(m.lab['S2NativePaletteHeader'],m.lab['S2NativePaletteHeader']+33),(m.lab['S2MainPalette'],m.lab['S2MainPalette']+60)];sites=sorted(set(pc for tags,pc in z['trace']if tags[1]==246 and any(lo<=pc<hi for lo,hi in ranges)))
  cuts=[]
  for pc,kind in itertools.product(sites,['NMI','IRQ']):
   m=copy.deepcopy(bases[0]);M.put(m,S2PaletteAck=255,VRAM_Buffer1_Offset=0,VRAM_Buffer_AddrCtrl=0,StarInvincibleTimer=0,NmiDisable=255);done=[False]
   def hook(c):
    if done[0]or c.pc!=pc or m.tags[1]!=246:return
    done[0]=True;regs=(c.pc,c.a,c.x,c.y,c.p,c.sp);maps=m.tags[:];smc=bytes(m.ram[0x15a:0x17b]);live=bytes(m.ram[0x101+c.sp:512]);shadow=[m.get('CurrentBank'),m.get('CurrentBankC')]
    if kind=='NMI':c.nmi()
    else:m.ram[0x5204]=128;c.p&=~4;regs=(regs[0],regs[1],regs[2],regs[3],c.p,regs[5]);c.irq()
    for _ in range(100000):
     if(c.pc,c.sp)==(regs[0],regs[5]):break
     m.pc=c.pc;assert m[c.pc]!=0;c.step()
    else:raise AssertionError('real vector bound')
    assert(c.pc,c.a,c.x,c.y,c.p,c.sp)==regs and m.tags==maps and bytes(m.ram[0x15a:0x17b])==smc and bytes(m.ram[0x101+c.sp:512])==live and[m.get('CurrentBank'),m.get('CurrentBankC')]==shadow
   C.invoke(m,'S2MainPalette',hook=hook);assert done[0];at=m.lab['VRAM_Buffer1'];assert list(m.ram[at:at+8])==[63,16,4,34,1,22,39,0];cuts.append(dict(pc=pc,kind=kind))
  assert cuts;ck['real_instruction_lagNMI_IRQ_cuts']=dict(cases=len(cuts),rows=cuts,AXYP_SP_live_stack_33SMC_rawmaps_exact=True)
  q['passed']=True
 except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
 finally:
  files={Path(__file__),J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',O.parent/'smb2-eye-sky-v3/source-proof.json',P/'candidate.nes',P/'candidate.dbg',R/'build/smb2-eye-role-audit-v2/audit.json',R/'build/smb2-sky-negative-v1/negative.json'}
  for mod in list(sys.modules.values()):
   f=getattr(mod,'__file__',None)
   if f and Path(f).resolve().is_relative_to(R/'tools'):files.add(Path(f).resolve())
  files|={Path(A.__file__),Path(M.__file__),Path(C.__file__)};q['bindings']={str(p.resolve()):sha(p)for p in files if p.is_file()};p=O/'controls.json';p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=q['passed'],error=q.get('error'),path=str(p),sha256=sha(p))),flush=True)
if __name__=='__main__':main()
