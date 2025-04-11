import asyncio
import sys
import loguru
from curl_cffi.requests import AsyncSession
from eth_account.messages import encode_defunct
from web3 import AsyncWeb3

logger = loguru.logger
logger.remove()
logger.add(sys.stdout, colorize=True, format="<g>{time:HH:mm:ss:SSS}</g> | <level>{message}</level>")


class Mmbot:
    def __init__(self, private_key: str):
        self.client = AsyncSession(timeout=120, impersonate="chrome120")
        self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider('https://arbitrum.blockpi.network/v1/rpc/public'))
        self.account = self.w3.eth.account.from_key(private_key)



    async def Login(self):
        try:
            sig_msg = f'Login'
            signature = self.account.sign_message(encode_defunct(text=sig_msg)).signature.hex()
            json_data = {
                "address": self.account.address,
                "invite_code":"tfWrNPrW",
                "signature": signature,
                "message": "Login"
            }
            res = await self.client.post("https://api.mmbot.org/api/user/login", json=json_data)
            if res.json()['code'] == 1:
               self.client.headers.update({"Authorization": f"{res.json()['data']['token']}"})
               logger.success(f"【{self.account.address}】登录成功")
               return await self.Mint()
            else:
               logger.error(f"【{self.account.address}】登录失败")
               return False
        except Exception as e:
            logger.error(f"注册出现异常: {e}")
            return False 
            
    async def Mint(self):
        try:
            res = await self.client.post("https://api.mmbot.org/api/index/startup")
            if res.status_code == 200:
               logger.success(f"【{self.account.address}】启动成功:{res.text}")
            else:
               logger.error(f"【{self.account.address}】启动失败")
               return False
            return True
        except Exception as e:
            logger.error(f"[{self.wallet_address}] 启动异常: {e}")
            return True      


async def do(semaphore, private_key):
    async with semaphore:
        for _ in range(3):
            if await Mmbot(private_key).Login():
                break

async def main(filePath, thread):
    semaphore = asyncio.Semaphore(int(thread))
    tasks = []
    with open(filePath, 'r') as f:
        for account_line in f:
            tasks.append(do(semaphore, account_line.strip()))
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main("addresses.txt", 1))
