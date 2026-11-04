#!/usr/bin/env bash
# Render the "Al ogive + Cu liner" 3D views of lnl_target_design.html to JPEGs for the slides (headless Chrome, WebGL via SwiftShader).
#   bash lnl/viz/render_culiner_shots.sh            → lnl/out/target/culiner_pf/*.jpg
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); OUT=$HERE/../out/target/culiner_pf; mkdir -p "$OUT"
TMP=$(mktemp -d); PORT=8766
python3 -m http.server $PORT -d "$HERE" >/dev/null 2>&1 & SRV=$!; trap 'kill $SRV; rm -rf "$TMP"' EXIT; sleep 1
for v in d:design d:tip d:explode d:his b:shell b:etch b:cu b:li b:beam; do
  n=${v/:/_}
  timeout 90 google-chrome --headless=new --no-sandbox --use-angle=swiftshader --enable-unsafe-swiftshader --hide-scrollbars \
    --window-size=1600,$([[ $v == b:* ]] && echo 690 || echo 1000) --virtual-time-budget=7000 --screenshot="$TMP/$n.png" \
    "http://localhost:$PORT/lnl_target_design.html?shot=$v" >/dev/null 2>&1
  ~/PycharmProjects/nTof_x17/.venv/bin/python -c "from PIL import Image; Image.open('$TMP/$n.png').convert('RGB').save('$OUT/$n.jpg', quality=86)"
done
ls -la "$OUT"
