from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;O=D/'mmc3-flag-fix-v23';T=O/'physical-replay-v3';T.mkdir(exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();parent=D/'streaming-replay-v1/capture.py';text=parent.read_text()
assert text.count("out/'chr-commit.json'")==1;text=text.replace("out/'chr-commit.json'","out/'mmc3-cache-guard.json'")
assert text.count('body_chr=chr_proof')==1;text=text.replace('body_chr=chr_proof','mapper_cache_guard=chr_proof')
text=text.replace('save timestamped direct-console lossless frames','save timestamped direct-console lossless MMC3 frames')
anchor="'--option=--nes.ramPowerOnState=AllZeros'";assert text.count(anchor)==1;text=text.replace(anchor,"'--emulator','C:\\\\Users\\\\kando\\\\Videos\\\\SMB Crossover Archive\\\\2026-10-24-native-rest-py\\\\mmc3-flag-fix-v23\\\\script-budget-probe-v2\\\\emulator\\\\Mesen.exe','--option=--doNotSaveSettings',"+anchor)
driver=T/'capture-mmc3.py';driver.write_text(text)
source=O/'native-tests-v1/fresh-twinbee-easy';q=json.loads((O/'native-tests-v1/proof.json').read_text());assert q['passed']and q['fresh_discovery']['passed']
with(T/'host.log').open('w')as log:p=subprocess.run([sys.executable,str(driver),'--rom',str(O/'candidate.nes'),'--route',str(source),'--output',str(T/'twinbee-easy')],cwd=R,stdout=log,stderr=subprocess.STDOUT)
assert p.returncode==0,(T/'host.log').read_text()[-2000:]
proof=json.loads((T/'twinbee-easy/proof.json').read_text());assert proof['passed']and proof['mapper_cache_guard']['passed']and proof['ROM_sha256']==sha(O/'candidate.nes')
report=dict(passed=True,goal_complete=False,ROM_sha256=sha(O/'candidate.nes'),capture_proof_sha256=sha(T/'twinbee-easy/proof.json'),original_capture_driver_sha256=sha(parent),bound_capture_driver_sha256=sha(driver),callback_host_budget_seconds=5,source_emulated_frame_bounds_unchanged=True,scope='Independent exact controller/CPU trace replay with every actual PPU frame retained and RGB/index/gzip checks, plus the mapper-specific native CHR/cache/bank witness. This does not reuse or invent the MMC5-only body-CHR observer, and is not yet exhaustive visual/campaign/physical hardware admission.')
(T/'proof.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
