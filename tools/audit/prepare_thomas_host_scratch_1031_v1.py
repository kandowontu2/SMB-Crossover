"""New isolated Thomas RAM3 kernel with genuine a126 imported R0..R7.

This is a source build, not a cartridge overlay or a loader/admission claim.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
import thomas_original_cpu_1031_v1 as T
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
P=R/'build/thomas-c2-eight-melee-v1'
J=R/'build/contra-force-world-roles-1031-v2/joint'
O=R/'build/thomas-host-scratch-1031-v1'
G=R/'docs/qa/checkpoints/2026-10-31/thomas-first-host-resource-v1/resource-contract.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def main():
 assert not O.exists();(O/'source').mkdir(parents=True)
 assert sha(J/'candidate.nes')=='a12661c1ddad2e15a8ce0589e86b5510703fd390e6346a982b14a6be0b742e3c'
 assert sha(P/'component.bin')=='5cef447d11d74da8cec85ddd2fcc4b754c64a280558b976fed337afa3eb55a67'
 b=qualified(J/'candidate.nes');scratch=[address(b,'R'+str(i))for i in range(8)]
 assert scratch==list(range(3,11))
 src=(P/'source/component.s').read_text(encoding='utf-8');changes=[];out=[]
 for line in src.splitlines():
  body,sep,comment=line.partition(';')
  # Only instruction operands, never immediates/data/comments/label values.
  m=re.search(r'\b(?:lda|ldx|ldy|sta|stx|sty|adc|sbc|and|ora|eor|cmp|cpx|cpy|inc|dec|asl|lsr|rol|ror|bit|jmp)\s+(?:a:)?\(?\$([0-9a-fA-F]{2,4})(?![0-9a-fA-F])',body,re.I)
  if m and int(m[1],16)<8:
   old=body;start=m.start(1)-1;body=body[:start]+'R'+str(int(m[1],16))+body[m.end(1):]
   changes.append(dict(before=old,after=body))
  out.append(body+(sep+comment if sep else ''))
 src='\n'.join(out)+'\n'
 src=src.replace(' .segment "CODE"',' .importzp R0,R1,R2,R3,R4,R5,R6,R7\n .segment "CODE"',1)
 src+='\n.export ThomasKernelEnd\nThomasKernelEnd:\n'
 (O/'source/component.s').write_text(src,encoding='utf-8')
 # Actual host imports are verified against its DBG and original memory producer.
 memory=R/'build/bt-ready-menu-1031-v2/joint/src/memory.s'
 assert 'RESERVE_ZP NmiR0, 1' in memory.read_text() and 'RESERVE_ZP R0, 1' in memory.read_text()
 host='; Isolated link imports, values authenticated from exact current host DBG.\n'
 for i,a in enumerate(scratch):host+=f'.exportzp R{i}\nR{i}=${a:02X}\n'
 (O/'source/host-imports.s').write_text(host,encoding='utf-8')
 # Cold table and player HP dependencies become real emitted source data.
 # Nonplayer-only damage tables remain explicit, not borrowed host addresses.
 donor=T.donor();prg=donor[16:16+32768]
 deps=' .setcpu "6502"\n .segment "CODE"\n'
 for start,end in [(0x80f8,0x8120),(0xbca0,0xbdd0)]:
  names=[int(n,16)for n in re.findall(r'\.import ThomasOriginal_([0-9A-F]{4})',src)if start<=int(n,16)<end]
  for at in range(start,end):
   if at in names:deps+=f'.export ThomasOriginal_{at:04X}\nThomasOriginal_{at:04X}:\n'
   deps+=f' .byte ${prg[at-0x8000]:02X}\n'
 # This foreign-enemy release branch is deliberately non-admitted. Any accidental
 # execution fails loudly rather than reaching unrelated host code at old $B243.
 deps+='.export ThomasOriginal_B243\nThomasOriginal_B243: brk\n.export ThomasImageEnd\nThomasImageEnd:\n'
 (O/'source/dependencies.s').write_text(deps,encoding='utf-8')
 (O/'source/component.cfg').write_text('MEMORY { LAB:start=$A000,size=$2000,file=%O,fill=yes,fillval=$ff; }\nSEGMENTS { CODE:load=LAB,type=ro; }\n',encoding='utf-8')
 cc=R/'tools/Windows/cc65/bin';commands=[]
 def run(cmd):
  guard=validate(cmd,O,cwd=O);p=subprocess.run([str(v)for v in cmd],cwd=O,capture_output=True,text=True)
  commands.append(dict(command=list(map(str,cmd)),guard=guard,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr));assert not p.returncode,p.stderr
 for n in ['component','dependencies','host-imports']:
  run([cc/'ca65.exe',O/f'source/{n}.s','-g','-o',O/f'{n}.o','-l',O/f'{n}.lst','--create-full-dep',O/f'{n}.dep'])
 run([cc/'ld65.exe','-C',O/'source/component.cfg',*[O/f'{n}.o'for n in ['component','dependencies','host-imports']],'-o',O/'component.bin','--dbgfile',O/'component.dbg','-Ln',O/'component.lbl','-m',O/'component.map'])
 dump(O/'build-commands.json',commands);dump(O/'scratch-source-projection.json',changes)
 labels=T.labels(O/'component.lbl');size=labels['ThomasImageEnd']-0xa000
 dump(O/'source-stage.json',dict(status='SOURCE_LINKED_ISOLATED_TRUE_HOST_SCRATCH',native=False,cartridge_changed=False,
  parent=sha(P/'source-stage.json'),host_sha256=sha(J/'candidate.nes'),scratch_imports=scratch,
  code_origin=0xa000,emitted_bytes=size,kernel_bytes=labels['ThomasKernelEnd']-0xa000,emitted_original_dependency_bytes=size-(labels['ThomasKernelEnd']-0xa000),
  physical_state='SelectedC2 C000..C817 retained; transaction scratch saves physical03..0A only. Logical original00..07 live in canonicalC2.',
  clarification='Frozen10f119 packet borrows literal00..07 and its ISR is a synthetic lab model. Its R0..7 wording does not describe actual a126 addresses.',
  unsupported='Nonplayer damageX0..5 and original indirect enemy damage metadata are not admitted; B243 fails by explicitBRK. Source playerX6 tested separately.',
  future_grant=sha(G),bindings={str(p):sha(p)for p in [Path(__file__),P/'source-stage.json',P/'source/component.s',J/'candidate.nes',J/'candidate.dbg',J/'candidate.lbl',memory,G,R/'tools/audit/private_build_outputs_v1.py']+[p for p in O.rglob('*')if p.is_file()]}))
 print(json.dumps(dict(result='SOURCE_LINKED',bytes=size,scratch=scratch,stage_sha256=sha(O/'source-stage.json'))))
if __name__=='__main__':main()
