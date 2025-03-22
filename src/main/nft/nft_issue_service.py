#1. 포인트를 기준으로 사용자 나열하기
# 조건) 500포인트 이상인 사람만 걸러서 나열할 것

#2. 포인트에 따른 nft 등급 매핑

#3.nft 발급 대상자 선정
#  1) 전체 상위 3퍼센트 + 1500포가 넘는지 checking(저장) -> nft 발급
#  2) 전체 상위 10퍼 + 상위 3퍼센트 제외 + 1000포가 넘는지 checking(저장) -> nft 발급급
#  3) 전체 상위 40퍼 + 상위 3 + 상위 10 제외 + 500포 이상 chekcing(저장) -> ntt 발급

#4. nft 발급 구현(병렬 처리)
#5. db에 저장
#6. return 값은 void로 하는데 checking 용으로 해보기
# service/nft_service.py

from src.main.nft.nft_model import NFTRecord
from src.main.nft.nft_Info_dto import NftResponseDTO
from src.main.users.repository.UserRepository import UserRepository
from src.main.nft.nft_repository import save_nfts_bulk 
from datetime import datetime, timezone, timedelta
import asyncio

# XRPL 관련 모듈
#pip install xrpl-py + python -m poetry add xrpl.py
from xrpl.asyncio.transaction import submit_and_wait
from xrpl.models.transactions.nftoken_mint import NFTokenMint, NFTokenMintFlag
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.wallet import Wallet
from xrpl.clients import JsonRpcClient
import json

# service 내부에서 임시 유저 생성
# 예시 User 클래스 (있다고 가정)
# class User:
#     def __init__(self, wallet, point):
#         self.wallet = wallet
#         self.point = point

# # 개별 사용자 생성
# user1 = User(wallet="rWallet1", point=1800)
# user2 = User(wallet="rWallet2", point=1300)
# user3 = User(wallet="rWallet3", point=800)

# # 리스트로 묶어서 사용
# users = [user1, user2, user3]

repo = UserRepository()
users = repo.get_all_user()


# XRPL 설정
print("Connecting to Testnet...")
JSON_RPC_URL = "https://s.devnet.rippletest.net:51234/"
client = JsonRpcClient(JSON_RPC_URL)


#등급 조건건
GRADE_RULES = [
    {"grade": "platinum", "percent": 0.03, "min_point": 1500},
    {"grade": "gold", "percent": 0.10, "min_point": 1000},
    {"grade": "silver", "percent": 0.40, "min_point": 500},
    {"grade": "bronze", "percent": 1, "min_point": 0}
]

# 등급별 Taxon 값 설정 (NFT 분류 번호)
NFT_GRADE_TAXON = {
    "platinum": 4,
    "gold": 3,
    "silver": 2,
    "bronze": 1  # 기본값
}

#metadataUri
NFT_METADATA_URI = {
    "platinum" : "일단 플래티넘 주소",
    "gold": "일단 골드 주소",
    "silver" : "일단 실버 주소",
    "bronze": "일단 브론즈즈 주소"
}

# 테스트 지갑 생성 (테스트넷용)
# generate~ 함수는 내부적으로 비동기 함수임(asyncio.run()) -> ㅇ미 비동기에서 비동기로 겹침침
async def generate_wallet ():
    wallet = await generate_faucet_wallet(client=client)
    return wallet, wallet.address

# #포인트별로 필터링 함수
# def filter_users_by_rank_and_point(users, start_idx, end_idx, min_point):
#     return [
#         #전체 사용자 중 
#         # 특정 범위의 사용자 중 최소 포인트 이상인 사람만 필터링해서 반환환
#         user 
#         for i, user in enumerate(users[start_idx:end_idx]) 
#         if user.point >= min_point
#         ]

# XRPL 기반 NFT 민팅(XRPL 에서 NFT를 실제로 발급(MINt) 하는 핵심 함수)
# 개별 사용자 1명에게 NFT를 발급하는 함수
async def mint_nft_on_xrpl(user, grade, issuser_wallet, issuserAddr):
    # 발급일 = 현재 날짜 + 자정
    issued_at = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    # 만료일 = 6개월 자정
    expired_at = issued_at + timedelta(days=180)

    # now = datetime.utcnow()
    # NFT 발급을 위한 트랜잭션 객체 생성
    # 트랜잭션 : 블록체인에서 일어나는 모든 행동을 기록한 데이터 조각
    # XRPL노드로 전송되면 블록체인에 기록 되고 실제 NFT가 생성됨됨
    # ex) A가 B에게 10코인을 보냄 등.,,
    mint_tx = NFTokenMint(
        account=issuserAddr, # 발급자(대표자)
        nftoken_taxon=NFT_GRADE_TAXON[grade], # NFT 분류 Id (의미를 부여) grade에 따라 자동 적용용
        flags=NFTokenMintFlag.TF_TRANSFERABLE,# NFT 가 전송 가능한 것인지 여부 설정정
        uri=NFT_METADATA_URI[grade].encode("utf-8").hex() # NFT의 이미지, 무슨 등급, 이름/설명/속성 등을 설명해주는 정보 묶음
    )

    try:
        # xrpl에서 해당 정보를 트랜잭션에 넘기기기
        # submit_and_wait(transaction, client(노드 클라이언트 자체), wallet(서명에 사용될 지갑 객체체))
        response = await submit_and_wait(transaction=mint_tx, client=client, wallet=issuser_wallet)
        # transaction 처리 결과
        result = response.result

        #print("result" + result)

        # 트랜잭션 해시 추출(트랜잭션 고유 ID) -> 블록 탐색기에서 이 해시로 NFT 상태 조회 가능
        tx_hash = result['hash']
        if not tx_hash or not isinstance(tx_hash, str):
            raise Exception("트랜잭션 해시를 정상적으로 받지 못했습니다.")
        
        # NFT ID 파싱을 위함
        nft_id = ""
        
        
        #print("트랜잭션 결과:\n", json.dumps(result, indent=2))


        # XRPL 은 발급된 NFT의 ID를 직접 반환 x 
        # -> AffectedNodes에서 새로 생성된 노드를 찾아서 안의 ID를 추출해야함함
        #for node in result['meta']['AffectedNodes']:
         #   if "CreatedNode" in list(node.keys())[0]:
          #      created = node['CreatedNode']['NewFields']
           #     if "NFToken" in created.get("NFTokens", [{}])[0]:
            #        nft_id = created["NFTokens"][0]["NFToken"]["NFTokenID"]
             #       break
        
        for node in result['meta']['AffectedNodes']:
            node_data = node.get("CreatedNode") or node.get("ModifiedNode")
            if node_data and node_data["LedgerEntryType"] == "NFTokenPage":
                tokens = node_data.get("NewFields", {}).get("NFTokens") or node_data.get("FinalFields", {}).get("NFTokens")
                if tokens:
                    for token in tokens:
                        nft = token.get("NFToken")
                        if nft and "NFTokenID" in nft:
                            nft_id = nft["NFTokenID"]
                            break
            if nft_id:
                break



        if not nft_id:
            raise Exception("NFT ID 추출 실패")

        return {
            "user_wallet": user.wallet,
            "point": user.point,
            "nft_id": nft_id,
            "nft_grade": grade,
            "transaction_hash": tx_hash,
            "nft_metadata_uri": NFT_METADATA_URI[grade].encode("utf-8").hex(),
            "issued_at": issued_at,
            "expired_at": expired_at
        }
    
    except Exception as e:
        print(f"NFT 민팅 실패: {e}")
        return None

