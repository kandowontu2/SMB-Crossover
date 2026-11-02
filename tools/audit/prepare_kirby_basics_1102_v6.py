"""Current earned Kirby healing, inflation, spit and slide regression packet."""
import sys
from prepare_selected_native_packet_v1 import R

def main():
    source=R/'tools/audit/prepare_kirby_all_copies_1102_v5.py'
    text=source.read_text()
    text=text.replace("choices=['copies-low','copies-high']", "choices=['basics']")
    text=text.replace("1102-v5", "1102-v6")
    text=text.replace("prepare_kirby_all_copies_1102_v5.py", "prepare_kirby_basics_1102_v6.py")
    text=text.replace("Current Hard Kirby earned-copy batch ", "Current Hard Kirby earned basics/healing batch ")
    sys.argv=[str(source),'--unit','basics']
    exec(compile(text,str(source),'exec'),{'__name__':'__main__','__file__':str(source)})

if __name__=='__main__':main()
