"""Freeze remaining-five source readiness and generic result-parser mode models."""
from pathlib import Path
import argparse,copy,csv,difflib,hashlib,json,shutil
from final_item_abilities_remaining731_run_v1 import collect,verify_manifest,PROFILES
from final_item_abilities_static_prepare_v2 import CURRENT,D,ROOT
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 ready=json.loads((a.ready/'proof.json').read_text());assert ready['prepared']and not ready['native_run']and not ready['native_granted']and ready['ROM_sha256']==CURRENT
 assert sha(a.ready/'manifest.json')==ready['manifest_sha256'];count=verify_manifest(a.ready/'manifest.json')
 assert len(ready['profiles'])==5 and sum(q['planned_ability_cases']for q in ready['profiles'])==52
 for q in ready['profiles']:assert not(Path(q['output'])/'launch.json').exists()and not(Path(q['output'])/'proof.json').exists()
 put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n')
 model=a.output/'HOST-MODEL-ONLY-not-native';model.mkdir()
 with(model/'actual-ppu.argb').open('wb')as f:f.truncate(101*256*240*4)
 with(model/'case-example.argb').open('wb')as f:f.truncate(256*240*4)
 with(model/'actual-ppu-index.csv').open('w',newline='')as f:
  w=csv.DictWriter(f,fieldnames=['ordinal','ppu_frame']);w.writeheader();w.writerows(dict(ordinal=i,ppu_frame=i)for i in range(1,102))
 with(model/'ability-dma-epochs.jsonl').open('w')as f:
  for i in range(1,102):
   f.write(json.dumps(dict(kind='completed-DMA-before-render-enable',id=i,page=2,start=dict(pc=0xe005,oamaddr=0,mask=0),complete=dict(oamaddr=0,mask=0),source=list(range(256)),hardware=list(range(256)),differences=[],writes=[dict(value=j,stamp=dict(oamaddr=j,mask=0))for j in range(256)]))+'\n')
   f.write(json.dumps(dict(kind='startFrame-hardware',completed_dma_id=i,hardware=list(range(256))))+'\n');f.write(json.dumps(dict(kind='actual-PPUMASK-write',scoped=True,enabling=True,safe=True,stamp=dict(scanline=-1,cycle=274)))+'\n')
 tests=[]
 for profile in ready['profiles']:
  cfg=json.loads((Path(profile['output'])/'config.json').read_text());assert(cfg['family'],cfg['hard'],cfg['mode_value'],len(cfg['abilities']))==PROFILES[profile['profile']]
  n=dict(passed=True,family=cfg['family'],hard=cfg['hard'],actual_mode_readback=cfg['mode_value'],abilities=[dict(q=q)for q in cfg['abilities']],physical_collections=[dict(transformCalls=60,ownerCalls=1)]*2,nmis=101,irq_scroll_stores=101,complete_dma_checks=101,hardware_chr_checks=1201,minSP=128)
  put(model/'native-abilities.json',n);put(model/'ppu-capture-native-result.json',dict(passed=True,frames=101,bytes=101*256*240*4,actual_mode_readback=cfg['mode_value'],original_done_seen=True))
  q=collect(model,cfg);assert q['passed'],q['errors'];tests.append(dict(profile=profile['profile'],kind='synthetic-valid-parser-input',passed=True,actual_parser_accept=True,not_native=True))
  n['actual_mode_readback']=1-cfg['mode_value'];put(model/'native-abilities.json',n);q=collect(model,cfg);assert not q['passed'];tests.append(dict(profile=profile['profile'],kind='opposite-mode-rejected',passed=True,actual_parser_accept=False,not_native=True))
 put(a.output/'host-parser-mode-models.json',dict(passed=True,native_run=False,host_model_only=True,tests=tests))
 old=ROOT/'tools/audit/final_item_abilities_pit731_run_v1.py';new=ROOT/'tools/audit/final_item_abilities_remaining731_run_v1.py'
 (a.output/'runner-delta.patch').write_text(''.join(difflib.unified_diff(old.read_text().splitlines(True),new.read_text().splitlines(True),fromfile='qualified-one-PitEasy',tofile='explicit-one-of-five-current731')),encoding='utf-8')
 report=ROOT/'docs/qa/final-item-abilities-remaining731-ready-2026-10-26.txt';assert not report.exists()
 lines=['Remaining five current731 acquired-ability source readiness,2026-10-26','',
 'PREPARED ONLY:zero native launches/grants/workers. No production/default/settings/Git edits.',
 'ROM '+CURRENT,'Readiness '+str(a.ready/'proof.json'),'Readiness SHA256 '+sha(a.ready/'proof.json'),
 'Manifest SHA256 '+sha(a.ready/'manifest.json'),str(count)+'bindings independently verified.','',
 'Exactly5profiles/52plans: PitHard10,RygarEasy12,RygarHard12,ScroogeEasy9,ScroogeHard9.',
 'Each command can launch only ONE named profile, once. No automatic next profile/retry.',
 'One owned sequential worker; runner refuses if two projecttestRunner workers already exist.',
 'No native launch is authorized by this preparation. ROOT review/explicit grant required.','']
 for q in ready['profiles']:
  lines +=[q['profile']+':numeric'+str(q['actual_mode_required'])+',plans'+str(q['planned_ability_cases'])+',scriptSHA '+q['script_sha256'],ready['commands'][q['profile']]]
 lines +=['','Exact per-profile source owners/linked PCs/bytes/lines and all setup:',str(a.ready/'seed-policies.json'),'SHA256 '+sha(a.ready/'seed-policies.json'),
 'Pit: type38hammer,6bothfacing/tierhits;lowtierrefusal;exactFE8000/60fuel/exhaust/release/groundrecharge.',
 'Rygar: native disk free/hit,bothfacings,tier40/64/88 extension/retraction,mirrored handanchor/realcatch;12plans per mode.',
 'Scrooge: groundpogo/release and airborne enemycontact bothfacings per tier;nativeFA2500bounce;9plans per mode. Tier is ordinaryhostprogression,not a new stronger cane.',
 '',
 'All actual731 template mechanics/controllers/10or12or9outcome assertions normalize BYTE-EXACT',
 'after removing only the same read-only fullPPU capture module qualified in PitEasy.32static',
 'memory callbacks,fullrange return dispatcherLAST;fullPPU record before originalstop.',
 'All5full generated Lua5.4 scripts load and execute3inactive mock capture epochs each.',
 'Numeric modes are explicit booleans+0/1 config and actual RAM readback is mandatory.',
 'Opposite actual mode is rejected in each of5host-only parser controls;5synthetic valid',
 'parser controls pass. These are NOT native receipts or real PPU/gameplay observations.',
 '',
 'Same original two real head/block/fullrise/no-premature-grant collections0→1→2 and',
 'two60-update transformations in eachprofile. Explicit post-rise collision alignment',
 'is retained. A physical prefix is not an unassisted route. B world/player/motion/',
 'fractions/facing/scroll/oldempty-pool/protection setup is controlled and disclosed.',
 'Pit/6Rygarhitcases use raised valid native GoombaID6/high1/defaultHP0 targets.',
 'Scrooge enemy target is introduced only under actualairborne/separated condition;',
 'groundpogo/free-disk cases have no target. No tier/fuel/flight/reach/returning/pogo',
 'outcome writes. Prior native catch/pogo/attack cleanup is asserted before setup.',
 '',
 'Full actual PPU/index,original case captures/events and raw256DMA/source/destination/',
 'perwriteOAMADDR/mask/PPUstamps remain. E005notcomplete;E008afterLDA/beforeSTA.',
 'Original actualbank/SP/fiveSMC/IRQ31/CHR/publication and scoped enable deadline retained.',
 'Actual image/contact/cleanup review remains separate after any newly granted execution.',
 'The unchanged inherited4000..4017counter includes4014/4016: report pureaudio subset',
 'separately,never infer SFX/waveform fidelity. Qualified PitEasy packet remains its own scope.',
 '',
 'Fresh isolated runtime from actualworker settings'+ready['environment']['worker_settings_sha256'],
 'User context freshlybound '+ready['environment']['user_context_sha256'],
 'doNotSave/AllZeros/nonrandom/hardware8/adaptiveoff/noextraPPU/runahead0/100%speed.',
 'Persisted RAMRandom is overridden only by actualcommand. No user/sourceworker writes.',
 '',
 'Open:star/1up,cappedpickup,other arrows/cane/specificedge/pool/facinguse assertions',
 'outside these plans,injury/reacquisition,fullsourceart/audio/no-flicker/campaign.',
 'No completepowerupcell or Hard-from-Easy inference. Prior mode corrections/hashes unchanged.']
 report.write_text('\n'.join(lines)+'\n',encoding='utf-8')
 files=[Path(__file__),report,a.ready/'proof.json',a.ready/'manifest.json',a.ready/'seed-policies.json',a.ready/'static-controls.json',a.ready/'commands.json',a.output/'runner-delta.patch',a.output/'host-parser-mode-models.json']
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(f),sha256=sha(f),bytes=f.stat().st_size)for f in files]))
 proof=dict(passed=True,prepared=True,native_run=False,native_granted=False,ROM_sha256=CURRENT,ready_proof_sha256=sha(a.ready/'proof.json'),ready_manifest_sha256=sha(a.ready/'manifest.json'),ready_bindings_verified=count,profiles=5,planned_abilities=52,host_mode_parser_models=10,manifest_sha256=sha(a.output/'manifest.json'),report_sha256=sha(report),runner_delta_sha256=sha(a.output/'runner-delta.patch'),maximum_launches_per_profile=1,native_worker_held=False,commands=ready['commands'])
 put(a.output/'proof.json',proof);print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),**proof),indent=2))

if __name__=='__main__':main()
