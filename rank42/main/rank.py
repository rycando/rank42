"""
rank42에서 사용되는 Rank 관련 코드
"""
from typing import List, Callable, Sequence

from .models import Tier, FtUser


class SingleTier:
	def __init__(self, tier_name, tier_img):
		self.tier_name = tier_name
		self.tier_img = tier_img


class RankTier:
	"""rank42에서 사용되는 티어 시스템 생산 및 수정 등 모든 부분을 관리하는 class"""
	challenger_name = "Challenger"
	challenger_per = 1.5
	challenger_img = "https://opgg-static.akamaized.net/images/medals/challenger_1.png"
	diamond_name = "Diamond"
	diamond_per = 4.2
	diamond_img = "https://opgg-static.akamaized.net/images/medals/diamond_1.png"
	platinum_name = "Platinum"
	platinum_per = 8.3
	platinum_img = "https://opgg-static.akamaized.net/images/medals/platinum_1.png"
	gold_name = "Gold"
	gold_per = 24
	gold_img = "https://opgg-static.akamaized.net/images/medals/gold_1.png"
	silver_name = "Silver"
	silver_per = 30.2
	silver_img = "https://opgg-static.akamaized.net/images/medals/silver_1.png"
	bronze_name = "Bronze"
	bronze_img = "https://opgg-static.akamaized.net/images/medals/bronze_1.png"
	unranked_name = "Unranked"
	unranked_img = "https://opgg-static.akamaized.net/images/medals/default.png"

	def __init__(self, number: int = None):
		"""
		'number(캠퍼스의 본과 참여 학생수)'에 맞게 티어별 수를 생성
		
		:type number: int
		"""
		if number:
			tier_class_list: List[SingleTier] = []

			def split_tier(
					number: int,
					tier_name: str,
					tier_img: str,
					tier_class_list: List[SingleTier],
					flag: int = None,
			) -> None:
				"""
				한 티어에 존재하는 인원을 5개로 나눠 각각의 티어 이름을 리스트에 추가함

				:param number: 해당 티어에 존재하는 인원수
				:param tier_name: 해당 티어 이름 ex) 브론즈
				:param tier_img: 해당 티어의 이미지 url
				:param tier_class_list: 조건에 맞게 설정된 세부 티어 클래스를 담음
				:param flag: 5단계의 티어를 나눌지 말지 설정하는 플래그, 0은 나눔, 1은 안나눔 ex) challenger 같은 티어에 사용
				:return: 리턴 값은 없고, tier_class_list에 담음.
				"""
				if not flag:
					# flag가 없을 경우, 5개의 세부 티어로 나눠서 설정함
					numbers: list[int] = []
					numbers_append: Callable[[int], None] = numbers.append
					for i in range(5, 0, -1):
						numbers_append(int(number / i))
						number -= numbers[-1]

					tier_class_list_append: Callable[[SingleTier], None] = tier_class_list.append
					for i, numbers_i in enumerate(numbers):
						for _ in range(numbers_i):
							single_tier: SingleTier = SingleTier(f"{tier_name}{i + 1}", tier_img)
							tier_class_list_append(single_tier)
				else:
					# flag가 존재할 경우(challenger 티어 같은 경우), 따로 안나눔
					tier_class_list_append: Callable[[SingleTier], None] = tier_class_list.append
					for _ in range(number):
						single_tier: SingleTier = SingleTier(tier_name, tier_img)
						tier_class_list_append(single_tier)

			self.rank_users_number: int = int(number)
			# 각 티어의 인원과 조건에 맞게 split_tier를 통해 SingleTier 클래스를 만들어, tier_class_list에 담음.
			self.challenger: int = round(number * (self.challenger_per / 100))
			split_tier(self.challenger, self.challenger_name, self.challenger_img, tier_class_list, 1)
			self.diamond: int = round(number * (self.diamond_per / 100))
			split_tier(self.diamond, self.diamond_name, self.diamond_img, tier_class_list)
			self.platinum: int = round(number * (self.platinum_per / 100))
			split_tier(self.platinum, self.platinum_name, self.platinum_img, tier_class_list)
			self.gold: int = round(number * (self.gold_per / 100))
			split_tier(self.gold, self.gold_name, self.gold_img, tier_class_list)
			self.silver: int = round(number * (self.silver_per / 100))
			split_tier(self.silver, self.silver_name, self.silver_img, tier_class_list)
			self.bronze: int = number - (self.challenger + self.diamond + self.platinum + self.gold + self.silver)
			split_tier(self.bronze, self.bronze_name, self.bronze_img, tier_class_list)
			self.tier_class_list: List[SingleTier] = tier_class_list

	def set_tier(self, ft_users: Sequence[FtUser], unrank_ft_users: Sequence[FtUser] = None):
		"""
		본과 유저들의 queryset을 가지고 전체적으로 티어를 설정함

		:param ft_users: 점수가 존재하는 본과 유저 queryset
		:param unrank_ft_users: (선택)점수가 존재하지 않는 본과 유저 queryset
		:return: 본과 유저 queryset
		"""
		for i, ft_user in enumerate(ft_users):
			temp = {}
			tier: Tier = Tier.objects.get(FtUser=ft_user)
			temp["tier_name"]: str = self.tier_class_list[i].tier_name
			ft_user.tier_img = self.tier_class_list[i].tier_img
			temp["tier_rank"]: int = i + 1
			if temp["tier_rank"] != tier.tier_rank or temp["tier_name"] != tier.tier_name:
				tier.tier_name = temp["tier_name"]
				tier.tier_rank = temp["tier_rank"]
				tier.save()

		# 점수가 존재하지 않는 본과 유저에 대해 처리할지는 선택 가능. 리턴값이 다름.
		if unrank_ft_users:
			for ft_user in unrank_ft_users:
				ft_user.tier_img = self.unranked_img
				tier: Tier = Tier.objects.get(FtUser=ft_user)
				tier.tier_name = self.unranked_name
				tier.tier_rank = 0
				tier.save()
			return ft_users, unrank_ft_users
		return ft_users

	def get_tier_img(self, tier_name: str) -> str:
		return eval(f"self.{''.join(c for c in tier_name if not c.isdigit()).lower()}_img")

	def get_rank_users_number(self) -> int:
		"""class 생성시 'number(캠퍼스의 본과 참여 학생수)'에 입력된 값을 반환"""
		return self.rank_users_number
