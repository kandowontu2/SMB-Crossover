"""Freeze the one5354 death-observer native failure and first wrong HUD owners."""
from pathlib import Path
import argparse,csv,hashlib,json
from PIL import Image,ImageDraw
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
readrows=lambda p:[json.loads(s)for s in p.read_text().splitlines()]


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['run','old-run','ready','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 result=json.loads((a.run/'lifecycle-proof.json').read_text());assert result['passed']is False and all(v is None for v in result['component_bindings'].values())
 assert 'Actual prelease source blank tile'in(a.run/'candidate-run.log').read_text()
 hud=readrows(a.run/'hud-events.jsonl');bus=readrows(a.run/'oam-bus.jsonl');frames=readrows(a.run/'hud-frames.jsonl');life=readrows(a.run/'lifecycle-events.jsonl');scroll=readrows(a.run/'scroll-events.jsonl');epochs=readrows(a.run/'epochs.jsonl')
 cfg=json.loads((a.run/'config.json').read_text());b=scoped_load(a.run/'candidate.nes');labels=cfg['hud_labels']['1']
 before=next(x for x in frames if x['finished']['frame']==514);bad=next(x for x in frames if x['finished']['frame']==515)
 assert before['start']['chr'][8]==396 and before['start']['ram']['InvHudActive']==3 and before['start']['labels']==labels
 assert bad['start']['chr'][8]==0 and bad['start']['ram']['InvHudActive']==0 and bad['start']['labels']==labels
 cancel=next(x for x in hud if x['kind']=='write-InvHudActive'and x['previous']==3 and x['value']==0 and x['ppu']['frame']==514)
 badfont=next(x for x in bus if x['kind']=='CHR-write'and x['address']==0x5128 and x['ppu']['frame']==515 and x['nmi_depth']==1)
 assert badfont['physical']==0
 pending=next(x for x in hud if x['kind']=='write-X5HudChrUpper'and x['ppu']['frame']==811 and x['value']==133)
 pending_cancel=next(x for x in hud if x['kind']=='write-X5HudChrUpper'and x['ppu']['frame']==811 and x['previous']==133 and x['value']==1)
 assert pending_cancel['packet'][:42]==pending['packet'][:42] and pending_cancel['ram']['VRAM_Buffer1_Offset']==42
 stale_write=next(x for x in bus if x['kind']=='2007-data'and x['ppu']['frame']==813 and x['vram_address']==0x2022)
 assert stale_write['value']==labels[0]
 finalstart=next(x['state']for x in scroll if x['kind']=='visible-start'and x['state']['ppu']['frame']==813)
 assert finalstart['active']==0 and finalstart['font']==0 and finalstart['labels']==labels
 instruction=[]
 for row,name in [(cancel,'death-clear-active'),(pending_cancel,'restart-clear-pending')]:
  pc=row['pc']-3;at=16+row['physical_bank']*8192+pc%8192;op=list(b['raw'][at:at+3]);target=cfg['hud_ram']['InvHudActive'if name=='death-clear-active'else'X5HudChrUpper']
  assert op==[0x8d,target&255,target>>8]
  instruction.append(dict(case=name,instruction_PC=pc,callback_PC=row['pc'],bank=row['physical_bank'],instruction=op,owner='PnHudCancelLife',native_evidence=row))
 death_epochs=[]
 for e in epochs:
  pub=e['dma']['publication'];body=pub.get('body');source=body and body.get('source',{})
  if source and source.get('body_family')=='native-death':
   assert source['variant']==1 and source['physical_chr']==892 and e['chr_banks'][0]==892
   assert e['start_hardware_exact_source']and e['dma_finished_before_start']and e['dma']['data_writes']==256
   death_epochs.append(dict(frame=e['start']['frame'],publication=pub['id'],DMA=e['dma']['id'],generation=pub['generation'],source=source['label'],physical_chr=e['chr_banks'][0],exact256=True,body_row=e.get('body_row')))
 assert len(death_epochs)>=100
 prefix={};bindings=[]
 for f in sorted(a.old_run.glob('frame-*.argb')):
  assert sha(f)==sha(a.run/f.name),f.name;bindings.append(dict(name=f.name,sha256=sha(f)))
 prefix['actual_RGB_frames_equal']=len(bindings)
 for name in ['inputs.csv','trace.csv']:
  old=list(csv.DictReader((a.old_run/name).open()));new=list(csv.DictReader((a.run/name).open()));assert new[:len(old)]==old,name;prefix[name]=dict(rows_equal=len(old))
 for name in ['lifecycle-events.jsonl','scroll-events.jsonl','hud-events.jsonl','oam-bus.jsonl','epochs.jsonl','body-writes.jsonl']:
  old=readrows(a.old_run/name);new=readrows(a.run/name);assert new[:len(old)]==old,name;prefix[name]=dict(parsed_prefix_rows_equal=len(old))
 evidence=dict(passed=False,native_run=True,launches=1,retries=0,worker_released=True,ROM_sha256=result['ROM_sha256'],failure='Actual prelease source blank tile',failure_capture_frame=813,
               lifecycle_result=result,first_correct_to_wrong_HUD=dict(correct514=before,wrong515=bad),first_wrong_owners=instruction,
               first_wrong_death_font_write=badfont,restart_pending_admission=pending,restart_pending_cancel=pending_cancel,
               first_stale_label_PPU_write=stale_write,restart_visible_start=finalstart,lifecycle_events=life,
               death_epochs=death_epochs,death_record_admissions=sum(x['kind']=='qualified-death-record-admission'for x in bus),prefix=prefix,
               regular_raw_frames=len(list(a.run.glob('frame-*.argb'))),capture_only_failure_frame='capture-scroll-000813.argb',
               classification='Visible ROM defect: cancellation clears the HUD font lease while committed or queued custom label tiles remain. Death515 and restart813 display native glyphs for custom label indices. No relaxation of blank/font guards.',
               limits='One failed bounded death run. Actual death/life decrement/restart are observed, but all5terminalcomponents are absent and45fresh updates are not certified. Old negatives and menu success stay separate. No native retry/area/adoption.')
 (a.output/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n');(a.output/'prefix-RGB.json').write_text(json.dumps(bindings,indent=2)+'\n')
 chosen=[512,514,515,520,528,536,548,580,612,634,635,638,640,642,655,800,810,811,812,813]
 sheet=Image.new('RGB',(5*256,4*260),'#202020');d=ImageDraw.Draw(sheet);samples=[]
 for i,n in enumerate(chosen):
  f=a.run/('capture-scroll-000813.argb'if n==813 else f'frame-{n:06d}.argb');im=Image.frombytes('RGBA',(256,240),f.read_bytes(),'raw','BGRA').convert('RGB');xy=(i%5*256,i//5*260);sheet.paste(im,(xy[0],xy[1]+20));d.text(xy,str(n),fill='white');samples.append(dict(frame=n,path=str(f),sha256=sha(f)))
 sheet.save(a.output/'selected-full-PPU.png');Image.frombytes('RGBA',(256,240),(a.run/'capture-scroll-000813.argb').read_bytes(),'raw','BGRA').save(a.output/'failure813.png')
 (a.output/'selected-frames.json').write_text(json.dumps(samples,indent=2)+'\n')
 files=set(f.resolve()for f in a.run.iterdir()if f.is_file())|set(f.resolve()for f in a.output.iterdir()if f.is_file())
 ledger=json.loads((a.ready/'manifest.json').read_text())
 for f,h in ledger.items():assert sha(f)==h;files.add(Path(f).resolve())
 files.add((a.ready/'proof.json').resolve());files.add((a.ready/'manifest.json').resolve());files.add(Path(__file__).resolve())
 for f in a.old_run.iterdir():
  if f.is_file():files.add(f.resolve())
 manifest={str(f):sha(f)for f in sorted(files,key=str)};(a.output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 q=dict(passed=False,native_run=True,launches=1,retries=0,worker_released=True,ROM_sha256=result['ROM_sha256'],
        original_failures_preserved=True,evidence_sha256=sha(a.output/'evidence.json'),ready_sha256=sha(a.ready/'proof.json'),
        selected_whole_PPU_frames=20,human_visual_review=False,manifest_bindings=len(manifest),manifest_sha256=sha(a.output/'manifest.json'),
        prefix=prefix,limits=evidence['limits'])
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2));print('proof_sha256='+sha(a.output/'proof.json'))


if __name__=='__main__':main()
