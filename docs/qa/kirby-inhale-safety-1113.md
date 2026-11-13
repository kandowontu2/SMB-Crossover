# Kirby inhale safety follow-up, November 13

Input nightly: `a3c5fa63872fbb3103ae57d9748fef233e8b2273e26d985aa4006b2492d81b8a`.
Kirby PRG74 SHA256:
`119a6fe415a914c415a51bc46f0cc22569cd4c7e1282d83f512c3b2031573e9d`.
The delivered capture-frame and red-catch code authenticate by exact inverse
preimages and source forward recomposition. No ROM change is proposed yet.

The retained1112 audit already covers the18 positive mapped IDs at ordinary
distances, both directions/difficulties, vertical boundaries, water branch,
the Lakitu/Spiny same-capture update, and green/red shell behavior. This
follow-up does not rerun those passed suites or claim new emulator coverage.

New explicit CPU fixtures cover initial front gaps0..5 for all18 named inputs,
both facings and both difficulties. Actual native enemy initialization and the
real reset-tail/IdleLoop/GameLoop caller execute. Walking velocities are
mirrored as legal actor-data fixtures; no ability, result or executable bytes
are seeded. All432 cases retain HP6;408 capture an enemy. The24 noncaptures
remain separated from a claim that every initializer yields a live visible
actor. No front-start contact-order injury was demonstrated.

Source: `tools/audit/check_kirby_inhale_safety_1113.py --part boundaries`, run
through the bounded runner with Python `-B`. All results remain in memory;
zero outputs, captures and Mesen launches. No allocation is requested.

Remaining scope: live native state changes including enemies descending below
the visible playfield, front/rear contacts after another capture, and actual
mouth→spit/copy attacks against grounded native targets. The general non-shell
projectile Y-page admission also needs a current witness; the older source
audit flagged it separately from the already repaired shell contact helper.
Those are investigation targets, not new qualified defects or delivered fixes.
