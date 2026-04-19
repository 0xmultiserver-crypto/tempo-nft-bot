#!/usr/bin/env python3
"""
Tempo Turtlos - Auto Mint Bot (PUBLIC Phase Only)
Wait for PUBLIC phase, then mint
"""

import time
from eth_account import Account
from web3 import Web3

RPC_URL = "https://rpc.tempo.xyz"
CHAIN_ID = 4217
CONTRACT = "0x0D2bBDC50ccA675f4fD9A27b7e8997E18Dc57e0b"
PRIVATE_KEY = "YOUR_PRIVATE_KEY_HERE"

MINT_SIG = "ba41b0c6"

w3 = Web3(Web3.HTTPProvider(RPC_URL))
acct = Account.from_key(PRIVATE_KEY)

print(f"Wallet: {acct.address}")
print(f"Web3: {w3.is_connected()}")


def encode_mint_data(quantity, proof=None):
    if proof is None:
        proof = []
    data = MINT_SIG
    data += hex(quantity)[2:].zfill(64)
    data += "0000000000000000000000000000000000000000000000000000000000000040"
    data += hex(len(proof))[2:].zfill(64)
    for p in proof:
        if p.startswith("0x"):
            p = p[2:]
        data += p.zfill(64)
    return "0x" + data


def check_phase():
    """Check if PUBLIC phase is open by simulating mint"""
    data = encode_mint_data(1)
    try:
        result = w3.eth.call({
            'to': CONTRACT,
            'data': data
        })
        # If call succeeds without revert, PUBLIC is open
        return True, "Mint available"
    except Exception as e:
        error_str = str(e)
        if "Not WL" in error_str:
            return False, "Still WL/GTD phase"
        elif "Vault only" in error_str:
            return False, "Vault only - not public yet"
        elif "Exceeds Public cap" in error_str:
            # Public phase IS open, but cap reached - just wait for refill
            return True, "Public open but cap reached - waiting for refill"
        else:
            # Other error - might be public but other issue
            return False, f"Other error: {error_str[:50]}"


def try_mint_tx(quantity=3):
    """Execute the mint transaction"""
    try:
        nonce = w3.eth.get_transaction_count(acct.address)
        gas_price = w3.eth.gas_price
        
        data = encode_mint_data(quantity)
        
        tx = {
            'to': CONTRACT,
            'value': 0,
            'gas': 500000,
            'gasPrice': gas_price * 3,
            'nonce': nonce,
            'chainId': CHAIN_ID,
            'data': data,
        }
        
        signed = acct.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt['status'] == 1:
            return True, None, tx_hash.hex()
        else:
            return False, "tx_reverted", tx_hash.hex()
            
    except Exception as e:
        return False, str(e), None


def main():
    print("=" * 60)
    print("  Tempo Turtlos - PUBLIC Phase Mint Bot")
    print("=" * 60)
    print(f"Wallet:  {acct.address}")
    print(f"Contract: {CONTRACT}")
    print("=" * 60)
    
    attempt = 0
    phase_check_interval = 3  # Check phase every 3 seconds
    
    while True:
        attempt += 1
        print(f"\n[Attempt {attempt}] Checking phase... (minting 1 NFT)")
        
        is_public, status = check_phase()
        print(f"   Phase check: {status}")
        
        if is_public:
            print("\n🎉 PUBLIC PHASE IS OPEN! Executing mint...")
            
            # Try to mint
            success, error, tx_hash = try_mint_tx(3)
            
            if success:
                print(f"\n🎉 SUCCESS! Minted 3 NFTs!")
                print(f"   Tx: https://explore.tempo.xyz/tx/{tx_hash}")
                return
            else:
                print(f"   Mint failed: {error}")
                if tx_hash:
                    print(f"   Tx: https://explore.tempo.xyz/tx/{tx_hash}")
                # If mint failed, might still be checking - retry
                print("   Retrying in 10s...")
                time.sleep(10)
        else:
            # Still waiting for public
            print(f"   Waiting {phase_check_interval}s before next check...")
            time.sleep(phase_check_interval)


if __name__ == "__main__":
    main()