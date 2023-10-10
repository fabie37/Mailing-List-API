# Running the app in production
## Follow this guide https://www.rosehosting.com/blog/how-to-deploy-flask-application-with-nginx-and-gunicorn-on-ubuntu-20-04/

### Running as a service
```
gunicorn --bind 0.0.0.0:5000 wsgi:app

```

### Setting up systemmd Service File
```
vim /etc/systemd/system/flask.service
```

```
[Unit]
Description=Gunicorn instance to serve Flask
After=network.target
[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/Mailing-List-API
Environment="PATH=/home/ubuntu/Mailing-List-API/venv/bin"
ExecStart=sudo /home/ubuntu/Mailing-List-API/venv/bin/gunicorn --bind 0.0.0.0:5000 wsgi:app
[Install]
WantedBy=multi-user.target
```

```
chown -R ubuntu:www-data /home/ubuntu/Mailing-List-API
chmod -R 775 /home/ubuntu/Mailing-List-API
```

```
systemctl daemon-reload
systemctl start flask
systemctl enable flask
systemctl status flask
```

### Setting up nginx
```
vim /etc/nginx/conf.d/flask.conf
```

```
server {
    listen 80;
    server_name <yourdomainhere>.com;
    location / {
        include proxy_params;
        proxy_pass  http://127.0.0.1:5000;
    }
    server_name <yourdomain>.com www.<yourdomain>.com
}
```

```
nginx -t
```

```
systemctl restart nginx
```

### Installing SSL (Let's encrypt!)

using this tutorial https://www.nginx.com/blog/using-free-ssltls-certificates-from-lets-encrypt-with-nginx/

```
$ apt-get update
$ sudo apt-get install certbot
$ apt-get install python3-certbot-nginx
```

```
sudo certbot --nginx -d example.com -d www.example.com
```

```
$ crontab -e
```

```
0 12 * * * /usr/bin/certbot renew --quiet
```