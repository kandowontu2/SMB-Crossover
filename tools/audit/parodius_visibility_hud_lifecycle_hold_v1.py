"""Freeze the single failed menu lifecycle run without retry or new verdict."""
from pathlib import Path
import argparse,collections,hashlib,json,shutil
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 run=json.loads((a.run/'lifecycle-proof.json').read_text());assert not run['passed']and run['runner_exit']==1
 assert all(v is None for v in run['component_bindings'].values());log=(a.run/'host.log').read_text();assert 'Visible init has complete exact hardware source'in log
 rows=[json.loads(s)for s in(a.run/'oam-bus.jsonl').read_text().splitlines()];counts=dict(collections.Counter(q['kind']for q in rows));pubs=[q for q in rows if q['kind']=='lifecycle-init-publication'];dma=next(q for q in reversed(rows)if q['kind']=='lifecycle-init-4014-start')
 assert len(pubs)==2 and all(len(q['oam'])==256 for q in pubs)
 assert dma['ppu']==dict(cycle=322,frame=278,cpu=8248743,scanline=257)and dma['mask']==30 and dma['oam_address']==0 and dma['writer_pc']==0xe005 and dma['bank']==127
 assert '4014-complete-after-next-LDX'not in counts
 frames=sorted(int(f.stem.removeprefix('frame-'))for f in a.run.glob('frame-*.argb'));assert frames==list(range(150,278))
 h=[json.loads(s)for s in(a.run/'hud-frames.jsonl').read_text().splitlines()];assert h[-1]['finished']['frame']==277 and h[-1]['start']['ram']['OperMode']==0
 first=dict(assertion='Visible init has complete exact hardware source',classification='INIT_COMPLETION_AT_START_ASSERTION_HELD',game_defect_proven=False,host_AV=False,last_recorded_actual_DMA=dma,publications=pubs,preceding_same_NMI_UpdateScreen_entries=[q for q in rows if q['kind']=='UpdateScreen-owner'and q['ppu']['frame']==278],failure_callback='new inactive startFrame observer, before its snapshot/log row',missing_evidence=['actual failing startFrame PPU stamp','actual failing hardware256B snapshot','first differing hardware byte','post-LDX DMA completion endpoint','first actual portrait raster row','actual full frame278'],limits='Actual source publication and DMA start are recorded; the guard stopped before the next startFrame observation row. Its completion predicate was not satisfied at that point. No visible body corruption, ROM clearance or timing extrapolation is claimed. Original live guard remains unchanged and no live coverage occurred.')
 (a.output/'first-observed-failure.json').write_text(json.dumps(first,indent=2)+'\n')
 sheet=Image.new('RGB',(4*256,260),'#161616');draw=ImageDraw.Draw(sheet)
 for i,n in enumerate([274,275,276,277]):
  f=a.run/f'frame-{n:06}.argb';im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB');im.save(a.output/f'actual-PPU-{n}.png');sheet.paste(im,(256*i,20));draw.text((256*i,2),f'Actual PPU {n} before failure',fill='white')
 sheet.save(a.output/'last-four-completed-PPU.png')
 manifest={str(f.resolve()):sha(f)for f in a.run.rglob('*')if f.is_file()}
 for f in [a.ready/'proof.json',a.ready/'manifest.json',Path(__file__),ROOT/'docs/qa/parodius-hud-menu-native-hold-2026-10-25.txt']:
  manifest[str(f.resolve())]=sha(f)
 for f in a.output.iterdir():
  if f.is_file():manifest[str(f.resolve())]=sha(f)
 (a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(passed=False,native_run=True,native_worker_released=True,retries=0,ROM_sha256=run['ROM_sha256'],script_sha256=sha(a.run/'run.lua'),readiness_sha256=sha(a.ready/'proof.json'),original_lifecycle_receipt_sha256=sha(a.run/'lifecycle-proof.json'),first_observed_failure_sha256=sha(a.output/'first-observed-failure.json'),manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),actual_raw_ARGB_frames=frames,complete_terminal_components=0,required_terminal_components=5,original_dependencies_unchanged=json.loads((a.run/'proof.json').read_text())['dependencies_unchanged'],bus_kind_counts=counts,actual_captured_menu_modes=sorted(set(x['mode']for x in h)),all4variants_cancel_reentry_covered=False,meaningful_active_play_covered=False,settings_modified=False,tool_sha256=sha(Path(__file__)),limits='One explicitly granted menu1800 attempt stopped on first Lua assertion before active play. All failures and128 lossless frames retained. No automatic retry/death/area/body tests. Four last completed menu frames are presentation aids, not exhaustive visual review or failed-start evidence. Native and source hypotheses require a separately reviewed diagnostic before further execution.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=q['manifest_sha256'],bindings=len(manifest)),indent=2))


if __name__=='__main__':main()
