from email.policy import default
from typing import Dict, List, Any

from fastapi import FastAPI, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3, HttpProvider


web3_provider = Web3(HttpProvider('http://127.0.0.1:8545'))


app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/send_tx", response_model=Dict[str, Any], summary="Send transaction to node")
async def send_transaction(
    to_address: str = Query(min_length=42, max_length=42, regex="^0x[0-9a-fA-F]*$", description='Address to send transaction'),
    data: str = Query(default='0x', regex="^0x[0-9a-fA-F]*$", description='Transaction input data'),
    value: int = Query(default=0, ge=0, description='Transaction eth value'),
) -> Dict[str, Any]:

    from_address = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8'
    private_key = '0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d'

    tx = {
        'nonce': web3_provider.eth.getTransactionCount(from_address),
        'to': web3_provider.toChecksumAddress(to_address),
        'value': value,
        'gas': 100000,
        'gasPrice': web3_provider.eth.gas_price,
        'chainId': web3_provider.eth.chainId,
        'data': data
    }
    try:
        gas_estimate = web3_provider.eth.estimateGas(tx)
        tx['gas'] = int(gas_estimate*2)
    except Exception as e:
        return {'tx_hash': '', 'error': str(e), 'status': False}
    
    signed_tx = web3_provider.eth.account.sign_transaction(tx, private_key)
    try:
        tx_hash = web3_provider.eth.send_raw_transaction(signed_tx.rawTransaction)
        return {'tx_hash': tx_hash, 'error': '', 'status': True}
    except Exception as e:
        return {'tx_hash': '', 'error': str(e), 'status': False}
