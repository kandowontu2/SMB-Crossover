"""Actual Downloads natural mushroom/flower tests for both Bowsers."""
from hashlib import sha256
from pathlib import Path
import json

import replay_bowser_natural_powerups_1113 as P
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

ROM=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
OUT=Path(__file__).resolve().parents[2]/'build/metal-flower-native-1112'
PIN='7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
SCRIPTS=('58d777bc44d5b7ff370ace86b20a76e57f69f6f70e11e0cc57940a263f4e4de1',
         'd23ba56d64b6efacc3ba21463717df4764623bba3b10100073758f3cb5d2fb63')


def main():
    assert check(ROM)['ROM_sha256']==PIN
    raw=ROM.read_bytes()
    for identity in range(2):
        text=P.controller(raw,identity)
        assert sha256(text.encode()).hexdigest()==SCRIPTS[identity]
        script=OUT/'controller.lua';script.write_text(text,encoding='utf-8',newline='\n')
        result=run(script,ROM,OUT/'capture',PIN,180)
        print(json.dumps(dict(passed=result['passed'],ROM_SHA256=PIN,
            script_SHA256=result['script_SHA256'],receipt_SHA256=result['receipt_SHA256'],
            receipt=result['receipt'],outputs_written=result['outputs_written']),
            separators=(',',':')),flush=True)
        assert result['passed'],'Actual Bowser mushroom/flower route failed'
    assert check(ROM)['ROM_sha256']==PIN


if __name__=='__main__':
    main()
