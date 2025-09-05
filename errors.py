
class Errors:

    # Error return [message: str, code: int], The code is a three-digit number.
    # Codes description:
    # 1__ - problems with data
    # 2__ - problems with database
    # 3__ - unexpected errors
    # 4__ - wallet errors
    # 5__ - groups errors
 
    DID_NOT_RECEIVE_ANY_INFORMATION = ["Didn't receive any information in request.", 100]

    INCORRECT_STRUCTURE = ["Incorrect data structure of request.", 101]

    INCORRECT_DATA_TYPES = ["Incorrect types of data vars request.", 102]

    CANT_GET_ACCOUNT = ["Can't get account with this id.", 107]

    CANT_ACCESS_TO_DB =  ["Technical problems, unable to connect to database.", 200]

    CANT_CREATE_WALLET =  ["Can't create wallet, maybe it exist.", 201]

    CANT_BUY_SHOP_PRODUCT = ["Can't buy shop product, maybe it exist or no money.", 202]

    THAT_NAME_OF_GROUP_ALREADY_EXIST = ["That name of a group already exist.", 500]

    CANT_GET_GROUP = ["Can't get group.", 501]

    @staticmethod
    def DID_NOT_RECEIVE_FIELD(field: str):
        return ["Can't find field '" + field + "' in request data.", 103]

    @staticmethod
    def INCORRECT_FIELD_VALUE(field: str):
        return ["Incorrect value of field '" + field + "' in request data.", 104]

    @staticmethod
    def INCORRECT_FIELD_TYPE(field: str):
        return ["Incorrect type of field '" + field + "' in request data.", 105]

    @staticmethod
    def CANT_RECOGNIZE_METHOD(method_name: str):
        return ["Can't recognize '" + method_name + "' method.", 106]

    @staticmethod
    def DB_CANT_ADD_ROW_IN_TABLE(table_name: str):
        return ["DB can't add row in table '" + table_name + "'.", 201]
    
    @staticmethod
    def  UNEXPECTED_ERROR_IN_METHOD(method_name: str, message: str):
        return ["Unexpected error in '" + method_name + "' method with message: " + message, 300]