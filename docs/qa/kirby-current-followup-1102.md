# Kirby follow-up on the current nightly

Current ROM: `build/thomas-current-candidate-1102-v3/candidate.nes`, SHA-256
`d0b445a71d6c539804d7c559fafc2c328ebf97ab4e35e8f3273f94ff8a25d01d`.

Read-only comparison against the previously tested
`build/kirby-approach-owner-1101-v3/candidate.nes` confirms that the complete
`KbWeapons` (2,278 bytes), `KbBodyContact` (207 bytes), `KbMovement` (1,519 bytes)
and `KbInjuryStart` (110 bytes) components remain byte-identical at their
original file offsets. The complete PRG bank 72 is also identical, covering
the inhale-friction helper whose exported alias has no size metadata.
PRG bank 74 has other changes; it is not claimed wholly identical.

The earlier immediate-suction and grounded copied-shell repairs have therefore
not been removed from these components. This is preservation evidence, not a
fresh gameplay pass. The older emulator packet assumes 32 roster slots; the
current roster has 33. Refresh its navigation and current hook bindings before
running fresh close-enemy inhale and both shell-power tests. Full 1-1 and all
powerups remain separate outstanding requirements.
