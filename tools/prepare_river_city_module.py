"""Assemble the isolated River City leaf with actual project declarations.

This does not change shared source/config, link a cartridge, or run Mesen.
Root owns the final character/menu/mapper dispatch and CHR partition.
"""
from pathlib import Path
import configparser,hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    out=ROOT/'build/river-city-module';out.mkdir(exist_ok=True)
    entry=ROOT/'src/entrypoint.s'
    text=entry.read_text()
    unit=out/'river-city-assembly.s'
    unit.write_text(text+'\n'+('' if '.include "river_city.s"' in text else '.include "river_city.s"\n'))
    config=configparser.ConfigParser();config.optionxform=str;config.read(ROOT/'build_options.ini')
    options={k:v for s in config.values() for k,v in s.items()}
    options.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
    command=[str(ROOT/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g',
             '-I',str(ROOT/'src'),'-I',str(ROOT),'--bin-include-dir',str(ROOT),
             '-o',str(out/'river-city-module.o'),str(unit)]
    for key,value in options.items():command.extend(['-D',key+'='+value])
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    (out/'assembly.log').write_text(result.stdout+result.stderr)
    if result.returncode:
        print(result.stdout+result.stderr);return result.returncode
    owned=sorted((ROOT/'src').glob('river_city*'))+[ROOT/'chr/characters/river-city.chr']
    proof=dict(passed=True,scope=__doc__,native_ROM_sha256=sha('C:/NES/River City Ransom (USA).nes'),
               compiled_inputs={str(p.relative_to(ROOT)):sha(p)for p in owned},
               parent_entrypoint_sha256=sha(entry),object_sha256=sha(out/'river-city-module.o'),
               command=command,unrun=['linked cartridge','native gameplay','PPU/NMI/IRQ/cadence'],
               allocations=dict(PRG_core='bank81 A300..BFFF',PRG_art='bank70 CB80..DB7F',
                                CHR='pages716..723',variant='5FED',persistent='5FA0..5FAF',scratch='5C00..5C7F'))
    (out/'assembly.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=True,object_sha256=proof['object_sha256'],compiled_inputs=len(owned))))
    return 0
if __name__=='__main__':raise SystemExit(main())
