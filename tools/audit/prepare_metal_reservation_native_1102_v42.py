"""Prepare controller-only Metal reservation and full-stage regression tests."""
import re
from pathlib import Path
from prepare_selected_native_packet_v1 import R, prepare, sha

O = R / 'build/metal-reservation-1102-v42'
ROM = O / 'candidate.nes'
P = R / 'build/metal-oam-order-1102-v2/native'
S = R / 'build/metal-storm-idle-shots-1101-v41'


def main():
    text = (P / 'controller.lua').read_text(encoding='utf-8')
    labels = {n: int(a, 16) for a, n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',
                                                 (O / 'component.lbl').read_text(), re.M)}
    for name in ['MsRenderDraw', 'MsRenderGraphics', 'MsRenderColors', 'MsEmitPacket', 'MsRBody']:
        text, count = re.subn(r'local ' + name + r'=\d+', f'local {name}={labels[name]}', text)
        assert count == 1, name
    marker = " orderCounts[name]=(orderCounts[name]or 0)+1"
    assert text.count(marker) == 1
    text = text.replace(marker, """
 assert((r('RgOamRotation')&3)==0,'Metal hardware OAM rotation must remain four-byte aligned')
 local p=r('SmPosePtr')+256*r('SmPosePtr',1)
 assert(p==L.ObjectMetasprite and emu.read(p,emu.memType.nesDebug)==0,'Stable native zero reservation pointer')
""" + marker)
    refs = [Path(__file__), O / 'assembly.json', O / 'component.s', O / 'component.lbl']
    prepare(O / 'native', ROM, text, refs + [P / 'controller.lua'], expected=sha(ROM),
            timeout=90, allow_interactive=True,
            scope='Actual cold menu, idle/walk, valid stable zero header and four-byte OAM rotation '
                  'at every observed Metal draw/reservation/native emission. Passive receipts and one PNG.')
    controller = S / 'route/controller.lua'
    text = controller.read_text(encoding='utf-8')
    # The retained route requires a genuine native defeat and active1-2 with
    # unchanged lives. Do not turn its historic success into current evidence.
    prepare(O / 'route', ROM, text, refs + [controller], expected=sha(ROM),
            timeout=120, allow_interactive=True,
            scope='Exact current successor, retained actual controller route, genuine native enemy defeat '
                  'and full1-1 to active1-2, unchanged lives; at most three PNGs, no writes/video.')


if __name__ == '__main__':
    main()
