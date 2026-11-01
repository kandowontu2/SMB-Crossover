# Karnov first-stage progression investigation

Candidate: `367266d2ec4e62fcefc15fffb3a05095a16060ad52f9d68348f213d94b31268c`.
No ROM changes or delivery were made for these probes.

Controller-only cold-boot routes, no state writes, two PNGs per run:

- `build/karnov-stage-route-1101-v3/probe/capture`: waiting until world X638
  misses the preceding pipe edge. At X637 the actor is grounded at Y128;
  by X638 he is already falling. This attempt is an invalid edge-jump test.
- `build/karnov-stage-route-1101-v4/probe/capture`: launch threshold X636
  successfully jumps from that pipe. X669/Y80 is the apex, X693/Y107 on
  descent, X698/Y122, X706/Y152. He reaches the next pipe wall only after
  falling below its top. Maximum world X722, no death, 3200 game frames.

The second trace is evidence that this launch does not clear the obstacle,
not proof that every possible controller/equipment route fails. Earlier
automatic-jump routes launched too early. The next investigation is whether
equipment can be earned before this obstacle, whether supported horizontal
controls alter reach, and whether a source-consistent accommodation using
existing native platforms is needed. Do not change jump constants merely to
make the controller replay pass. Full 1-1 clearance remains unverified.

Recipe: `tools/audit/prepare_karnov_stage_route_1101_v3.py` (final X636).
Each capture's generated controller preserves its exact launch threshold.
