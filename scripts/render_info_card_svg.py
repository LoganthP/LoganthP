from __future__ import annotations

import os
from pathlib import Path


PALETTE = {
    "bg": "#050816",
    "primary": "#00F7FF",
    "secondary": "#2DD4BF",
    "text": "#D7F9FF",
}

ROWS = [
    ("Name", "Loganth"),
    ("Now", "Cybersecurity | AI | Full Stack"),
    ("Stack", "C/C++ | Python | Java | React | Node.js"),
    ("Cloud", "AWS | GCP | Docker | Kubernetes | Terraform"),
    ("Tools", "Git | GitHub | GitLab | Linux | Postman | n8n"),
    ("Connect", "loganthp19@gmail.com"),
]


def main() -> None:
    static = os.getenv("STATIC") == "1"
    width = 490
    height = 372
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Loganth profile info card">',
        f'<rect width="100%" height="100%" rx="10" fill="{PALETTE["bg"]}"/>',
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="none" stroke="{PALETTE["primary"]}" stroke-opacity="0.35"/>',
        f'<rect x="1" y="1" width="{width - 2}" height="38" rx="10" fill="{PALETTE["primary"]}" opacity="0.12"/>',
        f'<circle cx="24" cy="20" r="5" fill="#ff5f57"/><circle cx="43" cy="20" r="5" fill="#ffbd2e"/><circle cx="62" cy="20" r="5" fill="#28c840"/>',
        f'<text x="86" y="25" font-family="Consolas, Menlo, monospace" font-size="13" fill="{PALETTE["text"]}">loganthp-info-card</text>',
    ]
    for index, (label, value) in enumerate(ROWS):
        y = 78 + index * 45
        opacity = "1" if static else "0"
        lines.append(f'<g opacity="{opacity}" transform="translate(0,{8 if not static else 0})">')
        if not static:
            begin = 0.18 + index * 0.14
            lines.append(f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{begin:.2f}s" fill="freeze"/>')
            lines.append(f'<animateTransform attributeName="transform" type="translate" from="0 8" to="0 0" dur="0.4s" begin="{begin:.2f}s" fill="freeze"/>')
        lines.append(f'<text x="30" y="{y}" font-family="Consolas, Menlo, monospace" font-size="12" fill="{PALETTE["secondary"]}">{label}</text>')
        lines.append(f'<text x="118" y="{y}" font-family="Consolas, Menlo, monospace" font-size="13" fill="{PALETTE["text"]}">{value}</text>')
        lines.append(f'<line x1="30" y1="{y + 16}" x2="460" y2="{y + 16}" stroke="{PALETTE["primary"]}" stroke-opacity="0.12"/>')
        lines.append("</g>")
    lines.append(f'<text x="30" y="342" font-family="Consolas, Menlo, monospace" font-size="12" fill="{PALETTE["primary"]}">status: building secure intelligent systems</text>')
    lines.append("</svg>")
    Path("loganthp-info-card.svg").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
