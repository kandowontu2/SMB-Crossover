# Prince private-window proposal, not mounted

Current exact f11 is the read-only input. No graphics allocation, CPU overlay,
game candidate, ROM output, native test or installation is claimed here.
The earlier body-world e418 packets and four-cap controllers remain frozen.

`tools/audit/plan_prince_window567_1114.py` derives all239 pose tags,170 unique
formatted packets and1069 unique tile bytes (873 compact,153 wide,43 raw).
Direct scatter mutation is rejected: offsets664/673/674/2136/2332/2776/2898/
3115 are also another pose's header or coordinate. The proposal instead
remaps each independent packet and deterministically packs identical bytes.
Its new records fit[478,3157) inside the current immutable pose data extent
[478,3174), with all source tags rebound while preserving format flags.
The204 present poses/408 facings/2578 part vectors retain exact X/Y, pages
and pattern-pair offsets. No data/code after that pose extent changes, apart
from the separately declared two-byte tile mask below.

For raw/wide literal tiles the new value is old even tile+65. Compact encoded
tile bytes become old+64, which preserves their coordinate bit0; replacing
the existing AND#FE with ORA#01 then publishes old even tile+65 to TileOut.
This maps private windows0/1/2→5/6/7 while freeing native0..4, including
Mushroom1 and Goomba2. It adds no instruction, storage, scratch or per-piece
cycles. The publisher's saved metadata cursor is2+pageIndex; three INYs select
5+pageIndex at an additional2 cycles per page, at most6 for the three-page pose.

The exact proposed decoded extents are:

| Stream/live address | Bytes | Current SHA256 | Proposed SHA256 |
| --- | ---: | --- | --- |
| runtime0 BC40 |3|d2b8938f123735855ed77637718bff82df2693250e733c3abfbc91488b44251b|618d85b03952ddeaababc40e17149d3a672bcd19890c9390d3c815f696afc57d|
| metadata1 D779 |2|a87807befd0b9038daaa5104c4be735fef522dbe22defa4ad087582dc2363d44|1e41fa5a397c649fafed65eff53596d2a39f114b8142acb53a5cb5a7b564496e|
| metadata1 C800..D466 |3174|585fedc5269ececbd0e4279d86003873f833ad41cd7aca7804ffdd4c149700fb|979f1afc958ff010a7b3108e1a9e0b31e3bebe406779f94e2d28add83b5db1e1|

BC40 changes `AC04BD`→`C8C8C8`; D779 changes `29FE`→`0901`.
LDA#75 immediately replaces publisher N/Z, while A/X and C/V/I/D retain
their old meanings; streamY is saved before the farcall and restored after.
AND/ORA both preserve C/V/X/Y and the following STA/PLA replaces transient
N/Z. The subsequent compact coordinate read still consumes the original
encoded low bit. Returned tile bits intentionally change; ReadX's BIT then
replaces N/V/Z while C stays unchanged. These are local liveness arguments,
not yet a complete current CPU/IRQ/ingress/owner proof.

Pure decoder-math receipt:
`ee7351010a903e72e040408f98523ea134ab00c8d8b3fec57deee88cf96c4a40`.
Current metadata SHA256:
`12723b0ee33c0e9acda75831e5c0b20a4afd61c96daead0b9d396096cacf89ea`.
No claim is made that this is a complete current graphics or gameplay fix.
Root review/lease is required before in-memory renderer fixtures; current
caller/reference domains, all408 CPU renders, interrupt cuts and private
window owner/retirement guards remain to be qualified under that lease.
