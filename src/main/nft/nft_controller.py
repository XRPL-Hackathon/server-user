# controller/nft_controller.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

#from database import get_db
#from nft_issue_service import process_nft_issuance_with_response
#from nft_
from src.main.nft.nft_issue_service import test_process_nft_issuance_without_db
from src.main.nft.nft_Info_dto import NftResponseDTO

router = APIRouter(
    prefix="/nft",
    tags=["NFT 발급"]
)

@router.post("/issue", response_model=List[NftResponseDTO])
async def issue_nfts():
    try:
        #results = await process_nft_issuance_with_response()
        results = await test_process_nft_issuance_without_db()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NFT 발급 중 오류 발생: {str(e)}")
