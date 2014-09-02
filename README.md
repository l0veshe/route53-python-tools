先配置KEY
vim ~/.boto  
或者
vim /etc/boto

> [Credentials]

> aws_access_key_id = 

> aws_secret_access_key = 

然后执行rou53.py

python ./rou53.py --all ok
python ./rou53.py --short  ok
python ./rou53.py -I Z2GJJUHWQ6G8I4 -d blog2.aa-v.com:54.92.67.181 ok
python ./rou53.py -I Z2GJJUHWQ6G8I4 -d blog.aa-v.com:8.8.8.11,8.8.8.12,8.8.8.13 ok
python ./rou53.py -I Z2GJJUHWQ6G8I4 -c blog2.aa-v.com:54.92.67.181:A:300 ok 
python ./rou53.py -I Z2GJJUHWQ6G8I4 -c blog.aa-v.com:8.8.8.11,8.8.8.12,8.8.8.13:A:300 ok
python ./rou53.py -I Z2GJJUHWQ6G8I4 -u blog2.aa-v.com:54.92.67.181:A:300 -U blog2.aa-v.com:54.92.67.181:A:300 ok

如此操作，ok 忽略
