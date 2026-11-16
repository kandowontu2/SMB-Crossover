# Sonic ceiling repair: independent source components

Public Downloads remains verified1327. Neither proposed Sonic image has
been written to a ROM file, launched in Mesen or delivered.

The first80-byte imagef7 fixes the real hidden5F/60 rejection. Root's executed
classifier component passes274432 cases, receipt
`2eda2c621f4ad131088ef6f344102721215c0bfa3e21198698a1ddc0607fcee1`.
Tool `check_sonic_hidden_leaf_abi_root_1116.py` SHA256
`3b041ec39b0ae3be02a4fdf504399b95ef8f242c917ba71e9e9a89f7c44ec8b0`.
All266240 nonhidden cases retain AXYP/SP/target exactly with six extra
cycles;512 upward hidden cases reach original stage,7680 other hidden
cases reach original EmptyCell. The actual stage SEC/LDA kills transient
A/C/N/Z. All256 stack bytes remain exact, with zero RAM/SMC/mapper writes.
These are explicit flat6502 ABI fixtures, not natural play or interrupt proof.

Later source execution found f7's head stop was incomplete: the original
held-jump timer reasserted negative VY on the next update. Actual writer
receipt902a4915 binds Timer6 and the original A505 store. The original motor
is unchanged; its own Suppress path clears the hold flag once Timer is zero.
The complete94-byte a2 proposal therefore adds one existing kind4 Pending
store hook and an11-byte helper that repeats Pending1, clears existing
C058 Timer, restores A1 and returns. It leaves all5526 original motor bytes
and all direct flags unchanged.

Root static review `audit_sonic_ceiling_plan_root_1116.py`, SHA256
`7acb477fb51588adc989220f87463ff5cf6713c0f26883b1e4ca069f4e9e0db2`,
passes receipt5ed119b5650d549ba2ed71f7554f22c57bdd107606ebc0a334d1742b9afaded6.
The actual kind4/A1 domination, declared tail funding, old-hook ingress and
new-tail literal/writer census are bound. This is source-bound review,
not arbitrary-pointer exclusion. The new immutable source lease is
`allocations/sonic-ceiling-source-root-1116.json`, SHA c4d913a2.

Root executes the complete actual-a2 caller component with
`check_sonic_ceiling_abi_root_1116.py`, SHA256
`50d0394d44a9bfd5fce7056d759c8e035d4285e60e71c796ddee05a697e686d9`.
Receipt:
`ecbb13b207c043910d44dd436043c96d334e82e71d588a3086b0239675e47d49`.
The65536 cases cover all256 Timer values,32 flag fixtures, two X/Y pairs,
two stack positions including wrap, and two Pending values. AXYP/SP and
every live caller-stack byte are exact. Only the two known dead JSR return
bytes and intended Pending1/Timer0 are written. The ceiling path costs20
extra cycles and two transient stack bytes. No new state is allocated.

The a2 classifier also executes1072 tile/direction cases. Its19 entry bytes
and45 helper bytes exactly match the versionedf7 component; the earlier
274432-case result remains explicitly versioned. New a2 code is
`a2d9d1218504dedf186cfe352ee4c927160529af4f8d09fe6e2aafccfae477c7`,
94 owned/91 changed bytes over1327. Its composer c4456eb7 and facade13b1050e
execute actual a2;1327 supplies symbols only. Guard/lifecycle, IRQ/busy-NMI,
natural pickups, sustained ceiling behavior, full stages and native promotion
remain separate gates. No frame-rate improvement is claimed.

All three root components use their exact absent bounded output roots,
max1/600 seconds, with zero generated files. The single native queue remains
owned by root; existing Downloads and the shared candidate remain1327.
