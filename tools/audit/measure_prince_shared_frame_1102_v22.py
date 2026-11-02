"""Measure one source-equivalent Sh/Ex/BB transport frame; no ROM/grant."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/reference'),str(R/'tools/audit')]
import compile_prince_host_lifecycle_1102_v12 as L
from check_tmnt_render_oa import address
from link_pit_rygar_sophia_audit_cpu import scoped_load
from private_build_outputs_v1 import validate
O=L.O;B=R/'build/bubble-bobble-source-1101-v1'


def main():
 b=scoped_load(L.BASE);old=(O/'dispatch-factor-v21.s').read_text();head=old[:old.index('.segment "FACTOR"')]
 head+='CoCheckCode=$aef3\nExForeignUi=$b031\n'
 # The two original frames have identical saved-AXYP/Cmapping/5SMC layout.
 # Selector family is bound to the actual fixed AA88/B08C public veneers.
 prefix=old[old.index('ShDispatch:\n'):old.index(' lda SelectedCharacter\n')]
 call=old[old.index(' lda #2\n sta CurrentBankC\n'):old.index('ShDispatchEnd:\n')]
 text=head+'''
.segment "SH_FRAME"
.export ShDispatch,ShDispatchEnd,PrSharedCall,ShDispatchNo
'''+prefix+''' jmp PrFamily
PrSharedCall:
 sta FarcallJmpTarget_SMC+2
'''+call+'''ShDispatchEnd:
.segment "EX_SELECT"
.export ExDispatch,PrSelectEnd,ExForeignLo,ExDispatchNo
ExDispatch:
 jmp ShDispatch
PrFamily:
 lda FarcallJmpTarget_SMC+2
 cmp #>ShServiceVeneers
 beq PrSh
 lda SelectedCharacter
 and #$fd
 cmp #37
 beq PrOdd
 lda FarcallJmpTarget_SMC+1
 jmp ExForeignUi
PrOdd:
 jsr CoCheckCode
 jcc ShDispatchNo
 lda FarcallJmpTarget_SMC+2
 cmp #$b0
 jne ShDispatchNo
 lda FarcallJmpTarget_SMC+1
 sec
 sbc #$8c
 jcc ShDispatchNo
 cmp #114
 jcs ShDispatchNo
 sta FarcallJmpTarget_SMC+1
 lda SelectedCharacter
 cmp #39
 beq PrOddBB
 lda #$a5
 jmp PrSharedCall
PrOddBB:
 lda #$a0
 jmp PrSharedCall
PrSh:
 lda SelectedCharacter
 cmp #36
 jne ShDispatchNo
 lda FarcallJmpTarget_SMC+1
 sec
 sbc #<ShServiceVeneers
 sta FarcallJmpTarget_SMC+1
 lda FarcallJmpTarget_SMC+2
 sbc #>ShServiceVeneers
 jne ShDispatchNo
 lda FarcallJmpTarget_SMC+1
 cmp #111
 jcs ShDispatchNo
 jsr ShCheckCode
 jcc ShDispatchNo
 lda #$a0
 jmp PrSharedCall
ExDispatchNo=ShDispatchNo
ExForeignLo:
'''+'.byte '+','.join(f'${n:02x}'for n in (B/'native-proxy-routes.bin').read_bytes()[176:178])+'''
PrSelectEnd:
'''
 cfg=O/'shared-frame-v22.cfg';cfg.write_text('MEMORY{S:start=$aaf7,size=$dd,file=%O;E:start=$a740,size=$b2,file="'+(O/'shared-selector-v22.bin').as_posix()+'";}SEGMENTS{SH_FRAME:load=S,type=ro;EX_SELECT:load=E,type=ro;}')
 asm=O/'shared-frame-v22.s';asm.write_text(text);cc=R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe','-g',asm,'-o',O/'shared-frame-v22.o'],[cc/'ld65.exe','-C',cfg,O/'shared-frame-v22.o','-o',O/'shared-frame-v22.bin','-Ln',O/'shared-frame-v22.lbl']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
 labs=L.P.T.labels(O/'shared-frame-v22.lbl');frame=(O/'shared-frame-v22.bin').read_bytes();selector=(O/'shared-selector-v22.bin').read_bytes();foreign=bytearray((B/'native-proxy-route-foreign.bin').read_bytes())
 assert foreign[9]==0xbd and foreign[44]==0x4c
 foreign[10:12]=(labs['ExForeignLo']-4).to_bytes(2,'little');foreign[45:47]=labs['ShDispatchNo'].to_bytes(2,'little');(O/'shared-foreign-v22.bin').write_bytes(foreign)
 assert len((B/'native-proxy-routes.bin').read_bytes())==184
 # The six-byte typed-input shim A7F2..A7F8 remains at its original address.
 q=dict(measured=True,qualified=False,ROM_written=False,shared_sources_written=False,symbolic_composition_only=True,Sh_original_bytes=221,Sh_new_bytes=len(frame),Sh_free_half_open=[0xaaf7+len(frame),0xabd4],Ex_original_body_bytes=178,Ex_new_bytes=len(selector),Ex_free_half_open=[0xa740+len(selector),0xa7f2],total_source_funding=221+178-len(frame)-len(selector),fixed_Shinobi_37_veneers=True,fixed_Ex_37_veneers=True,fixed_Bub_typed_input_A7F2=True,all_other_resident_addresses_unchanged=True,foreign_UI_changed_operand_bytes_only=[0xb03b,0xb03c,0xb05e,0xb05f],manager_required_bytes=120,remaining_after_manager=221+178-len(frame)-len(selector)-120,Prince_public_routing_not_yet_counted=True,grant=False,scope='Private source-equivalent transport factoring measurement. Family classification is closed only for fixed AA88+3row/B08C+3row and genuine typedB029 ingresses; no arbitrary forged indirect entry contract. No new owner support, ROM, menu or native gameplay.',bindings={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()for p in [Path(__file__),O/'dispatch-factor-v21.s',O/'shared-frame-v22.bin',O/'shared-selector-v22.bin',O/'shared-foreign-v22.bin',B/'native-proxy-routes.bin',B/'native-visible-owner.bin',L.BASE]})
 (O/'shared-frame-measurement-v22.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
