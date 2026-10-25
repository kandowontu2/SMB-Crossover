from pathlib import Path
import csv,hashlib,json
from PIL import Image,ImageDraw
D=Path(__file__).resolve().parent;V=D/'mmc3-static-call-v37';C=V/'direct-sophia-v1/direct-sophia-easy';O=V/'sophia-review-v1';O.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cap=json.loads((C/'proof.json').read_text());borrow=json.loads((V/'borrowed-sophia-v1/proof.json').read_text());native=json.loads((V/'native-sophia-v2/proof.json').read_text())
assert cap['passed']and borrow['passed']and native['passed']
assert cap['ROM_sha256']==borrow['ROM_sha256']==native['ROM_sha256']==sha(V/'candidate.nes')
observed=set(borrow['runs'][0]['borrowed_frames'])
trace=list(csv.DictReader((C/'trace.csv').open()));active=[z for z in trace if z['engine']=='8'and z['mode']=='1'and z['task']=='3'and z['world']==z['level']=='0']
pairs=[(a,b)for a,b in zip(active,active[1:])if int(b['frame'])==int(a['frame'])+1]
violations=[]
for a,b in pairs:
 dx=abs(int(b['x'])-int(a['x']));dc=int(b['camera'])-int(a['camera']);assert 0<=dc<=4
 if dx>8:
  assert {int(a['frame']),int(b['frame'])}&observed
  violations.append(dict(previous=int(a['frame']),current=int(b['frame']),raw_dx=dx))
assert len(violations)==2*len(observed)==10
visible=[z for z in csv.DictReader((C/'scroll-writes.csv').open())if z['engine']=='8'and z['mode']=='1'and z['task']=='3'and z['world']==z['level']=='0'and z['screenDisabled']=='0'and z['renderingEnabled']=='1']
assert len(visible)>1000 and all(z['scanline']=='31'and z['writerBank']=='254'for z in visible)
idx=list(csv.DictReader((C/'direct-frame-index.csv').open()));assert sha(C/'direct-frame-index.csv')==cap['frame_index_sha256']
for row in idx:assert sha(C/'frames'/(row['frame'].zfill(6)+'.png'))==row['PNG_sha256']
def sheet(name,frames,cols):
 image=Image.new('RGB',(cols*256,((len(frames)+cols-1)//cols)*260),(24,28,36));draw=ImageDraw.Draw(image)
 for i,f in enumerate(frames):
  image.paste(Image.open(C/'frames'/('%06d.png'%f)).convert('RGB'),(i%cols*256,i//cols*260+20));draw.text((i%cols*256+4,i//cols*260+3),'Sophia '+str(f),fill='white')
 p=O/(name+'.png');image.save(p);return dict(path=str(p),sha256=sha(p),frames=frames)
sheets=[sheet('overview',[int(idx[round(i*(len(idx)-1)/23)]['frame'])for i in range(24)],6),sheet('specific-query-origins',[f+d for f in sorted(observed)for d in[-1,0,1]],3)]
pole=next(int(z['frame'])for z in trace if z['engine']=='4'and z['world']==z['level']=='0')
sheets.append(sheet('loading-start-pole',[408,432,456]+[native['runs'][0]['result']['stage_entries']['0-0']+d for d in[0,1,2]]+[pole+d for d in[-2,-1,0,1,2,3]],6))
q=dict(passed=True,goal_complete=False,ROM_sha256=cap['ROM_sha256'],independent_direct_capture_proof_sha256=sha(C/'proof.json'),positive_query_origin_proof_sha256=sha(V/'borrowed-sophia-v1/proof.json'),native_route_proof_sha256=sha(V/'native-sophia-v2/proof.json'),specific_tagged_query_frames=sorted(observed),all_raw_spikes_identified=violations,all_completed_updates_bounded=borrow['runs'][0],visible_scanline31_writes=len(visible),physical_frames=len(idx),human_visual_review='pending',sheets=sheets,scope='Specific current-hash Sophia evidence: five raw physical-frame origins are positively identified actual block probes with nearby saved body origins; every native body draw and completed loop restores the body and obeys original motion bounds. Independent exact inputs/trace and verified actual PPU pixels retained. Original generic raw-motion review failure remains retained. No blanket queried-origin waiver, source-perfect graphics/audio, full-roster or all-powerup claim.')
(O/'proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(dict(passed=True,physical_frames=len(idx),specific_queries=sorted(observed),sheets=[z['path']for z in sheets])),flush=True)
