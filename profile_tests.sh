#!/bin/sh

python -m cProfile -o profile $(which py.test)

python -c "import pstats; p = pstats.Stats('profile'); \
p.sort_stats('tottime').print_stats(64)"

rm -f profile




exit 0;
