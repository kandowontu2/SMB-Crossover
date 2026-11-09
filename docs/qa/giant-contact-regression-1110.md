# Mega Giant Mario contact regression

The installed nightly `9906787a73b6d319cd30a2d3a89f50e4aa6892d912a9c22e9c5e19a14e581835`
reproduces the reported first-Goomba death. The controller selects Mario alternate
9 through the menu and holds Right without jumping or enabling cheats. Native
death begins at world X=271, with 148 Giant draws recorded.

Evidence: `build/giant-walk-baseline-1110/capture/result.json` and its bound native
packet. This is an expected failing regression, not a qualification pass.

The earlier full 1-1 clear jumped over the first Goomba. It establishes traversal,
not ground-contact immunity or enemy defeat. Do not cite that clear as combat
coverage.

The donor hack redirects damage contacts to native enemy defeat and shatters
admitted block materials. Its structural exclusions (including pipes, ground and
exit objects) remain intact.

## Delivered fix

Nightly `12f3e4163631887e134cbce7f1caa015bfe4b3786c2ee3d71217c80c1f677a6c`
is installed in Downloads, and Current is Latest with its sole IPS asset updated.
The actual Downloads launch passed the no-jump first-Goomba test. It observed
native enemy defeat, zero injury calls, and seven shatters including both question
block types and plain bricks. Giant also cleared 1-1 into active 1-2 with both lives.

The first candidate exposed a separate failure at the late staircase gap: native
side collision stopped Giant on destructible and pending-shatter tiles. The final
Giant-only side query treats those materials as passable while the native block
actors finish their effects. It leaves native foot landing and structural
materials intact. The unchanged controller then passed the complete level.

Mini's regression retained 3,494 gameplay updates over 3,494 physical gameplay
frames, with zero missed updates or lag NMIs in that interval. No helper was added.

Evidence:

- `build/giant-impact-delivery-1110/verified-delivery.json`
- `build/giant-impact-side-native-1110/{contact,full11,mini}/capture/`
- `build/mega-giant-impact-1110/proof.json`
- `build/mega-giant-crush-side-1110/proof.json`

IPS SHA-256: `d46f761ed8f4ec77fe3f4593476f3ab39fd23877927ac211290f15e77a92174d`.
Delivery receipt SHA-256: `5d5f7669b96f43630f4795b3fe5fbf8a2927464fdd6349a96b76cf19dd6b787e`.

Direct body contact intentionally defeats enemies the donor sometimes stomped or
kicked, matching the user's request. Firebars and thrown hammers use separate
hazard paths; their donor-specific behavior is still pending and is not covered
by this delivery's enemy-contact claim. The full roster goal remains active.
