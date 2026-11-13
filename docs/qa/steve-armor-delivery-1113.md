# Steve armor delivery qualification

Target ROM SHA256:
`62ba7f54117875ec018d6f85fb1c74408aa11f0fe0f6a85b8b4f601034a17639`

IPS SHA256:
`e45931e9493a4731e2e3c6f6734a9520a30f00d7243040525dec5396000a5def`

Clean headered SMB(World) base:
`0b3d9e1f01ed1668205bab34d6c82b0e281456e137352e4f36a9b2cfa3b66dea`.
The2,099,506-byte IPS reconstructs the exact tested image in memory.
Parent is previously deliveredaa501; exact source inverse reconstructs it.

Source4e998e0c qualifies full armor and the13-byte inactive-path fix;8b2eda14
qualifies natural stock pickups. Root independently verifies final proposal,
inverse and complete cold readback:2,398,039 instructions, packet8,839bytes,
268bytes spare and all three complete owner headers. Detailed ABI, source,
wave, clock, owner-transition and interrupt scope is in
`steve-armor-live-1113.md`. No new helper or public level data is introduced.

## Actual private Mesen qualification

|Case|Controller SHA256|Receipt SHA256|
|---|---|---|
|Empty-opening cadence|604f3c3b2a4822380af815ce0e65a517bebbe3cc8a8c569377eb6d2147417e19|aaa90ccb8083e7e6fe07d220d8fe2e3c229642771e6b6221b05446c380e4b05b|
|Steve full1-1→grounded1-2|3c477bf925743d320a3e51e008f582708297a2b78f0ad19be5112bde6ba8144d|98124f1b550dae5ffa0e8245ab0806e421596254b26071b1366db1feb76cbf8d|
|Jay authored pickup|b198a94852e46c85922cc065ce39a0349298aaccd42f34f8da272d7363d8e11c|0e074e671022bca1fb61f4ce758341d725973d8605c0cb2c2bddc386d4447d9d|
|Jay fullstage/machine gun|9189a9408ea6f52778a2dc53f6206e632ec4534b9d9e4057d91b08fb3ec34e29|29054e3e121585e6f4bc09a30a874c14b53f15350d0a8449548fcd3b594d1cd6|
|Quick four items/fullstage|20595adf32d5b12c9e6498f8ca0ef2542a849ffcda871c919c6c5b0e3075dc12|51abb4384389fa19a1f13d679cf59d8c28806329caf44a5ba24f44237c1a31b3|
|Steve stock336/1248 Alpha pickups|82ace2fe3ead540390e5a0eb3dd5c9003461238fba925a686fdd5aa7d9a465a6|b9fb05190e4d73b30999a268b0fb96389701e0444fed599b82d43f7d9d357cbe|
|Separate private combat fixture|81c9abab8969d68f07d858b2ce5ad25e202380894db85b627663d8e450bf0849|2de36a11174bace173888750732f755e9fd767e20bf1c728c08fbbc543c7ae49|

The six unmodified-ROM cases above execute exact62ba. Cadence measures
walk36updates/37physicalframes and idle25/25, all frames input-polled. This
removes the large private2aa slowdown; it is not an all-stage zero-lag claim.
The stock pickup run lasts2,917physicalframes/1,411updates, earns two source
Alpha tokens through actual authored blocks and keeps both lives. Its one
Goomba injury is not represented as a no-damage run. Steve's6,175-frame
full-stage run reaches grounded1-2. Jay retains actual first pickup/health
and native helper access, full stage and five machine-gun shots. Quick earns
four authored items and reaches grounded1-2 atHP40/lives3 in5,693frames.

The combat fixture is a separate private level-data-only ROM,
`7b82c7c3c52b0d8bba2f304501e5d3e58999e5f77bfaaf0780f844f3a52c6274`.
It changes15level-data and7enemy-data bytes, with no runtime state seeds or
code changes. Actual Mesen passes5,913physicalframes/3,633updates, six real
questions/collections, armor entry, a protected Goomba contact atHP6, two
native Goomba defeats by one persistent right-facing wave, a left-facing
wave,44physical DMA cell matches and natural expiry. Both lives remain.
The fixture is never installed or published. Its disposable candidate is
restored byte for byte to unmodified62ba in a finally block.

The initial Quick run used its parent's literal receipt ROM hash. The shared
runner correctly rejected the mismatch. Regenerating the controller from
exact62ba changes only that one literal: old7711ef40→new20595adf. The rerun
above is the qualified actual-image result; no gameplay byte changed.

## Delivery state

All private native checks and the six-binding/IPS metadata check pass.
`deliver_steve_armor_native_1113.py` directly replaced Downloads without a
backup and repeated all six unmodified-ROM receipts above exactly. Installed
bytes equal tested62ba; sidecar-patch guards pass before/after. The sole
Current/Latest publication is the remaining delivery step at this snapshot.
Full roster, original ability, audio, visual and difficulty review continues;
these character-specific checks do not establish overall goal completion.
