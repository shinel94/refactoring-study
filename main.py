# 기능 명세서
# invoice_list.json파일에 존재하는 각각 유저에 대해서 어떤 서비스를 이용했는지 내역이 적혀있다.
# 또한 court.json의 파일에 존재하는 코트들은 각각 name필드로 구분할 수 있고, 각각 서비스들이 제공하는 시간과 그에 따른 비용이 적혀있다.
# 이때 개별 유저들에 대해서 지불한 총 금액과, 총 이용 시간, 총 마일리지, 그리고 개별 코트 타입별 이용 시간과 비용 그리고
# 개별 코트의 판매 금액과 판매시간에 대해서 문자열로 반환

# 이때 코트의 경우에는 2시간 이상 연속으로 빌리는 경우에는 전체 비용의 5%, 최대 2000점의 마일리지가 적립됨
# 이때 볼머신의 경우에는 1시간 이상 연속으로 빌리는 경우에는 전체 비용의 10%의 마일리지가 적립됨
# 이떄 레슨의 경우에는 30분 이상 연속으로 빌리는 경우에는 전체 비용의 5%, 최대 1000점의 마일리지가 1회에 적립됨

import json


def main():
    with open('./data/court.json', 'r', encoding='utf-8') as f:
        court_list = json.load(f)
    with open('./data/invoice_list.json', 'r', encoding='utf-8') as f:
        invoice_list = json.load(f)

    result = {
        "user_result": [],
        "court_result": [],
    }

    for user_invoice in invoice_list:
        user_result = {
            "user_name": user_invoice['user_name'],
            "total_fee": 0,
            "total_used": 0,
            'mileage': 0,
            "details": {}
        }
        for invoice in user_invoice['invoice']:
            for court in court_list:
                if court['name'] == invoice['name']:

                    fee = invoice['duration'] * court['fee']
                    used = invoice['duration'] * court['unit']
                    mileage = 0
                    if court['type'] == 'court':
                        if used >= 60:
                            mileage = min(fee * 0.05, 2000)
                    elif court['type'] == 'machine':
                        if used >= 120:
                            mileage = fee * 0.1
                    elif court['type'] == 'lesson':
                        if used >= 30:
                            mileage = min(fee * 0.05, 1000)
                    user_result["total_fee"] = user_result["total_fee"] + fee
                    user_result['total_used'] = user_result['total_used'] + used
                    user_result['mileage'] = user_result['mileage'] + mileage
                    try:
                        detail = user_result[court['type']]
                        detail['used'] = detail['used'] + used
                        detail['fee'] = detail['fee'] + fee
                    except KeyError:
                        detail = {
                            'used': used,
                            'fee': fee
                        }
                        user_result['details'][court['type']] = detail
                    used_court_invoice = None
                    for court_invoice in result['court_result']:
                        if court_invoice['court_name'] == court['name']:
                            used_court_invoice = court_invoice
                            used_court_invoice['used'] += used
                            used_court_invoice['fee'] += fee
                            break

                    if used_court_invoice is None:
                        used_court_invoice = {
                            "court_name": court['name'],
                            "used": used,
                            "fee": fee
                        }
                        result['court_result'].append(used_court_invoice)

        result['user_result'].append(user_result)

    result_string = "전체 유저 정산 결과\n"
    result_string += "-" * 20 + '\n'
    for user in result["user_result"]:
        result_string += user["user_name"] + "님 정산 결과\n"
        result_string += f"전체 이용 시간 : {user['total_used']}분 / 전체 이용 요금 : {user['total_fee']}원\n"
        result_string += f'적립된 마일리지 : {user["mileage"]}\n'
        result_string += "상세 코트 타입별 이용 내역\n"
        for court_name, court_result in user['details'].items():
            result_string += f"  {court_name} - {court_result['used']}분 / {court_result['fee']}원\n"
        result_string += "-" * 20 + '\n'
    result_string += "전체 코트 정산 결과\n"
    result_string += "-" * 20 + '\n'
    for court in result['court_result']:
        result_string += court["court_name"] + "정산 결과\n"
        result_string += f"  전체 이용 시간 : {court['used']}분 / 전체 이용 요금 : {court['fee']}원\n"

    return result_string


if __name__ == "__main__":
    print(main())
