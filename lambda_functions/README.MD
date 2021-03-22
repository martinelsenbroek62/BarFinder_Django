###resize_image.py

Add virtual env in your vagrant box -> virtualenv -p /usr/local/bin/python3.6 .env
Activate virtualenv -> source .env/bin/activate
Install Pillow and pyexif 'pip install Pillow piexif'
Go to cd .env/lib/python3.6/site-packages/
Zip sitepackages zip -r9 /vagrant/lambda_functions/resize_image.zip *
Go back cd /vagrant/lambda_functions/
Add Your lambda to package zip -g resize_image.zip resize_image.py
Upload it to lambda console

###resize_notifier.py

Add virtual env in your vagrant box -> virtualenv -p /usr/local/bin/python3.6 .venv
Activate virtualenv -> source .venv/bin/activate
Install pyJWT and requests 'pip install pyJWT requests'
Go to cd .venv/lib/python3.6/site-packages/
Zip sitepackages zip -r9 /vagrant/lambda_functions/resize_notifier.zip *
Go back cd /vagrant/lambda_functions/
Add Your lambda to package zip -g resize_notifier.zip resize_notifier.py
Upload it to lambda console