"""Reproduce the installed wall source and assemble its fixed-footprint successor."""
from pathlib import Path
import hashlib,json,re,subprocess
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
R=Path(__file__).resolve().parents[2]
O=R/'build/arthur-side-clamp-1101-v8'
BASE=R/'build/shinobi-bbox-candidate-1101-v30/candidate.nes'
SHA='6f319d2039f920bc85e4a6bfe6ee3327996b42020e03c09e671142eada2a6428'
SOURCE=R/'tools/reference/arthur_side_clamp_1101_v8.s'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 O.mkdir(exist_ok=True);b=scoped_load(BASE);assert sha(BASE)==SHA
 src=(R/'src/samus.s').read_text();start=src.index('.proc SamusStopAtWallBanked');end=src.index('.endproc',start)+len('.endproc')
 old='.segment "SAMUS"\n'+src[start:end]+'\n';new=SOURCE.read_text()
 combined=re.sub(r';[^\n]*','',old+new)
 local=set(re.findall(r'(?m)^\s*([A-Za-z]\w*):',combined))|{'SamusStopAtWallBanked'}
 tokens=set(re.findall(r'\b[A-Za-z]\w*\b',combined));pre='.setcpu "6502"\n.macpack longbranch\n'
 for name in sorted(tokens&set(b['syms'])-local):pre+=f'{name}=${address(b,name):04x}\n'
 assert address(b,'CHARACTER_SIMON')<128
 pc=address(b,'SamusStopAtWallBanked');at=location(b,'SamusStopAtWallBanked');cc=R/'tools/Windows/cc65/bin'
 assert pc==0xa290 and(at-16)//8192==10
 (O/'wall.cfg').write_text(f'MEMORY{{M:start=${pc:04x},size=215,file=%O;}}SEGMENTS{{SAMUS:load=M,type=ro;}}')
 def assemble(name,text):
  (O/(name+'.s')).write_text(pre+text)
  for cmd in [[cc/'ca65.exe','-g',O/(name+'.s'),'-o',O/(name+'.o')],[cc/'ld65.exe','-C',O/'wall.cfg',O/(name+'.o'),'-o',O/(name+'.bin'),'-Ln',O/(name+'.lbl')]]:
   cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
  return(O/(name+'.bin')).read_bytes()
 previous=assemble('old-wall',old);assert len(previous)==215 and previous==b['raw'][at:at+215]
 current=assemble('new-wall',new);assert len(current)==215
 q=dict(source_reproduced_previous_wall=True,installed_base_sha256=SHA,physical_PRG_bank=10,CPU_half_open=['A290','A367'],new_payload_bytes=215,new_PRG_CHR_RAM_bytes=0,source_funding='Shared foreign probe arithmetic via Y/stack while retaining SmTempX/Page; shared velocity/fraction return; reuse original left-away gate; Arthur CMP32 carry feeds exact SBC1/ADC15.',source_only=True,private_candidate_emitted=False,bindings={str(p.relative_to(R)):sha(p)for p in [Path(__file__),SOURCE,O/'new-wall.bin',O/'new-wall.lbl',R/'src/samus.s']})
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
