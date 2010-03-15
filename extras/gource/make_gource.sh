#!/usr/bin/bash

# This script generates a Gource vid via ffmpeg - please feel free to hack on it!
# Note: You need a git repo!
# You can get it at: http://github.com/bingos/poe

if [ ! $1 ]
then
  echo "Please supply a path! ( make_gource.sh /home/apoc/git_repos )"
  exit
fi
cd $1

gource poe/ -1280x720 -s 0.01 --auto-skip-seconds 0.1 --user-image-dir poe/extras/gource/avatars/ \
  --highlight-all-users --multi-sampling --file-filter "/CVSROOT|/htmldocs|/wiki|/extras|/poexs|/queue|/docs" \
  --stop-on-idle --output-ppm-stream - | \
  ffmpeg -y -b 3000K -r 24 -f image2pipe -vcodec ppm -i - -vcodec mpeg4 gource_POE.mp4
