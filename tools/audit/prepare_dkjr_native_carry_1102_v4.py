"""Private actual-native platform bbox production and typed carry-event leaves."""
import json,re,subprocess,zipfile
import prepare_dkjr_native_world_1102_v3 as P
R=P.R;O=P.O


def main():
 checkpoint=R/'docs/qa/checkpoints/2026-11-02/dkjr-native-world-v3';manifest=json.loads((checkpoint/'manifest.json').read_text());assert P.P.sha((checkpoint/'inputs.zip').read_bytes())==manifest['archive_SHA256']
 with zipfile.ZipFile(checkpoint/'inputs.zip')as archive:
  rel='build/dkjr-native-source-1102-v2/native-world-v3.s';blob=archive.read(rel);assert P.P.sha(blob)==manifest['files'][rel]['SHA256'];source=blob.decode().replace('\r\n','\n')
  prior=json.loads(archive.read('build/dkjr-native-source-1102-v2/native-world-v3-layout.json'))
  prior_code=archive.read('build/dkjr-native-source-1102-v2/native-world-v3.bin')
 b=P.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');raw=P.CURRENT.read_bytes();assert P.P.sha(raw)==P.PIN
 bindings={n:P.address(b,n)for n in['R0','ObjectOffset','FarCallCommon','SafecallA_SMC','FarcallJmpTarget_SMC','GameEngineSubroutine','TimerControl']}
 source=source.replace('DkjrComponentEnd:\n.export DkjrComponentEnd','')
 old='DImport_cf62: jmp DImport_cf62 ; closed local trap until typed host binding'
 assert source.count(old)==1;source=source.replace(old,'DImport_cf62: jmp DkjrNativeLifeTerminal ; original terminal becomes native lifecycle event')
 for name,pc in bindings.items():source='%s=$%04x\n'%(name,pc)+source
 source+='''
.export DkjrNativeRefreshPlatforms,DkjrNativeCarryEvent,DkjrNativeLifeTerminal,DkjrNativeLifeReset
CarryTop=$c8f5
CarryReason=$c8f6
CarryPhase=$c8f7
LifeCommitted=$c8f8
; Current native primitives recompute all platform boxes before the source
; actor probes them. This does NOT move actors or run their AI. Preserve
; caller AXYP/R0..7/ObjectOffset, all33live SMC bytes and PRG maps. Native
; relative/offscreen scratch and platform bbox publication are declared writes.
DkjrNativeRefreshPlatforms:
 php
 pha
 txa
 pha
 tya
 pha
 ldx #5
FindPlatform:
 lda Enemy_Flag,x
 beq FindNext
 bmi FindNext
 lda Enemy_ID,x
 cmp #$24
 bcc FindNext
 cmp #$2d
 bcc HasPlatform
FindNext:
 dex
 bpl FindPlatform
 jmp RefreshReturn
HasPlatform:
 ldx #7
PushScratch:
 lda R0,x
 pha
 dex
 bpl PushScratch
 lda ObjectOffset
 pha
 ldx #32
PushSMC:
 lda $015a,x
 pha
 dex
 bpl PushSMC
 ldx #5
RefreshSlot:
 lda Enemy_Flag,x
 beq NextRefresh
 bmi NextRefresh
 lda Enemy_ID,x
 cmp #$24
 bcc NextRefresh
 cmp #$2d
 bcs NextRefresh
 stx ObjectOffset
 jsr NativeOffscreen
 jsr NativeRelative
 ldx ObjectOffset
 lda Enemy_ID,x
 cmp #$2b
 bcs RefreshSmall
 jsr NativeLargeBBox
 jmp ReloadRefresh
RefreshSmall:
 jsr NativeSmallBBox
ReloadRefresh:
 ldx ObjectOffset
NextRefresh:
 dex
 bpl RefreshSlot
 ldx #0
PopSMC:
 pla
 sta $015a,x
 inx
 cpx #33
 bne PopSMC
 pla
 sta ObjectOffset
 ldx #0
PopScratch:
 pla
 sta R0,x
 inx
 cpx #8
 bne PopScratch
RefreshReturn:
 pla
 tay
 pla
 tax
 pla
 plp
 rts
; This is an UNWIRED typed event endpoint, NOT support/speed inference.
; Future owner routing must invoke it ONLY after the actual native platform
; position service has placed the player; incomingX is its real platformslot.
; This is an actual-event contract: native collision already admitted the
; positioning; a future Main must publish the true sourceDY for that caller.
; Preserve the original pre-snap fall-distance test at the exact injury edge.
DkjrNativeCarryEvent:
 cpx #6
 bcs CarryReject
 lda GameEngineSubroutine
 cmp #8
 bne CarryReject
 lda TimerControl
 bne CarryReject
 lda $c06b
 cmp #1
 beq CarryPhaseValid
 cmp #3
 beq CarryPhaseValid
 cmp #4
 jne CarryReject
CarryPhaseValid:
 sta CarryPhase
 lda Enemy_Flag,x
 beq CarryReject
 lda Enemy_ID,x
 cmp #$24
 bcc CarryReject
 cmp #$2d
 bcs CarryReject
 lda Enemy_Y_HighPos,x
 cmp #1
 bne CarryReject
 lda Player_Y_HighPos
 cmp #1
 bne CarryReject
 lda Player_Y_Position
 clc
 adc #32
 bcs CarryReject
 sta CarryTop
 cmp Enemy_Y_Position,x
 beq CarryAccepted
 lda Enemy_ID,x
 cmp #$2b
 bcc CarryReject
 lda AreaPointer
 cmp #$62
 bne CarryVanillaSecond
 lda WorldNumber
 cmp #1
 beq CarrySourceSecond
 cmp #4
 bne CarryVanillaSecond
CarrySourceSecond:
 lda Enemy_State,x
 jmp CarryCompare
CarryVanillaSecond:
 lda Enemy_Y_Position,x
 clc
 adc #128
CarryCompare:
 cmp CarryTop
 bne CarryReject
CarryAccepted:
 lda CarryPhase
 cmp #1
 beq CarryGround
 ; Validate screen representation before publishing any source context.
 ; ImportAnchor must not force a pre-snap injury comparison to use snappedY.
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta WAnchorX
 lda Player_PageLoc
 sbc ScreenLeft_PageLoc
 bne CarryReject
 lda WAnchorX
 cmp #8
 bcc CarryReject
 cmp #232
 bcs CarryReject
 lda CarryTop
 sta $c043
 jsr DkjrFallDistance
 sta CarryReason
 beq CarrySafeLanding
 ; Original DA22 injury branch does not snap or redraw the source body.
 lda #5
 sta $c06b
 sec
 rts
CarrySafeLanding:
 jsr DkjrNativeImportAnchor
 bcc CarryReject
 jsr DkjrLand
 lda #1
 sta $c06b
 sec
 rts
CarryGround:
 jmp DkjrNativeImportAnchor
CarryReject:
 clc
 rts
; Original CF37/DAF7 choose the exact terminal time. Reuse native
; MegaManDeathUpdate::EndDeath verbatim to enter native PlayerLoseLife;
; never decrement lives or fabricate player/respawn/checkpoint bookkeeping.
DkjrNativeLifeReset:
 lda #0
 sta LifeCommitted
 rts
DkjrNativeLifeTerminal:
 lda $c06b
 cmp #5
 bne LifeReject
 lda LifeCommitted
 bne LifeReject
 lda GameEngineSubroutine
 cmp #8
 beq CommitLife
 cmp #$0b
 bne LifeReject
CommitLife:
 lda #1
 sta LifeCommitted
DkjrNativeEndDeath:
 lda #6
 sta GameEngineSubroutine
 lda #0
 sta TimerControl
DkjrNativeEndDeathDone:
 sec
 rts
LifeReject:
 clc
 rts
'''
 calls=[]
 for label,name in[('NativeOffscreen','GetEnemyOffscreenBits'),('NativeRelative','RelativeEnemyPosition'),('NativeLargeBBox','HpNativePlatformBBoxGate'),('NativeSmallBBox','SmallPlatformBoundBox')]:
  pc=P.address(b,name);pos=P.location(b,name);bank=((pos-16)//8192)|128
  source+='\n%s:\n lda #$%02x\n sta FarcallJmpTarget_SMC+1\n lda #$%02x\n sta FarcallJmpTarget_SMC+2\n lda #$%02x\n jmp FarCallCommon\n'%(label,pc&255,pc>>8,bank)
  calls.append(dict(private_thunk=label,native_target=name,CPU_address=pc,physical_bank=bank&127,file_offset=pos,first16_SHA256=P.P.sha(raw[pos:pos+16]),unchanged_from_full_metadata_base=raw[pos:pos+16]==b['raw'][pos:pos+16]))
  assert calls[-1]['unchanged_from_full_metadata_base']
 source+='\nDkjrNativeCarryEnd:\nDkjrComponentEnd:\n.export DkjrNativeCarryEnd,DkjrComponentEnd\n'
 source=re.sub(r'\n (b(?:cc|cs|eq|ne|mi|pl)) CarryReject',lambda m:'\n j'+m[1][1:]+' CarryReject',source)
 (O/'native-carry-v4.s').write_text(source);(O/'native-carry-v4.cfg').write_text('MEMORY{C:start=$a000,size=$2000,file=%O;}SEGMENTS{DKJR:load=C,type=rw;}')
 cc=R/'tools/Windows/cc65/bin'
 for cmd in[[cc/'ca65.exe',O/'native-carry-v4.s','-g','-o',O/'native-carry-v4.o'],[cc/'ld65.exe','-C',O/'native-carry-v4.cfg',O/'native-carry-v4.o','-o',O/'native-carry-v4.bin','-Ln',O/'native-carry-v4.lbl']]:
  p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
 blob=(O/'native-carry-v4.bin').read_bytes();labels={n:int(a,16)for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'native-carry-v4.lbl').read_text(),re.M)};assert len(blob)<=8160
 changed=[i for i in range(len(prior_code))if blob[i]!=prior_code[i]];cf62=labels['DImport_cf62']-0xa000;assert changed==[cf62+1,cf62+2],changed
 native_end=P.location(b,'MegaManDeathUpdate::EndDeath');end_length=P.address(b,'MegaManDeathUpdate::Done')-P.address(b,'MegaManDeathUpdate::EndDeath');endbytes=raw[native_end:native_end+end_length];local=labels['DkjrNativeEndDeath']-0xa000;local_end=labels['DkjrNativeEndDeathDone']-0xa000;assert blob[local:local_end]==endbytes
 q=dict(passed=True,ROM_written=False,native_grant=False,native_owner_admitted=False,base_ROM_SHA256=P.PIN,inherited_archive_SHA256=manifest['archive_SHA256'],component_bytes=len(blob),additional_bytes=len(blob)-prior['component_bytes'],header_reserved_spare=8160-len(blob),private_state_half_open=[0xc000,0xc900],code_SHA256=P.P.sha(blob),labels=labels,native_constants=bindings,native_calls=calls,source_v3_prefix_changes=[dict(offset=cf62,old=prior_code[cf62:cf62+3].hex(),new=blob[cf62:cf62+3].hex(),role='Original CF62 import binds native exactly-once death terminal')],native_end_death=dict(file_offset=native_end,bytes=10,SHA256=P.P.sha(endbytes),source='src/megaman_death.s::MegaManDeathUpdate::EndDeath',verbatim=True),remaining_imports=10,carry_event_scope='Unwired explicit actual-positioning event: ground carry and jump/fall landing, including original pre-snap fall-distance injury. Requires future sourceDY publication/current native collision caller admission. No actual owner dispatch or public row is functional.',unimplemented=['Native carry event caller/routing/admission and sourceDY publication','Ten phase/fruit/UI imports; actual native death-row/Main linkage','Full Main/body/head/side/native render/owner/cold/menu/ISR qualification'])
 q['native_end_death']['bytes']=end_length
 (O/'native-carry-v4-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in['passed','ROM_written','native_owner_admitted','component_bytes','additional_bytes','header_reserved_spare','code_SHA256']}))


if __name__=='__main__':main()
