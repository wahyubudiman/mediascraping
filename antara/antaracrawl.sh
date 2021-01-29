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
sudo -u admin hdfs dfs -mkdir -p /analytic/sentimentanalysis/$TOPIC/antara

echo "proses crawling berdasarkan keyword $KEYWORDS"
source /opt/scrapy/bin/activate && cd $BERITAHOME/antara/ && scrapy crawl antara -a hashtag="$KEYWORDS" -o hsl$TOPIC$KEYWORDS$TODAY.json -t json >> $BERITAHOME/antara/log_$TODAY.log 2>&1

echo "upload into hdfs /analytic/sentimentanalysis/$TOPIC/antara"
sudo -u admin hdfs dfs -put $BERITAHOME/antara/hsl$TOPIC$KEYWORDS$TODAY.json /analytic/sentimentanalysis/$TOPIC/antara/.

echo "create database if not exists $TOPIC"
echo "" > antararaw.hql

cat <<EOT >> antararaw.hql
create database if not exists $TOPIC;
use $TOPIC;
create external table if not exists antara_raw (json string) location '/analytic/sentimentanalysis/$TOPIC/antara';

create table if not exists antara_stg
stored as parquet as
select
row_number() over () as id,
get_json_object(json,'$.title') as title,
get_json_object(json,'$.link') as link,
get_json_object(json,'$.category') as kategori,
get_json_object(json,'$.date') as tanggal,
get_json_object(json,'$.desc') as deskripsi
from antara_raw;

insert overwrite table antara_stg
select
row_number() over () as id,
get_json_object(json,'$.title') as title,
get_json_object(json,'$.link') as link,
get_json_object(json,'$.category') as kategori,
get_json_object(json,'$.date') as tanggal,
get_json_object(json,'$.desc') as deskripsi
from antara_raw;
EOT

echo "isi ulang antara tabel staging"
sudo -u admin hive -f antararaw.hql