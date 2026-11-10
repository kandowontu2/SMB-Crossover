# Donkey Kong Jr. second-gap platform

Donkey Kong Jr., the Select alternate on Donkey Kong's slot, cleared the four
pipes and both early gaps in World 1-1 with two lives in a continuous Mesen
replay from the title screen. The first gap still uses his original jump.
The second gap uses the original horizontal platform actor, ID `$28`, box 6.

| Stage | Pit span, world X | Initial platform left X | Initial center X | Initial top Y | Width |
|---|---:|---:|---:|---:|---:|
| 1-1 | 1376–1423 | 1408 | 1432 | 208 | 48 |

The platform spawned with camera-left X1121, 287 pixels right of the camera
origin. Its first in-bounds sample was at moving left edge X1397
and camera-left X1143. Donkey Kong Jr. took off at X1366/Y176 with Right+A for
eight source updates. His original landing routine found the platform at X1393
over an empty ground tile. The published stock collision box supplied that
update's platform top. The far bank accepted him at X1412/Y176, and the replay
ended at X1425/Y176 with two lives, after 11,853 physical frames and 5,055
observed original Main entries. The controller jumped past the first Goomba,
backed up to X1187, and timed the second jump for the Goomba falling from the
ledge. The route used only controller input.

The exact Sonic parent remains intact outside the 248 new DK Jr. byte edits.
The source recipe reconstructed the full candidate, and compiled Start and A
checks matched for all 100 named roster entries. The
[admission checks](dkjr-second-gap-admission-1110.md) cover 14,336 camera and
ordinal cases, 108 stock actor retry/birth cases, and 810 paired refresh cases.
The replay measures the crossing through the second gap. Later pipes, the
full stage clear, earned powerups, and performance still need work.

The Downloads launch reproduced the candidate's native receipt exactly. Its
separate Sonic replay reproduced the previous ring pickup, visible ring-loss
and recovery gameplay receipt after normalizing the ROM hash. The Downloads
patch guards passed before and after replacement. No backup or capture file
was retained.

- Parent ROM SHA-256 `36e9a6a8b2f8dfb79447c8d9e74633245dd412ede0a408d075e3df2db01b85ca`
- Candidate ROM SHA-256 `3d327d47b8127c1e76d9868191d34b8ebb1ca9ec29d6bb609ccab9c60c6cb3d8`
- Reconstructed IPS SHA-256 `ba9b6a0460d76341ba96bdf620eeba4f3fba2a9ba59194c06d896732acba05e6`
- Controller source SHA-256 `97c4da3f2bcc228b022a01e2b8cf4aa89c480e57e6fb762905d4dc0c6bb19697`
- Native receipt SHA-256 `1aa9e6dfcaf255ae750717eb69e7a394f7c3f1773e2871a5989e54c7998bcfad`
- Installed Sonic regression receipt SHA-256 `6342b3d6c408bb5082a2283fb0a648394110be713d6da6759fe8ac025717e31b`
- Normalized Sonic gameplay SHA-256 `aac201ce41ac6813019c3ba7f6c743ba0f99e098272d6c823a76024e58535d2b`
