"""Recover/reassemble exact donor source slices; allocate no host resources."""
import hashlib,json,subprocess
import recover_bubble_bobble_source_1101_v1 as B
from py65.disassembler import Disassembler

R=B.R;O=B.O
SPANS=[('oam_helpers',7,0xc38f,0xc3a8),('distance',7,0xc43e,0xc470),
 ('source_clock',7,0xce30,0xce4d),
 ('tile_queries',7,0xd0be,0xd162),('players',7,0xd18a,0xd771),
 ('bubbles',7,0xd882,0xe009),('trapped_enemy',6,0x9528,0x9603),
 ('special_pop',7,0xefd9,0xf01e)]


def main():
 idx=json.loads((O/'instruction-index.json').read_text());instructions={(b,pc):c for b,pc,c in idx['rows']}
 source=['; Bubble Bobble USA, exact original instruction/data slices.\n; Recovered labels are semantic annotations, not a claim of original source names.\n.setcpu "6502"']
 cfg=['MEMORY {'];segments=[];packed=[];entries=[];edges=[];known=lambda b,p:any(bb==b and lo<=p<hi for _,bb,lo,hi in SPANS)
 for name,bank,lo,hi in SPANS:
  m=B.image(bank);d=Disassembler(m);seg=name.upper();cfg.append(f' M_{seg}:start=${lo:04x},size=${hi-lo:x},file=%O;');segments.append(f' {seg}:load=M_{seg},type=ro;')
  source.append(f'\n.segment "{seg}"\n.org ${lo:04x}\n; Original physical PRG16K bank {bank}, ${lo:04X}..${hi-1:04X}.')
  pc=lo;count=0
  while pc<hi:
   code=instructions.get((bank,pc))
   if code and pc+len(code)<=hi:
    n,asm=d.instruction_at(pc);assert n==len(code) and bytes(code)==bytes(m.memory[pc:pc+n])
    mode=m.disassemble[code[0]][1]
    if mode in ['abs','abx','aby'] and code[1]+256*code[2]<256:asm=asm.replace('$','a:$',1)
    source.append(f' {asm} ; {bank}:{pc:04X} '+bytes(code).hex(' '));count+=1
    if code[0]in[0x20,0x4c]:
     dest=code[1]+256*code[2];db=7 if dest>=0xc000 else 6 if bank==7 else bank
     if not known(db,dest):edges.append(dict(bank=bank,pc=pc,target_bank=db,target=dest,kind='call'if code[0]==0x20 else'jump'))
    pc+=n
   else:
    end=pc+1
    while end<hi and (bank,end)not in instructions and end-pc<16:end+=1
    source.append(' .byte '+','.join(f'${x:02x}'for x in m.memory[pc:end])+f' ; {bank}:{pc:04X} data/unclassified')
    pc=end
  data=bytes(m.memory[lo:hi]);packed.append(data);entries.append(dict(name=name,bank=bank,start=lo,end_exclusive=hi,bytes=len(data),instructions=count,sha256=B.sha(data)))
 cfg+=['}','SEGMENTS {']+segments+['}'];(O/'donor-source.s').write_text('\n'.join(source)+'\n');(O/'donor-source.cfg').write_text('\n'.join(cfg)+'\n')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe',O/'donor-source.s','-o',O/'donor-source.o'],[cc/'ld65.exe','-C',O/'donor-source.cfg',O/'donor-source.o','-o',O/'donor-source.bin']]:
  p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,'\n'.join(p.stderr.splitlines()[:10])
 actual=(O/'donor-source.bin').read_bytes();assert actual==b''.join(packed)
 raw=B.ROM.read_bytes()[16+131072:];tiles=[];payload=bytearray()
 # Normal play CHR0=1; stage CHR1 banks2..5 share the actual blink tile.
 for t in range(0,0x30,2):
  at=4096+t*16;data=raw[at:at+32];tiles.append(dict(oam_tile=t,CHR_4k_bank=1,CHR_offset=at,output_offset=len(payload),bytes=32,sha256=B.sha(data)));payload+=data
 blank=raw[2*4096+0x260:2*4096+0x280]
 assert not any(blank) and all(raw[b*4096+0x260:b*4096+0x280]==blank for b in [2,3,4,5])
 tiles.append(dict(oam_tile=0x27,CHR_4k_bank=2,CHR_offset=2*4096+0x260,output_offset=len(payload),bytes=32,sha256=B.sha(blank)));payload+=blank
 (O/'donor-chr-closure.bin').write_bytes(payload)
 palette=list(B.image(7).memory[0xc556:0xc566])
 chrmeta=dict(bytes=len(payload),sha256=B.sha(payload),bitplane_8x8_tile_count=len(payload)//16,native_8x16_pair_count=len(payload)//32,normal_player_and_bubble=True,normal_sprite_CHR_bank=1,blink_CHR1_banks_verified_identical=[2,3,4,5],sprite_palette_source_address=0xc556,sprite_palette_bytes=palette,Bub_palette=palette[12:16],Bob_palette=palette[:4],tiles=tiles,not_included='Powerup fire/thunder/water, item/reward art and original enemy graphics; normal trap overlay can retain native enemy art only through an explicit host adapter. Boss mode switches CHR0 to6 and is not this component.')
 (O/'chr-closure.json').write_text(json.dumps(chrmeta,indent=2)+'\n')
 q=dict(passed=True,ROM_sha256=B.PIN,host_allocated=False,menu_admitted=False,source_bytes=len(actual),instruction_count=sum(x['instructions']for x in entries),source_ranges=entries,assembly_exact=True,source_sha256=B.sha(actual),external_direct_edges=edges,scope='Source recovery/reassembly only. Instructions/data are byte-exact at original addresses. External edges remain explicit imports; no relocation or host claim.')
 (O/'source-closure.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','source_bytes','instruction_count','assembly_exact','host_allocated']}))


if __name__=='__main__':main()
