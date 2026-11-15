# Battletoads idle cadence — November 14

Root86156 observes exact installedf11 in Mesen through normal title/roster/
Start and then48 completed idle GameLoop returns. The dedicated controller
only holds neutral input; it writes no game state, creates no actors and
captures no images or files. This is a timing observation, not a stage run.

Lua SHA256 `f6cc1a294935e7e8a76ba301f8de423b9227880b34059731f9f7b375f89a336e`;
receipt `52d1f1f4d179ac568505e021ed03d40e38349d54f31c5b4206c27aa4d67f4ea0`.
The bounded existing two-file flag slot uses `--resume --max-files 2
--timeout 600`; native capture watchdog remains active. Actual Downloads
bytes and patch guards are unchanged before/after.

- Start observation: Main273/frame297, source step1, NmiSkipped22.
- End: Main321/frame369, source step49, NmiSkipped70.
- Interval:48 completedMain across72 physical frames,48 additional skipped
 NMI counts. Zero active native enemy/powerup actors throughout the interval.
- Rash remains40/Y176/high1/native0/engine8/HP47/lives2/power0/Star0.

The bounded measurement confirms real idle lag on this build. Its48/72
update ratio must not be presented as a universal frame-rate guarantee or
confused with the separately completed full-stage receipts. It also does not
show that the camera fix caused the lag: that patch adds only65 source CPU
cycles per BT step and the earlier parent already had the expensive paths.

A separate source profile reports approximately36604 scheduler cycles for
idle Main and36865 for walking, with exact GameLoop entry/return counting
being verified. Twelve BtCheck calls consume3900 cycles; nested generic
validation and farcall overhead merit investigation. Model CPU counts are
not hardware timing proof. No caching, dispatch bypass or performance patch
is allocated here; existing cookie, foreign, SMC and ISR contracts must be
preserved by any proposed optimization. Source profile has its own owned QA.
