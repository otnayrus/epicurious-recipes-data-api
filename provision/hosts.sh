# Add hostname
sudo bash -c "echo '192.168.16.64 mongo-config-1' >> /etc/hosts"
sudo bash -c "echo '192.168.16.65 mongo-config-2' >> /etc/hosts"
sudo bash -c "echo '192.168.16.66 mongo-query-router' >> /etc/hosts"
sudo bash -c "echo '192.168.16.67 mongo-shard-1' >> /etc/hosts"
sudo bash -c "echo '192.168.16.68 mongo-shard-2' >> /etc/hosts"
sudo bash -c "echo '192.168.16.69 mongo-shard-3' >> /etc/hosts"
