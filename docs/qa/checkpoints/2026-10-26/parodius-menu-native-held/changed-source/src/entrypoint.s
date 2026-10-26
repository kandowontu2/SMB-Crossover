
; Single entrypoint that includes files to make building this easier


.macpack longbranch
.macpack generic

.linecont on
.feature force_range


.include "options.s"


.include "inc/nes2header.inc"

;--------------------------------
; NES2.0 header

.if MAPPER_MMC5
nes2mapper 5 ; mmc5
.elseif MAPPER_MMC3
nes2mapper 4 ; mmc3
.endif
.if ::MAPPER_MMC5 .and ::ENABLE_MMC5_EXPANDED
 .assert ::MAPPER_MMC5 .and (.not ::MAPPER_MMC3), error, "Expanded cartridge is MMC5-only"
 .assert ::ENABLE_MMC5_EXPANDED, error, "Separate expanded build flag required"
nes2prg $100000
nes2chr $100000
.else
nes2prg $80000
nes2chr $40000
.endif
.if ::ENABLE_CROSSOVER
nes2wram $2000
.else
nes2bram $2000
.endif
nes2mirror 'V'
nes2tv 'N'
nes2end



_COMMON_DEFINE_SEGMENTS = 1
.include "inc/common.inc"

.include "inc/charmap.inc"
.include "inc/constants.inc"
.if ::ENABLE_MMC5_EXPANDED
ProtoVariant=$73dd
ProtoAudioState=$73de
.export ProtoVariant,ProtoAudioState
DarkwingVariant=$73df
DwHealth=$73ef
DwGas=$73f0
DwAdaptor=$73f1
DwMode=$73f2
DwAnim=$73f3
DwPhase=$73f4
DwAnimTick=$73f5
DwPrevious=$73f6
DwHang=$73f7
.export DarkwingVariant,DwHealth,DwGas,DwAdaptor,DwMode,DwAnim,DwPhase,DwAnimTick,DwPrevious,DwHang

.endif
.include "memory.s"
.if ::ENABLE_MMC5_EXPANDED
.include "kirby_state.inc"
.include "cv3_state.inc"
.include "little_mac_state.inc"
.include "tmnt_state.inc"
.endif

.if MAPPER_MMC5
.include "mmc5.s"
.endif
.if MAPPER_MMC3
.include "mmc3.s"
.endif

.include "metasprite_engine.s"
.include "metasprite.s"
.if ::ENABLE_CROSSOVER
.include "guest_publish_chr.inc"
.endif

.include "common.s"
.include "collision.s"
.include "level_tiles.s"
.include "reset.s"
.include "game.s"

.include "player.s"
.if ::ENABLE_CROSSOVER
.include "characters.s"
.include "megaman_weapons.s"
.include "megaman_physics.s"
.include "megaman_environment.s"
.include "megaman_palette.s"
.include "megaman_death.s"
.include "megaman_audio.s"
.include "samus.s"
.include "samus_weapons.s"
.include "samus_audio.s"
.include "guest_powerups.s"
.include "roster.s"
.include "roster_weapons.s"
.include "roster_audio.s"
.include "guest_audio.s"
.include "water.s"
.include "character_select.s"
.include "expanded.s"
.include "pit_collision.s"
.include "guest_body_contact.s"
.include "guest_injury.s"
.include "megaman_injury.s"
.include "lsr_injury.s"
.include "ordinary_body_layout.s"
.include "luigi_native.s"
.include "expanded_weapons.s"
.include "source_motion.s"
.include "ryu_wall.s"
.include "source_weapons.s"
.include "link_fragments.s"
.include "ryu_projectile_motion.s"
.include "expanded_audio.s"
.include "bass_audio.s"
.include "inventory.s"
.include "special_weapons.s"
.include "inventory_drops.s"
.include "world_firebars.s"
.include "lance_metasprites.inc"
.if MAPPER_MMC5
.include "chr_map_mmc5.inc"
.else
.include "chr_map_mmc3.inc"
.endif
.endif
.include "object.s"
.if ::ENABLE_CROSSOVER
.include "enemy_offscreen_fast.s"
.endif
.include "screen_render.s"
.include "sprite_render.s"


.segment "AUDIO"

.include "music_drivers/audio.s"


; .segment "FIXED"

; FarcallTableLo:
; .repeat ::_FARCALL_COUNT, I
;   .byte .ident(.sprintf("_LEFT_%d_LO", I))
; .endrepeat
; FarcallTableHi:
; .repeat ::_FARCALL_COUNT, I
;   .byte .ident(.sprintf("METASPRITE_LEFT_%d_LO", I))
; .endrepeat
; FarcallTableBank:
; .repeat ::_FARCALL_COUNT, I
;   .byte .ident(.sprintf("METASPRITE_LEFT_%d_LO", I))
; .endrepeat

