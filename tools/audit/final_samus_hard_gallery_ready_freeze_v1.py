"""Read-only finite Samus Hard readiness self-verification; never launches."""
from pathlib import Path
import argparse,hashlib,json
from final_item_abilities_remaining731_run_v1 import verify_manifest
from final_samus_hard_gallery_source_v1 import D,ROOT,SHA
from final_samus_hard_gallery_prepare_v2 import compose
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--ready',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 proof=json.loads((a.ready/'proof.json').read_text());assert proof['prepared']and not proof['native_run']and proof['ROM_sha256']==SHA and proof['mode_value']==1 and proof['maximum_cases']==8
 assert sha(a.ready/'manifest.json')==proof['manifest_sha256'];bindings=verify_manifest(a.ready/'manifest.json')
 native=Path(proof['output']);assert not(native/'launch.json').exists()and not(native/'proof.json').exists()and not(a.ready/'ROOT-grant.json').exists()
 cfg=json.loads((native/'config.json').read_text());script=(native/'run.lua').read_text();expected,guards=compose(cfg);assert script==expected
 assert sha(native/'run.lua')==proof['script_sha256']and sha(native/'candidate.nes')==SHA
 assert guards==(native/'inherited-NMI-stack-APU-guards.lua').read_text()and sha(native/'inherited-NMI-stack-APU-guards.lua')=='6ab7cd71f41f441f4d4d752e2412f83c2b16da06b9e10d3cdf05180c63bf5fdf'
 static=json.loads((a.ready/'static-controls.json').read_text());cpu=json.loads((a.ready/'additional-CPU-controls.json').read_text());models=json.loads((a.ready/'phase-models.json').read_text());policy=json.loads((a.ready/'seed-policy.json').read_text())
 assert static['passed']and cpu['passed']and models['passed']and static['CPU_source_cases']==cpu['cases']==25 and static['phase_models']==len(models['models'])==32
 assert static['callbacks']==41 and static['dispatcher_last']and static['endFrame_callbacks']==2 and static['controller_probes']==24
 assert len(static['return_models'])==8 and len(static['DMA_models'])==13
 assert len(cfg['cases'])==8 and sum(len(q['tasks'])for q in cfg['cases'])==policy['subphase_count']==27 and policy['acquisition']is False
 assert cfg['dma_protocol']['window_start']==0xe005 and cfg['dma_protocol']['complete_pc']==0xe008 and len(cfg['dma_protocol']['window_bytes'])==8
 old=D/'current3b112-samus-hard-gallery-ready-v1';oldcfg=json.loads((old/'native/config.json').read_text());oldtext=(old/'native/run.lua').read_text()
 assert cfg==oldcfg and script[script.index('\nlocal inheritedAbilityAssert'):]==oldtext[oldtext.index('\nlocal inheritedAbilityAssert'):]
 put(a.output/'preparation-clarifications.json',dict(passed=True,current_ready_sha256=sha(a.ready/'proof.json'),previous_source_preparation=dict(path=str(old/'proof.json'),sha256=sha(old/'proof.json'),native_run=False),native_script_tail_and_config_semantics_exact=True,config_literal_key_order_may_differ=True,clarifications=['The V1 preparation wording no HP writes was overbroad: complete legal actor setup seeds the uncached0 health fields. There are no post-contact HP/result writes; this was already the literal unchanged mechanics. V2 states that explicitly.','V2 adds8 actual CPU controls:6 owned/unowned missile refill2/cap20 cases and2 actual spatial Ice resistance contacts for Lakitu/Bowser; these remain CPU-only, not native boss scenes.','V2 also retains the prior17 CPU cases:8 complete palette getters,2 actual Ice emission/contact/thaw-break gateways,1 three-bomb pool/expiry and6 complete renderer gateways. No native controller/guard/seed/module change from V1.','All preparation attempts stay external; no native attempt has occurred.']))
 files=[a.ready/'proof.json',a.ready/'manifest.json',a.ready/'plans.json',a.ready/'static-controls.json',a.ready/'additional-CPU-controls.json',a.ready/'phase-models.json',a.ready/'seed-policy.json',a.ready/'environment.json',native/'config.json',native/'run.lua',native/'inherited-NMI-stack-APU-guards.lua',ROOT/'tools/audit/final_samus_hard_gallery_native_v1.lua',ROOT/'tools/audit/final_samus_hard_gallery_prepare_v1.py',ROOT/'tools/audit/final_samus_hard_gallery_prepare_v2.py',ROOT/'tools/audit/final_samus_hard_gallery_run_v1.py',Path(__file__),ROOT/'docs/qa/final-samus-hard-gallery-prepared-v2-2026-10-26.txt',a.output/'preparation-clarifications.json']
 put(a.output/'manifest.json',dict(bindings=[dict(path=str(q.resolve()),bytes=q.stat().st_size,sha256=sha(q))for q in files]))
 put(a.output/'proof.json',dict(passed=True,source_only=True,native_run=False,native_granted=False,ready_sha256=sha(a.ready/'proof.json'),ready_manifest_sha256=sha(a.ready/'manifest.json'),verified_ready_bindings=bindings,ROM_sha256=SHA,mode=1,cases=8,finite_subphases=27,static_callbacks=41,CPU_added_cases=25,return_models=8,DMA_models=13,controller_models=24,phase_models=32,script_sha256=sha(native/'run.lua'),manifest_sha256=sha(a.output/'manifest.json'),stable_command=proof['stable_command'],actual_graphics_APU_native_claim=False,maximum_launches=1,native_worker_reserved=False))
 verify_manifest(a.output/'manifest.json');print(json.dumps(dict(proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),ready_sha256=sha(a.ready/'proof.json'),bindings=bindings,stable_command=proof['stable_command']),indent=2))

if __name__=='__main__':main()
