"""Root independent frozen-route admission. No native launch or runtime edits."""
from pathlib import Path
import collections,csv,datetime,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
rows=lambda p:list(csv.DictReader(Path(p).open(newline='')))
def catalogue(p,expected):
 assert sha(p)==expected
 c=read(p)
 for n,v in c.items():
  q=R/n;assert q.stat().st_size==v['bytes'] and sha(q)==v['sha256'],n
 return len(c)
def hooks(p):
 b=read(p);im=b.get('image',b.get('ROM'));rom=Path(im['rom']['path']).read_bytes()
 for v in b['hooks'].values():
  assert list(rom[v['rom_offset']:v['rom_offset']+8])==v['bytes'] and (v['rom_offset']-16)//8192==v['physical_bank']
 return len(b['hooks'])
def oam_review(D):
 render=rows(D/'render.csv');positive={int(z['frame']):z for z in render if int(z['dmaCount'])};oam=rows(D/'oam.csv')
 assert [int(z['frame'])+1 for z in oam]==list(positive) and len(oam)==sum(int(z['dmaCount'])for z in render)
 assert [int(z['frame'])for z in render]==list(range(500,27059)) and all(z['behaviorVersion']=='0'for z in render)
 for z in oam:
  raw=bytes.fromhex(z['oamHex']);assert len(raw)==256
  visible=hud=0;edges=collections.Counter()
  for i in range(0,256,4):
   y=raw[i]+1
   if y<240:
    visible+=1;hud+=y<32;first,last=max(32,y),min(240,y+16)
    if first<last:edges[first]+=1;edges[last]-=1
  maximum=count=0
  for y in range(32,240):count+=edges[y];maximum=max(maximum,count)
  assert(visible,hud,maximum)==(int(z['visible']),int(z['hudSprites']),int(z['maxSprites']))
  assert int(positive[int(z['frame'])+1]['maxSprites'])==maximum
 return dict(render_frames=len(render),DMA_snapshots=len(oam),flagged_lagNmi=sum(int(z['lagNmi'])!=0 for z in render),APU_writes=sum(int(z['apuWrites'])for z in render))
