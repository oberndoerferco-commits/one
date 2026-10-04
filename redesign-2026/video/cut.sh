F=${FFMPEG:-ffmpeg}
# segments: start dur cropcentre(0..1 of height)
SEG="1.0 3.2 0.40|66.0 3.6 0.52|72.0 4.0 0.55|98.5 3.6 0.55"
build(){ # mode: land|port
  i=0; inputs=""; filt=""; cat=""
  IFS='|'; for s in $SEG; do IFS=' ' read st du cy <<< "$s"
    inputs="$inputs -ss $st -t $du -i v14-orig.mov"
    if [ "$1" = land ]; then
      y=$(python3 -c "print(max(0,min(3840-1215,int($cy*3840-607))))")
      filt="$filt[$i:v]crop=2160:1215:0:$y,scale=1920:1080:flags=lanczos,setpts=1.4*(PTS-STARTPTS),fps=30,format=yuv420p[v$i];"
    else
      filt="$filt[$i:v]scale=720:1280:flags=lanczos,setpts=1.4*(PTS-STARTPTS),fps=30,format=yuv420p[v$i];"
    fi
    cat="$cat[v$i]"; i=$((i+1)); done; IFS=' '
  eval $F -loglevel error -y $inputs -filter_complex "\"${filt}${cat}concat=n=$i:v=1:a=0[out]\"" -map "[out]" -an -c:v libx264 -preset slow -crf $2 -movflags +faststart $3
}
build land 23 obm-atelier-film-1920.mp4
