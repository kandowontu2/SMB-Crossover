"""Private v6: native backdrop + in-place status name, frozen v5 preserved."""
import json,re
from pathlib import Path
import check_bubble_bobble_native_proxy_1102_v5 as Q
P=Q.P;R=Q.R;O=Q.O;address=Q.address
BASE=R/'build/bub-menu-candidate-1102-v2/combined2.nes';PIN='00971c9fa4906440e1f52d37ca76b7adde287e902a31e72982dee171b35bfa60'


def main():
 raw=BASE.read_bytes();assert P.sha(raw)==PIN;b=P.scoped_load(P.ROM)
 f=json.loads((O/'native-proxy-qualified-1102-v5.json').read_text())
 def frozen(name):
  rel='build/bubble-bobble-source-1101-v1/'+name;assert P.sha((R/rel).read_bytes())==f['files'][rel]['SHA256'];return(R/rel).read_text()
 old=json.loads(frozen('native-proxy-layout.json'));source=frozen('native-proxy-leaves.s');helpers=frozen('native-proxy-helpers.s');cfg=frozen('native-proxy-leaves.cfg').replace('native-proxy-','native-visible-')
 # All public vectors and host calls now use visible FullBox; the old private
 # 9px rectangle copier has no remaining direct/indexed/indirect entry.
 retired=old['labels']['BbNativeContactBox'];end=old['labels']['BbNativeContacts'];assert end-retired==16
 assert not any(v['target']==retired for v in old['vectors'].values())
 assert not re.search(r'(?m)^\s*(?:jsr|jmp|j\w+|b\w+) BbNativeContactBox\b',source)
 image=(O/'native-proxy.bin').read_bytes();imports=json.loads((O/'component-layout.json').read_text())['imports'];assert all(int.from_bytes(image[x['vector']-0xa000+1:x['vector']-0xa000+3],'little')!=retired for x in imports)
 # Original source opcodes cannot hold a call into that private host hole.
 assert bytes([0x20,retired&255,retired>>8])not in image[0x100:0x153a]and bytes([0x4c,retired&255,retired>>8])not in image[0x100:0x153a]
 color_source=Q.Q.Q.location(b,'X5QueueAreaBackdrop');color_pc=address(b,'X5QueueAreaBackdrop');native=raw[color_source:color_source+64]
 assert native[:3]==bytes([0xae,address(b,'VRAM_Buffer1_Offset')&255,address(b,'VRAM_Buffer1_Offset')>>8]),'Native backdrop inputA is dead'
 # Build helper first: both native call shims occupy fixed owned source holes.
 helpers=f'BbNativeAreaBackdrop=${old["code_end"]:04x}\nBbNativeColorsAdmission=$a074\nBbNativeStatusBob=${retired:04x}\n'+helpers
 oldpart=' ldy #12\n ldx #10\n bne BbHelperQueue\n';assert helpers.count(oldpart)==1
 helpers=helpers.replace(oldpart,''' tsx
 lda $0103,x                  ; Actual WriteGameText message A, before pushes.
 bne BbHelperRegsRestore       ; Other native messages retain every byte.
 ldy #6
BbHelperStatusCopy:
 lda BbHelperPackets+12,y
 sta VRAM_Buffer1+11,y         ; Patch only the original seven-name field.
 dey
 bpl BbHelperStatusCopy
 jmp BbNativeStatusBob
''')
 helpers=helpers.replace(' ldy #32\n ldx #19',' ldy #19\n ldx #19')
 oldpart=' ldy #0\n ldx #6\n bne BbHelperQueue';assert helpers.count(oldpart)==1
 helpers=helpers.replace(oldpart,' jsr BbNativeColorsAdmission\n ldy #0\n ldx #6\n bne BbHelperQueue')
 oldpart='BbHelperQueueDone:\n pla\n sta R0\n pla\n tay';assert helpers.count(oldpart)==1
 helpers=helpers.replace(oldpart,'BbHelperQueueDone:\n pla\n sta R0\nBbHelperRegsRestore:\n pla\n tay')
 olddata=' .byte $20,$43,7,$0b,$1e,$0b,$24,$24,$24,$24\n .byte $20,$43,7,$0b,$18,$0b,$24,$24,$24,$24'
 assert helpers.count(olddata)==1;helpers=helpers.replace(olddata,' .byte $0b,$1e,$0b,$24,$24,$24,$24')
 helpers+='\n.export BbHelperRegsRestore,BbHelperStatusCopy\n'
 h=P.assemble('native-visible-helpers',helpers,'MEMORY{H:start=$d320,size=$e0,file=%O;}SEGMENTS{BB_HELPERS:load=H,type=ro;}');helper=(O/'native-visible-helpers.bin').read_bytes();assert len(helper)<=224
 # Replace the unused16-byte copier by13-byte Bob-middle tail, returning to
 # the same already-saved helper AXYP frame. No R0 frame exists on this path.
 begin=source.index('BbNativeContactBox:\n');finish=source.index('.segment "BB_HOST"',begin)
 source=source[:begin]+f'''BbNativeStatusBob:
 lda $c300
 beq :+
 lda #$18
 sta VRAM_Buffer1+12
:
 jmp ${h['BbHelperRegsRestore']:04x}
'''+source[finish:]
 # Remove only the now-retired export, not any public source/vector table.
 source=re.sub(r'(?m)^\.export ([^\n]+)$',lambda m:'.export '+','.join(n for n in m[1].split(',')if n!='BbNativeContactBox'),source)
 names=['VRAM_Buffer1_Offset','VRAM_Buffer1','FarcallJmpTarget_SMC','FarCallCommon']
 source=''.join(f'{n}=${address(b,n):04x}\n'for n in names if not re.search(r'(?m)^'+n+'=',source))+source
 bank=((color_source-16)//8192)|128
 source+=f'''
.export BbNativeAreaBackdrop,BbNativePaletteEnd,BbNativeStatusBob
.segment "BB_HOST"
BbNativeAreaBackdrop:
 lda #${color_pc&255:02x}
 sta FarcallJmpTarget_SMC+1
 lda #${color_pc>>8:02x}
 sta FarcallJmpTarget_SMC+2
 lda #${bank:02x}
 jmp FarCallCommon             ; InputA dead; native leaf does not touch R0..7.
BbNativePaletteEnd:
.segment "BB_VISIBLE_ADMISSION"
.export BbNativeColorsAdmission
BbNativeColorsAdmission:
 ldx VRAM_Buffer1_Offset
 cpx #41                       ; Complete native4B +own6B packet under old45B gate.
 bcs :+
 jmp BbNativeAreaBackdrop
:
 rts
'''
 cfg=cfg.replace('SEGMENTS{','MEMORY{V:start=$a074,size=$c,file="'+(O/'native-visible-admission.bin').as_posix()+'";}SEGMENTS{BB_VISIBLE_ADMISSION:load=V,type=ro;')
 lab=P.assemble('native-visible-leaves',source,cfg);body=(O/'native-visible-leaves.bin').read_bytes();assert lab['BbNativePaletteEnd']<=0xbfe0
 assert lab['BbNativeAreaBackdrop']==old['code_end']and lab['BbNativeStatusBob']==retired and lab['BbNativeColorsAdmission']==0xa074
 result=bytearray(image);result[0x1540:0x1540+len(body)]=body
 box=(O/'native-visible-box-hole.bin').read_bytes();result[0xb0:0xb0+len(box)]=box;admission=(O/'native-visible-admission.bin').read_bytes();assert len(admission)==11;result[0x74:0x74+len(admission)]=admission
 labels={**lab,**h,'NativeHead':old['labels']['NativeHead'],'NativeSide':old['labels']['NativeSide']}
 for row,item in old['vectors'].items():
  target=labels[item['name']];at=int(row)*3;result[at:at+3]=bytes([76,target&255,target>>8])
 assert result[0x100:0x153a]==image[0x100:0x153a]
 art=(O/'native-proxy-helper.chr').read_bytes()[:800]+helper+bytes(224-len(helper));cookie=bytes([0xa7,39,1])+bytes.fromhex(P.sha(result+art))[:13]
 (O/'native-visible.bin').write_bytes(result);(O/'native-visible-helper.chr').write_bytes(art);(O/'native-visible-BB-cookie.bin').write_bytes(cookie)
 owner=frozen('native-proxy-owner.s').replace('"native-proxy-BB-cookie.bin"','"native-visible-BB-cookie.bin"');own=P.assemble('native-visible-owner',owner,'MEMORY{P:start=$ae00,size=$1000,file=%O;}SEGMENTS{COMMON_OWNER_PROPOSAL:load=P,type=ro;}')
 oldowner=(O/'native-proxy-owner.bin').read_bytes();newowner=(O/'native-visible-owner.bin').read_bytes();co=oldowner.index(bytes.fromhex(old['BB_cookie']));assert newowner[:co]+newowner[co+16:]==oldowner[:co]+oldowner[co+16:]
 layout=dict(passed=True,ROM_written=False,base_ROM_SHA256=PIN,code_end=lab['BbNativePaletteEnd'],code_spare=0xbfe0-lab['BbNativePaletteEnd'],helper_bytes=len(helper),helper_spare=224-len(helper),labels=labels,vectors=old['vectors'],owner_labels=own,BB_cookie=cookie.hex(),common_cookie_ROM_file_offset=16+65*8192+0xe00+co,reclaimed_private_copier=dict(half_open=[retired,end],old_bytes=16,new_Bob_tail_bytes=13,no_current_public_or_import_vector=True,no_named_direct_call_or_original_source_JSR_JMP=True),original_A100_B53A_unchanged=True,native_backdrop=dict(physical_PRG=(color_source-16)//8192,PC=color_pc,input_A_dead=True,R0_R7_untouched=True,entry_bytes=native[:3].hex(),admission_offset_max=40,busy41_44_retains_only_old_opaqueRGB_behavior=True,busy45plus_no_append=True),scope='Compiled source-bound private successor only. Original native status header is patched in place only forA0; Menu18 remainsencoded16character queue. Exact public CPU/header/menu/backdrop/ISR proofs required before composition.')
 (O/'native-visible-layout.json').write_text(json.dumps(layout,indent=2)+'\n');print(json.dumps({k:layout[k]for k in['passed','ROM_written','code_spare','helper_bytes','helper_spare']}))


if __name__=='__main__':main()
