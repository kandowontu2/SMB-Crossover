"""Private unused-core absolute ROM reader optimization; no host hook/native use."""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess, sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'smb3-native-core-v5'
EXPECTED='a4be8e02de0f8c0c43e5a7c94e4719e8b62c2ae80c1b1769978b06e73f2cac98'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):assert not p.exists();p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();o=a.output.resolve()
 assert not o.is_relative_to(R);assert sha(BASE/'candidate.nes')==EXPECTED;o.mkdir(parents=True,exist_ok=False)
 src=o/'source';shutil.copytree(BASE/'source',src)
 oldmanifest={str(q.relative_to(src)).replace('\\','/'):sha(q)for q in src.rglob('*')if q.is_file()}
 f=src/'src/smb3_native_standalone.s';raw=f.read_bytes();nl='\r\n'if b'\r\n'in raw else'\n';text=raw.decode()
 prep=json.loads((BASE/'preparation.json').read_text());sites=[]
 for row in prep['emitted_original_instruction_rows']:
  m=re.fullmatch(r'jsr B3ReadAbs([XY])\n \.word \$([0-9a-f]{4})',row['linked_instruction'])
  if not m:continue
  reg,word=m[1],int(m[2],16);page=(word-0x8000)>>12;off=word&4095
  assert 0x8000<=word<=0xffff and off+255<4096,(word,off)
  pc=row['source_PC'];old=f'B3Source{pc:04X}:\n '+row['linked_instruction'];new=f'B3Source{pc:04X}:\n jsr B3Known{pc:04X}\n nop\n nop'
  old,new=(s.replace('\n',nl)for s in [old,new]);assert text.count(old)==1,(pc,text.count(old));text=text.replace(old,new)
  sites.append(dict(source_PC=pc,source_address=word,index_register=reg,logical_page=page,mapped_address=0xb000+off,index_domain=[0,255],last_source_address=word+255,last_mapped_address=0xb000+off+255,old_bytes=5,new_bytes=5,genuine_entry=f'B3Known{pc:04X}'))
 assert len(sites)==39 and sorted({x['logical_page']for x in sites})==[1,2,3,6]
 lines=['; Known absolute sites: every possible byte index stays in its logical4K page.',
        '; CurrentBank remains foreground/fixture shadow; no A lease or new state.',
        '; Preserve all original flags except LDA N/Z and X/Y; never borrow R0/R1.']
 for site in sites:
  lines +=[site['genuine_entry']+':',' php',f" jsr B3KnownPage{site['logical_page']}",f" lda ${site['mapped_address']:04x},{site['index_register'].lower()}",' jmp B3KnownRestore']
 for page in [1,2,3,6]:
  lines +=[f'B3KnownPage{page}:',' sty B3SavedY',f' ldy B3VirtualMaps+{page}',' lda B3PayloadBanks,y',' ora #MMC5_PRG_ROM',' BankPRGA a',' ldy B3SavedY',' rts']
 lines +=['B3KnownRestore:',' sta B3Value',' lda CurrentBank',' BankPRGA a',' plp',' lda B3Value',' rts','']
 assert text.count('B3CoreEnd:')==1;text=text.replace('B3CoreEnd:',nl.join(lines)+'B3CoreEnd:');f.write_bytes(text.encode())
 assert f.read_bytes().count(b'\r\n')==text.count('\r\n')
 newmanifest={str(q.relative_to(src)).replace('\\','/'):sha(q)for q in src.rglob('*')if q.is_file()};changed=[n for n in oldmanifest if oldmanifest[n]!=newmanifest[n]]
 assert changed==['src/smb3_native_standalone.s'],changed
 put(o/'source-manifest.json',newmanifest);put(o/'source-delta.json',[dict(path=n,old_sha256=oldmanifest[n],new_sha256=newmanifest[n])for n in changed]);put(o/'known-sites.json',sites)
 cmd=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(src),'--output',str(o/'candidate.nes')]
 run=subprocess.run(cmd,cwd=R,capture_output=True,text=True);put(o/'build-command.json',dict(command=cmd,returncode=run.returncode,stdout=run.stdout,stderr=run.stderr));assert run.returncode==0,run.stdout+run.stderr
 b=scoped_load(o/'candidate.nes');old=scoped_load(BASE/'candidate.nes');retained=0
 for n,s in old['syms'].items():
  if n=='B3CoreEnd':continue
  assert n in b['syms']and b['syms'][n]['val']==s['val'],('Old real PC changed',n,s,b['syms'].get(n));retained+=1
 differences={}
 for bank in range(128):
  at=16+bank*8192;dd=[i for i in range(8192)if old['raw'][at+i]!=b['raw'][at+i]]
  if dd:differences[bank]=len(dd)
 assert set(differences)=={38};assert old['raw'][:16]==b['raw'][:16]and old['raw'][16+128*8192:]==b['raw'][16+128*8192:]
 assert address(b,'B3CoreEnd')<=0xdfe8
 put(o/'proof.json',dict(passed=True,source_only=True,native_run=False,host_integration=False,parent_ROM_sha256=EXPECTED,ROM_sha256=sha(o/'candidate.nes'),changed_PRG_bytes=differences,changed_source=changed,known_absolute_sites=len(sites),source_index_domain=[0,255],generic_indirect_readers_unchanged=True,new_RAM_bytes=0,core_bytes=address(b,'B3CoreEnd')-address(b,'B3CoreStart'),core_cap=5120,retained_parent_symbols=retained,legitimate_symbol_exception='B3CoreEnd moves to the genuine new end of previously unused standalone core; no callable/host PC moves',source_EOL_preserved=True,old_E_clones_exact_to_OLD_parent_only=True,NOT_current3b_clone_or_native_evidence=True,tool_sha256=sha(__file__)))
 print((o/'proof.json').read_text())
if __name__=='__main__':main()
