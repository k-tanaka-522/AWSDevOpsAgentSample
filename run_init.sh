#!/bin/bash
export PGPASSWORD="I95bBZazdIH5U9o2txZtAkWynvLOhMna"
psql -h xray-poc-02-database-rds.cj0qqo84wrtl.ap-northeast-1.rds.amazonaws.com -U postgres -d postgres -f init.sql
