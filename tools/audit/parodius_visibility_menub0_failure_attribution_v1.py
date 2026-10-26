"""Read-only attribution of eight changed actual b0 menu frames; no new native run."""
from pathlib import Path
from collections import defaultdict
import argparse,csv,hashlib,json,sys
from PIL import Image,ImageDraw,ImageChops
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import address
from current3cee_postdma_mask_cpu_v4 import Bus
from parodius_visibility_menu_hint_cpu_v1 import packet
from verify_native_relocation import NesMPU
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 run=D/'parodius-menub0-preparation-v3/menu/baseline-early';old=D/'parodius-menu3cee-preparation-v2/menu/baseline-early';native=D/'parodius-menub0-native-v1';ready=D/'parodius-menub0-ready-v1'
 wanted=[184,194,206,218,230,242,254,266];owners=defaultdict(list);direct=defaultdict(list)
 for line in(run/'oam-bus.jsonl').open():
  if not any(k in line for k in ['UpdateScreen-owner','4014-complete','4014-start','2001-mask']):continue
  z=json.loads(line);n=z.get('ppu',{}).get('frame')
  if n in wanted:
   if z['kind']=='UpdateScreen-owner':owners[n].append(z)
   else:direct[n].append(z)
 hfr={z['finished']['frame']:z for z in map(json.loads,(run/'hud-frames.jsonl').read_text().splitlines())};b=scoped_load(run/'candidate.nes')
 modes=[(184,0,0,None),(194,0,0,4),(206,6,6,4),(218,13,12,1),(230,14,13,1),(242,15,14,1),(254,16,15,1),(266,17,16,1)]
 findings=[];source_rows=[]
 def pos(start,cpu):
  dots=(cpu-start['cpu'])*3;line,cycle=divmod(dots,341);return dict(frame=start['frame'],scanline=line-1,cycle=cycle,CPU=cpu)
 for n,previous,index,pressed in modes:
  actual=hfr[n]['start'];assert owners[n]and not direct[n]
  for z in owners[n]:assert z['actual_bankA']==0 and z['actual_bankC']==116 and z['mask']==6 and z['SP']==242 and z['nmi_depth']==1 and z['return_word']==0xc002
  q=Arena(b,previous);q.put(CrossoverBehaviorVersion=0,VvVariant=0,OperMode=0,OperMode_Task=3,GameEngineSubroutine=0,CrossoverMenuState=2,CrossoverMenuIndex=index,CrossoverMenuPressed=0,CrossoverMenuButtons=0,PlayerStatus=0,PlayerSize=1,ScreenLeft_PageLoc=0,ScreenLeft_X_Pos=0,Player_PageLoc=0,DisableScreenFlag=0,SavedJoypad1Bits=pressed or 0,SavedJoypad2Bits=0,Mirror_PPUCTRL=168,Mirror_PPUMASK=30)
  q.invoke('QueueSelection'if pressed is None else'CrossoverMenuInput');raw,commands=packet(q)
  assert len(raw)-1==actual['ram']['VRAM_Buffer1_Offset']and q.get('SelectedCharacter')==actual['ram']['SelectedCharacter']
  m=Bus(b,bytes(q.m[:0x8000]));m.page(1,0);m[address(b,'CurrentBank')]=128;c=NesMPU(memory=m,pc=0x5b00);m.cpu=c;c.sp=0xfd;c.nmi();entries=[];stop=None;branch_reload=q.get('ReloadCHRBank');wide=q.get('X5WideChrActive')
  for k in range(5000):
   if c.pc==address(b,'UpdateScreen'):entries.append(c.processorCycles)
   if c.pc==0xe008:stop=c.processorCycles;break
   c.step()
   if m.pending_dma:c.processorCycles+=514;m.pending_dma=False
  assert stop is not None
  observed=[y['ppu']['cpu']-x['ppu']['cpu']for x,y in zip(owners[n],owners[n][1:])];model=[y-x for x,y in zip(entries,entries[1:])];assert model==observed and len(commands)+1==len(entries)
  tail=stop-entries[-1];last=owners[n][-1]['ppu']['cpu']
  # This is a source/CPU-only interval with modeled513/514DMA and store timing.
  # Actual early E008/PPUMASK stamps were NOT saved by the ownership-gated observer.
  enable_low=last+tail-1+3;enable_high=last+tail+4
  before=Image.frombytes('RGBA',(256,240),(old/f'frame-{n:06d}.argb').read_bytes(),'raw','BGRA').convert('RGB');after=Image.frombytes('RGBA',(256,240),(run/f'frame-{n:06d}.argb').read_bytes(),'raw','BGRA').convert('RGB');changed=sum(x!=y for x,y in zip(before.getdata(),after.getdata()))
  row=dict(frame=n,visual_class='preview-restored'if n==184 else'REAL_VERTICAL_WRAP_REGRESSION',actual_selected_character=actual['ram']['SelectedCharacter'],actual_startFrame=actual['ppu'],actual_queue_encoded_bytes=len(raw)-1,actual_parser_entries=len(owners[n]),actual_parser_first=owners[n][0]['ppu'],actual_parser_last=owners[n][-1]['ppu'],actual_C116_mask6_owner_and_SP_exact=True,actual_command_intervals_CPU=observed,source_reconstruction_intervals_exact=True,source_queue_produced_by='QueueSelection'if pressed is None else'CrossoverMenuInput',source_reconstructed_commands=[dict(PPU_address=(v[0]<<8)|v[1],control=v[2],payload=list(v[3:]))for v in commands],source_reconstructed_packet_sha256=hashlib.sha256(raw).hexdigest(),source_reload=branch_reload,source_wide_CHR=wide,model_tail_last_parser_to_E008_514DMA_CPU=tail,model_enable_interval=[pos(actual['ppu'],enable_low),pos(actual['ppu'],enable_high)],model_requires_reload_before_280=False if pos(actual['ppu'],enable_low)['scanline']>=0 else pos(actual['ppu'],enable_low)['cycle']<=280,actual_early_E008_or_enable_stamps_available=False,actual_early_data_absent_reason='DMA observers require selectedParodius and mask/profile bus logging requires wall>=440. These highlight frames select other identities before440; do not substitute source-model estimates for measured DMA/PPUMASK stamps.',actual_full_frame_changed_pixels=changed,before_sha256=sha(old/f'frame-{n:06d}.argb'),after_sha256=sha(run/f'frame-{n:06d}.argb'))
  findings.append(row);source_rows.append(dict(frame=n,encoded_packet=list(raw),source_CPU_entry_cycles=entries,source_E008_cycles=stop))
 put(a.output/'actual-and-modeled-timings.json',findings);put(a.output/'source-reconstructed-packets.json',source_rows);put(a.output/'actual-parser-owner-rows.json',dict(owners))
 sheet=Image.new('RGB',(1024,1040),'#202020');draw=ImageDraw.Draw(sheet)
 for i,n in enumerate(wanted):
  for row,(label,folder)in enumerate([('3cee',old),('b0',run)]):
   x=i%4*256;y=i//4*520+row*260;f=folder/f'frame-{n:06d}.argb';im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB');sheet.paste(im,(x,y+20));draw.text((x,y),label+' '+str(n),fill='white')
 sheet.save(a.output/'all-eight-changed-actual-frames.png')
 report=R/'docs/qa/parodius-menub0-native-held-2026-10-26.txt'
 report.write_text('''b0 menu1800: VISUAL FAILURE / HELD, 2026-10-26

One granted run only; worker RELEASED. All six original programmed semantic
components PASS, but the actual menu has a real background-scroll regression.
Candidate b0c152fa0c588a7df28171e1c673a8db31e2769c5e9114768742e328f1134a99
remains HELD; installed production3cee unchanged. No retry or new candidate.

ROOT identified actual full-PPU194/206/218/230/242/254/266 vertical wrapping,
duplicated portraits/text and displaced menu background. Agent independently
viewed all eight changed before/after pairs and confirms these seven defects;
184's missing preview is restored. Earlier selected24-frame sheet omitted the
seven bad highlight frames; selected sampling is not global visual clearance.
The immutable native-v1 passed result certifies its finite programmed checks,
not overall menu visual correctness. This additive packet has passed=false.

The preserved source/pixel audit remains valid within its scope:1799inputs
and trace rows plus1121completed-motion rows exact3cee;1122updates/1000DMAs/
797publications,1258observedHUDpairs and2254336HUDpixels exact.1000completed
observed transfers/1487visible epochs match256source bytes; captured early
wrong-menu frames are OUTSIDE those selected-Parodius ownership guards.
No silent extension of observed transfer coverage to other menu identities.

Actual early UpdateScreen entry rows DO survive: C116,mask6,NMIdepth1,SP242,
returnwordC002. Actual queue offsets194..266 are69/72/63/78/78/66/66bytes.
Genuine assembled CrossoverMenuInput reproduces every offset and all ordered
command timing intervals exactly. Packets include oldcursor erase, colors,
16name cells,20help cells,newcursor and some appended preview palettes.
Cursor1=122,palette3=154,palette4=170,name16=311,hint20=375CPUcycles.
Full payload bytes in this packet are SOURCE-RECONSTRUCTED, not saved native
RAM; validation is actual selected identity, encoded size and every native
per-command interval, not an invented complete-memory replay assertion.

Critical observer limit: beforewall440 these non-Parodius selections have NO
saved actual4014/E008/2001 stamps. No direct DMA or enable timestamps are
claimed. Compiled full-NMI source models are anchored to actual final parser
entry, retain real source-produced Reload/CHR paths, and model513/514DMA.
They predict enabling at/after visibleline0 for all seven bad frames, missing
pre-render280..304verticalreload. Their exact intervals and assumptions are
in actual-and-modeled-timings.json. This supports the root timing-budget lead;
it is not a replacement for a later actual pre-render observation.

No source repair/native continuation authorized here. Need a bounded root
proposal preserving real packet content/scroll/OAM and measured budget before
any new launch. Whole-menu visualFAIL is not waived by exact CHR or hardware
OAM. OriginalareaFALSE/natural pendingBuffer2 limitation, mixed body starvation,
tinyfont/readability and broad title/day2/campaign/DMC limits remain open.
''',encoding='utf-8')
 files={f.resolve()for f in a.output.rglob('*')if f.is_file()}|{report.resolve(),Path(__file__).resolve(),native/'proof.json',native/'evidence.json',native/'manifest.json',ready/'proof.json',run/'lifecycle-proof.json',run/'oam-bus.jsonl',run/'hud-frames.jsonl',run/'candidate.nes',run/'candidate.dbg',D/'root-menub0-independent-v1/proof.json',D/'root-menub0-independent-v1/eight-changed-menu-frames.png'}
 for folder in[old,run]:files.update(folder/f'frame-{n:06d}.argb'for n in wanted)
 manifest={str(f):sha(f)for f in sorted(files)};put(a.output/'manifest.json',manifest)
 proof=dict(passed=False,native_run=True,offline_attribution_only=True,visual_failure=True,source_or_native_components_retagged=False,original_six_components_passed=True,native_launches=1,retries=0,worker_released=True,ROM_sha256=sha(run/'candidate.nes'),actual_regression_frames=wanted[1:],actual_preview_restore_frame=184,agent_visual_review=True,all_actual_8changed_frames_reviewed=True,early_DMA_enable_direct_stamps_absent=True,source_reconstructed_command_intervals_all_exact=True,source_model_not_native_timing=True,original_native_packet_sha256=sha(native/'proof.json'),timing_sha256=sha(a.output/'actual-and-modeled-timings.json'),sheet_sha256=sha(a.output/'all-eight-changed-actual-frames.png'),report_sha256=sha(report),manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),limits='HELD VISUALFAIL; no retry/candidate change/production/default/settings/Git mutation. Missing early direct DMA/enable stamps remain missing, source model explicitly limited.')
 put(a.output/'proof.json',proof);print(json.dumps(proof,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))
if __name__=='__main__':main()
