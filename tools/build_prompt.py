"""Combine master block A with a plan-specific message into one prompt file."""
import re
import sys

PROJ = "/mnt/c/Projects/3d_visual/"


def build(msg_path, out_path):
    md = open(PROJ + "PROMPT_floorplan_3d.md", encoding="utf-8").read()
    a = re.search(r"## 1\. БЛОК A.*?```\n(.*?)```", md, re.S).group(1).strip()
    b = open(msg_path, encoding="utf-8").read().strip()
    head, rest = b.split("\n", 1)
    open(out_path, "w", encoding="utf-8").write(head + "\n\n" + a + "\n\n" + rest.strip() + "\n")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
