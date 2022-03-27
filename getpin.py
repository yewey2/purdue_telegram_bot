import requests


def getActivationData(code):
    
    HEADERS = {"User-Agent": "okhttp/3.11.0"}

    PARAMS = {
        "app_id": "com.duosecurity.duomobile.app.DMApplication",
        "app_version": "2.3.3",
        "app_build_number": "323206",
        "full_disk_encryption": False,
        "manufacturer": "Google",
        "model": "Pixel",
        "platform": "Android",
        "jailbroken": False,
        "version": "6.0",
        "language": "EN",
        "customer_protocol": 1,
    }

    ENDPOINT = "https://api-1b9bef70.duosecurity.com/push/v2/activation/{}"

    res = requests.post(ENDPOINT.format(code), headers=HEADERS, params=PARAMS)

    if res.json().get("code") == 40403:
        print(
            "Invalid activation code."
            "Please request a new link in BoilerKey settings."
        )
        return None


    if not res.json()["response"]:
        print("Unknown error")
        print(res.json())
        return None

    return res.json()["response"]

if __name__== "__main__":
    print('Please run the main file!')