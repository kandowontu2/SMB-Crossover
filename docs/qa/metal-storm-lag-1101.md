# Metal Storm overhead reduction

Installed Downloads nightly:
`128915e97e78891a585aa8f9fd904c166ca64dcd6dd1ee395fc68fd505c1e72c`.

Live service profiling identified three static rejected handlers (visibility9,
box13, UI29), each paying the full cache/mapper transport despite never reading
or modifying the cache. Their three-byte ROM veneers now directly return carry
clear. No supported service, source movement, graphics or cache header changed.
Future implementations of these rows must replace the short returns too.

Actual old/new public callback comparisons passed1584 cases, including all32
single-byte corruptions across the two16-byte cache headers. ReturnedAXYP,
non-stack nativeRAM, four WRAM banks and final mapper state match. Each valid
callback saves1149 CPU cycles. This is not removal of authentication from any
path that accesses or executes cache contents.

| Native empty-opening measurement | Before | After |
|---|---:|---:|
| Idle mean loop cycles | 34952.2 | 32638.4 |
| Walk mean loop cycles | 36939.6 | 34452.0 |
| Idle updates /120 physical frames | 80 | 80 |
| Walk updates /120 physical frames | 77 | 78 |

CPU cost fell about7%; physical update throughput barely changed. Lag remains,
so do not describe this as a lag fix or60fps. Original movement still dominates
the Metal service costs, and base engine/render scheduling also needs profiling.

The unchanged controller completed the full non-shortcut1-1 route through active
1-2 in5536 total frames without losing a life. No helper platforms were needed.
`build/metal-storm-decline-1101-v40/route/capture/result.json` and `binding.json`
bind that result to the installed ROM. This still does not cover powerups,
shortcut route or every mode. Gravity escape remains an open bug.

The nightly replaced Downloads directly without a backup, with patch guards
before/after and exact hash comparison. A separate cold menu/select/idle/walk
test launched the actual Downloads path and passed:
`build/metal-storm-decline-1101-v40/downloads/capture/result.json`.

Progress on functional roster continues; Metal's deeper review remains open
while the remaining unintegrated characters need admission and1-1 work.
