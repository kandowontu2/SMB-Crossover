"""One actual375 pair and bounded existing-log/source attribution; no native run."""
from pathlib import Path
import argparse, csv, hashlib, json, sys
from PIL import Image, ImageDraw
from check_tmnt_audio_fallback_oc import qualified
from check_tmnt_render_oa import load,address,location
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):assert not p.exists();p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def read_events(folder,name):return[json.loads(s)for s in(folder/name).open()]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 folders=[D/'parodius-menu-clean731-preparation-v1/menu/baseline-early',D/'current3b-nmi-regression-prepared-v1/menu/baseline-early'];raw=[(f/'frame-000375.argb').read_bytes()for f in folders];assert all(len(b)==256*240*4 for b in raw)
 pixels=[dict(x=i//4%256,y=i//4//256,before_RGB=list(raw[0][i:i+3][::-1]),after_RGB=list(raw[1][i:i+3][::-1]))for i in range(0,len(raw[0]),4)if raw[0][i:i+3]!=raw[1][i:i+3]];assert len(pixels)==39
 pair=Image.new('RGB',(520,264),'#d000a0');draw=ImageDraw.Draw(pair)
 for index,(label,data)in enumerate(zip(['731 actual frame375','3b actual frame375'],raw)):
  image=Image.frombytes('RGBA',(256,240),data,'raw','BGRA').convert('RGB');x=index*264;pair.paste(image,(x,24));draw.text((x+4,5),label,fill='white');assert pair.crop((x,24,x+256,264)).tobytes()==image.tobytes()
 pair.save(a.output/'actual-whole375-before-after.png')
 observations=[];bindings={str(Path(__file__).resolve()):sha(__file__)}
 for label,folder in zip(['731','3b'],folders):
  epoch=next(z for z in read_events(folder,'epochs.jsonl')if z.get('capture')=='frame-000375.argb');early=read_events(folder,'menu-early-timing.jsonl');life=next(z for z in read_events(folder,'lifecycle-events.jsonl')if z.get('ppu',{}).get('frame')==375 and z.get('kind')=='lifecycle-state')
  enables=[z for z in early if z.get('kind')=='early-render-enable'and 374<=z['ppu']['frame']<=376]
  entry=next(z for z in early if z.get('kind')=='early-NMI-entry'and z['ppu']['frame']==375)
  trace=[z for z in csv.DictReader((folder/'trace.csv').open())if 374<=int(z['frame'])<=376]
  assert epoch['mask']==6 and epoch['start_state']['ppu.mask.backgroundEnabled']is False and epoch['start_state']['ppu.mask.spritesEnabled']is False
  assert not any(z['ppu']['frame']==375 for z in enables)
  observations.append(dict(label=label,actual_start375=dict(stamp=epoch['start'],mask=epoch['mask'],phase=epoch['phase'],complete_PPU_state=epoch['start_state'],palette=epoch['palette'],CHR=epoch['chr_banks'],hardware_OAM=epoch['start_hardware']),actual_OperMode=life['oper'],actual_OperMode_Task=life['task'],actual_engine=life['engine'],actual_variant=life['variant'],lifecycle_stamp=life['ppu'],actual_NMI_entry375=entry,actual_enable_write_stamps374through376=enables,actual_trace374through376=trace,actual_DisableScreenFlag_numeric=None,actual_CrossoverMenuState_at_first_pixel=None,actual_NmiDisable_numeric=None,missing_observation='These three numeric fields and ALL PPUMASK writes were not logged before wall440. Ungated early observer captures every disabled-to-enabled mask transition; no such transition in375. Do not invent exact field values or missing write PCs/stamps.'))
  for name in ['frame-000375.argb','epochs.jsonl','menu-early-timing.jsonl','lifecycle-events.jsonl','trace.csv','oam-bus.jsonl','run.lua']:bindings[str(folder/name)]=sha(folder/name)
 before,after=observations;assert before['actual_start375']['complete_PPU_state']==after['actual_start375']['complete_PPU_state'];assert before['actual_start375']['palette']==after['actual_start375']['palette'];assert before['actual_start375']['CHR']==after['actual_start375']['CHR'];assert before['actual_start375']['hardware_OAM']==after['actual_start375']['hardware_OAM']
 candidate=D/'root-current-roster-composition-v1/candidate.nes';old=D/'mm-proto-clean-menu-candidates-v1/clean-menu-irq/candidate.nes';bs=[load(old),load(candidate)];records=[]
 for name in ['BuildScreen','CopyPage','ScreenPalette','CopyPalette','ScreenReady']:
  results=[]
  for b in bs:
   pc=qualified(old if b is bs[0]else candidate)[('CrossoverMenuInput',name)];off=location(b,'CrossoverMenuInput')+pc-address(b,'CrossoverMenuInput');results.append(dict(PC=pc,bank=(off-16)//8192,bytes=list(b['raw'][off:off+16])))
  assert results[0]==results[1];records.append(dict(label=name,**results[0]))
 for f in [candidate,candidate.with_suffix('.dbg'),old,old.with_suffix('.dbg'),D/'root-current-roster-composition-v1/source/src/character_select.s',D/'root-current-roster-composition-v1/source/src/game.s',D/'root-current-roster-composition-v1/source/src/reset.s',ROOT/'tools/audit/parodius_visibility_postdma_static_observer_v1.lua',ROOT/'tools/audit/parodius_visibility_menu59_timing_v2.lua']:bindings[str(f)]=sha(f)
 put(a.output/'all39-differing-pixels.json',pixels);put(a.output/'actual-observations-and-source.json',dict(observations=observations,unchanged_compiled_source_records=records,first_different_pixel=pixels[0],complete_start_PPU_state_palette_CHR_hardware_exact=True,forced_blank_observation='Both begin375 with actualmask6/BGoff/spritesoff. The ungated callback logs EVERY disabled-to-enabled transition, and none occurs375; the next recorded render-enable is376. Therefore375 remains forced blank, not active menu/gameplay rendering.',source_path='Unchanged bank66 CrossoverMenuInput BuildScreen waits for blank mask, clears name tables, directly copies1024menu bytes, changes menu state1→2, then ScreenPalette/CopyPalette writes16entries through2007 while blank, and ScreenReady clears DisableScreenFlag. GameLoop holds NmiDisableFF until PauseSkip. Captured startv22C2 corresponds to a partially completed2000..23FF copy; first RGB difference at255,39 is consistent with the following direct palette phase.',source_inference_not_actual_store_trace='The before440 observer did not log individual PPUDATA or all PPUMASK stores/CPUentryRAM. Exact native first palette-store PC/time and DisableScreenFlag/CrossoverMenuState/NmiDisable numeric values at pixel255,39 cannot be certified from this capture. Source route and forced-blank ownership are supported; precise first-write causality is still unproved.'))
 for f in a.output.iterdir():
  if f.is_file():bindings[str(f)]=sha(f)
 put(a.output/'bindings.json',bindings);put(a.output/'proof.json',dict(passed=True,scope='Read-only attribution facts, not acceptance or removal of original RGB_FALSE',native_launched=False,source_changed=False,original_menu_exact_RGB_gate_remains_FALSE=True,RGB_difference_pixels=39,first_difference=pixels[0],one_actual_whole_pair=str(a.output/'actual-whole375-before-after.png'),pair_sha256=sha(a.output/'actual-whole375-before-after.png'),forced_blank375_proven_by_actual_start_mask_and_ungated_enable_log=True,all_start_PPU_palette_CHR_OAM_values_exact=True,missing_actual_fields=['DisableScreenFlag numeric','CrossoverMenuState atfirstpixel','NmiDisable numeric','all pre440 PPUMASK writes','first direct PPUDATA-store timestamp/PC'],bindings=len(bindings),bindings_sha256=sha(a.output/'bindings.json')))
 print(json.dumps(json.loads((a.output/'proof.json').read_text()),indent=2))
if __name__=='__main__':main()
