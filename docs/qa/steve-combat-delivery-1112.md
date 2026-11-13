# Steve throw WIP delivery — November 12

Candidate ROM: `464c8f1af0401ba7d5393e331833af5bdd68882c536dfc3c77534b71508213c0`.
IPS: `508ac358f5d8476e3b33ae6e92b649a9954f457cf33734c57b283e65c1ac0a88`.

Steve's grounded/airborne robot throw, player recovery, returning robot,
enemy contact damage and robot destruction are connected. Pointer scratch
now survives NMI; destruction clears laser draw tags as well as projectile
types. The combat allocation occupies 1024 bytes.

Physical Mesen controller-only qualification:

- Earned Laserbot, grounded throw, recovery and robot OAM, return alive:
  4209 frames, two lives. Receipt
  `7bb20e43fbf248c1353e245a9a8796f377f505efe71fef9082b8bc8686770c5e`.
  Controller `fccbdf72f986998351d896d6c04ae60f18c8f6ac5e86578619f6fa129a4d9318`.
- Earned Laserbot, beam hit Goomba at X2027/Y184, cleared 1-1 into 1-2:
  6884 frames, two lives. Receipt
  `b26c99c95c2116bb9ac7a67773691bb1aa80d84024930d7d039480a998f6da81`.
  Controller `714edb4457af658cf796106c134681eb429b85be8676813d1bf1ea41a9c4de32`.

CPU tests additionally cover six throw cases (three launch states, both
facings), eight contact/death cases, 78 cold-load interrupt cuts, actual
foreign-owner overwrite/restore, donor death behavior, and precise projectile
cleanup. These do not establish a full-roster regression pass.

Original throw/hit/explosion cues still have no audible consumer. Additional
robot attacks, armor and the overall roster/powerup review remain incomplete.
No helper platform locations changed. No capture files or ROM backups were
created. Previous generated lift candidate/controller were pruned; source
recovery remains available.

Downloads was directly replaced with the exact candidate, without backups.
Both controller replays passed from the Downloads path with the exact receipts
above. Pre/post automatic-patch guards found no matching sidecars. Bounded
installer 70762 exited successfully; its first attempt stopped before writing
because script line endings differed, then the exact CRLF encoding was restored.

The delivery recipe embeds a compact reverse patch to recover the exact prior
80e6 image in memory. Forward IPS reconstruction equals the installed ROM.
Current was marked Latest and its sole IPS replaced (asset 741705154).
An independent download reconstructed the exact Downloads ROM. Publication
source was `fd61a1218b537affab028524293571bd814a44ab`; publication-time report
SHA256 was `ca1bfba712ee38f02048dcf041dca2ee9671d64fdffd52f82cc361af731539a5`.
Bounded publisher 73415 exited successfully without generated patch files.
