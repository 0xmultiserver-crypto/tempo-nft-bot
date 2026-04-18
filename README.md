# Tempo NFT Mint Bot

Auto-mint bot for NFT projects on Tempo chain - waits for PUBLIC phase before executing mint.

## Requirements

- Python 3.8+
- `web3` library
- `eth-account` library

```bash
pip install web3 eth-account
```

## Configuration

Edit `nftbot.py` and change these values:

### 1. PRIVATE_KEY
```python
PRIVATE_KEY = "YOUR_PRIVATE_KEY_HERE"  # Replace with your wallet private key
```

### 2. CONTRACT
```python
CONTRACT = "0x..."  # NFT contract address
```

### 3. MINT_SIG (if different)
```python
MINT_SIG = "ba41b0c6"  # mint(uint256, bytes32[]) function signature
```

Most Tempo NFT projects use `0xba41b0c6` for the mint function.

### 4. Quantity (optional)
Default is 1 NFT. To change:
```python
success, error, tx_hash = try_mint_tx(1)  # Change to 2, 3, etc.
```

### 5. RPC URL (optional)
Default is Tempo mainnet. For testnet:
```python
RPC_URL = "https://rpc.testnet.tempo.xyz"  # Testnet
CHAIN_ID = 4218  # Testnet chain ID
```

## Usage

```bash
python nftbot.py
```

The bot will:
1. Check if PUBLIC phase is open (every 30 seconds)
2. When PUBLIC opens, execute mint automatically
3. Bot stops after successful mint

## How It Works

- **Phase Check**: Uses `eth_call` to simulate mint transaction
- If call reverts with "Not WL" → still in WL/GTD phase, keep waiting
- If call succeeds → PUBLIC phase is open, execute mint
- Gas price: 3x current gas price for fast inclusion

## Find Contract Address

1. Go to NFT project mint page
2. Check browser DevTools → Network tab
3. Look for contract interactions in JavaScript
4. Or search on Tempo explorer

## Example

```python
# Tempo Turtlos (already configured)
CONTRACT = "0x0D2bBDC50ccA675f4fD9A27b7e8997E18Dc57e0b"
RPC_URL = "https://rpc.tempo.xyz"
CHAIN_ID = 4217
```

## Troubleshooting

- **"Not WL" error**: Wallet not whitelisted, need PUBLIC phase
- **"Vault only owner" error**: Contract not public yet
- **tx_reverted**: Mint failed, check contract requirements
- **Connection issues**: Check RPC URL and network connectivity