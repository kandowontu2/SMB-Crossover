"""Locate original float state producers in complete updates."""
from pathlib import Path

R=Path(__file__).resolve().parents[2]


def main():
    prior=R/'tools/audit/smb3plus_whole_controller_probe_1031_v2.py';text=prior.read_text()
    text=text.replace("O=R/'build/smb3plus-whole-controller-probe-1031-v2'",
        "O=R/'build/smb3plus-whole-controller-writes-1031-v1'")
    text=text.replace('itertools.product([2,3],range(7),[0,1],[0,128],[0,5,224,70])',
        '[(3,0,1,128,224),(3,3,1,128,0),(3,4,1,128,0)]')
    text=text.replace('path=[]','path=[];events=[]')
    text=text.replace('            cpu.step()', '''            observed=[0xa2,0xcf,0xee,0xd8,0x7ae4,0x7ae5,0x7ae6,0x7ae7]
            before=[bus.ram[at] for at in observed]
            cpu.step()
            changed=[dict(at=at,before=was,after=bus.ram[at]) for at,was in zip(observed,before) if was!=bus.ram[at]]
            if changed:events.append(dict(bank=bank,PC=path[-1][1],writes=changed))''')
    text=text.replace("source_ready=bus.ram[0x7ae7],source_VY=bus.ram[source['Player_YVel']]))",
        "source_ready=bus.ram[0x7ae7],source_VY=bus.ram[source['Player_YVel']],source_events=events))")
    ns={'__file__':str(Path(__file__).resolve()),'__name__':'private_controller_writes'}
    exec(compile(text,str(prior),'exec'),ns);ns['main']()


if __name__=='__main__':main()
