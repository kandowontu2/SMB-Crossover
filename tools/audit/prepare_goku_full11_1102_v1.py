"""Current Goku full-stage discovery, selecting Arthur's actual alternate."""
import prepare_kirby_full11_1102_v7 as P
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location
from observe_chip_committed_write import lua

def main():
    P.O=R/'build/goku-full11-1102-v1'
    b=scoped_load(R/'build/kirby-approach-owner-1101-v3/candidate.nes');raw=P.ROM.read_bytes()
    edges={k:list(raw[location(b,'X5Menu'+k.title()):location(b,'X5Menu'+k.title())+33]) for k in ['left','right','up','down']}
    routes=[]
    for start in range(33):
        queue=[(start,[])];seen={start}
        for node,route in queue:
            if node==31:routes.append(route[0] if route else '');break
            for key,table in edges.items():
                nxt=table[node];assert 0<=nxt<33
                if nxt not in seen:seen.add(nxt);queue.append((nxt,route+[key]))
        else:raise AssertionError('Unreachable Arthur/Goku slot')
    def publish(output,rom,script,refs,**kwargs):
        replacements={
            "local C=assert(CURRENT_KIRBY_META_EARNED)":"local C=assert(CURRENT_KIRBY_META_EARNED)\nC.navigation="+lua(routes),
            "ROSTER_CONFIG={name='kirby'}":"ROSTER_CONFIG={name='goku'}",
            "r('SelectedCharacter')==13 and r('KbVariant')==0":"r('SelectedCharacter')==24",
            "Cold Kirby Hard without cheats":"Cold Goku Hard without cheats",
            "if r('KbVariant')~=C.variant then":"if r('SelectedCharacter')~=24 then",
            "char=13,variant=0":"char=24,variant=0",
            "health=r('KbHealth'),copy=r('KbCopy'),mouth=r('KbMouth')":"character=r('SelectedCharacter'),player_status=r('PlayerStatus')"
        }
        for old,new in replacements.items():assert script.count(old)==1,old;script=script.replace(old,new)
        kwargs['scope']='Current Goku Hard controller-only natural1-1 discovery via Arthur Select alternate. Existing native helper actors retained; no state/ability/health seeds. One endpointPNG and bounded input CSV. Success requires active1-2 without life loss.'
        return prepare(output,rom,script,[*refs,Path(__file__),R/'build/kirby-approach-owner-1101-v3/candidate.dbg'],**kwargs)
    P.prepare=publish;P.main()

if __name__=='__main__':main()
