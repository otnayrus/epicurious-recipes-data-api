# Add hostname
sudo bash -c \\"echo '192.168.64.1 mongo-config-1' >> /etc/hosts\\"
sudo bash -c \\"echo '192.168.64.2 mongo-config-2' >> /etc/hosts\\"
sudo bash -c \\"echo '192.168.64.3 mongo-query-router' >> /etc/hosts\\"
sudo bash -c \\"echo '192.168.64.4 mongo-shard-1' >> /etc/hosts\\"
sudo bash -c \\"echo '192.168.64.5 mongo-shard-2' >> /etc/hosts\\"
sudo bash -c \\"echo '192.168.64.6 mongo-shard-3' >> /etc/hosts\\"

# Copy APT sources list
sudo cp /vagrant/sources/sources.list /etc/apt/
sudo cp /vagrant/sources/mongodb-org-4.2.list /etc/apt/sources.list.d/

# Add MongoDB repo key
sudo apt-get install gnupg
wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -

# Update Repository
sudo apt-get update
# sudo apt-get upgrade -y

# Install MongoDB
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo service mongod start