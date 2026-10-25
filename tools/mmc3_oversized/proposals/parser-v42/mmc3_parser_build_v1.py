from pathlib import Path
import argparse, configparser, hashlib, json, shutil, subprocess, sys

R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover')
D=Path(__file__).resolve().parent
P=D/'mmc3-static-call-v39'
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load,address,location

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def proc(text,name):
 a=text.index('.proc '+name+'\n');b=text.index('.endproc',a)+len('.endproc')
 return text[a:b]
def compile_rom(source,rom):
 cfg=configparser.ConfigParser();cfg.optionxform=str;cfg.read(source/'build_options.ini')
 opts={k:v for section in cfg.values()for k,v in section.items()}
 opts.update(MAPPER_MMC3='1',MAPPER_MMC5='0',ENABLE_CROSSOVER='1',ENABLE_MMC3_OVERSIZED='1',ENABLE_MMC5_EXPANDED='0')
 cmd=[str(R/'tools/Windows/cc65/bin/cl65.exe'),'--cpu','6502x','-t','nes','-g','-Oisr','-vm','-T','-C',str(source/'smb1base-mmc3-oversized.cfg'),'--ld-args','--dbgfile,'+str(rom.with_suffix('.dbg')),'--include-dir',str(source),'--asm-include-dir',str(source/'src'),'--asm-include-dir',str(source),'--bin-include-dir',str(source),'-m',str(rom.with_suffix('.map')),'-Ln',str(rom.with_suffix('.lbl')),'-o',str(rom)]
 for k,v in opts.items():cmd+=['--asm-define',k+'='+v,'-D',k+'='+v]
 cmd += [str(source/'src/main.c'),str(source/'src/entrypoint.s')]
 with rom.with_suffix('.build.log').open('w')as log: p=subprocess.run(cmd,cwd=source,stdout=log,stderr=subprocess.STDOUT)
 assert p.returncode==0,rom.with_suffix('.build.log').read_text()[-3500:]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--current',action='store_true');args=ap.parse_args()
 O=D/args.out;O.mkdir(exist_ok=False);source=O/'source'
 m=json.loads((R/'tools/mmc3_oversized/proposals/static-call-v39/repairs.proposed.json').read_text())
 if args.current:
  tools=O/'tools';tools.mkdir();shutil.copy(R/'tools/prepare_mmc3_oversized.py',tools);shutil.copy(R/'tools/mmc3_current_repairs.py',tools)
  assets=tools/'mmc3_oversized';assets.mkdir();shutil.copy(R/'tools/mmc3_oversized/mmc3-menu-previews.chr',assets)
  (assets/'repairs.json').write_text(json.dumps(m,indent=2))
  with(O/'prepare.log').open('w')as log:p=subprocess.run([sys.executable,str(tools/'prepare_mmc3_oversized.py'),'--source-root',str(R),'--output',str(source),'--reference-rom','C:/Users/kando/Downloads/SMB-Crossover-Current-MMC5.nes'],cwd=R,stdout=log,stderr=subprocess.STDOUT)
  assert p.returncode==0,(O/'prepare.log').read_text()[-3500:]
  baseline=O/'baseline.nes';compile_rom(source,baseline)
 else:
  shutil.copytree(P/'source',source,ignore=shutil.ignore_patterns('*.o'))
  baseline=P/'candidate.nes'
 old=load(baseline)
 warp_off=location(old,'WarpZoneNumbers');window=old['raw'][warp_off:warp_off+256];assert len(window)==256
 oldmega=(source/'src/megaman_weapons.s').read_text()
 native=proc((D/'mmc3-ship-lives-v25/source/src/megaman_weapons.s').read_text(),'MegaManResetBlockHealth')
 begin=oldmega.index('.proc MegaManResetBlockHealth\n');end=oldmega.index('\n.popseg',begin)+len('\n.popseg')
 common=oldmega[oldmega.index('::FarCallCommon:',begin):oldmega.index('  .res 25,$ea',begin)]
 assert common.count('\n  rts\n')==1
 newmega=oldmega[:begin]+native+oldmega[end:]
 oldbill=(source/'src/bill_native_rare.s').read_text();readwarp=proc(oldbill,'BillNativeReadWarp')
 resident=common+'  .assert *-FarCallCommon=49,error,"Resident common stays inside old51-byte warp-read slot"'
 newbill=oldbill.replace(readwarp,resident,1)
 cold='''
.pushseg
.segment "LOWCODE"
.proc BillNativeReadWarp
  BillRareCall M3ReadWarpCold
.endproc
.popseg
.pushseg
.segment "M3_WARP_READ"
.proc M3ReadWarpCold
  ldy M3WarpIndexedWindow,x
  ; Original endfar reloads the incoming A, setting only its N/Z result.
  sta BillNativeReturnA
  lda BillNativeReturnA
  jsr BillNativeCaptureP
  lda #7 | PRG_FIXED_8
  sta BillNativeReturnSelector
  rts
.endproc
M3WarpIndexedWindow:
'''+''.join('  .byte '+','.join('$%02x'%b for b in window[i:i+16])+'\n'for i in range(0,256,16))+'.popseg\n'
 newbill+='\n'+cold
 oldcfg=(source/'smb1base-mmc3-oversized.cfg').read_text()
 newcfg=oldcfg.replace('    M3_CELL_RESET: load=M3_FREE_FD,type=ro; # Append after native audio; preserve its original bytes.','    M3_WARP_READ: load=M3_FREE_FD,type=ro; # Cold warp read after exact native Gradius driver.')
 assert newcfg!=oldcfg
 changes=[('src/megaman_weapons.s',oldmega,newmega),('src/bill_native_rare.s',oldbill,newbill),('smb1base-mmc3-oversized.cfg',oldcfg,newcfg)]
 for path,before,after in changes:
  (source/path).write_text(after)
  row=next((z for z in m['text_repairs']if z['path']==path),None)
  if row is None:row=dict(path=path,chunks=[]);m['text_repairs'].append(row)
  # Only narrow exact replacements belong in the additive proposal.
  if 'megaman' in path: a=oldmega[begin:end];b=native
  elif 'bill_native' in path: a=readwarp;b=resident
  else:a='    M3_CELL_RESET: load=M3_FREE_FD,type=ro; # Append after native audio; preserve its original bytes.';b='    M3_WARP_READ: load=M3_FREE_FD,type=ro; # Cold warp read after exact native Gradius driver.'
  row['chunks'].append(dict(old=a,new=b))
  if 'bill_native' in path:row['chunks'].append(dict(old='; Append in the existing bank9 tail. Only an admitted ordinary Sophia head',new=cold+'\n; Append in the existing bank9 tail. Only an admitted ordinary Sophia head'))
 m['scope']='PRIVATE parser timing repair: six-byte original-base tiny code, resident common in old warp-read slot, native hot cell reset restored; cold warp table duplicates all256 indexed native source bytes. No native qualification or adoption.'
 m.pop('expected_ROM_sha256',None)
 (O/'repairs.proposed.json').write_text(json.dumps(m,indent=2))
 rom=O/'candidate.nes';compile_rom(source,rom);new=load(rom)
 assert new['raw'][:16]==old['raw'][:16]and len(new['raw'])==len(old['raw'])
 assert address(new,'MegaManResetBlockHealth')==address(old,'MegaManResetBlockHealth')
 assert new['raw'][location(new,'MegaManResetBlockHealth'):location(new,'MegaManResetBlockHealth')+92]==(D/'mmc3-ship-lives-v25/candidate.nes').read_bytes()[location(load(D/'mmc3-ship-lives-v25/candidate.nes'),'MegaManResetBlockHealth'):location(load(D/'mmc3-ship-lives-v25/candidate.nes'),'MegaManResetBlockHealth')+92]
 assert new['raw'][location(new,'M3WarpIndexedWindow'):location(new,'M3WarpIndexedWindow')+256]==window
 diff=[i for i,(a,b)in enumerate(zip(old['raw'],new['raw']))if a!=b]
 q=dict(compiled=True,adopted=False,native_tested=False,ROM_sha256=digest(rom),baseline_ROM_sha256=digest(baseline),current_source=args.current,changed_ROM_bytes=len(diff),changed_PRG_banks=sorted(set((i-16)//8192 for i in diff)),warp256_sha256=hashlib.sha256(window).hexdigest(),parser_body_bytes_exact_native=True,resident_common=address(new,'FarCallCommon'),public_warp_stub=address(new,'BillNativeReadWarp'),cold_warp=address(new,'M3ReadWarpCold'),cold_warp_bank=(location(new,'M3ReadWarpCold')-16)//8192,proposal_sha256=digest(O/'repairs.proposed.json'))
 (O/'build-proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)

if __name__=='__main__':main()
