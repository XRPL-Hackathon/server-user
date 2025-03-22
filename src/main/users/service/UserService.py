from xrpl.clients import JsonRpcClient
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.models.requests import AccountInfo
from xrpl.utils import xrp_to_drops
from src.main.users.repository.UserRepository import UserRepository
import boto3
import os
from src.main.users.dto.UserInfoDto import UserInfoResponse
from dotenv import load_dotenv

load_dotenv()

TESTNET_URL = "https://s.altnet.rippletest.net:51234"
client = JsonRpcClient(TESTNET_URL)
class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        if os.environ.get('ENV') == 'local-profile':
            self.cognito_client = boto3.client(
                'cognito-idp',
                region_name=os.environ.get('AWS_REGION', 'ap-northeast-2'),
                profile_name=os.environ.get('AWS_PROFILE', 'default')
            )
        else:
            self.cognito_client = boto3.client(
                'cognito-idp',
                region_name=os.environ.get('AWS_REGION', 'ap-northeast-2')
            )
            self.user_pool_id = os.environ.get('COGNITO_USER_POOL_ID', '')
    
    def get_wallets(self, user_id: str):
        wallets = self.user_repository.find_wallets_by_user_id(user_id)
        if not wallets:
            return {"message": "No wallets found for this user"}
        return wallets
    
    async def generate_wallet(self, user_id: str):
        wallet = await generate_faucet_wallet(client=client, debug=True)
        wallet_address = wallet.classic_address
        result = self.user_repository.save_wallet(user_id, wallet_address)
        return result
    
    def get_account_info(self, client: JsonRpcClient, address: str, **kwargs) -> dict:
        """
        XRPL 네트워크에서 이 계정의 정보를 가져옵니다.

        Args:
            client (JsonRpcClient): 요청을 보낼 클라이언트입니다.
            address (str): 계정 정보를 조회할 계정의 주소입니다.
            **kwargs: 추가적인 선택적 매개변수들입니다.

        Returns:
            dict: 이 계정의 정보를 포함하는 딕셔너리 객체입니다.
        """
        return client.request(AccountInfo(account=address, **kwargs))
        
    def get_user_info(self, user_id: str) -> UserInfoResponse:
        # Cognito에서 nickname 조회
        nickname = "Unknown"
        try:
            if self.user_pool_id:
                # Cognito 사용자 풀에서 사용자 정보 조회
                response = self.cognito_client.list_users(
                    UserPoolId=self.user_pool_id,
                    Filter=f'sub = "{user_id}"'
                )
                
                if response.get('Users') and len(response['Users']) > 0:
                    # 사용자의 속성에서 nickname 찾기
                    for attr in response['Users'][0].get('Attributes', []):
                        if attr['Name'] == 'nickname':
                            nickname = attr['Value']
                            break
        except Exception as e:
            print(f"Error fetching user from Cognito: {str(e)}")
        
        # MongoDB에서 사용자의 지갑 주소 조회
        point = 0.0
        wallets = self.user_repository.find_wallets_by_user_id(user_id)
        if wallets:
            try:
                # 첫 번째 지갑의 잔액 조회
                wallet_address = wallets[0].get('address')
                if wallet_address:
                    # XRPL 네트워크에서 계정 정보 조회
                    account_info = self.get_account_info(client, wallet_address)
                    if account_info and 'result' in account_info:
                        # 잔액 정보 추출
                        balance = account_info['result'].get('account_data', {}).get('Balance', '0')
                        # XRP 단위로 변환 (XRP는 소수점 6자리까지 표현)
                        point = float(balance) / 1000000
            except Exception as e:
                print(f"Error fetching account balance from XRPL: {str(e)}")
            
        # 응답 객체 생성 및 반환
        user_info = UserInfoResponse(
            user_id=user_id,
            nickname=nickname,
            level_title="조회되지 않음",  # 요구사항에 따라 하드코딩
            point=point,  # XRPL 계정 잔액으로 설정
            total_revenue=0.0  # 요구사항에 따라 하드코딩
        )
        
        return user_info