# Karnov original equipment WIP

The exact1c073196 candidate replaces the single Downloads nightly without a
backup. Reopen the ROM and start fresh. Rygar -> Select -> Karnov -> A/Start.

Select cycles earned Boots, Boomerang, Wings, then NONE. Down+freshB activates
the chosen equipment. A jumps; B fires. HoldUp/Down to move during flight.
Original source stock consumption,88px boots jump, boomerang return/base-shot
restoration and original timer leaves are retained. New life selects NONE;
same-life area transfers preserve selected equipment and stock.

Three native Mesen checks use six declared source inventory bytes to create
earned stock, then use real controller controls. They verify activation,
stock, displayed original body, boots jump, boomerang return and Up/Down flight.
They do not claim controller-earned equipment. CPU Main tests additionally
verify expiry and real IRQ/NMI resumption. The original curled flight pose
includes the wings in its body raster; no new wing artwork was invented.

Separate controller-only runs still defeat a Goomba with score/hitSFX, collect
an emerged mushroom and fire double shots, break a brick with debris, and
shoot a mushroom question block. All90 menu identities/124 transitions pass
the same sampled heading/gray-portrait/PPUMASK checks on this exact ROM.

The actual12-row loader verifies code before both complete16-byte cache
headers. Faults in either combat or equipment page deny both cache headers.
Native Main/cold-loader stack checks preserve at least12bytes above SMC.

Equipment HUD/icons, six other equipment types, original audio and full-stage
qualification remain unfinished. This is86 selectable WIP identities, not
a finished Karnov implementation or complete roster. Source/native packets
contain no ROM, full debugger/object tree, videos or per-frame captures.
