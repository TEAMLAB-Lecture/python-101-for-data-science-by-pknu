import os
import pickle
import requests
import json

ASSIGNMENT_ID = 3
ASSIGNMENT_NAME = "arithmetic_function.py"

TOKEN_PICKLE_FILE_NAME = "access_token"
HOST = "52.79.250.86"

# Get JWT token to access REST API
def getToken():
    if os.path.isfile(TOKEN_PICKLE_FILE_NAME):
        try:
            with open(TOKEN_PICKLE_FILE_NAME, "rb") as accesstoken:
                token_file = pickle.load(accesstoken)
                return token_file["token"], token_file["id"]
        except EOFError:
            print("Existing access_token is NOT validated")
            return None, None
    else:
        return None, None


def getLoginInformation():
    login_id = input("Login ID : ")
    login_password = input("Password : ")
    return [login_id, login_password]


def getAccessTokenFromServer(login_id, login_password):
    headers = {"Content-type": "application/json"}
    payload = {"pwd": login_password, "id": login_id}

    access_token_jwt = requests.post(
        "http://" + HOST + "/token", json=payload, headers=headers
    )

    if access_token_jwt.ok:
        return access_token_jwt.text
    else:
        return None


def makeAccessTokenPickle(access_token, login_id):
    pickle_file_Name = "access_token"
    pcikleObject = open(pickle_file_Name, "wb")
    loginID_json = {"id": login_id}
    token_json = {"token": access_token}
    data = json.loads(json.dumps(token_json, ensure_ascii=False))
    data.update(loginID_json)
    pickle.dump(data, pcikleObject)
    return pickle


def getFileContents(fileName):
    with open(fileName, "r", encoding="utf8") as contens_file:
        contens = contens_file.read()
    return contens


def submitAssignmentFileToServer(access_token, assignment_file_name):

    assignment_contents = getFileContents(assignment_file_name)

    # [basename, ext] = assignment_file_name.split(".")

    payload = {
        "assignment_id": ASSIGNMENT_ID,
        "submit_code": assignment_contents,
    }

    accesstoken_dict = json.loads(access_token)
    headers = {"authorization": accesstoken_dict["token"]}
    result = requests.post(
        "http://" + HOST + "/submit",
        json=payload,
        headers=headers,
    )

    # TODO Add exception handling

    return result


def removeExpiredAccessKey():
    if os.path.isfile(TOKEN_PICKLE_FILE_NAME):
        os.remove(TOKEN_PICKLE_FILE_NAME)
    else:  ## Show an error ##
        print("Error: %s file not found" % TOKEN_PICKLE_FILE_NAME)


def printTestResults(text):
    json_data = json.loads(text)

    a = "-" * 20
    b = "-" * 10
    c = "-" * 20
    print("%20s | %10s | %20s" % (a, b, c))
    print("%20s | %10s | %20s" % ("Function Name", "Passed?", "Feedback"))
    print("%20s | %10s | %20s" % (a, b, c))

    for function_name, result in json_data["test_result"].items():
        if result == ("S"):
            passed = "PASS"
            feedback = "Good Job"
        else:
            passed = "Not Yet"
            if result == ("E"):
                feedback = "Check Your Logic"
            if result == ("F"):
                feedback = "Check Your Grammar"
        print(
            "%20s | %10s | %20s"
            % (function_name.replace("test_", ""), passed, feedback)
        )

    print("%20s | %10s | %20s" % (a, b, c))


def main():

    # Check Your Access Token
    [access_token, login_id] = getToken()

    # Get New Access Token
    if access_token == None:
        while access_token == None:
            [login_id, login_password] = getLoginInformation()
            access_token = getAccessTokenFromServer(login_id, login_password)
            if access_token == None:
                print("Wrong Email or password. Please, input again.")

    # Make access pickle before end of program
    makeAccessTokenPickle(access_token, login_id)

    assignment_name = ASSIGNMENT_NAME

    # if os.path.isfile(assignment_name) == False:
    #     print(
    #         "The file cannot be found. Please check the file name of file path."
    #     )

    result = submitAssignmentFileToServer(access_token, assignment_name)
    if result.status_code == 200:
        print("Assignment submission has been successfully completed.")
        printTestResults(result.text)
        # Make access pickle before end of program
    elif result.status_code == 400:
        print(result.text)
        removeExpiredAccessKey()
        print("Your expired access key removed. Please, try again")
    elif result.status_code == 419:
        print("Token is not valid. Please, try again")
        removeExpiredAccessKey()
    elif result.status_code == 500:
        print(
            "Unexpected error exists. Please contact teamlab.gachon@gmail.com"
        )
    else:
        print(result)
        print(result.text)
        


if __name__ == "__main__":
    main()
