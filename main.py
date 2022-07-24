from email.policy import default
from typing import Dict, List, Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3, HTTPProvider


web3_provider = Web3(HTTPProvider('https://polygon-mainnet.g.alchemy.com/v2/KuObbYiGCpdKUC15mfrpwX0YzX2W3yna'))

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/send_tx", summary="Send transaction to node")
async def send_transaction(
    to_address: str = Query(min_length=42, max_length=42, regex="^0x[0-9a-fA-F]*$", description='Address to send transaction'),
    data: str = Query(default='0x', regex="^0x[0-9a-fA-F]*$", description='Transaction input data'),
    value: int = Query(default=0, ge=0, description='Transaction eth value'),
) -> Dict[str, Any]:

    from_address = '0x95C527C91E53B04e10E8Abcdf5fd89f1213E4479'
    private_key = ''

    tx = {
        'from': from_address,
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
        print({'tx_hash': '', 'error': str(e), 'status': 'Can not estimate gas'})
    signed_tx = web3_provider.eth.account.sign_transaction(tx, private_key)
    try:
        tx_hash = web3_provider.eth.send_raw_transaction(signed_tx.rawTransaction).hex()
        return {'tx_hash': tx_hash, 'error': '', 'status': True}
    except Exception as e:
        return {'tx_hash': '', 'error': str(e), 'status': False}
