# Current Downloads roster transition regression

Actual Downloads1327 passes the full D-pad/Select transition observer.
Root33825 is terminal/exit0, native receipt
`5c2378cc9b1c461ad5da866e0c14a53d570b1dc98d870e6746682af32dcd4ca4`.
ROM SHA256:
`13272464e34237f09c7fce87ac276b20da299f8028640cc51155759d6c642a4d`.

The current compiled source census resolves101 distinct named entries, all
confirmable with both Start and A. It supplies the actual32-slot Select cycles
for a snake-shaped native menu route. Mesen then makes136 transitions over
3137 physical frames, cycling every slot and returning through the D-pad to
Mario. Mini Mario is observed at Select step8. Every transition settles to
its expected slot/raw owner.

The unchanged pixel observer samples the actual screen buffer at endFrame.
There are zero changed heading hashes, zero visible-scanline writes to
PPUMASK or the observed background-CHR registers, and zero additional
transient background/grid/preview/name hashes outside each transition's
old/new pair. No screenshot or video is created. This checks this specific
flicker pattern; it does not certify each portrait's art, facing, silhouette,
colors, full-frame pixels or live in-game sprites. Alternate-specific names
and variant state come from the separate compiled census; the native route
asserts slot/raw identity, not every alternate-specific state byte.

The legacy Lua file remains byte-exact, SHA256
`2c3c9c267a0e94950183031d8e85bd54dcdb55d0f71d61cb732e56c14904190a`.
It labels a diagnostic read at007F as NmiDisable. Current symbol binding
correctly identifies NmiDisable at0139, so the generated controller changes
only that diagnostic read, retaining all pixel and PPU assertions. Its LF
Lua SHA256 is
`f46884e0743772b4077a9de52744cbb8068ef56608e9432a18e50b3914fb9ccc`.

Earlier69009 stopped before the source census or Mesen at the address guard
that exposed this diagnostic mismatch. It is an observer setup negative,
not a gameplay failure. No ROM bytes or UI implementation changed between
that guard failure and the passing33825 regression.

Root runner: `tools/audit/run_roster_pixels_1327_root_1116.py`.
Bounded existing two-file root `build/smb2-flag-native-1113`, max2/600 seconds.
The only mutation is replacement of its existing controller.lua; candidate
and actual Downloads bytes remain exact1327. New files/images/videos0;
pre/post automatic-patch guards clear. Other Mesen processes remain untouched.
Root's single native queue is free after the terminal pass.
