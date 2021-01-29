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
sudo -u admin hdfs dfs -mkdir -p /analytic/sentimentanalysis/$TOPIC/kompas

echo "proses crawling berdasarkan keyword $KEYWORDS"
source /opt/scrapy/bin/activate && cd $BERITAHOME/kompas/ && scrapy crawl kompas -a hashtag="$KEYWORDS" -o hsl$TOPIC$KEYWORDS$TODAY.json -t json >> $BERITAHOME/kompas/log_$TODAY.log 2>&1

echo "upload into hdfs /analytic/sentimentanalysis/$TOPIC/kompas"
sudo -u admin hdfs dfs -put $BERITAHOME/kompas/hsl$TOPIC$KEYWORDS$TODAY.json /analytic/sentimentanalysis/$TOPIC/kompas/.

echo "create database if not exists $TOPIC"
echo "" > kompasraw.hql

cat <<EOT >> kompasraw.hql
create database if not exists $TOPIC;
use $TOPIC;
create external table if not exists kompas_raw (json string) location '/analytic/sentimentanalysis/$TOPIC/kompas';

create table if not exists kompas_stg
stored as parquet as
select
row_number() over () as id,
get_json_object(json,'$.title') as title,
get_json_object(json,'$.link') as link,
get_json_object(json,'$.category') as kategori,
get_json_object(json,'$.date') as tanggal,
get_json_object(json,'$.desc') as deskripsi
from kompas_raw;

insert overwrite table kompas_stg
select
row_number() over () as id,
get_json_object(json,'$.title') as title,
get_json_object(json,'$.link') as link,
get_json_object(json,'$.category') as kategori,
get_json_object(json,'$.date') as tanggal,
get_json_object(json,'$.desc') as deskripsi
from kompas_raw;
EOT

echo "isi ulang kompas tabel staging"
sudo -u admin hive -f kompasraw.hql