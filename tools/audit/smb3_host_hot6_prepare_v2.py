"""Private fixed-original-page6 lease; frozen7469 is never overwritten."""
from pathlib import Path
import argparse, json, re, shutil, subprocess, sys, traceback
from smb3_host_current3b_cpu_v1 import D,R,SOURCE_ROWS,sha,put
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

BASE=D/'smb3-host-current3b-v3'
PARENT='7469d9f62af3161c896b844546ead66002bb425ba8b5143692b1c2ae1d9f1219'

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();o=a.output.resolve();assert not o.is_relative_to(R);o.mkdir(parents=True,exist_ok=False)
 try:
  assert sha(BASE/'candidate.nes')==PARENT
  src=o/'source';src.mkdir()
  manifest=json.loads((BASE/'source-manifest.json').read_text())
  for name,h in manifest.items():
   f=BASE/'source'/name;assert sha(f)==h,name;target=src/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target)
  f=src/'src/smb3_native_standalone.s';raw=f.read_bytes();nl='\r\n'if b'\r\n'in raw else'\n';text=raw.decode();plain=text.replace('\r\n','\n')
  # Original reachable executable writes mapper slots4/5 only. Cold sets6=3.
  mapper=[r for r in SOURCE_ROWS if re.search(r'\$5ff[89a-f]',r['source_instruction'],re.I)]
  assert mapper and all(re.search(r'\$5ff[cd]',r['source_instruction'],re.I)for r in mapper),mapper
  assert 'B3InitialMaps:\n .byte 7,0,1,2,5,6,3,4' in plain
  writes=[s for s in plain.splitlines()if re.search(r'\b(sta|stx|sty|inc|dec)\s+B3VirtualMaps',s,re.I)]
  assert writes==[' sta B3VirtualMaps,x',' sta B3VirtualMaps+4',' sta B3VirtualMaps+5'],writes
  # Preserve old generic/known callable helpers as compatibility paths. Only
  # source-owned call operands use new fixed-map readers. Those readers execute
  # entirely in C38; the A86 caller resumes only after the real restore bridge.
  helper=[];delta=[]
  for m in re.finditer(r'^(B3Known[0-9A-F]+):\n php\n jsr B3KnownPage6\n lda (\$b[0-9a-f]{3},[xy])\n jmp B3KnownRestore$',plain,re.M):
   old,target=m[1],m[2];new=old.replace('B3Known','B3Hot6')
   before=f' jsr {old}\n nop\n nop';assert plain.count(before)==1,(old,plain.count(before));plain=plain.replace(before,f' jsr {new}\n nop\n nop')
   helper +=[new+':',' lda #93|MMC5_PRG_ROM',' BankPRGA a',' lda '+target,' rts']
   delta.append(dict(original_helper=old,new_helper=new,source_PC=int(old[7:],16),physical_payload_page=3,physical_A_bank=93,load=target))
  assert len(delta)==13
  before=' jsr B3SourceA000\n jsr B3Restore';assert plain.count(before)==1;plain=plain.replace(before,' jsr B3Hot6Play\n jsr B3Restore')
  extra='\n'.join(helper+['B3Hot6Play:',' jsr B3SourceA000',' php',' pha',' lda #86|MMC5_PRG_ROM',' BankPRGA a',' pla',' plp',' rts'])+'\n'
  assert plain.count('B3CoreEnd:')==1;plain=plain.replace('B3CoreEnd:',extra+'B3CoreEnd:')
  f.write_bytes(plain.replace('\n',nl).encode())
  put(o/'source-manifest.json',{str(q.relative_to(src)).replace('\\','/'):sha(q)for q in src.rglob('*')if q.is_file()})
  put(o/'preparation.json',dict(source_only=True,native_run=False,parent_ROM_sha256=PARENT,source_map_writers=mapper,compiled_adapter_mapper_writes=writes,constant_map6=3,actual_private_sites=delta,new_RAM_bytes=0,checked_generic_and_known_compatibility_helpers_unchanged=True,source_change=[dict(path='src/smb3_native_standalone.s',before=sha(BASE/'source/src/smb3_native_standalone.s'),after=sha(f))],checker_sha256=sha(__file__)))
  cmd=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(src),'--output',str(o/'candidate.nes')];r=subprocess.run(cmd,cwd=R,capture_output=True,text=True);put(o/'build-command.json',dict(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0,r.stdout+r.stderr
  cmd=[sys.executable,str(R/'tools/prepare_smb3_dmc_mirrors.py'),'--source',str(src),'--rom',str(o/'candidate.nes')];r=subprocess.run(cmd,cwd=R,capture_output=True,text=True);put(o/'mirror-command.json',dict(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr));assert r.returncode==0,r.stdout+r.stderr
  old,new=scoped_load(BASE/'candidate.nes'),scoped_load(o/'candidate.nes');changed=[]
  assert old['raw'][:16]==new['raw'][:16]and old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
  for bank in range(128):
   n=sum(x!=y for x,y in zip(old['raw'][16+bank*8192:16+(bank+1)*8192],new['raw'][16+bank*8192:16+(bank+1)*8192]))
   if n:changed.append(dict(bank=bank,changed_bytes=n))
  assert {r['bank']for r in changed}=={38,86},changed
  # Real old boundaries remain exact except the expanded true core-end marker.
  moved=[]
  for name,sym in old['syms'].items():
   if name not in new['syms']:raise AssertionError(('Removed old symbol',name))
   if sym.get('val')!=new['syms'][name].get('val'):moved.append(name)
  assert moved==['B3CoreEnd'],moved
  put(o/'layout.json',dict(passed=True,source_only=True,native_run=False,parent_ROM_sha256=PARENT,ROM_sha256=sha(o/'candidate.nes'),changed_banks=changed,header_and_all_CHR_exact=True,old_public_entries_and_following_boundaries_preserved=True,legitimate_true_end_symbol_growth=moved,core_end_before=address(old,'B3CoreEnd'),core_end_after=address(new,'B3CoreEnd'),core_remaining=0xdfe8-address(new,'B3CoreEnd'),additional_RAM_bytes=0,E70_E97_and_final127_literal_to_parent=True,limits='Private measured-reader optimization only; no native/timing or authentic-music adoption claim. Original compatibility helpers remain, genuine source caller A-window policy changes intentionally.'))
  print(json.dumps(dict(passed=True,ROM_sha256=sha(o/'candidate.nes'),changed_banks=changed,core_remaining=0xdfe8-address(new,'B3CoreEnd'))))
 except Exception as e:put(o/'failure.json',dict(passed=False,error=str(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
