# SMB2/Doki natural item qualification — November 13

Exact input is public Downloads
`7ef2de351d3a4ae60b3ada2eb1aa56b330873dc106ad43428ec6803bf420d4fc`.
This work changes no game code, health, terrain, actor, item maturity, position,
inventory, physics or palette. Fixtures after the established real native menu
use only ordinary controller inputs and actual Main/NMI scheduling. No ROM,
capture, receipt or other generated file was written by this helper. Root owns
the single Mesen queue and native delivery. GitHub releases remain empty.

## Existing item policy, confirmed

The October29 design in `smb2-roster-main-source-2026-10-29.txt` explicitly
documents an initially large/two-heart form selecting a Flower, and Mushroom
selection after an actual injury to one heart. This remains the intended
current adaptation. The tentative suspicion that healthy Flower selection was
a new bug is superseded by that source/design evidence; no discriminator patch
was made.

`UnionPwrUpCore` chooses kind0/1 from PlayerStatus before S2MainPrepare.
S2ExportPosition projects HP>=16 as status1; the source's separate S2Size owns
USA/Doki body art. S2MainPrepare records native ownership and rise state without
rewriting the item kind. Mushroom gives the original maximum-heart increment
(max index0→1→2, cap2) and full health1F/2F/3F. Flower adds3 original vegetable
reserves, cap9. Star/1UP retain the native fallback. Fresh supported-ground B
can spend an earned reserve only after successful allocation; source lift/throw
timing and vegetable hitboxes remain original. Those latter flower/attack and
Star/1UP routes are not qualified by the first-Mushroom proof below.

An ordinary healthy Imajin CPU route genuinely avoids the first Goomba, stops
atX328, jumps and hits the actual authored C1 at336. At logical iteration278,
the real native head caller sees HP31/max0/size0/status1. S2MainPrepare sees
kind1/state1 at336/136; the real actor is born kind1/state2 at336/135. Both lives
and full health remain. This is preparation/birth evidence, not maturity or
physical collection. The pure `healthy-flower-birth` factory is separate from
the injured route and needs its own controller/native qualification.

## Genuine injured Mushroom route

API:
`replay_smb2_natural_powerups_1113.controller(exact7ef, variant, 'injured-mushroom')`.
The same factory also has the explicitly limited `healthy-flower-birth` mode.
Menu raw25 is reached with Down×3 from slot0, then actual Select cycles0..7.
After Start/constructor, the injured route walks into the real first Goomba,
continues to the first authored question, settles atX328..329, presses fresh A,
walks toX395 and waits for the actual mature Mushroom returning from the first
pipe. The real physical collector is observed through S2MainPickup and its
true stack return. Sixty ordinary neutral updates verify resumed source play.

All eight exact Lua controllers pass actual CPU/Main/NMI/controller execution
on the unchanged authored stage, with zero gameplay seeds or grants:

| Variant | Identity | Logical scheduler iterations | Size before Mushroom |
|---|---|---:|---:|
|0|SMB2 Mario|540|1|
|1|SMB2 Luigi|544|1|
|2|SMB2 Toad|540|1|
|3|SMB2 Peach|540|1|
|4|Imajin|508|0|
|5|Lina|508|0|
|6|Papa|508|0|
|7|Mama|512|0|

Every run has exactly one real31→15 Goomba injury, the real C1 head, native
kind0 preparation/birth, mature state128 and physical Mushroom405/184 contact
at player395/176. The actual source grant changes HP15→47/max0→1, erases the
native actor, writes sound32 and popup6; both lives survive. USA size1 returns
to0 through its original changing-size timing. All four Doki modes retain
size0 after injury and recovery. These are CPU-model results, not hardware
cadence or full-stage evidence.

The initial development probe allowedX326..329 and could hit the adjacent
brick51 atX326; no item was born in that bounded negative. The qualified exact
controller settles atX328..329 before fresh A. No ROM or physics change was
needed.

Root independently ran actual Downloads7ef with frozen controllers:

| Identity | Lua SHA256 | Actual result |
|---|---|---|
|Imajin|36e52aae4abee6a26a42dd396239137d41195e4fe72ab85dfd0dfcb75b3bb81d|PASS906physical/503all-Main; receipt afc423ce870ec83de92b5ab94dedbd2fc5980f45a09219f46fc157e28e27bc1f|
|SMB2 Mario|18ffdb276851310ca47b3cf81b4c6296553c51880973fe821bda4ba5ac604637|PASS874physical/534all-Main; receipt bba0072b061cdfefc5342ace8ad91b99ba9c235e8e8dbda11d172935bfe6e8cc|

Native Imajin: injury177, actual C1 head257 at329/150, kind0 birth258 at336/135,
mature406/184 collector443 atplayer396/176, source HP47/max1, native erasure,
sound32/popup6 and60 resumed updates. Root's subsequent serial run4811 passed
all remaining identities on actual Downloads7ef. All8 native physical/all-Main
counts are Mario874/534, Luigi904/541, Toad899/537, Peach920/537, Imajin906/503,
Lina916/508, Papa951/522 and Mama954/526. Actual pickup Main indices are
474/481/477/477 for USA0..3 and443/448/462/466 for Doki4..7. Each confirms real
injury, C1, mature kind0, HP47/max1, erase/sound32/popup6, both lives and60 resumed
updates. Root retains the aggregate native receipt/hashes separately. No new
helper platform exists.

Reproduce CPU decisions without outputs:

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/karnov-equipment-1113 --resume --max-files 1 --timeout 180 -- python -B tools/audit/check_smb2_natural_powerups_1113.py --controller --variant 4
```

The CPU scheduler models one completed Main per iteration and does not predict
the native physical frame count. Authored1248 flower maturity/physical
collection, earned vegetable lift/throw/contact and native Star/1UP remain open.
The separate private flag0e9e reaches native flag/castle/entrance but exposes a
real engine7 mapped-data halt; it is not a delivered full-stage success.
