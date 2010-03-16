#!/usr/bin/bash

# This script generates a Gource video via ffmpeg - please feel free to hack on it!
# Note: You need a git repo!
# You can get it at: http://github.com/bingos/poe

# Processing the git repo as of March 16, 2010 results in a 1m8s long video clocking in at 41.1MB

if [ ! $1 ]
then
  echo "Please supply a path! ( make_gource.sh /home/apoc/git_repos )"
  exit
fi
cd $1

# Extra options we could use?
# --file-filter "/CVSROOT|/htmldocs|/wiki|/extras|/poexs|/queue|/docs"

gource poe/ -1280x720 -s 0.001 --highlight-all-users --multi-sampling \
  --user-image-dir poe/extras/gource/avatars/ --user-scale 1.5 \
  --disable-bloom --elasticity 0.0001 --max-file-lag 0.000001 --max-files 1000000 \
  --date-format "%B %d, %Y" --disable-progress --stop-on-idle \
  --output-ppm-stream - | ffmpeg -y -b 5000K -r 40 -f image2pipe -vcodec ppm -i - -vcodec mpeg4 gource_POE.mp4
