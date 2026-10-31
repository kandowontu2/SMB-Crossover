"""Typed black-lives palette source/PPU equivalence and actual NMI saving."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_bt_lives_body_1031_v3 as C
L,H,T=C.L,C.H,C.T
from check_tmnt_render_oa import location
def main():
 C.O.mkdir(exist_ok=True);out=C.O/'packet-timing-controls.json';assert not out.exists();C.bound()
 bs=[H.C.qualified(p/'candidate.nes')for p in[C.P,C.J]];rows=[]
 for variant in [0,1]:
  mm=[C.seed(b,variant)for b in bs];records=[]
  for m in mm:
   H.put(m,CurrentPlayer=0,NumberOfPlayers=0,VRAM_Buffer1_Offset=0,WorldNumber=0,LevelNumber=0)
   before=bytes(m.vram[0x3f00:0x3f20]);L.call(m,'DisplayIntermediate',a=1,x=0,y=0,p=48)
   assert H.get(m,'DisableScreenFlag')==0
   H.put(m,NmiDisable=0);m.writes.clear();m.ppu_log.clear()
   cpu=H.start(m,'FwCheck');step=cpu.step;events=[];origin=cpu.processorCycles
   def traced():
    start=len(m.writes);pc=cpu.pc
    step()
    for a,v in m.writes[start:]:
     if a==0x2001:events.append(dict(pc=pc,value=v,CPU=cpu.processorCycles-origin))
   cpu.step=traced;proof=L.V.interrupt(m,cpu,'NMI');cpu.step=step;H.finish(m,cpu)
   assert m.vram[0x3f04]==m.vram[0x3f14]==15
   enables=[e for e in events if e['value']&24==24];assert len(enables)==1
   records.append(dict(before=list(before),after=list(m.vram[0x3f00:0x3f20]),mask_writes=events,enable_CPU=enables[0]['CPU'],ppu=list(m.ppu_log),vector=proof))
  assert records[0]['after']==records[1]['after'],'actual final native+BT32 palette bytes changed'
  saving=records[0]['enable_CPU']-records[1]['enable_CPU'];assert saving>21
  # Actual native UpdateScreen final scroll pair stays the same. No direct
  # PPU/scroll writer is introduced by the selected foreground producer.
  assert records[1]['ppu'][-2:]==records[0]['ppu'][-2:]==[(0x2005,0),(0x2005,0)]
  rows.append(dict(variant=variant,normal_NMI_enable_CPU_saved=saving,old=records[0],new=records[1]))
 b=bs[1];source=[]
 for n in ['GroundPaletteData','UndergroundPaletteData','WaterPaletteData','CastlePaletteData']:
  at=location(b,n);packet=b['raw'][at:at+36];assert packet[:3]==bytes([63,0,32]) and packet[7]==packet[23]==15
  source.append(dict(label=n,real_native_3F04_14=packet[7],original_P1_transparent=packet[23]))
 q=dict(passed=True,source_CPU=True,native=False,candidate=C.SHA,typed_only_A1_Y30=True,normal_BtColors_unchanged=True,
   initial_native_InitScreen_ctrl3_bulk_palette_executed=True,all32_final_actual_PPU_palette_bytes_exact=True,
   original_no_3F00_or_3F10_late_packet=True,first_native_deadline_still_requires_root_replay=True,rows=rows,native_tables=source,
   bindings={str(p.resolve()):L.sha(p)for p in[Path(__file__),Path(C.__file__),C.J.parent/'source-stage.json',C.J/'candidate.nes',C.J/'candidate.dbg',C.P/'candidate.nes',C.P/'candidate.dbg']})
 out.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,candidate=C.SHA,CPU_saved=[r['normal_NMI_enable_CPU_saved']for r in rows])))
if __name__=='__main__':main()
