# azure-vm-benchmarking

Testing

```bash
# Install Phoronix Test Suite
sudo apt update
sudo apt install -y php-cli php-xml unzip
wget https://github.com/phoronix-test-suite/phoronix-test-suite/releases/download/v10.8.4/phoronix-test-suite_10.8.4_all.deb
sudo dpkg -i phoronix-test-suite_10.8.4_all.deb

# Install tests
phoronix-test-suite install pts/nginx-3.0.1
phoronix-test-suite install pts/stockfish-1.6.0
phoronix-test-suite install pts/redis-1.4.0 

# Run tests
phoronix-test-suite benchmark pts/nginx-3.0.1         # use 500 connections
phoronix-test-suite benchmark pts/stockfish-1.6.0
phoronix-test-suite benchmark pts/redis-1.4.0         # Use SET and 50 connections
```



postgresql postgresql-contrib
cp $(which pgbench) .