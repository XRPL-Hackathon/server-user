from pydantic import BaseModel
from typing import Dict
from datetime import datetime

# 필요한 필드들(Response)
# 1. user-wallet id
# 2. nft-id
# 3. nft-grade
# 4. transaction_hash #nft 발급 트ㅐㄴ잭션이 성공적으로 기록 되어있는지 확인 가능한 정보
#(블록체인 익스플로어 에서 트ㅐㄴ잭션을 조회 가능함)
# 5. nft 메타 데이터
# 6. 발급일, 만료일
class NftResponseDTO(BaseModel):
    user_wallet_id: str
    point: int
    nft_id: str
    nft_grade: str
    transaction_hash: str
    nft_metadata_uri: str
    issued_at: datetime
    expired_at: datetime


# db 저자에 필요한 필드
# 1. nft-id
# 2. nft-grade
# 3. transacation_hash
# 4. meta_uri
# nft의 상세 정보(이미지, 설명, 속성 등) 외부 저장소(s3)에 보관
# 5. 발급, 만료일
class NftSaveDTO(BaseModel):
    id: str
    user_wallet: str
    nft_id: str
    nft_grade: str
    transaction_hash: str
    nft_metadata_uri: str
    issued_at: datetime
    expired_at: datetime

