"""Bind reviewed HUD readers, cancellation owners and caller liveness."""
from pathlib import Path
import argparse,hashlib,json,re
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);uses=[]
 for f in sorted((a.source/'src').rglob('*')):
  if f.suffix not in ['.s','.inc']:continue
  lines=f.read_text(encoding='utf-8').splitlines()
  for i,line in enumerate(lines):
   if re.search(r'\b(?:InvHudActive|InvHudPhysical|X5HudChrUpper)\b|\$73ed',line,re.I):uses.append(dict(file=f.relative_to(a.source).as_posix(),line=i+1,text=line,context=lines[max(0,i-7):i+8]))
 read=lambda n:(a.source/'src'/n).read_text(encoding='utf-8')
 # Source-level gates. The compiled CPU suite separately exercises them.
 assert 'ldy InvHudActive\n    beq HudChrDone\n      lda InvHudPhysical'in read('mmc5_expanded.s')
 assert 'ldy InvHudActive\n    beq HudChrDone\n      lda InvHudPhysical'in read('mmc5.s')
 assert 'lda X5HudChrUpper\n  and #3'in read('mmc5_expanded.s')
 assert 'lda InvHudActive\n  beq HudFontDone\n  lda X5HudChrUpper\n  and #3'in read('remaining_audio.s')
 assert 'lda InvHudPhysical\n  sta $5128'in read('remaining_audio.s')
 helper=read('parodius_hud_queue.s');assert all(n in helper for n in ['sta InvHudPhysical','ora #$81','cmp NmiR1','cmp NmiR0','cmp #42','cmp #6','sta InvHudActive','inc ReloadCHRBank','cpx #0','cpx #32','and #$7c','cmp #32','jsr UpdateScreen','sta VRAM_Buffer1,x','clv'])
 assert '  jmp PnHudPreUpdateScreen'in read('samus_freeze_render.s')
 assert 'lda InvHudActive\n jne Return ; ctrl6'in helper
 assert 'lda VvVariant\n asl\n asl\n ora #$81\n sta X5HudChrUpper'in helper
 assert 'lda VRAM_Buffer1_Offset\n cmp #42\n bne FullGeneral'in helper
 assert 'jsr PnHudCancelLife'in read('vic_adapter.s')and 'jsr PnHudNewLife'in read('vic_adapter.s')and 'jsr PnHudInventoryInit'in read('samus_freeze_render.s')and 'jmp PnHudTextCancel'in read('screen_render.s')
 assert 'PnHudBufferClear'not in read('reset.s')and '  sta VRAM_Buffer1_Offset,x' in read('reset.s')
 assert 'lda SelectedCharacter\n cmp #18\n bne Samus\n.if ::ENABLE_MMC5_EXPANDED'in read('parodius_bells.s')
 selector_writers=[]
 for f in (a.source/'src').glob('*.s'):
  for i,line in enumerate(f.read_text(encoding='utf-8').splitlines()):
   if re.search(r'\b(?:sta|stx|sty)\s+SelectedCharacter\b',line):selector_writers.append((f.name,i+1,line))
 assert len(selector_writers)==2 and {v[0]for v in selector_writers}=={'characters.s','character_select.s'}
 # No external ordinary owner writes the pending high bit. Other leases are
 # literal upper0/1/2, or initialization zero; raw73ED exists only at alias.
 aliases=[u for u in uses if '$73ed'in u['text'].lower()];assert len(aliases)==1 and aliases[0]['file']=='src/mmc5_expanded.s'
 assert read('vic_render.s').count('jsr VvHud')==1 and 'lda VvVariant\n beq :+\n jmp PnDraw'in read('vic_render.s')
 assert not re.search(r'\b(?:jsr|jmp)\s+(?:VvHud|PnHud)\b',read('parodius_render.s').split('.proc PnDraw',1)[1].split('.endproc',1)[0])
 assert '  ldx #$00\n  ldy #$07\n  lda PseudoRandomBitReg'in read('game.s')
 assert 'farcall WriteGameText'in read('level_tiles.s')
 assert '  farcall Z2ResetAreaGate'in read('game.s')and 'farcall Z2MenuPrepare'in read('character_select.s')
 assert 'farcall ProtoMenuPrepare'in read('zelda2_link_menu.s')
 assert read('protoman_cold.s').count('farcall X5ClearChrModes')==1 and read('roll_render.s').count('farcall X5ClearChrModes')==1
 for f,call in [('characters.s','farcall KbGlobalInit'),('kirby_core.s','farcall Z2GlobalInit'),('zelda2_link_motion.s','farcall DwGlobalInit'),('darkwing_core.s','farcall ProtoGlobalInit'),('protoman_cold.s','farcall X5InventoryInit'),('x5_profiles.s','farcall InventoryInit'),('inventory.s','jmp SamusFreezeInit')]:assert call in read(f)
 notes=[
  {'owner':'hardware font consumers','proof':'Every source InvHudPhysical hardware load is behind InvHudActive!=0 (MMC3/ordinary MMC5/expanded legacy and wide publishers; RemainingAudioBegin). Expanded upper-latch loads mask AND3. Full pending Active0 prevents the admission offset0 being interpreted as a physical font. Attribute pending keeps the valid physical140/141/142 font and Active3/5/7; its encoded offset only occupies masked Upper bits2..6.'},
  {'owner':'foreground admission','proof':'GameLoop sets NmiDisableFF before UI and keeps it private through PauseSkip. UI dispatch requires selected18/OperMode1/engine8. PnHud requires initialized50 and ready1 before first full42B append, only at Buffer1 offset0. Full pending holds Upper80|(variant<<2)|1, Active0 and physical0. Cached attributes admit only offset0..31 and encode Upper80|(offset<<2)|1 with Active3/5/7. Catch-up leaves either marker unchanged; new dirty meter state survives.'},
  {'owner':'final extent guard','proof':'The sole regular-NMI gateway guard runs after all foreground producers, with resident ctrl0 selecting linked Buffer1. Full pending flushes its HUD only when final extent is exactly42 and the display/live-engine checks hold; otherwise six headers and actual initial pointer are validated before skipping its42B, retaining all later native commands and forcing dirty. Attribute pending verifies linked initial pointer, offset0..31, exact23C008 header, extent through its11B and finite extent<=83. It admits final packets<=31B; otherwise native UpdateScreen flushes any prefix to a temporary zero header, restores that exact header, then flushes the original suffix. Queuebytes, native remaining PPUDATA order, final terminator pointer and public AXYP/SP are CPU-compared. The split adds two scroll writes and one extra status boundary inside blanking. Success never clears live Dirty raised after UI. No claim that every possible packet<=31B or arbitrary overflow packet meets a hardware deadline.'},
  {'owner':'flush commit','proof':'Immediately after UpdateScreen, a full pending owner additionally requires selected18/OperMode1/engine8/display-on/initialized50/paletteReady1 and matching variant, Active0, physical0, exact42B extent, consumed terminator pointer equal linked Buffer1+extent (including page crossing), and all six command header bytes before tag/font/reload publication. This is actual NMI completion, not foreground queue success. Ctrl6 preserves either marker; attribute markers are otherwise retired by the pre-guard. The common first-full pre-guard path relies on the actual resident ctrl0 pointer selection; exceptional removal paths verify it directly.'},
  {'owner':'append producers','proof':'Native gameplay digits/palette, ColorRotation, block metatile writes, Parodius palette and bomb-palette producers append from the live buffer offset. BlockObjMT updater requires empty Buffer1. Area graphics targets Buffer2. All family-exclusive other HUD code is dispatched away for selected18. Static label payload comes from unchanged A77 tables; only attrs vary with VvMeter.'},
  {'owner':'arbitrary text overwrite','proof':'WriteGameText writes Buffer1 from index0, including active warp-zone level_tiles delivery. New entry hook cancels pending/sets dirty before exact original PHA/ASL/TAY and native overwrite. The23B verified bank3 tail preserves its native entry ABI and saved-A stack item.'},
  {'owner':'discard','proof':'Original InitBuffer is byte-exact, with no new buffer-clear hook. In the SAME regular NMI ctrl0 pre-guard retires/defer-marks cached attrs and postflush commits/cancels full labels; ctrl6 retains either marker and clears onlyBuffer2; every other ctrl cancels before InitBuffer clears Buffer1. No foreground runs inside that NMI; native IRQ does not own/admit HUD packets. Compiled chronology executes every ctrl plus original InitBuffer for both marker classes. SelectedCharacter has only two source store owners: CrossoverInit cancels through the initialization chain, and menu index selection is outside live gameplay after reset/menu entry. Arbitrary externally edited foreign-selector pending states are outside this source reachability argument.'},
  {'owner':'reset/newlife/menu','proof':'VvReset cleanup and VvDeathStart clear Active and pending high bits; VvEnsure NewLife does so before the5D00 clear. InventoryInit reaches SamusFreezeInit and cancels pending there. InitializeArea calls the complete reset chain before RAM/screen setup; native nametable initialization and SecondaryGameSetup buffer clearing occur before active game core after that reset. Menu QueueSelection calls Z2MenuPrepare/ProtoMenuPrepare, whose wide-mode clear cancels upper high bits; pending Active0 never leases font. New game additionally clears inventory/profiles; continue takes the area reset. No cold/save-state import claim.'},
  {'owner':'foreign upper clear','proof':'X5ClearChrModes is reached by menu preparation or Roll death rendering, not selected18 live Parodius update; X5ColdInit clears it at boot. Other families renew upper0/1/2. This is scoped source ownership, not a new overlay byte.'},
  {'owner':'caller liveness','proof':'VvHud tail-calls PnHud. VvUiDispatch tails VvHud and GameLoop continuation loads X0/Y7 then overwrites A and flags before use. Parodius variants JMP PnDraw before VvDraw native second-HUD call; PnDraw does not call HUD. Therefore one Parodius UI call per update; dirty C-bracket restored-bank PLA result A/NZ is dead. Clean path returns original A0/NZ1 and preserves XY. The two-call budget row is conservative catch-up/component cost, not actual Parodius draw frequency.'},
  {'owner':'scope exception','proof':'Vic Viper variant0 retains its original pre-admission Active behavior. The Parodius protocol does not claim that broader behavior fixed. Unchanged variant0 CPU controls are included; fresh native cold/reset controls remain necessary.'}
 ]
 notes.append({'owner':'shared timing and arithmetic helper','proof':'The no-pending pre-guard adds9 CPU cycles globally; the existing Selected18 comparison still bypasses the postcommit hook for other identities. Arithmetic chunk copy changes only internal A/V, proven dead in the exact SEC/TYA/ADC pointer continuation; ROOT full-return20,284 cases separately compare all returned AXYP/SP, RAM, ordered I/O and banks with no A/V exclusion. Both helpers remain NMI-owned C116 and use only AXY/NmiR0/1/normal stack. Fresh whole gateway controls and full linked regular-NMI prefix costs are bound separately; no general60Hz, DMC, physical IRQ or native deadline claim.'})
 files={u['file']for u in uses}|{'src/game.s','src/character_select.s','src/level_tiles.s','src/screen_render.s','src/vic_dispatch.s','src/parodius_bells.s','src/parodius_adapter.s','src/protoman_cold.s','src/roll_render.s','src/zelda2_link_menu.s','src/samus_freeze_render.s','src/reset.s','src/characters.s','src/kirby_core.s','src/zelda2_link_motion.s','src/darkwing_core.s','src/x5_profiles.s'}
 q=dict(source_review_passed=True,native_run=False,whole_program_formal_proof=False,tool_sha256=sha(Path(__file__)),bindings={n:sha(a.source/n)for n in sorted(files)},reviewed_owner_notes=notes,all_symbolic_lease_uses=uses,SelectedCharacter_store_owners=selector_writers,limits='Source ownership argument bound to exact private files, supplemented by linked CPU chronology. No exhaustive hardware/PPU timing or native menu/death/warp replay claim. Native first-HUD delay, valid initial displayed glyphs, queue2 deferral and full shared NMI deadlines remain qualification gates.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(source_review_passed=True,uses=len(uses),files=len(files),proof_sha256=sha(a.output/'proof.json'))))
if __name__=='__main__':main()
