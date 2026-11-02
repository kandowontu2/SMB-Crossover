"""Use the same native helper route for each remaining real menu alternate."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/wwf-helper-stable-1102-v2'
def main():
    source=O/'native-hogan3/controller.lua';original=source.read_text();rom=O/'candidate2.nes'
    for variant in range(1,6):
        text=original
        before="local actions={'right','right','right','right','up'}"
        after="local actions={"+','.join(repr(v) for v in ['right']*4+['up']+['select']*variant)+'}'
        assert text.count(before)==1;text=text.replace(before,after)
        before="r('FmGroups')&7==0";assert text.count(before)==1
        text=text.replace(before,f"r('FmGroups')&7=={variant}")
        text=text.replace('HULK HOGAN',f'WWF VARIANT {variant}')
        prepare(O/f'native-wwf-{variant}',rom,text,[Path(__file__),source,O/'native-hogan3/capture/result.json'],
            expected=sha(rom),timeout=240,allow_interactive=True,
            scope=f'Actual WWF alternate{variant} selected through menu Select presses, same nativehelper/controller route, exact identity and active1-2 with no-life-loss required. OnePNG and aggregate helper carrying; no state writes.')
if __name__=='__main__':main()
