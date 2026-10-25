"""Bind the real native music fixture to original source register images."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
OB=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-native-audio-ob')


def main():
    p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--ram',choices=['AllZeros','AllOnes'],default='AllZeros')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    fixture=ROOT/'tests/tmnt-native-audio-oc.lua';debug=a.rom.with_suffix('.dbg')
    debug_text=debug.read_text()if debug.exists()else gzip.decompress(a.rom.with_suffix('.dbg.gz').read_bytes()).decode()
    segments=[dict(q.split('=',1)for q in row.split('\t',1)[1].split(',')if '='in q)
              for row in debug_text.splitlines()if row.startswith('seg\t')]
    music_segment=next(q for q in segments if q['name']=='"MUSIC"')
    music_bank=(int(music_segment['ooffs'],0)-16)//8192
    lines=['TMNT_GOLDEN={}',f'TMNT_VANILLA_MUSIC_BANK={music_bank}']
    coverage=json.loads((OB/'probe-v2/coverage.json').read_text())
    for song in [1,2,3,5,6,8,10,11,12,13,15]:
        f=OB/f'probe-v2/song-{song:02d}.json.gz'
        assert hashlib.sha256(f.read_bytes()).hexdigest()==coverage['songs'][str(song)]['capture_sha256']
        original=json.loads(gzip.decompress(f.read_bytes()));image=bytearray(20);frames=[]
        for q in original[:1502]:
            for at,v in q['writes']:
                if 0x4000<=at<=0x4013:image[at-0x4000]=v
            frames.append('"'+''.join(f'\\{v:03d}'for v in image)+'"')
        lines.append(f'TMNT_GOLDEN[{song}]={{'+','.join(frames)+'}')
    script=a.output/'run.lua';script.write_text('\n'.join(lines)+'\n'+fixture.read_text())
    z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output),str(script),str(a.rom),
        '--timeout','120','--option=--nes.ramPowerOnState='+a.ram,'--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],capture_output=True,text=True)
    (a.output/'host.log').write_text(z.stdout+z.stderr)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    result=dict(passed=z.returncode==0,ROM_sha256=sha(a.rom),fixture_sha256=sha(fixture),bound_script_sha256=sha(script),
                original_coverage_sha256=sha(OB/'probe-v2/coverage.json'),power_on_RAM=a.ram,exit=z.returncode)
    if(a.output/'proof.json').exists():result['proof']=json.loads((a.output/'proof.json').read_text())
    (a.output/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return z.returncode


if __name__=='__main__':raise SystemExit(main())
