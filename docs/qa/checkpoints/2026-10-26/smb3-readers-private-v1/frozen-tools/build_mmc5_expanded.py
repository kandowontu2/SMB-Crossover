"""Build the separate 1 MiB PRG / 1 MiB CHR MMC5 target from prepared assets.

This deliberately does not regenerate artwork or replace the normal mapper ROMs.
--source-overlay supports reviewing a staged packet without installing its files.
"""
from pathlib import Path
import argparse, configparser, hashlib, json, shutil, subprocess, sys

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--workspace',type=Path,default=Path(__file__).resolve().parents[1])
 p.add_argument('--source-overlay',type=Path)
 p.add_argument('--compiler',type=Path,help='External cl65 executable; otherwise use the bundled compiler or PATH')
 p.add_argument('--output',type=Path,help='Output ROM path; default build/smb-crossover-mmc5-expanded.nes')
 p.add_argument('--chr-extra',type=Path,help='Real prepared upper CHR bytes, at most 768 KiB; omitted bytes are zero')
 p.add_argument('--flag-off',choices=('mmc3','mmc5'),help='Verify the ordinary target using the staged sources')
 a=p.parse_args(); root=a.workspace.resolve(); overlay=(a.source_overlay or root).resolve()
 flag=not a.flag_off; mapper=a.flag_off or 'mmc5'
 out=(a.output or root/'build/smb-crossover-mmc5-expanded.nes').resolve()
 if out.suffix.lower()!='.nes':p.error('--output must end in .nes')
 if flag and out in [(root/'build'/f'smb-crossover-{m}.nes').resolve() for m in ('mmc3','mmc5')]:
  p.error('The expanded target must not overwrite an ordinary mapper ROM')
 out.parent.mkdir(parents=True,exist_ok=True)
 objects=out.parent/(out.stem+'-objects');objects.mkdir(exist_ok=True)
 config=configparser.ConfigParser();config.optionxform=str;config.read(root/'build_options.ini')
 options={k:v for s in config.values() for k,v in s.items()}
 options.update(MAPPER_MMC3=str(int(mapper=='mmc3')),MAPPER_MMC5=str(int(mapper=='mmc5')),ENABLE_CROSSOVER='1')
 if flag:options['ENABLE_MMC5_EXPANDED']='1'
 else:options.pop('ENABLE_MMC5_EXPANDED',None) # exercise the source default of zero
 for name in ('main.c','entrypoint.s'):
  src=overlay/'src'/name
  if not src.exists():src=root/'src'/name
  shutil.copyfile(src,objects/name)
 bundled=root/'tools/Windows/cc65/bin/cl65.exe'
 compiler=a.compiler.resolve()if a.compiler else bundled if sys.platform=='win32'and bundled.is_file()else shutil.which('cl65')
 if not compiler:p.error('Install cc65 on PATH')
 cfg=overlay/'smb1base-mmc5-expanded.cfg' if flag else root/'smb1base.cfg'
 command=[str(compiler),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(cfg),
  '--ld-args','--dbgfile,'+str(out.with_suffix('.dbg')),
  '--include-dir',str(root),'--asm-include-dir',str(overlay/'src'),'--asm-include-dir',str(root/'src'),
  '--asm-include-dir',str(root),'--bin-include-dir',str(overlay),'--bin-include-dir',str(root),'-m',str(out.with_suffix('.map')),
  '-Ln',str(out.with_suffix('.lbl')),'-o',str(out)]
 for k,v in options.items():command+=['--asm-define',k+'='+v,'-D',k+'='+v]
 command += [str(objects/'main.c'),str(objects/'entrypoint.s')]
 if a.chr_extra:
  if not flag:p.error('--chr-extra requires the expanded target')
  extra=a.chr_extra.resolve()
  if not extra.is_file() or extra.stat().st_size>768*1024:p.error('--chr-extra must be a file no larger than 768 KiB')
  asm=objects/'expanded_chr.s';asm.write_text('.segment "X5_CHR_MORE"\n.incbin "'+extra.as_posix()+'"\n')
  command.append(str(asm))
 result=subprocess.run(command,cwd=root,capture_output=True,text=True)
 out.with_suffix('.build.log').write_text(result.stdout+result.stderr)
 if result.returncode:print(result.stdout+result.stderr);return result.returncode
 if flag:
  from prepare_cv3_dmc_mirror import prepare
  prepare(root,out)
 rom=out.read_bytes();actual_mapper=(rom[6]>>4)|(rom[7]&240)|((rom[8]&15)<<8)
 assert actual_mapper==(5 if mapper=='mmc5' else 4)
 assert len(rom)==16+rom[4]*16384+rom[5]*8192
 if flag:assert len(rom)==2097168 and rom[4]==64 and rom[5]==128
 receipt=dict(output=str(out),sha256=hashlib.sha256(rom).hexdigest(),bytes=len(rom),mapper=actual_mapper,
  expanded=flag,extra_chr_sha256=hashlib.sha256(a.chr_extra.read_bytes()).hexdigest() if a.chr_extra else None)
 out.with_suffix('.build.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt));return 0
if __name__=='__main__':raise SystemExit(main())
