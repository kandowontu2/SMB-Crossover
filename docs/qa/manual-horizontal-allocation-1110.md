# Native horizontal support allocation

Root reviewed `check_manual_dual_platform_1110.py::funding` and the source CPU
receipt in `build/manual-dual-platform-1110/proof.json`. The exact current bank64
is reproduced from `PROTO_MM3_AUDIO`, except its already allocated manual-helper
gap. The source segment occupies A000..BFDD; the final command at BFDA is an
unconditional music jump to BF1C followed by the end marker. BFDD..C000 is linker
fill, not stream data.

The additional **physical PRG64, CPU BFDD..C000 (35 bytes)** is allocated to the
Mini Mario/Karnov dual-platform worker on the 095c lineage. The worker uses 34
bytes. This allocation accompanies the existing B378..B400 helper lease and
does not grant any additional audio bytes or RAM. Interrupt/audio qualification
and real native carrying/crossing tests remain required before delivery.

User control: Up + Select vertical; Down + Select horizontal. Each type has its
own ownership, pending request and replacement. Horizontal placement is in front
of the player; native platform actors provide movement and collision.
