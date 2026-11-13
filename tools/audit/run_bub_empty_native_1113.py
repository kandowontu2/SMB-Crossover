"""Root's zero-capture physical Bub/Bob empty-scene baseline."""
from hashlib import sha256
import argparse
import json

import profile_bub_empty_native_1113 as P
from nightly_patch_guard_v1 import check
from run_stdout_mesen_1110 import run

ROOT=P.B.R/'build/metal-flower-native-1112'
SCRIPTS=('34687e8faf3e5c150f41c55678a835410741a7b81d00c27e23489a10f3502666',
         '2839c0217a5cf1fa35201af979bbfb68c6f289089d630e899bd1885b84817f2f')
COST_SCRIPTS=('a5b78804480605c41f56c9fcae3d189e1e949ec35da13ae3cbed9f7d98fc9c8d',
              '5d3267b7892058a2fa3ed0032590db4f3a4672f474e7172b84fba1481a8e3150')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cost',action='store_true')
    args=parser.parse_args()
    rom=P.B.ROM
    assert check(rom)['ROM_sha256']==P.B.PIN
    raw=rom.read_bytes()
    for identity in range(2):
        text=P.cost_controller(raw,identity)if args.cost else P.controller(raw,identity)
        assert sha256(text.encode()).hexdigest()==(COST_SCRIPTS if args.cost else SCRIPTS)[identity]
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
