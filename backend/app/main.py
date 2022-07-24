from typing import Dict, List, Any
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3, HTTPProvider
from structlog import get_logger
from backend.abi import registry_abi

logger = get_logger()


web3_provider = Web3(HTTPProvider('https://polygon-mainnet.g.alchemy.com/v2/KuObbYiGCpdKUC15mfrpwX0YzX2W3yna'))
registry_contract = web3_provider.eth.contract(address='0x5dA678a2f59A78d004E0E11c8652C33e3Ab7fA60', abi=registry_abi)

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
        'gas': 10_000_000,
        'gasPrice': web3_provider.eth.gas_price,
        'chainId': web3_provider.eth.chainId,
        'data': data
    }
    try:
        gas_estimate = web3_provider.eth.estimateGas(tx)
        tx['gas'] = int(gas_estimate*1.2)
    except Exception as e:
        logger.error('Can not estimate gas', error=str(e))
    signed_tx = web3_provider.eth.account.sign_transaction(tx, private_key)
    try:
        tx_hash = web3_provider.eth.send_raw_transaction(signed_tx.rawTransaction).hex()
        return {'tx_hash': tx_hash, 'error': '', 'status': True}
    except Exception as e:
        return {'tx_hash': '', 'error': str(e), 'status': False}


@app.get("/registry/get_info", summary="Get registry info")
async def get_registry_info(
    address: str = Query(min_length=42, max_length=42, regex="^0x[0-9a-fA-F]*$", description='Address to get info')
) -> Dict[str, Any]:
    info = registry_contract.functions.recordOf(web3_provider.toChecksumAddress(address)).call()
    return {'metaPipeAddress': info[0], 'deadlineAt': info[1], 'gasLeft': info[2]}