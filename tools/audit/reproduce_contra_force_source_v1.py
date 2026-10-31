"""Genuine source reproduction from pinned original CF; guarded private outputs."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
from private_build_outputs_v1 import validate
P=R/'build/contra-force-source-v1';S=P/'source';O=R/'build/contra-force-reproduction-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def main():
 assert not O.exists();O.mkdir()
 h=json.loads((P/'source-fetch.json').read_text())
 assert sha(P/'source-fetch.json')=='613c5d1bdcbfe4f84335181a8b344e1975fb796192ecac11c3b5edf86eaf9e14'
 for e in h['entries']:assert sha(e['path'])==e['sha256']
 raw=Path(h['original_ROM']).read_bytes();assert sha(h['original_ROM'])==h['original_ROM_sha256']
 prefix=r'^.\s.\s.\s.\s.\s.\s0x......\s..:....:\s..\s..\s..'
 for p in sorted(S.iterdir()):
  if p.suffix in['.asm','.inc']:
   text=p.read_text(encoding='utf-8');out=re.sub(prefix,'   ',text,flags=re.M)
   assert not re.search(r'^.{12}0x[0-9A-Fa-f]{6}',out,re.M),p
   (O/('copy_'+p.name)).write_text(out,encoding='utf-8',newline='\n')
 (O/'ld65.cfg').write_bytes((S/'ld65.cfg').read_bytes())
 dpcm=raw[16+0x1c040:16+0x1cf00]
 assert len(dpcm)==3776 and hashlib.sha1(f'blob {len(dpcm)}\0'.encode()+dpcm).hexdigest()=='e237e250d47f80ed502f7cae16bb678d7196e66f'
 (O/'DPCM.bin').write_bytes(dpcm)
 ca=R/'tools/Windows/cc65/bin/ca65.exe';ld=R/'tools/Windows/cc65/bin/ld65.exe';logs=[]
 def run(cmd):
  proof=validate(cmd,O,cwd=O)
  p=subprocess.run([str(v)for v in cmd],cwd=O,capture_output=True,text=True)
  row=dict(command=[str(v)for v in cmd],cwd=str(O),outputs=proof,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
  logs.append(row);save(O/'commands.json',logs);assert p.returncode==0,row
 objects=[]
 for p in sorted(O.glob('copy_bank_*.asm')):
  o=p.with_suffix('.o');objects.append(o)
  run([ca,'--cpu','6502x','-U','-g','--create-full-dep',p.with_suffix('.dep'),'-o',o,p])
 run([ld,'-C',O/'ld65.cfg','-o',O/'PRG_ROM.bin','-Ln',O/'candidate.lbl','--dbgfile',O/'candidate.dbg','-m',O/'candidate.map',*objects])
 prg=(O/'PRG_ROM.bin').read_bytes();assert len(prg)==128*1024
 original=raw[16:16+128*1024];changes=[i for i,(a,b)in enumerate(zip(prg,original))if a!=b]
 assert not changes,(len(changes),changes[:20])
 (O/'candidate.nes').write_bytes(raw[:16]+prg+raw[16+128*1024:]);assert sha(O/'candidate.nes')==h['original_ROM_sha256']
 files={Path(__file__),P/'source-fetch.json',S/'ld65.cfg',ca,ld}|{Path(e['path'])for e in h['entries']}|{p for p in O.iterdir()if p.is_file()}
 proof=dict(passed=True,status='EXACT_ORIGINAL_SOURCE_REPRODUCTION_NO_HOST_ADMISSION',source_commit=h['commit'],original_ROM_sha256=h['original_ROM_sha256'],candidate_sha256=sha(O/'candidate.nes'),PRG_bytes=len(prg),changed_PRG_bytes=len(changes),original_header_CHR_preserved=True,native=False,host=False,bindings={str(p.resolve()):sha(p)for p in sorted(files)})
 save(O/'proof.json',proof)
 print(json.dumps(dict(passed=True,path=str(O/'proof.json'),sha256=sha(O/'proof.json'),ROM=proof['candidate_sha256'],bindings=len(proof['bindings']))),flush=True)
if __name__=='__main__':main()
