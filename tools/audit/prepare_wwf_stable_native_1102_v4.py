"""Allow the already-reached native flagpole/castle sequence to finish."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/wwf-helper-stable-1102-v2'
def main():
    source=O/'native-hogan2/controller.lua'
    text=source.read_text()
    for old,new in [('age>=10500','age>=18000'),('frame>=11500','frame>=19000'),('#trace<80','#trace<130')]:
        assert text.count(old)==1;text=text.replace(old,new)
    rom=O/'candidate2.nes'
    prepare(O/'native-hogan3',rom,text,[Path(__file__),source,O/'native-hogan2/capture/result.json',O/'native-hogan2/capture/helper-contact.json'],
        expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Same controls/ROM/helpers; prior run reached castle engine5 lives2to2 and72 actualnativecarry calls but hit wall-frame bound. Extend terminal wait only; retain genuine active1-2/no-life-loss completion requirement.')
if __name__=='__main__':main()
