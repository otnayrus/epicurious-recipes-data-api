# cp /vagrant/provision/copymongokey.sh .
# ./copymongokey.sh
sudo mkdir /opt/mongo
sudo cp /vagrant/sources/mongo-keyfile /opt/mongo
sudo chmod 400 /opt/mongo/mongo-keyfile
sudo chown mongodb:mongodb /opt/mongo/mongo-keyfile