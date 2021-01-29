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
sudo -u admin hdfs dfs -mkdir -p /analytic/sentimentanalysis/$TOPIC/tribun

echo "proses crawling berdasarkan keyword $KEYWORDS"
source /opt/scrapy/bin/activate && cd $BERITAHOME/tribun/ && scrapy crawl tribun -a hashtag="$KEYWORDS" -o hsl$TOPIC$KEYWORDS$TODAY.json -t json >> $BERITAHOME/tribun/log_$TODAY.log 2>&1

echo "upload into hdfs /analytic/sentimentanalysis/$TOPIC/tribun"
sudo -u admin hdfs dfs -put $BERITAHOME/tribun/hsl$TOPIC$KEYWORDS$TODAY.json /analytic/sentimentanalysis/$TOPIC/tribun/.

echo "create database if not exists $TOPIC"
echo "" > tribunraw.hql

cat <<EOT >> tribunraw.hql
create database if not exists $TOPIC;
use $TOPIC;
create external table if not exists tribun_raw (json string) location '/analytic/sentimentanalysis/$TOPIC/tribun';

create table if not exists tribun_stg
stored as parquet as
select
row_number() over () as id,
get_json_object(json,'$.title') as title,
get_json_object(json,'$.link') as link,
get_json_object(json,'$.category') as kategori,
get_json_object(json,'$.date') as tanggal,
get_json_object(json,'$.desc') as deskripsi
from tribun_raw;

insert overwrite table tribun_stg
select
row_number() over () as id,
get_json_object(json,'$.title') as title,
get_json_object(json,'$.link') as link,
get_json_object(json,'$.category') as kategori,
get_json_object(json,'$.date') as tanggal,
get_json_object(json,'$.desc') as deskripsi
from tribun_raw;
EOT

echo "isi ulang tribun tabel staging"
sudo -u admin hive -f tribunraw.hql