# 등급별 민팅(여러 사용자에게 등급별로 NFT를 발급해주는 함수)
async def mint_all_nfts(users, issuser_wallet, issuserAddr):
    total = len(users) # user가 몇명인지지
    used_indices = 0 # 등급별로 인덱스 나누기 위한 변수
    results = [] # 민팅 결과 담는 곳곳

    # 등급 조건 별로 for 문 돌리기기
    for rule in GRADE_RULES:
        # 퍼센트가 몇 등인지를 계산
        size = max(1, int(total * rule["percent"]))
        # 후보자 필터링(상위 인덱스 구간 내에서 최소 포인트 이상인 유저만)
        # fitler_user_by_rank_and_point(user, start_idx, end_idx, point)
        # candidates = filter_users_by_rank_and_point(
        #     users, used_indices, min(used_indices + size, total), rule["min_point"]
        # )
        # 다음 등급의 start_idx 설정정
        # used_indices += size

        # 후보자 리스트에서 nft 발급 준비
        # mint_nft_on_xrpl(user, grade)
        # tasks = []
        # for user in candidates :
        #   task = mint_nft_on_xrpl(user, rule["grade"])
        #   tasks.append(task)  
        # tasks = [mint_nft_on_xrpl(user, rule["grade"], issuser_wallet, issuserAddr) for user in candidates]
        tasks = [mint_nft_on_xrpl(user, rule["grade"], issuser_wallet, issuserAddr) for user in users]
        # nft 발급 결과를 비동기식으로 minted에 저장(minted)       
        minted = await asyncio.gather(*tasks) # 위 모든 동작을 동시에 실행행

        # 발급 실패한 사람 제외 results 에 저장해두기
        # extend([저장된 발급 결과에 None 이라 저장되어있는 것])
        results.extend([r for r in minted if r is not None]) 

    return results

# 전체 로직

async def process_nft_issuance_with_response() -> list[NftResponseDTO]:
    issuser_wallet, issuserAddr = await generate_wallet()

    # 포인트 별로 내림차순순
    users.sort(key=lambda u: u.point, reverse=True)
    
    # 모든 사용자 nft 발급 요청하기
    mint_results = await mint_all_nfts(users, issuser_wallet, issuserAddr)

    # DB 저장용 객체 변환
    nft_records = [
        NFTRecord(
            nft_id=result["nft_id"],
            user_wallet=result["user_wallet"],
            nft_grade=result["nft_grade"],
            transaction_hash=result["transaction_hash"],
            metadata_uri=result["nft_metadata_uri"],
            issued_at=result["issued_at"],
            expires_at=result["expired_at"]
        ) for result in mint_results
    ]
    save_nfts_bulk(nft_records)

    # DTO 변환
    return [
        NftResponseDTO(
            user_wallet_id=r["user_wallet"],
            point=r["point"],
            nft_id=r["nft_id"],
            nft_grade=r["nft_grade"],
            transaction_hash=r["transaction_hash"],
            nft_metadata_uri=r["nft_metadata_uri"],
            issued_at=r["issued_at"],
            expired_at=r["expired_at"]
        ) for r in mint_results
    ]


# async def test_process_nft_issuance_without_db() -> list[NftResponseDTO]:
#     issuser_wallet, issuserAddr = await generate_wallet()

#     # 포인트 별로 내림차순순
#     users.sort(key=lambda u: u.point, reverse=True)
#     # 모든 사용자 nft 발급 요청하기
#     mint_results = await mint_all_nfts(users, issuser_wallet, issuserAddr)

#     return [
#         NftResponseDTO(
#             user_wallet_id=r["user_wallet"],
#             point=r["point"],
#             nft_id=r["nft_id"],
#             nft_grade=r["nft_grade"],
#             transaction_hash=r["transaction_hash"],
#             nft_metadata_uri=r["nft_metadata_uri"],
#             issued_at=r["issued_at"],
#             expired_at=r["expired_at"]
#         )
#         for r in mint_results
#     ]

