# Link's first Mushroom block in Easy 1-1

The Mesen replays on Downloads `94fa7a02` use normal menu selection
and controller inputs. Each starts from power-on and saves no captures.

Link hit the X336 question block and picked up the emerged Mushroom at
X341/Y184. The native pickup awarded 1,000 points and played its cue.
He finished the growth animation, kept the first power tier and both
lives, then completed 25 further movement updates. The replay used
1,420 video frames.

Mesen receipt `b8d43eaceb25a79c3210ef538db7c196ca3ccd0f2344f3c1b55c4fb33e9e4fb0`.
Controller SHA-256 `5b652e85d7c83a11aaa1e0dc2d8abf08ca6d447cdd994cc6e86599c710c41a5e`.

Zelda II Link hit the same block and its Jump reward fully emerged at
X336/Y120. The first native attempt timed out with the player below the
block at X334/Y176 and Jump still unlearned. Native diagnostic receipt
`16f513a01eb27d1fa77738ab27b42662d4958d8bdabba3cdef8573ed15b38e73`.

The passing route released A and followed the falling reward. Link
collected it from X411/Y157 while standing on the floor. It taught
Jump, credited 1,000 points and queued healing. He finished with HP127
up from HP111, both lives, and 25 further grounded movement updates.
The replay used 825 video frames.

Mesen receipt `ab8d58c8dfcc19fdc6acadb205254359b58a874e3c1258b2694476dda1fe60b5`.
Controller SHA-256 `07dd433297e28f9f5233504cf78b68f8d1c7a2725026b9e089913d48921e236d`.

## Zelda II Link's hidden 1-UP

The Mesen continuation earned Jump and cast it with Select. The spell
reduced MP from 127 to 31 and helped reach the hidden block at X1024.
The normal 1-UP emerged and was collected. The delayed award advanced
the life counter from two to three and queued the extra-life cue. Zelda
II Link kept full health and the third life through 25 more movement
updates. The run took 1,693 video frames and saved zero captures.

Mesen receipt `fee955344d72cd896da97d1c9d79015d09aa189696b1b3f445c0c72f29ae6faa`.
Controller SHA-256 `d91e5610f8d7ff94907b06b53ab658f37961d3e5cdac753549c115877c28b2a1`.
On `3af597a7` the runner checks the same Link gameplay hooks and changes
only the expected ROM hash. The original Mesen pass still counts.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_link_family_mushroom_1123.py --run --form link
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_link_family_mushroom_1123.py --run --form zelda2 --pursuit
python -B tools/audit/run_bounded_build_v1.py --output build/smb2-flag-native-1113 --resume --max-files 2 --timeout 300 -- python -B tools/audit/run_link_family_stock_1123.py --form zelda2 --route life --run
```
