"""Root's zero-capture physical Bub/Bob empty-scene baseline."""
from hashlib import sha256
import json

import profile_bub_empty_native_1113 as P
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

ROOT=P.B.R/'build/metal-flower-native-1112'
SCRIPTS=('34687e8faf3e5c150f41c55678a835410741a7b81d00c27e23489a10f3502666',
         '2839c0217a5cf1fa35201af979bbfb68c6f289089d630e899bd1885b84817f2f')


def main():
    rom=P.B.ROM
    assert check(rom)['ROM_sha256']==P.B.PIN
    raw=rom.read_bytes()
    for identity in range(2):
        text=P.controller(raw,identity)
        assert sha256(text.encode()).hexdigest()==SCRIPTS[identity]
        script=ROOT/'controller.lua'
        script.write_text(text,encoding='utf-8',newline='\n')
        result=run(script,rom,ROOT/'capture',P.B.PIN,180)
        print(json.dumps(dict(passed=result['passed'],ROM_SHA256=P.B.PIN,
            script_SHA256=result['script_SHA256'],receipt_SHA256=result['receipt_SHA256'],
            receipt=result['receipt'],outputs_written=result['outputs_written']),
            separators=(',',':')),flush=True)
        assert result['passed'],'Current native Bub/Bob cadence baseline failed'
    assert check(rom)['ROM_sha256']==P.B.PIN


if __name__=='__main__':
    main()
