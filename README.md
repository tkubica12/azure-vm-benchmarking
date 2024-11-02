# Azure VM benchmarking
Simple guide to run few benchmarks to decide what VM SKU is best and what workload.

## Results
My results are [here](https://tkubica12.github.io/azure-vm-benchmarking/results_table.html)

## Testing
Configure ```config.yaml``` with SKUs to test.

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

Than fill in details in ```results.yaml``` and run ```calculate_table.py``` to generate results.