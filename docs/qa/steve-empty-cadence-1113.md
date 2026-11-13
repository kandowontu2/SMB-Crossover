# Steve empty-opening cadence regression

The private armor candidate2aa509 is not approved for delivery. Its native
armor lifecycle and full1-1 route pass, but a direct empty-opening comparison
finds slower source actor updates. Downloads remains deliveredaa501.

`profile_steve_empty_native_1113.py` uses the ordinary menu and60-update
ingress controller. Measurements start at the first active CA00 execution,
excluding forced-blank startup. They distinguish walking from idle using the
actual SavedJoypadBits, count input polling separately, and assert no active
normal NPC in the window. No emulated state or level data is changed.

|Image|Walk updates/physical frames|Idle updates/physical frames|Frames without input poll|
|---|---:|---:|---:|
|Publicaa501|36/36|25/25|0|
|Private armor2aa509|36/54|25/36|0|

At nominal60Hz these samples correspond to60/60 source updates per second
for the parent and40/41.67 for the candidate. These are short, enemy-free
source-update cadence samples, not an all-stage performance or emulator lag
counter claim. Both end atX85/Y176 withHP6 and both lives.

Parent Lua SHA256:
`65cda0d5e637c55731f1dd97658e4d4532aa4b2af3e95de27e11cdab0d134f0d`

Parent receipt SHA256:
`af7574784c5dcabfaf56262b3e78459f440b1f7067e87a2c67a88ab8b07f338f`

Candidate Lua SHA256:
`97e45facdc43b2dac53c2f7e2a40a9e72ef627a52335162e50d35e7ba3642adb`

Candidate receipt SHA256:
`32727b04cff3b7c3976bac52208b83d18ef7ece249e301b18926c944987cbdb9`

Parent authentication checks its two owned banks,raw2/raw3. Armor additionally
ownsraw1, so its observer checks all three. Unused wave observers are removed
from both ingress cases to avoid binding new runtime addresses to old code.
An earlier parent observer incorrectly required the unowned raw1 header;
it failed at the first update before measurement. That observer error is
separate from the measured regression. The initial reporting code also hid
that negative receipt through division by zero; zero-sample rows now report
null rather than suppressing the underlying failure.

Root requested per-update cycle attribution and an inactive-armor fast path
from the owning source agent before further physical qualification. There
are no captures, backups or new build files. The existing candidate and Lua
are overwritten in the bounded two-file task root.

## Measured fast path

The explicit opt-in13-byte bridge fast path skips rejected raw1 pose and
wave-draw calls. Main and its protection/grant side effects are retained.
It fits the existing136-byte grant exactly. The unchanged row ordering
candidate is
`62ba7f54117875ec018d6f85fb1c74408aa11f0fe0f6a85b8b4f601034a17639`;
its packed payload fits with268bytes spare and raw1 remains1,912bytes.
This image is still private pending the remaining full qualifications.

Root's actual native cadence pass measures walk36updates/37physicalframes
and idle25/25, with input polling in all62 observed frames. Both lives,
HP6 and X85/Y176 remain. Total startup/ingress is809physicalframes. This
removes the large measured40Hz regression; the short walking sample still
has one extra physical frame and is not a zero-lag/all-stage claim.

Lua SHA256:
`604f3c3b2a4822380af815ce0e65a517bebbe3cc8a8c569377eb6d2147417e19`

Native receipt SHA256:
`aaa90ccb8083e7e6fe07d220d8fe2e3c229642771e6b6221b05446c380e4b05b`

The helper's paired CPU attribution reports a saving of1,409cycles per
update, with the Main service unchanged. Root owns the physical result;
the full fast-path ABI/interrupt/cold/armor gates remain with the source
agent before another unmodified full-stage and Downloads qualification.
