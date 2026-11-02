"""Publish source body colors and retain native area backdrop before cold load."""
import json,subprocess
import prepare_shinobi_owning_graft_1101_v1 as S
import check_hogan_current_bounded_v1 as M
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
R=S.R;BASE=R/'build/shinobi-death-1101-v11';O=R/'build/shinobi-palette-1101-v12'


def main():
 O.mkdir(exist_ok=True);assert S.sha(BASE/'candidate.nes')=='fa5e38ce1202f6cb8de9eb79b25dd27627006ea020afded5ce090f40f1bab5aa'
 b=scoped_load(BASE/'candidate.nes');raw=bytearray(b['raw'])
 donor=(R/'build/shinobi-component-1101-v2/intro-reference.bin').read_bytes()
 assert donor[:8]==b'NATIVE01' and donor[8479:8482]==bytes([15,54,28])
 bg=bytes(raw[location(b,'BackgroundColors'):location(b,'BackgroundColors')+8])
 src=(BASE/'resident.s').read_text()
 for n in ['VRAM_Buffer1','VRAM_Buffer1_Offset','BackgroundColorCtrl','AreaType']:src+=f'{n}=${address(b,n):04x}\n'
 src+='.include "shinobi_palette_1101_v12.inc"\nShBackgroundColors:.byte '+','.join(map(str,bg))+'\n'
 (O/'resident.s').write_text(src)
 for name in ['resident.cfg','shinobi-cookie.bin','shinobi_damage_1101_v10.inc']:(O/name).write_bytes((BASE/name).read_bytes())
 cc=R/'tools/Windows/cc65/bin'
 def run(args):subprocess.run(list(map(str,args)),check=True)
 run([cc/'ca65.exe','-g','-I',O,'-I',R/'tools/reference','--bin-include-dir',O,O/'resident.s','-o',O/'resident.o'])
 run([cc/'ld65.exe','-C',O/'resident.cfg',O/'resident.o','-o',O/'resident.bin','-Ln',O/'resident.lbl'])
 lab=S.labels(O/'resident.lbl');code=bytearray((O/'resident.bin').read_bytes());assert len(code)<=1536
 for row,target in [(1,'ShChr'),(5,'ShInjury'),(26,'ShColors')]:
  at=lab['ShServiceVeneers']-0xa800+row*3;t=lab[target];code[at:at+3]=bytes([76,t&255,t>>8])
 start=16+65*8192+0x800;old=(BASE/'resident.bin').read_bytes()
 change=range(lab['ShServiceVeneers']-0xa800+78,lab['ShServiceVeneers']-0xa800+81)
 assert all(a==z or i in change for i,(a,z) in enumerate(zip(old,code)))
 raw[start:start+len(code)]=code;(O/'resident.bin').write_bytes(code)
 # Both Metal and Shinobi need native world palette before cache loading.
 gate=(R/'build/shinobi-route-1101-v8/route.s').read_text()
 oldtext=' lda SelectedCharacter\n cmp #36\n bne MetalRoute\n jmp ShinobiRoute\nMetalRoute:\n cpy #32\n bne MetalOrdinary'
 newtext=' cpy #32\n bne ChooseOwner'
 assert oldtext in gate;gate=gate.replace(oldtext,newtext)
 gate=gate.replace('MetalOrdinary:\n','ChooseOwner:\n lda SelectedCharacter\n cmp #36\n bne MetalOrdinary\n jmp ShinobiRoute\nMetalOrdinary:\n')
 (O/'route.s').write_text(gate)
 (O/'route.cfg').write_text((R/'build/shinobi-route-1101-v8/route.cfg').read_text().replace('shinobi-route-1101-v8','shinobi-palette-1101-v12'))
 run([cc/'ca65.exe',O/'route.s','-o',O/'route.o'])
 run([cc/'ld65.exe','-C',O/'route.cfg',O/'route.o','-o',O/'unused.bin'])
 at=16+79*8192+0x707;oldgate=(R/'build/shinobi-route-1101-v8/gate.bin').read_bytes()
 assert raw[at:at+48]==oldgate+bytes([234])*(48-len(oldgate))
 newgate=(O/'gate.bin').read_bytes();assert len(newgate)<=48
 raw[at:at+48]=newgate+bytes([234])*(48-len(newgate))
 assert (O/'route.bin').read_bytes()==(R/'build/shinobi-route-1101-v8/route.bin').read_bytes()
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.lbl','.dbg']:(O/('candidate'+suffix)).write_bytes((BASE/('candidate'+suffix)).read_bytes())
 b=scoped_load(O/'candidate.nes');seed=M.fresh(b);cases=0
 for control in range(8):
  for offset in [0,12,56,57]:
   m=M.fork(seed);M.put(m,SelectedCharacter=36,VRAM_Buffer1_Offset=offset,BackgroundColorCtrl=control,AreaType=1)
   at=address(b,'VRAM_Buffer1');m[at:at+64]=[165]*64;before=bytes(m[at:at+64])
   result=M.invoke(m,'HuColors');assert result['P']&1
   if offset<57:
    assert bytes(m[at+offset:at+offset+8])==bytes([63,16,4,bg[control or 1],15,54,28,0])
    assert M.get(m,'VRAM_Buffer1_Offset')==offset+7
    assert bytes(m[at:at+offset])==before[:offset]
   else:assert bytes(m[at:at+64])==before and M.get(m,'VRAM_Buffer1_Offset')==offset
   cases+=1
 q=dict(passed=True,ROM_sha256=S.sha(O/'candidate.nes'),resident_bytes=len(code),palette_cases=cases,source_body_colors=[15,54,28],native_background_preserved=True,cold_world_route=True,installed=False,menu_unlocked=False,
        limits='Original P0 body colors only; original shot/magic P2 colors still need native sharing/remap review. Cold callback CPU fixture, not emulator palette proof.')
 (O/'result.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