.if ::ENABLE_CROSSOVER
.include "player_outlines.s"
.include "scrooge.s"
.include "remaining_weapons.s"
.include "lsr_effects.s"
.include "remaining_audio.s"
.include "samus_collision_ram.s"
.endif
.segment "CHR"
CrossoverChrStart:
.if ::ENABLE_CROSSOVER
.if ::MAPPER_MMC5
.if ::ENABLE_MMC5_EXPANDED
.incbin "chr/characters/packed-mmc5-expanded.chr"
.else
.incbin "chr/characters/packed-mmc5.chr"
.endif
.else
.incbin "chr/characters/packed-mmc3.chr"
.endif
.else

; Water = 0
; Ground = 1
; UnderGround = 2
; Castle = 3

.if MAPPER_MMC5
.incbin "chr/mmc5/bg_water.chr"
.incbin "chr/mmc5/bg_ground.chr"
.incbin "chr/mmc5/bg_underground.chr"
.incbin "chr/mmc5/bg_castle.chr"

.incbin "chr/mmc5/sprites_mario.chr"
.incbin "chr/mmc5/sprites_misc.chr"
.incbin "chr/mmc5/sprites_enemies.chr"

.else

.incbin "chr/mmc5/bg_water.chr"
.incbin "chr/mmc5/bg_ground.chr"
.incbin "chr/mmc5/bg_underground.chr"
.incbin "chr/mmc5/bg_castle.chr"

.incbin "chr/mmc3/sprites_mario.chr"
.incbin "chr/mmc3/sprites_misc.chr"

.incbin "chr/mmc3/sprites_water.chr"
.incbin "chr/mmc3/sprites_overworld.chr"
.incbin "chr/mmc3/sprites_underground.chr"
.incbin "chr/mmc3/sprites_castle.chr"

.endif
.endif ; ENABLE_CROSSOVER packed CHR / original baseline layout

.pushseg
.segment "TITLE"
TitleScreenData:
.incbin "chr/raw/titlescreen.bin"
.byte $00 ; add terminator byte in case the data editor didn't
.popseg

; Append after every existing METASPRITE contributor to preserve all old addresses.
.if ::ENABLE_CROSSOVER && ::MAPPER_MMC5
.include "native_goomba_draw.s"
.endif

; Append after all existing OBJECT contributions; old native labels stay put.
.if ::ENABLE_CROSSOVER && ::MAPPER_MMC5
.include "ground_goomba_terrain.s"
.endif

; Append after all SPECIAL_ROSTER contributors; preserve every old code PC.
.if ::ENABLE_CROSSOVER
.include "ryu_grapple_adjust.s"
.endif

; Append after all old SPECIAL_ROSTER bytes; old PCs stay unchanged.
.if ::ENABLE_CROSSOVER
.include "ryu_wall_coin_filter.s"
.endif

; New resident gap tails follow every pre-existing contributor.
.if ::ENABLE_CROSSOVER
.include "samus_crouch_collision.s"
.endif

; Append after every old SRAM/code contributor; baseline remains unchanged.
.if ::ENABLE_CROSSOVER
.include "ryu_platform.s"
.endif

; Source normal-air/platform admission appends after every old ROSTER PC.
.if ::ENABLE_CROSSOVER
.include "ryu_platform_source_overlap.s"
.endif

; Append the preference after all old SRAM and the tiny resident policy leaf.
.if ::ENABLE_CROSSOVER
.include "menu_behavior.s"
.endif

; Private source-head admission/foot tail relocation, after all old ROSTER PCs.
.if ::ENABLE_CROSSOVER
.include "guest_foot_side.s"
.include "ryu_source_head.s"
.include "easy_link_head_response.s"
.include "easy_link_firebar.s"
.endif

; Easy damage lifecycle appended after all pre-existing RAM/code.
.if ::ENABLE_CROSSOVER
.include "guest_legacy_injury.s"
.endif

.if ::ENABLE_CROSSOVER
.include "guest_source_stomp.s"
.endif

.if ::ENABLE_CROSSOVER
.include "easy_lsr.s"
.include "easy_link_order.s"
.include "easy_link_rect_animation.s"
.include "easy_link_animation_l.s"
.include "easy_link_death_l.s"
.endif

.if ::ENABLE_CROSSOVER
.include "mario_source.s"
.endif

.if ::ENABLE_CROSSOVER
.include "samus_legacy_bomb.s"
.endif

.if ::ENABLE_CROSSOVER
.include "ryu_source_body.s"
.include "bill_source_body.s"
.include "union_rare.s"
.endif

.if ::ENABLE_CROSSOVER
.include "ryu_corner_head.s"
.endif

.if ::ENABLE_CROSSOVER
.include "guest_victory_control.s"
.endif

.if ::ENABLE_CROSSOVER
.include "sophia_source_body.s"
.include "sophia_source_terrain.s"
.include "sophia_land_audio.s"
.endif

.if ::ENABLE_CROSSOVER
.include "samus_ice_hit.s"
.include "samus_freeze_render.s"
.endif

; Preserve all old contribution addresses; reuse the bank11 cold tail.
.if ::ENABLE_CROSSOVER
.include "samus_head_axis.s"
.endif

