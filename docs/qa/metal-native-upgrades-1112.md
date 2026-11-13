# Metal Storm native upgrades, November 12

The installed Kirby catch image
`f228e61399432c1a205b8f5ac6dad13d990515f9c2e2f5024bcd5ce443c76653`
composes through `tools/audit/compose_metal_column_wait_1112.py` to
`19e86f855f80da1a651d1ecd1bab0502a2cf5d757298505a056ad01fe075646a`.
Each stage checks its complete owned preimages and has an exact inverse.
The image combines the original item0 grant, deferred native head contact,
authenticated pickup maturity, and a synchronous host acknowledgment for the
source column stream.

The head and flower image reproduced an overlapping mature mushroom that
never reached `PlayerEnemyCollision`. Live trace
`6632cdf0d29363f07039e9b0e1b3f877ef1a55ed78d3576ea271cabf92da314f`
showed the earlier `NrPickupCollision` admission as the failing step.
Metal row23 at D44A now reaches its four-byte maturity policy at BFBA,
returning bit7 of the native `Enemy_State,X` in carry. This gate admits the
native actor overlap only after the rise. The existing collector still owns
the armor and donor item0 state updates, cleanup, sound request, score, and
native tier progression.

The policy fits the existing actor bridge. Its prior return saved status
through an old C-bank restore using six extra bytes. The outer authenticated
frame already restores AXYP and reads only the result carry. The original
bank writes and return preserve that carry, so removing the inner status
save fits the four-byte worker and leaves two padding bytes.

For the maturity image
`b99c43dd7caca2af8677d3a588078864d27a2f1759a1e58c9a502a498bef767d`,
the CPU checks exercised the real player bounding box gate and native
`PowerUpObjHandler` for every enemy slot. Twelve mushrooms gave armor,
twelve flowers gave the original weapon, and 24 mature Stars and 1-Ups
reached native collection. The other 144 actor cases kept their item. The
old image reproduced rejection before native player overlap. The public
ABI matrix passed all 1,536 state/slot cases, 32 corrupt-header rejections,
44 foreign-owner pairs, and 84 other public service comparisons.
The compacted bridge passed 22 IRQ and 22 FF lag-NMI cuts at minimum SP160.
Seven readback corruptions failed closed, including the new vector and
worker. The donor shot comparison passed 22 actual public movement phases,
eight type81 births across both slots and four aims, and two native enemy
contacts.

The controller retreat toward the flower exposed a separate original
column-stream wait. The live PC and stack trace
`9fa5f492f74d724d64ff795e9984dfac328ec14998d7f3baca38f8a61358f665`
places the stopped actor at translated B0A3/B0A6, donor BA86/BA88, called
through donor BC04. Original NMI reaches D7DA with queue index ED zero,
reads the terminator, then D872 clears write index EE and increments ED.
The resumed source routine builds the next column header and calls FF18.
The SMB host already owns PPU writes, block buffers and camera streaming,
and its existing typed FF18 records the source boundary. The five-byte
replacement supplies the value of the original completed acknowledgment,
preserving the rest of the original column routine and its FF18 call.

The original donor CPU executed FCFD, D7DA, D872 and D876 once each, then
resumed at BA8A with ED1 and EE0. The final host CPU matched the acknowledged
original path on 336 register and state comparisons, including 288 source
FF18 handoffs. The old host wait reproduced with ED0 and the new host
completed. The new instructions passed four IRQ and four FF lag-NMI cuts
at minimum SP198. Final cold copy read 24,600 PPU bytes and published both
full headers. A readback corruption at the replacement opcode failed before
either header was published.

On the final private image, Mesen collected the natural mushroom and
flower, then fired the donor's type81 shot by frame2356. The previously
stalled retreat advanced on the same route. Receipt
`90c3a08b622f665cc3ecb95004394c1c3984cc75d525539f094e7c4cceab84c8`.
A separate controller replay on the same image cleared 1-1 and entered
active 1-2 in 5,491 frames with both lives. Receipt
`c327b5c4a38c1ce5c4c5ad5f626182473b9261a6bf758a36fdea46bbbeb1ea79`.

The zero-output CPU commands run through the shared bounded runner:

```
python -B tools/audit/run_bounded_build_v1.py --output build/metal-head-cpu-1112 --max-files 1 --timeout 600 -- python -B tools/audit/check_metal_pickup_maturity_1112.py
python -B tools/audit/run_bounded_build_v1.py --output build/metal-pickup-faults-1112 --max-files 1 --timeout 600 -- python -B tools/audit/check_metal_pickup_maturity_1112.py --faults-only
python -B tools/audit/run_bounded_build_v1.py --output build/metal-column-cpu-1112 --max-files 1 --timeout 600 -- python -B tools/audit/check_metal_column_wait_1112.py
```
