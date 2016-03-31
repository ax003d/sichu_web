# Sichu Web Application

![Image of travis-ci](https://travis-ci.org/ax003d/sichu_web.svg?branch=master)

## Introduction

This is an application that you can manage your own books, and it enables you to share your books with your friends.
You can visit it on: http://sichu.sinaapp.com

## Run local

Generally speaking, this is a django application, to run local, you should have some basic knowledge about django.

You have to install git, python2.7, virtualenv, pip, mysql in your local OS.

Then follow commands below. (Assume that your local MySQL Server's user and password is root/root).
```
$ mysql -u root -proot -e "create database sichu default character set utf8;"
$ cd ~/workspace
$ git clone git@github.com:ax003d/sichu_web.git
$ virtualenv ~/workspace/env-sichu
$ source ~/workspace/env-sichu/bin/activate
$ cd sichu_web
$ pip install -r requirements.txt
$ cd sichu
$ python manage.py syncdb
$ python manage.py migrate
$ python manage.py runserver
```
Open your browser and visit http://127.0.0.1:8000.
