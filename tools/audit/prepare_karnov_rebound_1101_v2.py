"""Give post-BG its own private row; retain the real public bounce contract."""
from pathlib import Path
R=Path(__file__).resolve().parents[2]
O=R/'build/karnov-host-resource-base-1101-v1'


def once(t,a,b):
    assert t.count(a)==1,(a,t.count(a))
    return t.replace(a,b)


def prepare(resident,write):
    # Original table lease is exactly256B. One additional JMP spends3 of its
    # 34 trailing FF bytes and leaves all subsequent native addresses fixed.
    p=O/'megaman_physics.s'
    t=once(p.read_text(),'''::KrServiceVeneers:
  .repeat 36
    jmp ::KrDispatch
  .endrepeat
  .res $22,$ff''','''::KrServiceVeneers:
  .repeat 37
    jmp ::KrDispatch
  .endrepeat
  .res $1f,$ff''')
    write(p,t)
    resident=once(resident,' cmp #108\n bcs KrDispatchNo',' cmp #111\n bcs KrDispatchNo')
    p2=O/'hot_render_gate.s'
    t=once(p2.read_text(),' farcall KrServiceVeneers+81,jmp',' farcall KrServiceVeneers+108,jmp')
    write(p2,t)
    source=R/'tools/reference/karnov_host_rebound_1101_v2.inc'
    write(O/'kr-rebound.inc',source.read_text())
    return resident,[Path(__file__),source,O/'kr-rebound.inc',p,p2]
