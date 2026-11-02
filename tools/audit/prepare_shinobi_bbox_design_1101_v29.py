"""Assemble bounded bbox design and prove its existing-owned byte funding.

No candidate ROM is written. The public933 baseline remains immutable.
"""
import json,re,subprocess
import prepare_shinobi_owning_graft_1101_v1 as S
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load

R=S.R;O=R/'build/shinobi-bbox-design-1101-v29';BASE=R/'build/roster-combined-1101-v1/candidate.nes'
PIN='933c0650ea5c1db0e613836be7ba9d07c67a25142276fe4efa6874f1063e04df'
PAGES=[506,507,508,509,510,513,515]


def assemble(name,source,cfg):
 (O/(name+'.s')).write_text(source);(O/(name+'.cfg')).write_text(cfg)
 cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe','-I',O,'-I',R/'build/shinobi-menu-1101-v13','-I',R/'tools/reference','--bin-include-dir',O,O/(name+'.s'),'-o',O/(name+'.o')],[cc/'ld65.exe','-C',O/(name+'.cfg'),O/(name+'.o'),'-o',O/(name+'.bin'),'-Ln',O/(name+'.lbl')]]:
  z=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert z.returncode==0,z.stderr
 return bytearray((O/(name+'.bin')).read_bytes()),S.labels(O/(name+'.lbl'))


def main():
 O.mkdir(exist_ok=True);assert S.sha(BASE)==PIN;b=scoped_load(BASE);raw=b['raw']
 constants={n:address(b,n)for n in b['syms']if re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',n)}
 constants.update(S.labels(R/'build/shinobi-hurt-layout-1101-v5/component.lbl'))
 oldtable=raw[16+1048576+515*1024+0x2f8:16+1048576+515*1024+0x3f8]
 native=location(b,'MTileAttribute');assert address(b,'MTileAttribute')==0xef36 and(native-16)//8192==127
 assert oldtable==raw[native:native+256]
 cookie=raw[16+65*8192+0xa78:16+65*8192+0xa88];(O/'shinobi-cookie.bin').write_bytes(cookie)
 source=(R/'build/shinobi-menu-1101-v13/resident.s').read_text()
 owner=(R/'build/shinobi-chr-owner-1101-v18/owner.s').read_text().split('.segment "OWNER"\n',1)[1]
 source+='\n.segment "SHINOBI_RESIDENT"\n.export ShShotBankGate\nShShotBankGate:\n'+owner
 cfg='MEMORY { B:start=$a800,size=$600,file=%O; } SEGMENTS { SHINOBI_RESIDENT:load=B,type=ro; }'
 original,oldlab=assemble('resident-original',source,cfg)
 def vectors(code,lab):
  for row,name in [(1,'ShChr'),(5,'ShInjury'),(26,'ShColors')]:
   at=lab['ShServiceVeneers']-0xa800+3*row;t=lab[name];code[at:at+3]=bytes([76,t&255,t>>8])
  for row,name in [(10,'BlockBufferColli_Head'),(14,'BlockBufferColli_Side')]:
   at=lab['ShServiceVeneers']-0xa800+3*row;t=address(b,name);code[at:at+3]=bytes([76,t&255,t>>8])
 vectors(original,oldlab)
 assert original==raw[16+65*8192+0x800:16+65*8192+0x800+len(original)],'Current resident preimage differs'
 damage=(R/'build/shinobi-menu-1101-v13/shinobi_damage_1101_v10.inc').read_text()
 save=' .repeat 8,I\n lda R0+I\n pha\n .endrepeat'
 restore=' .repeat 8,I\n pla\n sta R0+7-I\n .endrepeat'
 assert damage.count(save)==damage.count(restore)==1
 damage=damage.replace(save,' ldx #0\nShInjurySaveScratch:\n lda R0,x\n pha\n inx\n cpx #8\n bne ShInjurySaveScratch').replace(restore,' ldx #7\nShInjuryRestoreScratch:\n pla\n sta R0,x\n dex\n bpl ShInjuryRestoreScratch')
 (O/'shinobi-damage-compact.inc').write_text(damage)
 source=source.replace('.include "shinobi_damage_1101_v10.inc"','.include "shinobi-damage-compact.inc"')
 source+='''
.export ShBBoxIngress
ShFullBoxVeneer=ShServiceVeneers+48
ShBBoxIngress:
 php
 pha
 lda SelectedCharacter
 cmp #36
 beq ShBBoxOwn
 pla
 plp
 jmp BoundingBoxCore
ShBBoxOwn:
 pla
 plp
 ShRomFar ShFullBoxVeneer,193
 bcs ShBBoxDone
 jmp BoundingBoxCore
ShBBoxDone:
 rts
'''
 source='BoundingBoxCore=$%04x\n'%address(b,'BoundingBoxCore')+source
 resident,newlab=assemble('resident-design',source,cfg);vectors(resident,newlab)
 assert len(original)==1524 and len(resident)==1534
 assert newlab['ShBBoxIngress']==0xadd6 and newlab['ShShotBankGate']==oldlab['ShShotBankGate']-30
 # Save the fully linked source proposal, including the real veneer overrides.
 (O/'resident-design.bin').write_bytes(resident)
 worker=(R/'tools/reference/shinobi_bbox_design_1101_v29.inc').read_text()
 names=set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b',worker))
 defs=''.join(f'{n}=${constants[n]:04x}\n'for n in sorted(names&constants.keys()))
 code,worklab=assemble('body-design','.setcpu "6502"\n'+defs+worker,'MEMORY { B:start=$baf8,size=256,file=%O; } SEGMENTS { SHINOBI_KERNEL:load=B,type=ro; }')
 q=dict(passed=True,baseline_sha256=PIN,ROM_written=False,current_resident_preimage_exact=True,original_resident_bytes=len(original),compact_save_restore_saves_bytes=30,design_resident_bytes=len(resident),resident_gate_start=newlab['ShBBoxIngress'],resident_gate_bytes=40,resident_remaining=1536-len(resident),worker_start=worklab['ShFullBox'],worker_bytes=len(code),worker_granted_span=256,duplicate_native_attributes_exact=True,table_fixed_bank=127,table_fixed_address=0xef36,required_rebindings={n:dict(old=oldlab[n],new=newlab[n])for n in ['ShColors','ShMenuResolve','ShShotBankGate']},required_shared_hook=dict(bank=205,pc=0xab09,old_target_bank=217,old_target=0xac1b,new_target_bank=193,new_target=newlab['ShBBoxIngress']),caveat='Assembly funding/source preimages only. Proposed foreign direct-native fallback requires full raw-owner CPU proof of Sunny bypass before acceptance. Proposed worker/compacted injury ABI and ISR cuts remain unverified.')
 (O/'design.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
