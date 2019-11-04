#!/usr/bin/env bash

echo "Benchmark report" > reports/benchmark_report.txt
echo "--------------------" >> reports/benchmark_report.txt
i="0"
total=0
while [ $i -lt 5 ]
do
    start=`date +%s`
    python3 -m pytest -q tests/integration/
    end=`date +%s`
    runtime=$((end-start))
    total=$((total+runtime))
    i=$[$i+1]
    echo " - Time spent job $i: $runtime second(s)" >> reports/benchmark_report.txt
done

mean=$((total/5))
echo "--------------------" >> reports/benchmark_report.txt
echo "Total time spent ($i jobs): $total second(s)" >> reports/benchmark_report.txt
echo "Time spent per job: $mean second(s)" >> reports/benchmark_report.txt
echo "--------------------" >> reports/benchmark_report.txt