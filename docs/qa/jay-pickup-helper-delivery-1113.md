# Jay head and first-pickup access — November 13

Combined ROM SHA256:
`aa50112845d1cf70cae0924f03326647b3d2514f876c756d70b134ee44f971d1`

Installed parent SHA256:
`4641ca4fb72699c0478e31b831d4c4ea0ffd2227be7f8446666092d2cc26e1d3`

IPS SHA256:
`a5ecdd50c6e186415f9b4e3c75f53bcef7cf69df3012f02e6466a7e7413e33a1`
(2,099,506 bytes; exact reconstruction from the existing clean SMB base).

## Behavior

Jay's original ceiling-stop path now reaches the real native item-block
handler before upward movement is cancelled. His53-pixel original jump and
screen-minimum clamp remain unchanged. An existing native25 vertical platform
provides access to the first brick row and its health pickup without scrolling
the pickup behind the original left boundary. This is a native actor, with no
new artwork or custom platform physics.

Jay (Mike Jones, Select once) has these fixed1-1 platforms, width32:

|Purpose|World left X|Center X|Initial top Y|
|---|---:|---:|---:|
|First pickup, new|384|400|192|
|Third pipe, retained|688|704|192|
|Fourth pipe, retained|880|896|192|

The new platform is born offscreen at relativeX286/camera98, before entering
view. Existing placements are unchanged. Adding the new four table bytes is
funded by removing the obsolete lower-camera-page restriction; the owned
worker stays247 bytes. The primary packed carrier stays2048 bytes. Source
checkpoints: head bridge1eaa4e9b and native-helper2af1fd0c. No resource grant
or WRAM expansion is needed.

## Qualification

Root independently repeats the helper's960 spawn/decline cases,40 scene and
retry guards,256 incoming-status ABI cases,134 IRQ plus134 lag-NMI cuts with
SP168,140 forced-blank decoder cuts with the same parent SP122, complete
32800-read cold/zero-read warm admission, three new readback fault rejections,
80 paired Mike/Steve updates each, and387 identical CPU/Lua pickup inputs.
The head bridge's separate full native-caller/terrain gates are documented in
`jay-powerups-current-1113.md`. These are scoped fixtures, not a full-roster
gameplay claim.

The final ROM is explicit composition Quick.transform(eac09fa8), retaining
Quick's exact previously qualified source. Inverses recover helper→head→a3,
then the Quick-only installed4641 exactly. All three private native runs below
execute this exact combinedaa501 image, using ordinary controller input only.

|Native case|Controller SHA256|Receipt SHA256|
|---|---|---|
|Jay first authored health pickup|15f10a41e774053c56ef569aaf22e13e585eaa0fd8b33a893bfc37e8186cf97d|abe9281690573229b2b45fec8ca414c7fbbc9f823ce1b545b86344e23f73b0ca|
|Quick four-item/full-stage regression|7711ef407ad23be3b432c586bec52dac0d801e1c43c3121a7c5bb269297bf052|50d2332176f026d924ce91d26851b18ff220dff37cbbd8e494e928b428c8666e|
|Jay full1-1 and machine gun in1-2|dd7c656145ea98860e4ff3fe50828d36bb9045e031c345a8b6d53b077fcc4e60|4e1140c6872cc1e91b7cbb0055a4938d614f51ed1ebc8d4f2d4fb3d2a089b9da|

Jay's pickup run lasts1077 frames/388 updates. The actual C1 head hit produces
a native item; the helper has a real supported board and fresh left jump.
The mature stationary heart is collected from dynamic slot4 atX348/Y112,
HP6→8/maxhearts3→4, native sound and actor erasure. It remains at least eight
updates afterward. This is the currently inherited Mike health icon/policy,
not a claim of original Silius weapon powerups.

Jay's separate5520-frame stage run clears all six pipes, three gaps, flag
and castle, reaches grounded1-2 with both lives, selects the earned machine
gun and produces five held-B shots. Quick's5693-frame regression collects
four mature authored items and reaches grounded1-2 at full health/lives3.

## Delivery

Private native checks and exact IPS roundtrip pass. The remaining steps are
direct Downloads replacement, all three exact installed replays, automatic
patch guards and sole Current/Latest asset refresh. The delivery recipe is
`deliver_jay_pickup_helper_1113.py`; no backup ROM or capture files are created.
Steve armor remains private; broader roster/powerup/audio review continues.
