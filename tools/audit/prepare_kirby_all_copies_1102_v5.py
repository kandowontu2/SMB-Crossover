"""Current-ROM earned-copy batches, reusing the verified focused harness."""
import sys,argparse
from prepare_selected_native_packet_v1 import R

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--unit',choices=['copies-low','copies-high'],required=True);a=ap.parse_args()
    source=R/'tools/audit/prepare_kirby_current_native_1102_v4.py';text=source.read_text()
    text=text.replace("O=R/'build/kirby-current-native-1102-v4'",f"O=R/'build/kirby-{a.unit}-1102-v5'")
    needle="    space={'__name__':'kirby_current_packet','__file__':str(source)}"
    inject="""    anchor='    cfg=dict(ROM_sha256='
    assert text.count(anchor)==1
    text=text.replace(anchor,"    from current_kirby_meta_earned_cpu_v1 import plans\\n    plan=plans(UNIT,b)\\n    for i,task in enumerate(plan):task['image']=i<3\\n"+anchor)
"""
    assert text.count(needle)==1;text=text.replace(needle,inject+needle)
    text=text.replace("space['scoped_load']=lambda path:b","space['scoped_load']=lambda path:b\n    space['UNIT']=UNIT")
    text=text.replace("kw['allow_interactive']=True","kw['allow_interactive']=True\n        kw['scope']='Current Hard Kirby earned-copy batch '+UNIT+'; real inhale/Down/attack/Select cleanup. Disclosed native scene and effect-aligned target setup; no abilities or health seeded. Three PNG maximum. Not full1-1.'")
    text=text.replace("[*refs,Path(__file__),OLD", "[*refs,R/'tools/audit/prepare_kirby_all_copies_1102_v5.py',Path(__file__),OLD")
    exec(compile(text,str(source),'exec'),{'__name__':'__main__','__file__':str(source),'UNIT':a.unit})

if __name__=='__main__':main()
