#!/bin/bash
mysql -u root -p1q2w3e -h localhost -e "create database if not exists remento character set utf8 collate utf8_general_ci;"
mysql -u root -p1q2w3e -h localhost -e "create user 'remento'@'%' IDENTIFIED BY '1q2w3e'"
mysql -u root -p1q2w3e -h localhost -e "grant all privileges on remento.* to 'remento'@'%' with grant option;"
mysql -u root -p1q2w3e -h localhost -e "flush privileges;"