def main():
 out=V/'root49-current-route-review-cm.json';assert not out.exists()
 H=V/'specialist-mario-luigi-scrooge-current-g-a'
 assert sha(H/'review-e.py')=='c517364097fb32bf97ee9289c9091023c2024919abec55f2931cb2448ae59a17'
 p=subprocess.run([sys.executable,str(H/'review-e.py'),'--catalogue','milestone-freeze-j.json','--catalogue-sha256','3d9b0924354f960b2a712e5c4cbefc32ace64fb6779e9cbd4af27d0d02a52b4b','--handoff','milestone-handoff-j.json','--handoff-sha256','dbe7c1fba625f744d11accbbbcef22d39440fa8010ff7977b508428f08569ca7'],cwd=R,capture_output=True,text=True)
 assert p.returncode==0,p.stdout+p.stderr
 ml= json.loads(p.stdout)
 F=V/'agent-lsr-link-current-f-route-a';G=V/'agent-lsr-current-g-roster-a';P=G/'link-a-proof'
 assert sha(F/'freeze.json')=='6f2670544de700f4ba42d75dfb6e58b8d6301ebbe9fe2e90a79e18e69e65d25f'
 assert sha(F/'route-review.json')=='79b8e98a3c6d5378f6ac1207c9c615a9add0b3038777d147ec24f79da0f72314'
 nf=catalogue(F/'file-catalog.json','d510dc7aebfb84230d5f3fc2016b01b9b1d203153752dc8285c3e183accdf786');assert nf==1915
 assert sha(P/'freeze.json')=='b3547a01a0a54673a951e39b64ad60b7f8182fb6382dcc26dbb0b07be2152bfd'
 assert sha(P/'report.json')=='cad871a73040e661e4ae0c56d47a6c3a0ce7aef4aec1efefe9e6bb8228d6d50d'
 ng=catalogue(P/'catalog.json','d908bd8a2f012c5edd707f979f51e01e7b5bdb5a807b8b854e364fbafdd1d039');assert ng==46
 fs=Path(read(F/'route-review.json')['scope']['source_directory'])
 fc=read(F/'source-catalog.json');assert len(fc)==457 and all(sha(fs/n)==h for n,h in fc.items())
 for n,h in read(F/'freeze.json')['artifacts_exact'].items():assert sha(n)==h
 cp=R/'build/checkpoints/roster-audit-v49-samus-head-axis-g/manifest.json';assert sha(cp)=='feacfe9cf513d6c57dde8a4f2990e0bbd6c14ecda533d971747ad0011cee0fd0';c=read(cp);gs=Path(c['source_directory'])
 assert len(c['source_hashes'])==458 and all(sha(gs/n)==h for n,h in c['source_hashes'].items())
 assert len(c['generated11'])==11 and all(sha(gs/'build/generated'/n)==h for n,h in c['generated11'].items())
 for b in c['builds']:
  for v in b['artifacts'].values():assert sha(R/v['frozen_path'])==v['sha256']
 A=R/'build/roster-through-2-2/lsr-link-f-ai-4-v0-mmc3';B=R/'build/roster-through-2-2/lsr-link-f-aj-4-v0-mmc3';D=R/'build/roster-through-2-2/lsr-current-g-link-a-4-v0-mmc3'
 streams=['inputs.csv','trace.csv','events.csv','render.csv','oam.csv','chr.csv','scroll-writes.csv','audio-events.csv','stomp-events.csv']
 hashes={}
 for n in streams:
  assert (A/n).read_bytes()==(B/n).read_bytes()==(D/n).read_bytes(),n
  hashes[n]=sha(D/n)
 assert (B/'final-ram.csv').read_bytes()==(D/'final-ram.csv').read_bytes()
 endpoints=rows(D/'final-ram.csv');ram={int(z['address']):int(z['value'])for z in endpoints}
 assert len(ram)==len(endpoints)==10240 and set(ram)==set(range(2048))|set(range(0x6000,0x8000)) and all(0<=v<256 for v in ram.values())
 rf=read(F/'route-review.json')['endpoint']['fields']
 for n,v in rf.items():assert ram[v['address']]==v['value'],n
 for d,romhash in [(A,'ae0f981a8846238185d2d69549accf69f68b779832cafa7dd35bc431b00b09ca'),(B,'ae0f981a8846238185d2d69549accf69f68b779832cafa7dd35bc431b00b09ca'),(D,'151f3f6e8aa8753fce088c3f2ba6815df7290c1ec3b959018ca4717ae8f491cc')]:
  m=read(d/'manifest.json');q=m['result'];assert m['rom_sha256']==romhash and m['controller_only'] and m['full_frame_audit'] and not m['memory_or_register_writes']
  assert q['cleared'] and q['all_six_stages'] and q['frames']==27058 and q['polls']==27057 and q['deaths']==0 and q['failure'] is None
  assert not m['config']['record'] and read(d/'ordinary-identity.json')==dict(selected=4,mode=0,outlinesOff=1,variant=0)
  z=read(d/'stomp-summary.json');assert z['illegal_guest_events']==z['resident_opcode_mismatches']==0
  for n in ['policy.lua','harness.lua','audit.lua']:
   body=(d/n).read_text();assert not any(x in body for x in ['emu.write(','emu.setState(','emu.loadSavestate'])
  if d in [B,D]:assert m['verified_through_2_2'] and m['config']['replay'] and not m['config']['prefix'] and sha(m['config']['replay'])==hashes['inputs.csv']
 assert read(G/'actual-link-a-mmc3.json')['exit']==0
 trace=rows(D/'trace.csv');inputs=rows(D/'inputs.csv');assert len(trace)==27058 and len(trace[0])==21 and len(inputs)==27057
 real=[z for z in trace if (z['world'],z['level'],z['mode'],z['task'],z['engine'])==('1','2','1','3','8')];assert len(real)==25 and real[0]['x']=='40' and real[-1]['x']=='62'
 stage_entries={}
 for z in trace:
  if z['engine']=='8'and z['mode']=='1'and z['task']=='3':stage_entries.setdefault(z['world']+'-'+z['level'],int(z['frame']))
 assert set(stage_entries)>={'0-0','0-1','0-2','0-3','1-0','1-1','1-2'}
 fh=hooks(F/'binding-mmc3.json');gh=hooks(G/'binding-link-mmc3.json');hardware=oam_review(D)
 result=dict(status='PASS_ROOT_CURRENT_G_MARIO_LUIGI_BOTH_MAPS_AND_LINK_MMC3',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),script_sha256=sha(__file__),Mario_Luigi=ml,Link=dict(F_catalog_files=nf,G_catalog_files=ng,F_sources=457,G_sources=458,G_generated=11,F_hooks=fh,G_hooks=gh,source_checkpoints=dict(F=read(F/'route-review.json')['scope']['checkpoint']['sha256'],G=sha(cp)),result=read(D/'result.json'),stage_entries=stage_entries,whole_nine_literal_F_candidate_fixed_G_fixed=hashes,endpoint=dict(bytes=10240,sha256=sha(D/'final-ram.csv'),identity_fields=rf),actual_2_3=dict(controls=25,x=[40,62]),hardware=hardware,limits=['G MMC3 only for Link; F original candidate/fixed proof retains F scope. No MMC5/Hard inference.','Single fixed endpoint RAM literal F/G. No intermediate or candidate whole-RAM equality claim.','No dedicated complete Link accepted-ground-A log; final pipe is specifically observed, not universal support or source-perfect certification.','Native hardware observations are not completed frame-by-frame final audio/video inspection.','All14/all66 arsenal, acquisition/upgrade/SFX/media and remaining-route obligations remain open.']),accepted_release=False,goal_complete=False)
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],file=str(out.relative_to(R)),sha256=sha(out),Link_hardware=hardware)))
if __name__=='__main__':main()
