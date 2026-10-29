"""Finite actual queued-palette/full-Main/IRQ controls for the f467 successor."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import rogue_dawn_scheduler_controls_v3 as v
import rogue_dawn_scheduler_deep_edges_v1 as deep
from sunny_integrated_controls_v1 import app,registers
from proto_palette_coalesce_controls_v1 import ppu
q,get,put,address=v.q,v.get,v.put,v.address
P=R/'build/rogue-dawn-scheduler-v5';O=R/'build/rogue-dawn-backdrop-v1'

def packet(m):
 at=address(m.bundle,'VRAM_Buffer1');return bytes(m[at:at+get(m,'VRAM_Buffer1_Offset')+1])

def source_colors(m):
 q.invoke(m,'RdRenderPalettePointer')
 at=m[address(m.bundle,'R0')]+256*m[address(m.bundle,'R0')+1]
 return bytes(m[at+1:at+4])

def snap(m,c):
 class Q:pass
 x=Q();x.b=m.bundle;x.m=m
 return registers(c),app(x),q.physical(m)

def ready(b,**kw):
 m=q.make(b,0);v.nmi(m)
 put(m,VRAM_Buffer1_Offset=0,VRAM_Buffer1=0,VRAM_Buffer2_Offset=0,VRAM_Buffer2=0,
     VRAM_Buffer_AddrCtrl=0,DisableScreenFlag=0,**kw)
 return m

def main():
 assert not(O/'controls.json').exists(),'Frozen control'
 build=json.loads((O/'build.json').read_text())
 for z in build['bindings']:assert v.ref.binding(z['path'])==z,z['path']
 b=v.scoped_load(O/'candidate.nes');old=v.scoped_load(P/'candidate.nes')
 proof=dict(passed=False,source_CPU_only=True,native_run=False,checks={});checks=proof['checks']
 try:
  rows=[]
  native=bytes.fromhex('22220f0f0f220f0f')
  # Actual source suit/missile palette pointer, every native BG selection,
  # both boundary accepted offsets and first rejected offset. No fake pointer.
  for area,ctrl,gear,missile,offset in itertools.product(range(4),[0,4,5,7],[0,32],[0,1],[0,76,77]):
   m=ready(b,AreaType=area,BackgroundColorCtrl=ctrl,RdGear=gear,RdMissileMode=missile,RdColorRequest=1)
   colors=source_colors(m);at=address(b,'VRAM_Buffer1');m[at:at+96]=bytes(range(96));put(m,VRAM_Buffer1_Offset=offset)
   before=bytes(m[at:at+96]);cpu,z=q.invoke(m,'RdBodyQueuePalette')
   if offset>=77:
    assert bytes(m[at:at+96])==before and get(m,'VRAM_Buffer1_Offset')==offset and get(m,'RdColorRequest')==1 and not(cpu.p&1)
   else:
    want=bytes.fromhex('3f1004')+bytes([native[ctrl if ctrl else area]])+colors+b'\x00'
    assert bytes(m[at:at+offset])==before[:offset]
    assert bytes(m[at+offset:at+offset+8])==want
    assert bytes(m[at+offset+8:at+96])==before[offset+8:]
    assert get(m,'VRAM_Buffer1_Offset')==offset+7 and get(m,'RdColorRequest')==0 and cpu.p&1
   if gear==0 and missile==0 and offset==0:rows.append(dict(area=area,backgroundCtrl=ctrl,packet=packet(m).hex(),CPU=z['CPU'],minimum_SP=z['minimum_SP']))
  checks['192_native_background_source_colors_and_queue_boundary_cases']=dict(cases=4*4*2*2*3,all_canaries_and_request_ACK_exact=True,examples=rows)
  print('192 queue/ACK cases PASS',flush=True)
  # Real GetPlayerColors foreign paths and ordinary Samus keep exact effects.
  rows=[]
  for char in range(24):
   pair=[]
   for bundle in [old,b]:
    m=ready(bundle,SelectedCharacter=char,RdVariant=0,AreaType=1,BackgroundColorCtrl=0)
    c,z=q.invoke(m,'GetPlayerColors');pair.append((snap(m,c),packet(m),z['CPU']))
   assert pair[0][:2]==pair[1][:2],('foreign GetPlayerColors',char)
   rows.append(dict(character=char,CPU_delta=pair[1][2]-pair[0][2]))
  checks['24_actual_foreign_GetPlayerColors']=rows
  # Actual screen-color caller -> genuine full UpdateScreen consumes exactly
  # native universal22 plus source body colors, not source palette0F.
  rows=[]
  for area,ctrl in [(0,0),(1,0),(2,0),(3,0),(1,4),(1,5)]:
   m=ready(b,AreaType=area,BackgroundColorCtrl=ctrl,RdColorRequest=1)
   colors=source_colors(m);q.invoke(m,'GetPlayerColors');queued=packet(m)
   put(m,NmiDisable=0)
   z=v.nmi(m);image,bus=ppu(z['writes'])
   assert image[0x3f00]==native[ctrl if ctrl else area] # actual3F10 hardware mirror
   assert bytes(image[0x3f11+i]for i in range(3))==colors
   rows.append(dict(area=area,ctrl=ctrl,queued=queued.hex(),actual_ordered_PPU_writes=[list(x)for x in bus],NMI_CPU=z['CPU'],minimum_SP=z['minimum_SP']))
  checks['actual_scene_color_caller_fullNMI_PPU_publication']=rows
  print('actual PPU publication PASS',flush=True)
  # Ordinary star/transform state must retain real native backdrop selection.
  # These legal flags are typed CPU contexts, not native earned-Star evidence.
  rows=[]
  for star,transform,area,ctrl in [(0,0,1,0),(32,0,1,0),(1,0,1,0),(0,1,1,0),(0,0,2,0),(0,0,3,0)]:
   pair=[]
   for bundle in [old,b]:
    m=ready(bundle,StarInvincibleTimer=star,PlayerChangeSizeFlag=transform,AreaType=area,BackgroundColorCtrl=ctrl,RdColorRequest=1)
    c,z=q.mainstep(m)
    pair.append((m,c,z))
   om,oc,oz=pair[0];m,c,z=pair[1]
   assert bytes(m[0x5fb0:0x5fb6])==bytes(om[0x5fb0:0x5fb6])
   assert bytes(m[0x5c00:0x5c80])==bytes(om[0x5c00:0x5c80]),('source state',star,transform)
   assert registers(c)==registers(oc) and q.physical(m)==q.physical(om)
   assert get(m,'Player_X_Position')==get(om,'Player_X_Position') and get(m,'Player_Y_Position')==get(om,'Player_Y_Position')
   assert any(pc==address(b,'RdBackdropQueue')and bank==121 for pc,bank,sp in z['trace'])
   rows.append(dict(star=star,transform=transform,area=area,ctrl=ctrl,Main_CPU_delta=z['CPU']-oz['CPU'],minimum_SP=z['minimum_SP'],queued=packet(m).hex()))
  checks['six_complete_Main_star_transform_area_contexts']=rows
  # Exact PC/bank/SP-qualified real Main cut while the added palette call is
  # deepest. Replay genuine full lagNMI plus actual mapperIRQ, no stub ISR.
  def scene():return ready(b,RdColorRequest=1,AreaType=1,WorldNumber=0)
  m=scene();plain=deep.execute(m,'IdleLoop',253)
  start=next(i for i,k in enumerate(plain['trace'])if k[:2]==(address(b,'RdBackdropQueue'),121))
  entrySP=plain['trace'][start][2];tail=plain['trace'][start:]
  end=next(i for i,k in enumerate(tail[1:],1)if k[2]>entrySP)
  cut=min(tail[:end],key=lambda a:a[2])
  m=scene();z=deep.execute(m,'IdleLoop',253,cut,IRQ=(address(b,'RdaReadRom'),97,cut[2]-29))
  assert z['minimum_SP']>=128
  checks['natural_Main_added_palette_fullNMI_IRQ']=dict(cut=[hex(cut[0]),cut[1],cut[2]],minimum_SP=z['minimum_SP'],ISR=z['interrupt'])
  # Whole existing drivers/raw views/normal scheduler are physically exact;
  # the supported original Control192 stress still enters the same callbacks.
  m=ready(b,AreaType=1,WorldNumber=0);put(m,RdAction=0,NmiDisable=255)
  z=deep.execute(m,'RdControlStep',192);cut=min(z['trace'],key=lambda a:a[2])
  m=ready(b,AreaType=1,WorldNumber=0);put(m,RdAction=0,NmiDisable=255)
  r=deep.execute(m,'RdControlStep',192,cut,IRQ=(address(b,'RdaReadRom'),97,cut[2]-29))
  assert r['minimum_SP']>=128
  checks['retained_Control192_real_lagNMI_IRQ']=dict(minimum_SP=r['minimum_SP'],ISR=r['interrupt'])
  proof.update(passed=True,bindings=[v.ref.binding(p)for p in [Path(__file__),O/'build.json',O/'candidate.nes',O/'candidate.dbg',O/'candidate.lbl',P/'handoff.json',R/'tools/rogue_dawn_scheduler_deep_edges_v1.py',R/'tools/rogue_dawn_scheduler_controls_v3.py']],limits=['Finite CPU/source contexts; no native palette visual/deadline/performance claim.','Star/transform flags are actual compiled caller contexts, not an earned native powerup replay.','Palette helper changes only intended universal background plus authentic body colors; physical PPU palette mirroring is hardware, observed here as actual ordered2006/2007 publication.'])
 except Exception as e:
  proof.update(error=repr(e),traceback=traceback.format_exc())
  p=O/'controls-negative-1.json';i=2
  while p.exists():p=O/f'controls-negative-{i}.json';i+=1
  p.write_text(json.dumps(proof,indent=2)+'\n');raise
 (O/'controls.json').write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=True,checks=list(checks))))
if __name__=='__main__':main()
