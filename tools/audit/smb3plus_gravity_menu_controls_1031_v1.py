"""Retest all four names/Start and foreign menus on the gravity successor."""
from pathlib import Path

R=Path(__file__).resolve().parents[2]


def main():
    prior=R/'tools/audit/smb3plus_menu_controls_1031_v1.py';text=prior.read_text()
    text=text.replace("O=R/'build/smb3plus-menu-host-1031-v4'",
        "O=R/'build/smb3plus-peach-gravity-consumer-1031-v1'")
    text=text.replace("stage['status_names'][variant]","['MARIO3 ','LUIGI3 ',' TOAD3 ',' PEACH3'][variant]")
    ns={'__file__':str(Path(__file__).resolve()),'__name__':'private_gravity_menu_controls'}
    exec(compile(text,str(prior),'exec'),ns);ns['main']()


if __name__=='__main__':main()
