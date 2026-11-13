# Prince Star and 1UP semantics on the current nightly

`check_prince_star_oneup_current_1113.py` passes on actual Downloadsaa501
using its genuine menu/cold state. Source health, weapon and player position
are not seeded. Each case explicitly places a mature native actor, then uses
the real preparation, player box, powerup handler and24Main/NMI updates.
These are directed CPU fixtures, not natural level pickups or Mesen proof.

|Item|Immediate native result|After24Main/NMI updates|
|---|---|---|
|Star|Actor erased, timer35, AreaMusicQueue64|Timer33, health5, lives2|
|1UP|Actor erased, FloateyNum_Control11|Lives2→3, health5|

Both retain starting sword inventory0, status0 and playerX40/Y176. The
Star does not grant a sword or incorrectly change the health progression.
The 1UP award completes through the native floating-number update.

Test source SHA256:
`2e9367c41c45ec7fd95dbd2b32c4fcb01c92d7ea45d6b3fbf90fc28397ccbada`.

The separate natural mushroom/flower sword acquisition is qualified in
`prince-natural-sword-1113.md`; full1-1 remains separately qualified. Natural
Star/1UP access, physical animation/audio review and difficulty comparisons
are not proven by these two fixtures. No ROM bytes, helpers, captures or
temporary files were added.
