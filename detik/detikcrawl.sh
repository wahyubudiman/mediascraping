#!/bin/bash
TODAY=$(date +"%Y%m%d")
export SCRAPYHOME=/opt/scrapy
export BERITAHOME=/opt/scrapy/wartaberita
export TOPIC=$1
export KEYWORDS=$2
echo $TOPIC
#echo $KEYWORDS
#echo $TODAY

echo "membuat direktori di hdfs untuk topic = $TOPIC"
sudo -u admin hdfs dfs -mkdir -p /analytic/sentimentanalysis/$TOPIC/detik

echo "proses crawling berdasarkan keyword $KEYWORDS"
source /opt/scrapy/bin/activate && cd $BERITAHOME/detik/ && scrapy crawl detik -a hashtag="$KEYWORDS" -o hsl$TOPIC$KEYWORDS$TODAY.json -t json >> $BERITAHOME/detik/log_$TODAY.log 2>&1

echo "upload into hdfs /analytic/sentimentanalysis/$TOPIC/detik"
sudo -u admin hdfs dfs -put $BERITAHOME/detik/hsl$TOPIC$KEYWORDS$TODAY.json /analytic/sentimentanalysis/$TOPIC/detik/.

echo "create database if not exists $TOPIC"
echo "" > detikraw.hql

cat <<EOT >> detikraw.hql
create database if not exists $TOPIC;
use $TOPIC;
create external table if not exists detik_raw (json string) location '/analytic/sentimentanalysis/$TOPIC/detik';

create table if not exists detik_stg
stored as parquet as
select
row_number() over () as id,
get_json_object(json,'$.title') as title,
get_json_object(json,'$.link') as link,
get_json_object(json,'$.category') as kategori,
get_json_object(json,'$.date') as tanggal,
get_json_object(json,'$.desc') as deskripsi
from detik_raw;

insert overwrite table detik_stg
select
row_number() over () as id,
get_json_object(json,'$.title') as title,
get_json_object(json,'$.link') as link,
get_json_object(json,'$.category') as kategori,
get_json_object(json,'$.date') as tanggal,
get_json_object(json,'$.desc') as deskripsi
from detik_raw;
EOT

echo "isi ulang detik tabel staging"
sudo -u admin hive -f detikraw.hql