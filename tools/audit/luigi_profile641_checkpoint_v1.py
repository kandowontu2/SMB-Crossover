"""Small unadopted641 source/native review packet; no game/native/Git mutation."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
S = D / 'luigi-mario-profile731-v3'
N = D / 'luigi-profile641-native-ready-v2'
T = ROOT / 'docs/qa/checkpoints/2026-10-26/luigi-dry-profile641-unadopted-v1'
ROM = '641460e2646806c03fb98cf84f8a8c2e8de99c74dac8c5876c50f05ef1eb512c'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def get(p):return json.loads(Path(p).read_text())


def main():
    p=N/'native-result-freeze-v1/proof.json'
    assert sha(p)=='d950a12be58aa7ec848d3e951186a00c81f84940178579ea79378efbefc58df3'
    proof=get(p);assert proof['passed'] and not proof['adopted'] and len(proof['bindings'])==6094
    for f,h in proof['bindings'].items():assert sha(f)==h,f
    T.mkdir(parents=True,exist_ok=False);files=[]
    def copy(p,name,role):
        assert p.suffix.lower() in ['.s','.patch','.json','.txt','.log','.png','.py','.lua','.diff']
        assert p.name.lower()!='settings.json'
        t=T/name;t.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,t)
        files.append(dict(path=name,sha256=sha(t),bytes=t.stat().st_size,original_path=str(p),original_sha256=sha(p),role=role))
    for name in ['src/player.s','src/luigi_native.s','src/entrypoint.s','src/luigi_source_profile.s']:
        copy(S/'source'/name,'source-overlay/'+name,'Exact four-file private delta; preserve original raw line endings')
    for p,name,role in [
        (S/'implementation.patch','source/implementation.patch','Only intended four-file diff against frozen731; no held unrelated source'),
        (S/'preparation.json','source/preparation.json','Actual bank/symbol/source/EOL/canonical build summary'),
        (S/'source-manifest.json','source/source-manifest.json','Full exact private source hash catalog; no raw source ZIP'),
        (S/'source-ready-v1/readiness.json','source/readiness.json','Source-only receipt1824 bindings, historical native-unrun'),
        (S/'cpu-v2/proof.json','source/full-caller-CPU.json','114foreign/60inputs/18collision-history/428IRQ controls'),
        (S/'traits-v1/proof.json','source/traits.json','Mode-specific launch/brake/acceleration source controls'),
        (S/'handoffs-v1/proof.json','source/handoffs.json','Thirty unchanged handoffs; actual new live SMC values explicitly disclosed'),
        (N/'readiness.json','native/readiness.json','Original unmodified two-mode native readiness5323 bindings'),
        (N/'freeze-v1/receipt.json','native/preparation-seal.json','Additional five source-test/negative bindings'),
        (N/'command.json','native/command.json','Original two-launch exact command; do not rerun from this checkpoint'),
        (N/'native-proof.json','native/native-proof.json','Actual two native PASS receipts; zero retry, released worker'),
        (N/'native-result-freeze-v1/proof.json','native/result-proof.json','Independent exact-source/native result freeze6094 bindings'),
        (N/'native-result-freeze-v1/component-evidence.json','native/component-evidence.json','Actual reveal/pickup/growth/source-fire/contact/drain field analysis'),
        (N/'native-result-freeze-v1/agent-visual-review.json','native/agent-visual-review.json','Selected42 complete PPU placements reviewed; explicit visual limits'),
        (N/'native-result-freeze-v1/selected-images.json','native/selected-images.json','Original whole-image/source paths and hashes'),
        (D/'root-luigi641-build-v1/ROOT-review.json','ROOT-review.json','Parent independent exact641 plus both flagoff rebuilds; first host failure retained'),
        (D/'root-luigi641-build-v1/expanded.build.log','retained-negatives/ROOT-first-host-build.log','First extended-path stat host error; sequential exact641 succeeds'),
        (D/'luigi-mario-profile731-v1/assembly-error-freeze-v1/proof.json','retained-negatives/assembler-v1-proof.json','Original scope error; no candidate produced'),
        (D/'luigi-mario-profile731-v1/assembly-error-freeze-v1/build-host.log','retained-negatives/assembler-v1.log','Exact original assembler failure log'),
        (D/'luigi-mario-profile731-v2/assembly-error-freeze-v1/proof.json','retained-negatives/assembler-v2-proof.json','Original short branch range failure; no candidate produced'),
        (D/'luigi-mario-profile731-v2/assembly-error-freeze-v1/build-host.log','retained-negatives/assembler-v2.log','Exact original assembler failure log'),
        (S/'cpu-v1/failed-checker.py','retained-negatives/first-CPU-checker.py','A+B+Right193 misclassification; no game mutation'),
        (S/'cpu-v1/failed-proof.json','retained-negatives/first-CPU-proof.json','Original offline classifier failure retained'),
        (D/'luigi-profile641-native-ready-v1/failure-freeze-v1/proof.json','retained-negatives/first-native-preparation-proof.json','Static-equivalence fixture original wrong source-test input; no native launch'),
        (N/'result-checker-error-v1/failure.json','retained-negatives/result-checker-error.json','Offline seal schema mismatch; actual native receipts unchanged')]:copy(p,name,role)
    for mode in ['luigi-easy','luigi-hard']:
        copy(N/mode/'native-receipt.json',f'native/{mode}-receipt.json','Actual finite component native exit/CHR receipt')
        copy(N/mode/'configuration.json',f'native/{mode}-configuration.json','Genuine compiled hooks/owners/banks/code metadata, no callable aliases')
        copy(N/mode/'completed-loop-motion.json',f'native/{mode}-motion.json','Actual mode-specific complete-loop motion guard summary')
    for p in sorted((N/'native-result-freeze-v1').glob('*-selected-*.png')):
        copy(p,'image-samples/'+p.name,'42 selected complete256x240 actual641 placements across six sheets')
    for name in ['luigi_mario_profile731_prepare_v1.py','luigi_mario_profile731_cpu_v1.py','luigi_mario_profile731_traits_v1.py',
                 'luigi_mario_profile731_handoffs_v1.py','luigi_mario_profile731_ready_v1.py',
                 'luigi_profile641_native_v1.lua','luigi_profile641_native_prepare_v1.py','luigi_profile641_native_run_v1.py',
                 'luigi_profile641_result_v1.py','luigi_profile641_checkpoint_v1.py']:
        copy(ROOT/'tools/audit'/name,'frozen-tools/'+name,'Exact frozen versioned source/native preparation, runner or saved-data tool')
    for name in ['luigi-mario-profile731-source-2026-10-26.txt','luigi-profile641-native-preparation-2026-10-26.txt','luigi-profile641-native-2026-10-26.txt']:
        copy(ROOT/'docs/qa'/name,'reports/'+name,'Historical source/native preparation or fresh two-mode component report')
    readme='''Luigi dry movement641: PRIVATE / UNADOPTED source and two-mode item checkpoint

Candidate641460e2646806c03fb98cf84f8a8c2e8de99c74dac8c5876c50f05ef1eb512c.
Parent/production731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c.
Four exact source files and implementation.patch are ready for independent review.
Luigi uses current Mario's mode-specific dry movement, plus51/256 upward launch
speed and one-eighth less ground braking. Real Luigi identity/art/items remain.
Foreign paths have114 complete-call ZERO-cycle differences; OWNED movement cost
is not yet characterized here. No palette change or new RAM. Some legacy handoffs
leave new genuine live farcall operands: exact differences are disclosed, not
masked as byte identity. Water/climb/spring/control handoffs are not retuned.

Source/trait/full-wrapper/428IRQ controls and exact canonical/flagoff builds pass.
ROOT independently reproduced641/d444/f4ffd. Original source report is historical
NATIVE UNRUN; fresh result report adds exactly two zero-retry component launches.
Easy0: pickups867/1494,60+60 growth,13Rg3 source requests, liveKoopa contact1911,
all-ten-slotempty1912..1958,0deaths. Hard1: pickups959/1579,60+60 growth,15requests,
liveGoomba contacts2058/2077 (second already in flight during neutral), empty2078..
2105,0deaths. Both finalFire2; committedCHR0bad; motion maximumworld/camera3.
These are actual numeric modes, genuine physical items and real enemy contacts.

Six sheets show42 inspected complete PPU placements. No obvious corrupt scenery,
block displacement, body or HUD seen in those samples. Not every-frame, source-art,
audible waveform, fullE008 transfer/enable timing, ownedcadence, full1-1 or adoption
qualification. Fresh fullroute/ordinary stomp and exactinput replay remain required.

Review-files.json binds each copied file to its original path/hash/role. Native
captures/settings/ROM/audio stay external. Retained assembler/mock/host/checker
failures remain separate and are not relabeled game failures or native retries.
This checkpoint installs nothing, launches nothing and stages/commits nothing.
'''
    (T/'README.txt').write_text(readme,encoding='utf-8')
    files.append(dict(path='README.txt',sha256=sha(T/'README.txt'),bytes=(T/'README.txt').stat().st_size,role='Compact review entry point; unadopted and exact scope'))
    manifest=dict(passed=True,adopted=False,ROM_sha256=ROM,parent_ROM_sha256='731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c',
                  checkpoint_only=True,actual_native_launches_recorded=2,native_launches_by_checkpoint=0,
                  copied_ROM_audio_settings_raw_payload=False,files=files,total_bytes=sum(f['bytes'] for f in files))
    (T/'review-files.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    for r in files:assert sha(T/r['path'])==r['sha256']==r.get('original_sha256',r['sha256'])
    print(json.dumps(dict(passed=True,files=len(files),bytes=manifest['total_bytes'],review_map_sha256=sha(T/'review-files.json'),path=str(T)),indent=2))


if __name__=='__main__':main()
