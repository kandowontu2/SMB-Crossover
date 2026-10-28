"""Assemble the isolated Celeste Mario leaf with actual project declarations.

This does not change shared source/config, link a cartridge, or run Mesen.
Root owns the final character/menu/mapper dispatch and CHR partition.
"""
from pathlib import Path
import configparser,hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    out=ROOT/'build/celeste-mario-module';out.mkdir(exist_ok=True)
    entry=ROOT/'src/entrypoint.s'
    text=entry.read_text()
    unit=out/'celeste-mario-assembly.s'
    unit.write_text(text+'\n'+('' if '.include "celeste_mario.s"' in text else '.include "celeste_mario.s"\n'))
    config=configparser.ConfigParser();config.optionxform=str;config.read(ROOT/'build_options.ini')
    options={k:v for s in config.values() for k,v in s.items()}
    options.update(MAPPER_MMC3='0',MAPPER_MMC5='1',ENABLE_CROSSOVER='1',ENABLE_MMC5_EXPANDED='1')
    command=[str(ROOT/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g',
             '-I',str(ROOT/'src'),'-I',str(ROOT),'--bin-include-dir',str(ROOT),
             '-o',str(out/'celeste-mario-module.o'),str(unit)]
    for key,value in options.items():command.extend(['-D',key+'='+value])
    result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
    (out/'assembly.log').write_text(result.stdout+result.stderr)
    if result.returncode:
        print(result.stdout+result.stderr);return result.returncode
    owned=sorted((ROOT/'src').glob('celeste_mario*'))+[ROOT/'chr/characters/celeste-mario.chr']
    proof=dict(passed=True,scope=__doc__,native_ROM_sha256=sha(ROOT/'build/celeste-native-reference.nes'),
               compiled_inputs={str(p.relative_to(ROOT)):sha(p)for p in owned},
               parent_entrypoint_sha256=sha(entry),object_sha256=sha(out/'celeste-mario-module.o'),
               command=command,unrun=['linked cartridge','native gameplay','PPU/NMI/IRQ/cadence'],
               allocations=dict(PRG_core='bank98 B000..BFFF; data mirrorD000..DFFF',
                                CHR='pages740..755',variant='MarioVariant4',persistent='5F98..5F9F',scratch='5C00..5C7F'))
    (out/'assembly.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(passed=True,object_sha256=proof['object_sha256'],compiled_inputs=len(owned))))
    return 0
if __name__=='__main__':raise SystemExit(main())
