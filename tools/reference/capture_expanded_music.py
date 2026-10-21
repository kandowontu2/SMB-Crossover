"""Regenerate added-character APU references with Mesen (optional tooling)."""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import run_mesen

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--characters',default='pit,rygar,bass,ryu,sophia,death,victory')
    p.add_argument('--nes-dir',type=Path,default=Path('C:/NES'))
    p.add_argument('--emulator')
    a=p.parse_args();out=ROOT/'build/reference-audio';out.mkdir(parents=True,exist_ok=True)
    meta=json.loads((ROOT/'docs/reference/expanded.json').read_text())['sources']
    for role in a.characters.split(','):
        native=role in ('pit','rygar');begin=300 if native else 0
        length=180 if role=='death' else 600 if role=='victory' else 5400
        if native:
            source=a.nes_dir/meta[role]['file'];rom=source
        else:
            tag,track={'bass':('GameMegaMan10_Nsf',13),'ryu':('GameNinjaGaiden_Nsf',4),'sophia':('GameBlasterMaster_Nsf',3),'death':('GameSuperMarioBros_NSF',15),'victory':('GameSuperMarioBros_NSF',4)}[role]
            source=next((ROOT/'reference/crossover2/extracted/binaryData').glob('*'+tag+'.bin'))
            rom=out/(role+'.nsf')
        digest=hashlib.sha256(source.read_bytes()).hexdigest()
        if role in meta and digest!=meta[role]['sha256']:raise ValueError('Reference hash mismatch: '+str(source))
        if not native:
            data=bytearray(source.read_bytes());data[7]=track;rom.write_bytes(data)
        script=out/(role+'.lua')
        script.write_text('AUDIO_OUTPUT=[=['+(out/(role+'.csv')).as_posix()+']=]\nAUDIO_BEGIN='+str(begin)+'\nAUDIO_END='+str(begin+length)+'\nAUDIO_NATIVE='+repr(role if native else 'nsf')+'\nAUDIO_FREEZE='+str(role=='rygar').lower()+'\ndofile([=['+(ROOT/'tools/reference/capture_expanded_audio.lua').as_posix()+']=])\n')
        if run_mesen.run(script,rom,emulator=a.emulator,timeout=120):return 1
        if hashlib.sha256(source.read_bytes()).hexdigest()!=digest:raise RuntimeError('Original reference file changed')
    return 0

if __name__=='__main__':raise SystemExit(main())
