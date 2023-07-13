# 기능 명세서
# invoice_list.json파일에 존재하는 각각 유저에 대해서 어떤 서비스를 이용했는지 내역이 적혀있다.
# 또한 court.json의 파일에 존재하는 코트들은 각각 name필드로 구분할 수 있고, 각각 서비스들이 제공하는 시간과 그에 따른 비용이 적혀있다.
# 이때 개별 유저들에 대해서 지불한 총 금액과, 총 이용 시간, 총 마일리지, 그리고 개별 코트 타입별 이용 시간과 비용 그리고
# 개별 코트의 판매 금액과 판매시간에 대해서 문자열로 반환

# 이때 코트의 경우에는 2시간 이상 연속으로 빌리는 경우에는 전체 비용의 5%, 최대 2000점의 마일리지가 적립됨
# 이때 볼머신의 경우에는 1시간 이상 연속으로 빌리는 경우에는 전체 비용의 10%의 마일리지가 적립됨
# 이떄 레슨의 경우에는 30분 이상 연속으로 빌리는 경우에는 전체 비용의 5%, 최대 1000점의 마일리지가 1회에 적립됨

from abc import ABCMeta, abstractmethod

import json
from typing import List, Tuple, Dict


class BaseCourt(metaclass=ABCMeta):
    def __init__(self, name, type, fee, unit):
        self.name = name
        self.type = type
        self.fee = fee
        self.unit = unit

    def calculate_user_info(self, duration):
        fee = duration * self.fee
        used = duration * self.unit
        mileage = self._calcualte_mileage(used, fee)
        return fee, used, mileage

    @abstractmethod
    def _calcualte_mileage(self, used, fee):
        raise NotImplemented


class RentalCourt(BaseCourt):

    def __init__(self, name, type, fee, unit, mileage):
        super().__init__(name, type, fee, unit)

    def calculate_user_info(self, duration):
        fee, used, mileage = super().calculate_user_info(duration)
        return fee, used, mileage

    def _calcualte_mileage(self, used, fee):
        return min(fee * 0.05, 2000) if used >= 60 else 0


class MachineCourt(BaseCourt):

    def __init__(self, name, type, fee, unit):
        super().__init__(name, type, fee, unit)

    def calculate_user_info(self, duration):
        return super().calculate_user_info(duration)

    def _calcualte_mileage(self, used, fee):
        return fee * 0.1 if used >= 120 else 0


class LessonCourt(BaseCourt):

    def __init__(self, name, type, fee, unit):
        super().__init__(name, type, fee, unit)

    def calculate_user_info(self, duration):
        return super().calculate_user_info(duration)

    def _calcualte_mileage(self, used, fee):

        return min(fee * 0.05, 1000) if used>=30 else 0


def create_court_instance(name, type, fee, unit, **kwage) -> BaseCourt:
    if type == "court":
        return RentalCourt(name, type, fee, unit, kwage.get('mileage', 0))
    elif type == "machine":
        return MachineCourt(name, type, fee, unit)
    elif type == "lesson":
        return LessonCourt(name, type, fee, unit)
    else:
        raise ValueError("코트 타입이 잘못되었습니다.")
    pass

class InvoiceDetail:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration


class Invoice:

    def __init__(self, user_name, invoice):
        self.user_name = user_name
        self.invoice = [InvoiceDetail(**invoice_detail) for invoice_detail in invoice]

class UserCourtResult:  # DTO / DAO
    def __init__(self, used=0, fee=0):
        self.used = used
        self.fee = fee

    def add_result(self,used, fee):
        self.used += used
        self.fee += fee

class UserResult:
    def __init__(self, name):
        self.name = name
        self.total_fee = 0
        self.total_used = 0
        self.mileage = 0
        self.details: Dict[str, UserCourtResult] = dict()

    def add_result(self, fee, used, mileage):
        self.total_fee += fee
        self.total_used += used
        self.mileage += mileage

class CourtResult:

    def __init__(self):
        pass
def load_data() ->  Tuple[List[BaseCourt], List[Invoice], str]:
    with open('./data/court.json', 'r', encoding='utf-8') as f:
        court_list = [create_court_instance(**court_dict) for court_dict in json.load(f)]
    with open('./data/invoice_list.json', 'r', encoding='utf-8') as f:
        invoice_list = [Invoice(**invoice_dict) for invoice_dict in json.load(f)]

    return court_list, invoice_list, "string1"


def calculate(invoice_list: List[Invoice], court_list: List[BaseCourt]):
    result = {
        "user_result": [],
        "court_result": [],
    }

    for user_invoice in invoice_list:
        user_result = UserResult(user_invoice.user_name)
        for invoice in user_invoice.invoice:
            for court in court_list:
                if court.name == invoice.name:
                    fee, used, mileage = court.calculate_user_info(invoice.duration)
                    user_result.add_result(fee, used, mileage)
                    try:
                        user_result.details[court.type].add_result(used, fee)
                    except KeyError:
                        user_result.details[court.type] = UserCourtResult(used, fee)
                    used_court_invoice = None
                    for court_invoice in result['court_result']:
                        if court_invoice['court_name'] == court.name:
                            used_court_invoice = court_invoice
                            used_court_invoice['used'] += used
                            used_court_invoice['fee'] += fee
                            break

                    if used_court_invoice is None:
                        used_court_invoice = {
                            "court_name": court.name,
                            "used": used,
                            "fee": fee
                        }
                        result['court_result'].append(used_court_invoice)

        result['user_result'].append(user_result)
    return result


def render_string(calculated_result):
    result_string = "전체 유저 정산 결과\n"
    result_string += "-" * 20 + '\n'
    for user in calculated_result["user_result"]:
        user: UserResult
        result_string += user.name + "님 정산 결과\n"
        result_string += f"전체 이용 시간 : {user.total_used}분 / 전체 이용 요금 : {user.total_fee}원\n"
        result_string += f'적립된 마일리지 : {user.mileage}\n'
        result_string += "상세 코트 타입별 이용 내역\n"
        for court_name, court_result in user.details.items():
            result_string += f"  {court_name} - {court_result.used}분 / {court_result.fee}원\n"
        result_string += "-" * 20 + '\n'
    result_string += "전체 코트 정산 결과\n"
    result_string += "-" * 20 + '\n'
    for court in calculated_result['court_result']:
        result_string += court["court_name"] + "정산 결과\n"
        result_string += f"  전체 이용 시간 : {court['used']}분 / 전체 이용 요금 : {court['fee']}원\n"
    return result_string


def render(calculated_result, render_option='string1'):
    if render_option == 'string1':
        return render_string(calculated_result)
    elif render_option == "string2":
        return render_html(calculated_result)
    else:
        raise ValueError("렌더링 옵션이 잘못되었습니다.")

def main():

    court_list, invoice_list, render_type = load_data()

    result = calculate(invoice_list, court_list)

    return render(result, render_type)



if __name__ == "__main__":
    print(main())

