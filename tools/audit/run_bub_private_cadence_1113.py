"""Private bounded Bubble empty-loop threshold test; never installs a ROM."""
from hashlib import sha256
import json
from pathlib import Path

import bub_empty_loops_1113 as E
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

OUT=Path(__file__).resolve().parents[2]/'build/bub-empty-native-1113'
PARENT='7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc'
PIN='a77a71cf9b22837cb58d639b7653f527c7de2376cc1cffb1d1199a9f7081cd38'
SCRIPTS=('6c4c6d9ef3e1039adeae14d46ff915ce49d683963c899bcfcbc3d2f10dff0aa1',
         '5b498a2c6d966b85cfcffd381e7bca304cf0298f0c5b74e83b1af7bf66e5c299')


def main():
    nightly=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
    assert check(nightly)['ROM_sha256']==PARENT
    raw=nightly.read_bytes()
    image,info=E.proposal(raw)
    assert sha256(image).hexdigest()==PIN and E.inverse(image)==raw
    OUT.mkdir(exist_ok=True)
    rom=OUT/'candidate.nes';rom.write_bytes(image)
    for identity in range(2):
        text=E.controller(image,identity)
        assert sha256(text.encode()).hexdigest()==SCRIPTS[identity]
        script=OUT/'controller.lua';script.write_text(text,encoding='utf-8',newline='\n')
        result=run(script,rom,OUT/'capture',PIN,180)
        print(json.dumps(dict(passed=result['passed'],private_only=True,
            installed=False,parent_SHA256=PARENT,ROM_SHA256=PIN,
            script_SHA256=result['script_SHA256'],receipt_SHA256=result['receipt_SHA256'],
            receipt=result['receipt'],outputs_written=result['outputs_written']),
            separators=(',',':')),flush=True)
        assert result['passed'],'Private threshold probe failed its stated cadence window'
    assert check(nightly)['ROM_sha256']==PARENT


if __name__=='__main__':
    main()
