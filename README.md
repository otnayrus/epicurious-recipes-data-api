# Epicurious' Recipes Collections
Sebuah implementasi API koleksi resep Epicurous yang ditulis dengan Python dengan penyimpanan berbasis klaster mongoDB

## Skema Infrastruktur

- Config Servers
    1. mongo-config-1
        - OS  : Ubuntu 18.04
        - RAM : 512 MB
        - CPUs: 1
        - IP  : 192.168.16.64
    2. mongo-config-2
        - OS  : Ubuntu 18.04
        - RAM : 512 MB
        - CPUs: 1
        - IP  : 192.168.16.65
- Query Router Server
    1. mongo-query-router
        - OS  : Ubuntu 18.04
        - RAM : 512 MB
        - CPUs: 1
        - IP  : 192.168.16.66
- Storage Servers
    1. mongo-shard-1
        - OS  : Ubuntu 18.04
        - RAM : 512 MB
        - CPUs: 1
        - IP  : 192.168.16.67
    2. mongo-shard-2
        - OS  : Ubuntu 18.04
        - RAM : 512 MB
        - CPUs: 1
        - IP  : 192.168.16.68
    2. mongo-shard-3
        - OS  : Ubuntu 18.04
        - RAM : 512 MB
        - CPUs: 1
        - IP  : 192.168.16.69  


## Konfigurasi MongoDB Cluster

### Konfigurasi File Hosts
Supaya setiap node bisa mengenali node lainnya, perlu ditambahkan alamat entitas member dari cluster pada file `/etc/hosts`. Konfigurasi ini dilakukan di setiap node.
```
$ cd /vagrant/provision
$ ./hosts.sh
```

### Membuat User Admin di Node Config
Pembuatan user admin dilakukan pada node primary dari set replika config.
Masuk ke shell mongo terlebih dahulu.
```
$ mongo
```
Gunakan database `admin`
```
use admin
```
Buat User Admin dengan hak akses `root`, ganti 'password' dengan password yang diinginkan.
```
db.createUser({user: "mongo-admin", pwd: "password", roles:[{role: "root", db: "admin"}]})
```

### Membuat Key File
Key file bisa dibuat dengan menjalankan command `openssl rand -base64 756` yang menghasilkan rangkaian kunci acak yang akan dipakai oleh semua node. Contoh hasil file tertera pada `sources/mongo-keyfile` pada repo ini.

Key file disebar ke semua node, dengan menjalankan script `provision/copymongokey.sh`


### Konfigurasi Server Config
Ubah file `/etc/mongod.conf` dengan alamat IP sesuai dengan node yang bersangkutan
```
port: 27019
bindIp: <192.168.16.64 atau 192.168.16.65>

replication:
  replSetName: configReplSet

sharding:
  clusterRole: "configsvr"
```
Restart `mongod` service untuk mengaplikasikan perubahan
```
$ sudo systemctl restart mongod
```
Untuk masuk sebagai admin pada node `mongo-config-1` bisa dilakukan sebagai berikut
```
$ mongo mongo-config-1:27019 -u mongo-admin -p --authenticationDatabase admin
```
Menginisialisasi set replika pada shell mongo di node config
```
rs.initiate( { _id: "configReplSet", configsvr: true, members: [ { _id: 0, host: "mongo-config-1:27019" }, { _id: 1, host: "mongo-config-2:27019" } ] } )
```

