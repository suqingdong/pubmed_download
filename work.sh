set -e

mkdir -p log

per=1000000

for n in $(seq 1 $per 34000000);do

limit=$(( $n + $per - 1 ))
out=${n}_${limit}

echo crawling $out

scrapy crawl pubmed_spider \
  -t jsonlines \
  -o $out.jsonl \
  --logfile log/$out.log \
  --loglevel INFO \
  -a start=$n \
  -a limit=$limit

oss -dir novo-diease/suqingdong/pubmed -up $out.jsonl
rm -f $out.jsonl

done