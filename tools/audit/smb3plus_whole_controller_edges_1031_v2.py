"""Repeat full boundary probe on the original gravity-hook placement."""
from pathlib import Path

R=Path(__file__).resolve().parents[2]


def main():
    prior=R/'tools/audit/smb3plus_whole_controller_edges_1031_v1.py';text=prior.read_text()
    text=text.replace('smb3plus-whole-controller-edges-1031-v1','smb3plus-whole-controller-edges-1031-v2')
    text=text.replace('smb3plus-peach-complete-controller-1031-v3','smb3plus-peach-gravity-consumer-1031-v1')
    ns={'__file__':str(Path(__file__).resolve()),'__name__':'private_gravity_consumer_edges'}
    exec(compile(text,str(prior),'exec'),ns);ns['main']()


if __name__=='__main__':main()