.if ::ENABLE_CROSSOVER
.include "score_popup.s"
.include "cheats.s"
.include "water_shield_enemies.s"
.include "hud_tail.s"
.include "world_sprite_palette.s"
.endif

.if ::ENABLE_CROSSOVER
.include "megaman_super_arm.s"
.include "megaman_rush.s"
.include "megaman_rush_land.s"
.endif

.if ::ENABLE_CROSSOVER
.include "ryu_side_overlap.s"
.include "level_variants.s"
.include "crossover_helpers.s"
.endif

.if ::MAPPER_MMC5 .and ::ENABLE_MMC5_EXPANDED
.include "mmc5_expanded.s"
.include "protoman.s"
.include "darkwing.s"
.include "x5_profiles.s"
.include "zelda2_link_state.inc"
.include "zelda2_native_aliases.inc"
.include "zelda2_link_rpg.s"
.include "zelda2_native_motion.inc"
.include "zelda2_link_art.inc"
.include "zelda2_link_render.s"
.include "zelda2_link_motion.s"
.include "zelda2_link_rewards.s"
.include "zelda2_link_ui.s"
.include "zelda2_pause_panel.s"
.include "zelda2_inventory_glue.s"
.include "zelda2_inventory_original.inc"
.include "zelda2_link_items.inc"
.include "zelda2_link_draw_world.s"
.include "zelda2_link_combat.s"
.include "zelda2_link_projectiles.s"
.include "zelda2_link_damage.s"
.include "zelda2_link_block.s"
.include "zelda2_link_drops.s"
.include "zelda2_link_menu.s"
.include "kirby.s"
.include "chip_dale_state.inc"
.include "chip_dale_native_motion.inc"
.include "chip_dale_art.inc"
.include "chip_dale_core.s"
.include "chip_dale_motion.s"
.include "chip_dale_render.s"
.include "chip_dale_boxes.s"
.include "chip_dale_health.s"
.include "chip_dale_dispatch.s"
.pushseg
.segment "CD_CHR"
.incbin "chr/characters/chip-dale.chr"
.popseg
.include "tmnt.s"
.include "mike_jones_state.inc"
.include "mike_jones.s"
.include "x5_palette.s"
.include "vic_viper.s"
.include "gradius_audio.s"
.include "mac_native_music.s"
.include "mike_native_music.s"
.include "cv3.s"
.include "little_mac.s"
.include "smb3_mario_state.inc"
.include "smb3_native_controller.inc"
.include "smb3_mario_art.inc"
.include "smb3_mario_core.s"
.include "smb3_mario_motion.s"
.include "smb3_mario_render.s"
.include "smb3_native_projectiles.inc"
.include "smb3_mario_world_art.inc"
.include "smb3_mario_pickups.s"
.include "smb3_mario_combat.s"
.include "smb3_mario_world.s"
.include "smb3_mario_dispatch.s"
.include "x5_bounce.s"
.include "x5_menu_ui.s"
.include "roll.s"
.include "zelda2_link_terrain.s"
.include "zelda2_link_platform.s"
.pushseg
.segment "M3_CHR"
.incbin "chr/characters/smb3-mario.chr"
.popseg
.pushseg
.segment "Z2_CHR"
.incbin "chr/characters/zelda2-link-body.chr"
.incbin "chr/characters/zelda2-link-items.chr"
.popseg
.include "mac_visible_side.s"
.include "protoman_hurt_end.s"
.include "inventory_legacy_leaf.s"
.include "hot_collision_gate.s"
.include "hot_render_gate.s"
.include "z2_platform_late_render.s"

.endif

; Append after every original INVENTORY contributor: no old label moves.
.if ::ENABLE_MMC5_EXPANDED
.pushseg
.segment "INVENTORY"
; Source2.02 destroys robot attacks only when the equipped weapon changes.
; Non-robot behavior is unchanged. No additional RAM or stack frame.
.proc InventorySelectionCommit
  cpx #CHARACTER_MEGAMAN
  beq Check
  cpx #CHARACTER_BASS
  bne Commit
Check:
  cmp InvSelected,x
  beq Done
Commit:
  sta InvSelected,x
  jmp InventoryClearActive
Done:
  rts
.endproc
.popseg
.endif

.if ::ENABLE_MMC5_EXPANDED
.include "ryu_primary_gate.s"
.include "sophia_missile_capacity.s"
.endif

.if ::ENABLE_MMC5_EXPANDED
.include "smb3_projectile_damage.s"
.endif

.if ::ENABLE_MMC5_EXPANDED
.include "mac_tmnt_lifecycle.s"
.endif

.if ::ENABLE_MMC5_EXPANDED
.include "cd_contact_y_window.s"
.endif

.if ::ENABLE_MMC5_EXPANDED
.include "cv3_source_audio.s"
.endif

.if ::ENABLE_MMC5_EXPANDED
.include "cv3_dmc_injury.s"
.endif

.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
.include "cv3_dmc_complete.s"
.endif

.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
.include "nmi_vram_fast.s"
.endif

.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
.include "parodius_hud_queue.s"
.endif
