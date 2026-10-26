"""Bind unchanged qualified MegaEasy450 observer to independent common audio."""
from pathlib import Path
import argparse,ast,json,shutil
from smb3_host_current3b_cpu_v1 import D,R,sha,put

B=D/'common-audio-mixer-current3b-v3';BASE=D/'root-presentation450-3b112-v1'
ROM='f4efd9ccb222501877dfc77c5189841aa9dc500756736f15aaf02a6994ae8c0f'
SOURCE='0f06bee8a51b1303facfd554fc767335dae32ef901dffb9d62d5924e79a4b2d1'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);a=p.parse_args();ready=a.packet/'readiness.json';assert not(a.packet/'launch.json').exists()and not(a.packet/'observer-readiness.json').exists();q=json.loads(ready.read_text());assert q['passed']and not q['native_run']and q['ROM_sha256']==ROM
 source=B/'source-freeze-v1/readiness.json';assert sha(source)==SOURCE;s=json.loads(source.read_text());assert s['source_component_ready']and not s['native_run']and s['ROM_sha256']==ROM
 deps={Path(p):h for p,h in q['bindings'].items()};deps.update({Path(v['path']):v['sha256']for v in s['bindings']})
 for f,h in deps.items():assert sha(f)==h,f
 old=json.loads((BASE/'config.json').read_text());cfg=json.loads((a.packet/'config.json').read_text());assert {k:v for k,v in old.items()if k not in['out','prefix','ROM_sha256']}=={k:v for k,v in cfg.items()if k not in['out','prefix','ROM_sha256']}
 assert cfg['limit']==450 and cfg['hooks']['DmaComplete']['pc']==0xe008
 assert(a.packet/'prefix.csv').read_bytes()==(BASE/'prefix.csv').read_bytes();assert q['environment']==json.loads((BASE/'readiness.json').read_text())['environment']
 result=json.loads((BASE/'native-receipt.json').read_text());assert result['passed']and result['ROM_sha256']=='3b112e1d79ba7348f2f7a4c426f4675845a5781017ab74690feb235121a66287';assert [result['result'][n]for n in['completed_DMAs','polls','captured_actual_frames','scoped_enables']]==[402,449,275,72]
 for n in ['emulator','core','worker_settings','user_settings']:assert sha(q['environment'][n])==q['environment'][n+'_sha256'],n
 ast.parse((R/'tools/audit/common_audio_mixer_native_review_v1.py').read_text())
 plan='''PREPARE ONLY: one exactf4efd MegaEasy450 natural-input opening.
ExistingROOT3b450 is the genuine same-controller reference:402completeDMAs,
449actual input polls,275wholePPU images176..450 and72scoped safe enables.
The original qualified presentation_timing_preflight_v1.lua is UNCHANGED.
Hooks/RAM/5SMC/450cap/prefix/environment match the real3b fixture literally;
only output paths, actual candidate ROM hash and source bindings differ.
No selection/mode/status/resource/actor/audio/RNG writes; controller only.
Real endpoint still asserts selectedMega1/Proto0/Easy0 and active gameplay.
Hardware8sprite limit, allzero/nonrandom/no-extra-lines/runahead settings
and existing no-save deterministic command overrides remain unchanged.
One180second host timeout/oneworker/zero retries after a separateROOTgrant.

Original NMIAXY/SP/shadows/5SMC, actualIRQ31, E008/all256physicalDMA source
and destination/render-disabled guards, conservative pre-render274 deadline
and wholePPU capture remain. No new observer callbacks are added. Existing
static startup registration remains; callbacks do not grow callback vectors.
All actual input poll/frame/masks must match the real3b observation. Compare
net DMA counts and cumulative275visible capture cutoffs; retain ANY deficit
without retry or causal waiver. RGB/OAM equality is recorded separately,
with any first difference and actual wholeimages reviewed. Native mechanics
alone cannot establish source SFX waveform/music fidelity or allroster lag.
Existing8sprite body/shot contention on3b is not declared fixed by this test.

Source controls/ordinary d444+f4ffd and exact guarded f4efd are bound here.
No heldSMB3 core, cached music, stale clones or new samples enter this ROM.
Current production3b and all prior held receipts stay unchanged. No launch
or adoption is authorized by preparing this packet.
'''
 (a.packet/'PLAN.txt').write_text(plan,encoding='utf-8');shutil.copyfile(ready,a.packet/'observer-readiness.json')
 extra={Path(__file__),source,B/'proof.json',R/'tools/audit/presentation_timing_launch_v1.py',R/'tools/audit/common_audio_mixer_native_review_v1.py'}|{BASE/n for n in ['readiness.json','native-receipt.json','config.json','prefix.csv','result.json','launch.json','timing.jsonl','direct-index.csv','direct.argb']}
 extra|={f for f in a.packet.iterdir()if f.is_file()and f.name!='readiness.json'};deps.update({f:sha(f)for f in extra})
 final=q|dict(native_grant=False,maximum_launches=1,maximum_workers=1,source_readiness=str(source).replace('\\','/'),source_readiness_sha256=SOURCE,actual_current3b_reference=True,reference_DMAs=402,reference_input_polls=449,reference_PPU_pairs=275,reference_safe_enables=72,exact_original_observer_controller_guards=True,limits=plan,bindings={str(f.resolve()):h for f,h in sorted(deps.items())})
 ready.write_text(json.dumps(final,indent=2)+'\n',encoding='utf-8')
 put(a.packet/'preparation.json',dict(passed=True,prepared_only=True,native_run=False,native_grant=False,ROM_sha256=ROM,source_readiness_sha256=SOURCE,readiness_sha256=sha(ready),bindings=len(deps),command=q['command'],explicit_grant_launcher=str(R/'tools/audit/presentation_timing_launch_v1.py').replace('\\','/'),launcher_sha256=sha(R/'tools/audit/presentation_timing_launch_v1.py'),checker_sha256=sha(__file__)))
 print(json.dumps(dict(passed=True,prepared_only=True,bindings=len(deps),readiness_sha256=sha(ready))))
if __name__=='__main__':main()
