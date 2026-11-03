"""Rebind unchanged smoke/route guards to final source39 publication owner."""
from pathlib import Path
import prepare_mini_mario_native_final_1103_v36 as P
from prepare_selected_native_packet_v1 import R,prepare
O=R/'build/mini-mario-native-packets-1103-v41'

def main():
    old_prepare,old_output=P.prepare,P.O
    def publish(output,rom,text,refs,**kw):
        name={'smoke35':'smoke41','full36':'full41'}[output.name]
        kw['scope']=kw['scope'].replace('graphics32 successor','publication39 successor')
        prepare(O/name,rom,text,[*refs,Path(__file__)],**kw)
    try:
        P.O=O;P.prepare=publish;P.main()
    finally:P.O=old_output;P.prepare=old_prepare

if __name__=='__main__':main()
