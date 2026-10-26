"""Freeze all-ring source ownership, real symbol exceptions, unchanged banks and flag-off builds."""
from pathlib import Path
import argparse,concurrent.futures,difflib,hashlib,json,re,shutil,subprocess,sys
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'cv3-remaining-current50b-v1/baseline-source'
HELD=D/'cv3-remaining-resident-v4/qualified-v1/source-final'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def bank(b,n):return b['raw'][16+n*8192:16+(n+1)*8192]
def body(s,name):return s[s.index('.proc '+name+'\n'):s.index('.endproc',s.index('.proc '+name+'\n'))]
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);stage=a.output/'source-final';shutil.copytree(a.prepared/'source',stage)
 old,new=load(a.prepared/'baseline.nes'),load(a.prepared/'candidate.nes');assert sha(a.prepared/'baseline.nes')=='0802527d8a2e0cf8f9584e854d6dd263b72e330c3c89d30921abddc1b10c5790'
 oq,nq=qualified(a.prepared/'baseline.nes'),qualified(a.prepared/'candidate.nes');deltas={k:(v,nq.get(k))for k,v in oq.items()if nq.get(k)!=v};owners={'Cv3FxCancel','Cv3FxBatEnter','Cv3FxSpawn','Cv3FxMusicInit','Cv3FxTick','Cv3NoiseSceneReset'};assert len(deltas)==17 and all(len(k)==2 and k[0]in owners for k in deltas)
 refs=[]
 for f in(stage/'src').rglob('*'):
  if not f.is_file()or f.suffix not in['.s','.inc']:continue
  text=f.read_bytes().decode()
  for scope,name in deltas:
   for m in re.finditer(re.escape(scope+'::'+name)+r'\b',text):refs.append(dict(path=f.relative_to(stage).as_posix(),reference=m[0]))
 assert not refs,refs
 for name in ['Cv3FxOwnerInit','Cv3FxTick','Cv3FxMusicInit','Cv3FxSpawn','Cv3FxBatEnter','Cv3FxCancel','Cv3NoiseSceneReset','Cv3FxService','Cv3SaveAudioZp','Cv3RestoreAudioZp']:
  assert address(old,name)==address(new,name)and old['syms'][name]['size']==new['syms'][name]['size'],name
 for name in ['Cv3FxService','Cv3SaveAudioZp','Cv3RestoreAudioZp','Cv3FxResidentDispatch','Cv3FxResidentNoise']:
  n=int(old['syms'][name]['size'],0);assert old['raw'][location(old,name):location(old,name)+n]==new['raw'][location(new,name):location(new,name)+n],name
 frames=[n for n in old['syms']if re.fullmatch(r'Cv3Fx(?:1F|13|15|24|21|2F)(?:Noise|Pulse)Frame\d{3}',n)]
 for name in frames:
  assert address(old,name)==address(new,name)and location(old,name)==location(new,name)
  start=location(old,name);size=int(old['syms'][name]['size'],0)if'size'in old['syms'][name]else 1;assert old['raw'][start:start+size]==new['raw'][start:start+size]
 changed_banks=[dict(bank=i,bytes=sum(x!=y for x,y in zip(bank(old,i),bank(new,i))))for i in range(128)if bank(old,i)!=bank(new,i)];assert {x['bank']for x in changed_banks}=={28,29,82,84};assert old['raw'][:16]==new['raw'][:16]and old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
 # Complete source-level slab inventory, including the generated NSF input.
 lane=[];dynamic=[]
 for tree in ['src','audio','inc','build/generated/guest-audio']:
  for f in(stage/tree).rglob('*'):
   if not f.is_file()or f.suffix not in['.s','.inc']:continue
   for line,text in enumerate(f.read_bytes().decode().splitlines(),1):
    if'RgAudioZp'not in text:continue
    rec=dict(path=f.relative_to(stage).as_posix(),line=line,text=text.strip(),sha256=sha(f));lane.append(rec)
    if re.search(r'RgAudioZp(?:\+Offset)?\s*,[xy]',text,re.I)or'RgAudioZp+Offset'in text:dynamic.append(rec)
 s=(stage/'src/cv3_remaining_source_fx.s').read_text();producer=body(s,'Cv3FxProducer');command=body(s,'Cv3FxQueueCommand');owner=body(s,'Cv3FxOwnerInit')
 assert all(x not in producer+command for x in ['sta AvAudioRequest','sta Cv3FxOwned','sta Cv3FxPending','sta Cv3NoiseActive','sta Cv3FxNoiseID','sta Cv3FxPulseID'])
 assert 'sta Cv3FxQueue,y\n inc Cv3FxQueueHead'in producer and 'sta Cv3FxQueue,y\n inc Cv3FxQueueHead'in command
 assert 'sta Cv3FxQueueHead'not in s and 'lda Cv3FxQueueHead\n sta Cv3FxQueueTail'in owner
 assert'ldx #19\nLoop:sta Cv3FxNoiseID,x\n dex'in owner and'sta Cv3DmcPriority'not in owner
 # Existing wrappers are the only dynamic slab accesses: selected CV1 uses
 #24, Contra/Zelda17 and Gradius7. Imported driver channel RAM is the distinct
 #512-byte RgAudioRam allocation; no imported source names this lane directly.
 wrappers=(stage/'src/roster_audio.s').read_text();vg=(stage/'src/gradius_audio.s').read_text();assert'ZpCount=24'in wrappers and'ZpCount=17'in wrappers and'ldx #6\nResetPointers:'in vg
 assert all(r['path']in['src/roster_audio.s','src/gradius_audio.s']for r in dynamic),dynamic
 alias_old=[]
 for f in(HELD/'src').rglob('*'):
  if f.suffix not in['.s','.inc']or not f.is_file():continue
  for line,text in enumerate(f.read_bytes().decode().splitlines(),1):
   m=re.match(r'\s*(\w+)\s*=\s*RgAudioZp\+(\d+)',text)
   if m:alias_old.append(dict(symbol=m[1],offset=int(m[2]),path=f.relative_to(HELD).as_posix(),line=line,text=text))
 assert max(r['offset']for r in alias_old)==55
 source_refs=[]
 for f in(stage/'src').rglob('*'):
  if f.is_file()and f.suffix in['.s','.inc']:
   for i,t in enumerate(f.read_text().splitlines(),1):
    if'Cv3FxProducer'in t or'Cv3FxQueueCommand'in t or'Cv3FxCancel'in t or'Cv3FxBatEnter'in t:source_refs.append(dict(path=f.relative_to(stage).as_posix(),line=i,text=t.strip()))
 lane_report=dict(passed=True,existing_lane_address=address(new,'RgAudioZp'),existing_lane_size=160,old_numeric_aliases=alias_old,old_max_alias=55,all_RgAudioZp_source_mentions=lane,dynamic_mentions=dynamic,dynamic_bound=dict(CV1=24,Contra=17,Zelda=17,Gradius=7),new_aliases=dict(head=56,tail=57,overflow=58,queue=[64,128]),selected_family_exclusive=True,source_refs=source_refs,queue_capacity=64,source_graph_capacity_note='Main IdleLoop permits at most one catch-up after a lag NMI; audio advances on every lag NMI. Gameplay release branches emit at most3 projectiles per release, pool4. A full proof for every menu/scene/mute owner is separate from this layout audit; full guard rejects without overwrite. Menu repeated CANCEL bounded by separately proved idempotency.',no_global_gameplay_capacity_certification=True)
 (a.output/'lane-ownership.json').write_text(json.dumps(lane_report,indent=2)+'\n')
 files=[];changed=[];incremental=[];patch='';incpatch=''
 for f in sorted(stage.rglob('*')):
  if not f.is_file()or'__pycache__'in f.parts:continue
  rel=f.relative_to(stage)
  if rel.parts[0]in['build','docs','tests']or rel.parts[:2]==('tools','audit'):continue
  after=f.read_bytes();base=BASE/rel;before=base.read_bytes()if base.exists()else None;held=HELD/rel;prior=held.read_bytes()if held.exists()else None;files.append(dict(path=rel.as_posix(),sha256=digest(after),adopted50b_sha256=digest(before)if before is not None else None,held0802_sha256=digest(prior)if prior is not None else None))
  if after!=prior:
   incremental.append(dict(path=rel.as_posix(),sha256=digest(after),old_sha256=digest(prior)if prior else None));incpatch+=''.join(difflib.unified_diff(prior.decode().splitlines(True)if prior is not None else[],after.decode().splitlines(True),fromfile='a/'+rel.as_posix(),tofile='b/'+rel.as_posix()))
  if after==before:continue
  rec=dict(path=rel.as_posix(),sha256=digest(after),bytes=len(after),old_sha256=digest(before)if before else None,EOL='CRLF'if b'\r\n'in after else'LF')
  if before is not None:
   git=subprocess.run(['git','show','HEAD:'+rel.as_posix()],cwd=ROOT,capture_output=True,check=True).stdout;assert git.replace(b'\r\n',b'\n')==before.replace(b'\r\n',b'\n');rec.update(original_Git_sha256=digest(git),original_Git_EOL='CRLF'if b'\r\n'in git else'LF');assert rec['EOL']==rec['original_Git_EOL']
  changed.append(rec);patch+=''.join(difflib.unified_diff(before.decode().splitlines(True)if before is not None else[],after.decode().splitlines(True),fromfile='a/'+rel.as_posix()if before is not None else'/dev/null',tofile='b/'+rel.as_posix()))
 assert len(changed)==8 and {r['path']for r in incremental}=={'src/cv3_combat.s','src/cv3_source_audio.s','src/cv3_remaining_source_fx.s'}
 (a.output/'all-deployable-files.json').write_text(json.dumps(files,indent=2)+'\n');(a.output/'implementation.patch').write_text(patch,newline='\n');(a.output/'incremental-from0802.patch').write_text(incpatch,newline='\n')
 def build(name,flag=None):
  cmd=[sys.executable,str(stage/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/(name+'.nes'))]
  if flag:cmd+=['--flag-off',flag]
  with(a.output/(name+'.host.log')).open('w')as log:r=subprocess.run(cmd,cwd=stage,stdout=log,stderr=subprocess.STDOUT)
  assert not r.returncode,(name,(a.output/(name+'.host.log')).read_text()[-5000:]);return sha(a.output/(name+'.nes'))
 assert build('candidate')==sha(a.prepared/'candidate.nes')
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:ordinary=list(pool.map(lambda n:dict(mapper=n,sha256=build('ordinary-'+n,n)),['mmc3','mmc5']))
 assert ordinary==[dict(mapper='mmc3',sha256='d444cac88e13fa02b29ad16100b8f08fa565ba90f8cedde192de43fb2dc8f3eb'),dict(mapper='mmc5',sha256='f4ffd2483c51daa4d60bb575da2da8c4d817692cda407611c243031f67520833')]
 result=dict(passed=True,accepted=False,status='SOURCE_LAYOUT_FLAGOFF_FROZEN_PROTOCOL_CPU_SEPARATE',ROM_sha256=sha(a.prepared/'candidate.nes'),held0802_sha256=sha(a.prepared/'baseline.nes'),adopted_parent='50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363',source_files=changed,incremental_files=incremental,all_deployable_files=len(files),all_deployable_files_sha256=sha(a.output/'all-deployable-files.json'),implementation_patch_sha256=sha(a.output/'implementation.patch'),incremental_patch_sha256=sha(a.output/'incremental-from0802.patch'),legitimate_private_symbol_exceptions=[dict(scope=list(k),old=v[0],new=v[1],reason='Removed torn-main publication or moved genuine NMI dispatch branch. No external source reference; no fake alias.')for k,v in sorted(deltas.items())],retained_old_qualified_symbols=len(oq)-len(deltas),source_packet_PC_count=len(frames),service_Save_Restore_resident_payload_byte_exact=True,changed_banks=changed_banks,all_other_banks_CHR_header_exact=True,new_allocated_RAM_CHR=0,lane_ownership_sha256=sha(a.output/'lane-ownership.json'),ordinary_flagoff=ordinary,scope='Private exact source/layout/flag-off build only; lifecycle/protocol/ABI/ordinary/source-IRQ/cost receipts required before any native request. No cadence/lag/adoption claim.',tool_sha256=sha(__file__))
 (a.output/'qualification.json').write_text(json.dumps(result,indent=2)+'\n');shutil.copyfile(__file__,a.output/Path(__file__).name);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