### Konfigurasi Query Router
Membuat file konfigurasi baru `/etc/mongos.conf` yang berisi
```
# where to write logging data.
systemLog:
  destination: file
  logAppend: true
  path: /var/log/mongodb/mongos.log

# network interfaces
net:
  port: 27017
  bindIp: 192.168.16.66

security:
  keyFile: /opt/mongo/mongodb-keyfile

sharding:
  configDB: configReplSet/mongo-config-1:27019,mongo-config-2:27019
```
Membuat systemd unit file `/lib/systemd/system/mongos.service` untuk `mongos`
```
[Unit]
Description=Mongo Cluster Router
After=network.target

[Service]
User=mongodb
Group=mongodb
ExecStart=/usr/bin/mongos --config /etc/mongos.conf
# file size
LimitFSIZE=infinity
# cpu time
LimitCPU=infinity
# virtual memory size
LimitAS=infinity
# open files
LimitNOFILE=64000
# processes/threads
LimitNPROC=64000
# total threads (user+kernel)
TasksMax=infinity
TasksAccounting=false

[Install]
WantedBy=multi-user.target
```
Supaya tidak terjadi konflik dengan `mongod`, pastikan `mongod` terhenti, kemudian jalankan `mongos`
```
$ sudo systemctl stop mongod
$ sudo systemctl enable mongos.service
$ sudo systemctl start mongos
```
### Menambahkan Shard ke Cluster
Menambahkan IP dan cluster role di setiap node pada `/etc/mongod.conf`
```
bindIp: <192.168.16.67 atau 192.168.16.68 atau 192.168.16.69>

sharding:
  clusterRole: "shardsvr"
```
Buka koneksi ke query router pada salah satu node shard
```
$ mongo mongo-query-router:27017 -u mongo-admin -p --authenticationDatabase admin
```
Melakukan registrasi node shard
```
sh.addShard( "mongo-shard-1:27017" )
sh.addShard( "mongo-shard-2:27017" )
sh.addShard( "mongo-shard-3:27017" )
```

### Konfigurasi Shard
Membuka koneksi ke node router untuk melakukan registrasi node yang dipakai untuk sharding.
```
$ mongo mongo-query-router:27017 -u mongo-admin -p --authenticationDatabase admin
```
Node router akan menggunakan informasi registrasi pada node config, jika sudah masuk, registrasi shard dilakukan dengan menambahkan line berikut.
```
sh.addShard( "mongo-shard-1:27017" )
sh.addShard( "mongo-shard-2:27017" )
sh.addShard( "mongo-shard-3:27017" )
```

### Mengaktifkan Sharding pada Level Collection
Membuka koneksi ke query router dari node shard. Pastikan semua node shard menjalankan service `mongod`
```
$ mongo mongo-query-router:27017 -u mongo-admin -p --authenticationDatabase admin
```
Melakukan beberapa konfigurasi pada shell mongo
```
use epicuriousDB

db.recipesCollection.ensureIndex( { _id : "hashed" } )

sh.shardCollection( "epicuriousDB.recipesCollection", { "_id" : "hashed" } )
```

## Membuat user untuk akses dari App
Proses ini dilakukan pada panel admin `mongos` router
```
$ mongo mongo-query-router:27017 -u mongo-admin -p --authenticationDatabase admin
```
Melakukan registrasi user pada database epicuriousDB
```
use epicuriousDB

db.createUser({user:"epic-user",pwd:"password",roles: [ "readWrite", "dbAdmin" ]})
```

## Memuat data dari dataset
Menjalankan script `factory.py` kemudian buka `localhost:5000` (default) pada browser untuk memuat data. File data diperoleh dari kaggle, pada script ini, lokasi data adalah pada `'../data/full_format_recipes.json'`.

Hasil loading dataset :

<img src="img/sharddist.jpg" alt="Distribusi Data pada Shard" width="450"/>

## Membuat koneksi dari App ke Database
Menggunakan `pymongo` sebagai driver penghubung antara aplikasi (Python-Flask) dengan Database (MongoDB), dengan menggunakan potongan script berikut
```
from flask import Flask
from flask_pymongo import PyMongo


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://epic-user:password@192.168.16.66:27017/epicuriousDB"
mongo = PyMongo(app, retryWrites=False)
```

## Referensi
- https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/
- https://www.linode.com/docs/databases/mongodb/build-database-clusters-with-mongodb/
