# Metal Storm native flower bridge CPU qualification

The in-memory candidate is
`1595c7fcb6449fe20809124edbb4aa3e58fa69452c2f51bfc286485d93c6f3f7`,
composed on installed Prince successor
`cebb0ae64b4e6cc92e473a239cb8fd4011d54cfd5e6814013a3afbd2de2bf7d7`.
The transform validates only Metal-owned preimages and preserves unrelated
downstream changes. Its inverse reconstructs its exact input. It writes no ROM.

`compose_metal_flower_1112.transform(raw)` redirects the existing four-byte
flower rejection to a15-byte dispatcher and the41-byte original item0 grant.
The mature-item, source-ready and slot gates remain in the existing pickup.
Mushrooms retain original armor behavior. Flowers execute the complete original
grant, set native progression tier2, then use existing native item erasure,
score/SFX and inventory cleanup. GravityFire remains disabled.

Only86 ROM bytes differ. The existing extra allocation grows257→313 of352,
and both complete-cookie literals change together to
`a7232bb7d0447b9deb52b7f7518bae79`. Actor and renderer bytes are untouched.
No carrier, RAM or resident allocation grows.

Final bounded run54163 passed, exit0, zero generated files. Checker SHA-256:
`23b43a42a239cd40c6ed797bdfeecef38a89583fae3df7f5334d09dcc5fcc904`.
The stable files are `tools/audit/compose_metal_flower_1112.py`,
`tools/audit/check_metal_flower_1112.py` and
`tools/reference/metal_flower_dispatch_1112.s`.

- Both actual ROM cold loaders copy/read back24,600 PPU bytes and authenticate
  both complete headers; minimum SP184.
- All six actual `HandlePowerUpCollision` slot fixtures collect mature flowers,
  grant source `$0718=$80`, retain armor, set native tier2 and clear the native
  item/inventory records. Another96 native-pickup cases match the full original
  donor item0 source state across prior modes, armor and source poses.
- 36 mushroom pairs,12 native Star/1UP pairs,48 immature rejections and nine
  foreign-owner pairs retain their parent results. Every one of32 corrupted
  header bytes rejects without changing owner RAM.
- After the real directed pickup, actual `HuMovement` produces type81 shots in
  both source slots and all four aims. Twenty-two reached source shot phases
  match the original donor's AXYP and complete source state, excluding only
  the three declared artificial CPU stack cells. Two actual `HuWeaponTail`
  scenes call genuine native Goomba defeat and retire the upgraded projectile.
- Three actual new-code readback faults at DCA1/DCB0/DCD8 occur after24,506/
  24,521/24,561 PPU reads, using the copied code values C9/A9/60. Each fails
  closed before either complete header is published. An earlier harness
  intercepted the loader's preliminary zero check; it was corrected to require
  an actual copied byte after PPU reads before fault injection.
- Nineteen IRQ and19 genuine FF lag-NMI cuts preserve full owner RAM, scratch,
  SMC, mappings and registers; minimum SP166. This is the direct native pickup
  caller, not the deepest GameLoop stack or nested IRQ-inside-NMI qualification.
- Three synthetic unrelated-byte canaries survive composition and inverse;
  six conflicting owned preimages fail closed. Canary ROMs are not executed.

The root agent separately reports controller-only Mesen full1-1 into active1-2
on exact1595c7fc:5,328 frames, both lives, receipt
`4d689229dd14f84a1575f87657f265a20168aa2c9b95e7c0cdb79b626edff327`.
That route does not earn an item. Root's natural first-mushroom diagnostic
instead finds a genuine source ceiling contact before the native head probe;
a deferred head-effect bridge is separate work. This flower candidate remains
private pending real earned armor/flower and remaining integration checks.

```powershell
python -B tools/audit/run_bounded_build_v1.py --output build/metal-flower-cpu-1112 --max-files 1 --timeout 600 -- python -B tools/audit/check_metal_flower_1112.py
```

No source trees were extracted. Existing v42 ZIP members and current ROM bytes
were read in memory. The output directory was never created; storage guards
passed. Root owns Mesen, candidate emission, installation and publication.
