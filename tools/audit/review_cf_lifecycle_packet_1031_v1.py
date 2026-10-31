"""Root rehash of the exact frozen CF scene/life/presentation packet."""
from pathlib import Path

R=Path(__file__).resolve().parents[2]


def main():
    prior=R/'tools/audit/review_cf_followup_packets_1031_v1.py';text=prior.read_text()
    a=text.index('PACKETS=');z=text.index('\n\n\n',a)
    text=text[:a]+"PACKETS=[('contra-force-lifecycle-qualified-v1','141b7abeb5af5603cde8e5894e4a9cfb7453e69c959b664d05f9808bb450048e',7555,61)]"+text[z:]
    text=text.replace('cf-followup-root-review-v1','cf-lifecycle-root-review-v1')
    ns={'__file__':str(Path(__file__).resolve()),'__name__':'private_root_lifecycle_rehash'}
    exec(compile(text,str(prior),'exec'),ns);ns['main']()


if __name__=='__main__':main()
