"""Bounded original NES Karnov controller and instruction-coverage research."""
from pathlib import Path
import hashlib,json,os,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from run_mesen import run
from mesen_session_guard_v1 import require_free_workspace
O=R/'build/karnov-native-reference-1101-v1';ROM=Path('C:/NES/Karnov (USA).nes')
EXPECTED='0d49c1120fc13ead1efe4429f7cbb4f01b90e2486c66661c46e922dda6dc830a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert sha(ROM)==EXPECTED
    O.mkdir(exist_ok=True);assert not(O/'capture').exists();(O/'capture').mkdir()
    template=R/'tools/reference/karnov_original_probe_1101_v1.lua'
    controller=O/'controller.lua';controller.write_text('local KARNOV_SHA='+json.dumps(EXPECTED)+'\n'+template.read_text(),encoding='utf-8',newline='\n')
    other=require_free_workspace(R,ROM);print('Other-project Mesen sessions left untouched: '+json.dumps([p['ProcessId']for p in other]),flush=True)
    os.environ['SMB_RUN_OUTPUT']=str(O/'capture')
    refs=[Path(__file__),template,controller,ROM,R/'tools/run_mesen.py',R/'tools/audit/capture_budget.py',R/'tools/audit/mesen_session_guard_v1.py']
    bindings={str(p.resolve()):sha(p)for p in refs}
    result=run(controller,ROM,timeout=180,emulator_options=['--doNotSaveSettings','--nes.removeSpriteLimit=false','--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
    for p,h in bindings.items():assert sha(p)==h,p
    q=json.loads((O/'capture/reference.json').read_text());assert result==0 and q['passed']and q['ROM_sha256']==EXPECTED
    (O/'controls.json').write_text(json.dumps(dict(passed=True,native_original=True,port=False,installed=False,ROM_sha256=EXPECTED,player_updates=q['player_updates'],frames=q['frames'],instructions=len(q['executed_instructions']),bindings=bindings),indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in q.items()if k not in ['initial_fixture','entries','executed_instructions']}))


if __name__=='__main__':main()
