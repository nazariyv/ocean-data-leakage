source scripts/catch-errors.sh

printOcean() {
    # if 100 is cols
    # then $1 is int((cols * $1) / 100)
    # takes number from 0 to 100. 30 means that 30% of the width of the terminal will be ocean
    cols=$(tput cols)
    # ocean=$(echo "$cols * $1 * 0.01 * 0.5" | bc)
    ocean=$(echo "$cols * $1 * 0.005" | bc)  # not the above, because wave takes space of two chars
    printf %"$ocean"s"\n" | tr " " "🌊"
}
