from xrpl.clients import JsonRpcClient
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.models.requests import AccountInfo, AccountTx
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
        self.user_pool_id = os.environ.get('COGNITO_USER_POOL_ID', '')
        if os.environ.get('ENV') == 'local-profile':
            session = boto3.Session(
                profile_name=os.environ.get('AWS_PROFILE', 'default')
            )
            self.cognito_client = session.client(
                'cognito-idp',
                region_name=os.environ.get('AWS_REGION', 'ap-northeast-2')
            )
        else:
            self.cognito_client = boto3.client(
                'cognito-idp',
                region_name=os.environ.get('AWS_REGION', 'ap-northeast-2')
            )
    
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
    
    def get_account_transactions(self, client: JsonRpcClient, address: str, limit: int = 0, **kwargs) -> list:
        """
        XRPL 네트워크에서 이 계정의 거래 내역을 가져옵니다.

        Args:
            client (JsonRpcClient): 요청을 보낼 클라이언트입니다.
            address (str): 거래 내역을 조회할 계정의 주소입니다.
            limit (Optional[int]): 검색할 거래의 최대 개수입니다. 0이면 모두 검색합니다. 기본값은 0입니다.
            **kwargs: 추가적인 선택적 매개변수들입니다.

        Returns:
            list: 이 계정의 거래 내역을 포함하는 리스트입니다.
        """
        result = client.request(AccountTx(account=address, limit=limit, **kwargs))
        return result.get('result', {}).get('transactions', [])
        
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
        # point = 0.0
        # total_revenue = 0.0
        # wallets = self.user_repository.find_wallets_by_user_id(user_id)
        # if wallets:
        #     try:
        #         # 첫 번째 지갑의 잔액 조회
        #         wallet_address = wallets[0].get('address')
        #         if wallet_address:
        #             # XRPL 네트워크에서 계정 정보 조회
        #             account_info = self.get_account_info(client, wallet_address)
        #             if account_info and 'result' in account_info:
        #                 # 잔액 정보 추출
        #                 balance = account_info['result'].get('account_data', {}).get('Balance', '0')
        #                 # XRP 단위로 변환 (XRP는 소수점 6자리까지 표현)
        #                 point = float(balance) / 1000000
                        
        #             # 계정의 거래 내역 조회
        #             transactions = self.get_account_transactions(client, wallet_address)
                    
        #             # 사용자가 받은 모든 금액 합산 (수익)
        #             for tx in transactions:
        #                 # 트랜잭션이 '지불' 타입이고, 이 지갑이 수취인인 경우
        #                 if (tx.get('tx', {}).get('TransactionType') == 'Payment' and 
        #                     tx.get('tx', {}).get('Destination') == wallet_address):
        #                     # 지불된 금액 추출 (delivered_amount 또는 Amount 사용)
        #                     delivered_amount = tx.get('meta', {}).get('delivered_amount')
        #                     amount = tx.get('tx', {}).get('Amount')
                            
        #                     # 실제 받은 금액 계산
        #                     received_amount = 0
        #                     if delivered_amount and isinstance(delivered_amount, str):
        #                         received_amount = float(delivered_amount) / 1000000
        #                     elif amount and isinstance(amount, str):
        #                         received_amount = float(amount) / 1000000
                                
        #                     total_revenue += received_amount
                    
        #     except Exception as e:
        #         print(f"Error fetching data from XRPL: {str(e)}")

        # nft_grade, point, total_revenue 조회 -> 모두 `wallets` 컬렉션에서 조회
        total_revenue = 0.0
        point = 0.0
        nft_grade = "조회되지 않음"

        wallets = self.user_repository.find_wallets_by_user_id(user_id)
        if wallets:
            for wallet in wallets:
                total_revenue += wallet.get('total_revenue', 0.0)
                point += wallet.get('point', 0.0)
                nft_grade = wallet.get('nft_grade', "조회되지 않음")
            
        # 응답 객체 생성 및 반환
        user_info = UserInfoResponse(
            user_id=user_id,
            nickname=nickname,
            level_title=nft_grade,
            point=point,  # XRPL 계정 잔액으로 설정
            total_revenue=total_revenue  # 계산된 총 수익
        )
        
        return user_info