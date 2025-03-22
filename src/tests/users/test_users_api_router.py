# import requests
# import uuid

# BASE_URL = "http://localhost:8081" #"https://5erhg0u08g.execute-api.ap-northeast-2.amazonaws.com"

# TEST_USER_ID = "11111111-2222-3333-4444-555555555555" # str(uuid.uuid4())

# headers = {
#     "x-auth-sub": TEST_USER_ID  # 추후에 삭제할 부분
# }

# # 지갑 생성 또는 업데이트 (POST /users/wallets)
# def test_create_wallet():
#     response = requests.post(
#         f"{BASE_URL}/users/wallets",
#         headers=headers
#     )

#     print("POST response:", response.status_code, response.text)  # 로그 출력용

#     assert response.status_code == 200, f"Unexpected status: {response.status_code}, response: {response.text}"
#     data = response.json()
#     assert "wallet_address" in data
#     assert data["user_id"] == TEST_USER_ID
#     assert data["message"] in ["Wallet created", "Wallet updated"]

# # 유저 지갑 목록 조회 (GET /users/wallets)
# def test_get_wallets():
#     response = requests.get(f"{BASE_URL}/users/wallets", headers=headers)

#     assert response.status_code == 200, f"Unexpected status: {response.status_code}, response: {response.text}"
#     data = response.json()

#     if isinstance(data, dict) and "message" in data:
#         assert data["message"] == "No wallets found for this user"
#     else:
#         assert isinstance(data, list)
#         assert any("address" in wallet and wallet["address"].startswith("r") for wallet in data)