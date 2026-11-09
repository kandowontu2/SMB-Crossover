"""Bind all linked operand matches for the retired native ClearBitsMask."""

import argparse
import json
from pathlib import Path

from py65.devices.mpu6502 import MPU
import check_native_enemy_pair_offsets_1110 as Pair


P, R = Pair.P,Pair.R
DATA = ((46,0x16ba,'XG_MUSIC_2E','expanded/playlist-07.bin','src/expanded_music.inc','20d498'),
        (55,0x1f36,'XG_MUSIC_37','expanded/playlist-10.bin','src/expanded_music.inc','0dd298'),
        (108,0x02ff,'X5_FULL_MUSIC_08','full-roster/full-08.bin','src/full_roster_music.inc','b9d098'))


def validate(raw):
    assert P.sha(raw)==Pair.Q.PIN
    image = P.bundle(raw)
    resident = raw[16:16+128*8192]
    ops = {i for i,(_,mode) in enumerate(MPU.disassemble) if mode in ('abs','abx','aby','ind')}
    matched = [(i//8192,i%8192,resident[i:i+3].hex()) for i in range(len(resident)-2)
               if resident[i] in ops and Pair.START<=resident[i+1]+256*resident[i+2]<Pair.ENTRY]
    assert matched==[(bank,offset,code) for bank,offset,_,_,_,code in DATA]+[(126,0x1948,'3dd098')]
    inputs = []
    for bank,_,segment,name,source,_ in DATA:
        path, declaration = R/'audio'/name,R/source
        text = declaration.read_text()
        decl = text.split(f'.segment "{segment}"\n',1)[1].split('.segment ',1)[0]
        assert f'.incbin "audio/{name}"' in decl
        assert path.read_bytes()==resident[bank*8192:(bank+1)*8192]
        linked = [s for s in image['segs'].values() if s.get('name')==f'"{segment}"']
        assert len(linked)==1 and int(linked[0]['ooffs'],0)==16+bank*8192 and int(linked[0]['size'],0)==8192
        inputs.extend((path,declaration))
    return matched,inputs


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    proof = args.output/'proof-v2.json'
    cpu = json.loads(proof.read_text())
    matched,inputs = validate(Pair.Q.BASE.read_bytes())
    paths = [*inputs,proof,Path(__file__)]
    result = dict(passed=True,parent_SHA256=Pair.Q.PIN,
                  expected_memory_only_SHA256=cpu['expected_memory_only_SHA256'],
                  all_absolute_indexed_and_indirect_literal_matches=matched,
                  sole_code_consumer=[126,0x9948],other_matches_source_confirmed_music_data=True,
                  bindings={str(path.resolve()):P.sha(path.read_bytes()) for path in paths})
    (args.output/'readers-v2.json').write_text(json.dumps(result,indent=2)+'\n')
    print(matched,flush=True)


if __name__ == '__main__':
    main()
