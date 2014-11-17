Chat Project
============
Anonymous Chat App

Requirements
-------------
1. RabbitMQ
2. Redis
3. Elastic Search
4. NodeJs
5. Python 2.7x

### Installation

Install Pip and Virtual Environment

    sudo apt-get install python-pip python-dev build-essential
    sudo apt-get install python-pip
    sudo pip install --upgrade pip
    sudo pip install --upgrade virtualenv

Install Pillow Requirements
    sudo apt-get install libjpeg62-dev zlib1g-dev libfreetype6-dev tcl8.5-dev tk8.5-dev python-tk
    
Install Npm and Bower Packages
    
    bower install
    cd node/
    npm install

Create a virtual env:

    virtualenv chatproject
    source chatproject/bin/activate

Clone the repository and install requirements:

    cd chatproject
    git clone git@github.com:bahattincinic/chat-project.git chatproject
    pip install -r chat-project/requirements/local.txt

Create local settings file and change default settings
    
    cd chatproject
    ln -s configs/dev.py settings.py

To run the project, Follow the following commands:

    cd chatproject/
    python manage.py syncdb
    python manage.py runserver && node node/server.js
