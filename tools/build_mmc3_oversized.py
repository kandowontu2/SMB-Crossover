"""Build the separate 2 MiB PRG / 256 KiB CHR-RAM MMC3 candidate."""
from pathlib import Path
import argparse, configparser, hashlib, json, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-rom',type=Path,default=ROOT/'build/smb-crossover-mmc5-expanded.nes')
    parser.add_argument('--compiler',type=Path,help='External cl65; otherwise the bundled Windows compiler or PATH')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'build/oversized-mmc3-nf',help='Build directory, including prepared sources; may be outside the workspace')
    args=parser.parse_args()
    destination=args.output_dir.resolve()
    source=destination/'source'
    out=destination/'smb-crossover-mmc3-oversized.nes'
    subprocess.run([sys.executable,str(ROOT/'tools/prepare_mmc3_oversized.py'),
                    '--reference-rom',str(args.reference_rom.resolve()),'--output',str(source)],check=True)
    config=configparser.ConfigParser();config.optionxform=str;config.read(source/'build_options.ini')
    options={k:v for section in config.values() for k,v in section.items()}
    options.update(MAPPER_MMC3='1',MAPPER_MMC5='0',ENABLE_CROSSOVER='1',ENABLE_MMC3_OVERSIZED='1',ENABLE_MMC5_EXPANDED='0')
    bundled=ROOT/'tools/Windows/cc65/bin/cl65.exe'
    compiler=args.compiler.resolve() if args.compiler else bundled if sys.platform=='win32' and bundled.is_file() else shutil.which('cl65')
    if not compiler:parser.error('Install cc65 on PATH or pass --compiler')
    cmd=[str(compiler),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T',
         '-C',str(source/'smb1base-mmc3-oversized.cfg'),'--ld-args','--dbgfile,'+str(out.with_suffix('.dbg')),
         '--include-dir',str(source),'--asm-include-dir',str(source/'src'),'--asm-include-dir',str(source),
         '--bin-include-dir',str(source),'-m',str(out.with_suffix('.map')),'-Ln',str(out.with_suffix('.lbl')),'-o',str(out)]
    for k,v in options.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
    cmd+=[str(source/'src/main.c'),str(source/'src/entrypoint.s')]
    r=subprocess.run(cmd,cwd=source,capture_output=True,text=True)
    out.with_suffix('.build.log').write_text(r.stdout+r.stderr)
    if r.returncode:print(r.stdout+r.stderr);return r.returncode
    rom=out.read_bytes()
    assert len(rom)==2097168 and rom[4:6]==bytes([128,0]) and rom[11]==12
    receipt=dict(output=str(out),sha256=hashlib.sha256(rom).hexdigest(),bytes=len(rom),mapper=4,PRG=2097152,CHR_RAM=262144,status='candidate; emulator admission pending')
    out.with_suffix('.build.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt));return 0
if __name__=='__main__':raise SystemExit(main())
