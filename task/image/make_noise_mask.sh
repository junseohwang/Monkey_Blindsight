#!/usr/bin/env bash
set -euo pipefail

SRC="${1:-noise_mask.png}"
OUT_LEFT="${2:-noise_mask_left.png}"
OUT_RIGHT="${3:-noise_mask_right.png}"

# check tools
command -v identify >/dev/null || { echo "ImageMagick (identify) not found"; exit 1; }
command -v convert >/dev/null || { echo "ImageMagick (convert) not found"; exit 1; }

# get size
W=$(identify -format "%w" "$SRC")
H=$(identify -format "%h" "$SRC")
echo "Source: $SRC  (${W}x${H})"

# split width (floor for odd widths)
HALF=$(( W / 2 ))
echo "Half width: $HALF px"

# make alpha masks (white=opaque, black=transparent)
# left mask: left half white, right half black
convert -size "${W}x${H}" xc:black -fill white \
  -draw "rectangle 0,0 $((HALF-1)),$((H-1))" /tmp/_mask_left.png

# right mask: left half black, right half white
convert -size "${W}x${H}" xc:black -fill white \
  -draw "rectangle ${HALF},0 $((W-1)),$((H-1))" /tmp/_mask_right.png

# apply masks to the full-noise image -> per-pixel alpha
convert "$SRC" /tmp/_mask_left.png  -compose CopyOpacity -composite "$OUT_LEFT"
convert "$SRC" /tmp/_mask_right.png -compose CopyOpacity -composite "$OUT_RIGHT"

rm -f /tmp/_mask_left.png /tmp/_mask_right.png
echo "Wrote: $OUT_LEFT, $OUT_RIGHT"

