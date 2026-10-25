from pathlib import Path
import csv,hashlib,importlib.util,json,subprocess,sys
from PIL import Image,ImageDraw
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;V=D/'mmc3-ship-state-v24';O=V/'direct-v1';O.mkdir(exist_ok=False);ROM=V/'candidate.nes'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();source=V/'native-routes-v1/proof.json';q=json.loads(source.read_text());assert q['passed']and q['complete']and len(q['runs'])==4
driver=D/'mmc3-flag-fix-v23/physical-replay-v3/capture-mmc3.py';assert sha(driver)=='6aa7ad84fada41e9e8a313fcbfd80a958e204ac297e5a6deb78e7c7ba121103c'
helper=R/'build/verification/agent49g-samus-crouch-fix-proposal-b/image.py';sp=importlib.util.spec_from_file_location('img',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im);image=im.Image(ROM);irq=image.hook('IrqScrollSplit')
report=dict(complete=False,passed=False,goal_complete=False,ROM_sha256=sha(ROM),source_proof_sha256=sha(source),capture_driver_sha256=sha(driver),IRQ_hook=irq,runs=[],scope='Four independent fixed-input native MMC3 full1-1 replays, every actual PPU frame/RGB/index/gzip and exact CPU trace; original world<=8, camera0..4 and visible scanline31 bounds. Actual compiled IRQ writer bank replaces the MMC5 bank number; native mapper-specific body/cache/bank proof is used, never a fabricated MMC5 CHR proof. Sampled visual sheets and bounded route checks are not exhaustive source fidelity or full-roster mapper qualification.')
for row in q['runs']:
 name,mode=row['identity'],row['mode'];key=name+'-'+mode;route=Path(row['folder']);assert sha(route/'manifest.json')==row['manifest_sha256'];out=O/('direct-'+key)
 with(O/('capture-'+key+'.log')).open('w')as log:p=subprocess.run([sys.executable,str(driver),'--rom',str(ROM),'--route',str(route),'--output',str(out)],cwd=R,stdout=log,stderr=subprocess.STDOUT)
 entry=dict(identity=name,mode=mode,folder=str(out),capture_exit=p.returncode,passed=False);report['runs'].append(entry)
 if p.returncode==0:
  cap=json.loads((out/'proof.json').read_text());assert cap['passed']and cap['ROM_sha256']==sha(ROM)and cap['mapper_cache_guard']['passed']and cap['result']['cleared']and cap['result']['deaths']==0
  for n in ('inputs.csv','trace.csv'):assert(out/n).read_bytes()==(route/n).read_bytes(),n
  index=out/'direct-frame-index.csv';assert sha(index)==cap['frame_index_sha256'];frames=list(csv.DictReader(index.open()));assert [int(z['frame'])for z in frames]==list(range(200,cap['result']['frames']))
  for z in frames:assert sha(out/'frames'/(z['frame'].zfill(6)+'.png'))==z['PNG_sha256']
  trace=list(csv.DictReader((out/'trace.csv').open()));active=[z for z in trace if z['engine']=='8'and z['mode']=='1'and z['task']=='3'and z['world']==z['level']=='0'];pairs=[(a,b)for a,b in zip(active,active[1:])if int(b['frame'])==int(a['frame'])+1];assert len(pairs)>1000
  world=max(abs(int(b['x'])-int(a['x']))for a,b in pairs);camera=[int(b['camera'])-int(a['camera'])for a,b in pairs];assert world<=8 and min(camera)>=0 and max(camera)<=4
  visible=[z for z in csv.DictReader((out/'scroll-writes.csv').open())if z['engine']=='8'and z['mode']=='1'and z['task']=='3'and z['world']==z['level']=='0'and z['screenDisabled']=='0'and z['renderingEnabled']=='1'];assert visible and all(z['scanline']=='31'and int(z['writerBank'])==irq['physical_bank']for z in visible)
  selected=[int(frames[round(i*(len(frames)-1)/23)]['frame'])for i in range(24)];sheet=Image.new('RGB',(1536,1040),(24,28,36));draw=ImageDraw.Draw(sheet)
  for i,f in enumerate(selected):sheet.paste(Image.open(out/'frames'/('%06d.png'%f)).convert('RGB'),(i%6*256,i//6*260+20));draw.text((i%6*256+4,i//6*260+3),key+' '+str(f),fill='white')
  overview=O/('overview-'+key+'.png');sheet.save(overview)
  start=cap['result']['stage_entries']['0-0'];pole=next(int(z['frame'])for z in trace if z['engine']=='4'and z['world']==z['level']=='0');chosen=[start+i for i in (0,1,2,3,4,5)]+[pole+i for i in(-2,-1,0,1,2,3)];sheet=Image.new('RGB',(1536,520),(24,28,36));draw=ImageDraw.Draw(sheet)
  for i,f in enumerate(chosen):sheet.paste(Image.open(out/'frames'/('%06d.png'%f)).convert('RGB'),(i%6*256,i//6*260+20));draw.text((i%6*256+4,i//6*260+3),key+' '+str(f),fill='white')
  detail=O/('start-pole-'+key+'.png');sheet.save(detail)
  entry.update(passed=True,capture_proof_sha256=sha(out/'proof.json'),max_world_step=world,min_camera_step=min(camera),max_camera_step=max(camera),visible_scanline31_writes=len(visible),visible_irq_writer_bank=irq['physical_bank'],overview=str(overview),overview_sha256=sha(overview),start_pole_sheet=str(detail),start_pole_sha256=sha(detail),physical_frames=len(frames),source_manifest_sha256=sha(route/'manifest.json'))
 (O/'progress.json').write_text(json.dumps(report,indent=2));print(json.dumps(entry),flush=True)
report.update(complete=True,passed=all(r['passed']for r in report['runs']));(O/'proof.json').write_text(json.dumps(report,indent=2));(O/'progress.json').write_text(json.dumps(report,indent=2))
