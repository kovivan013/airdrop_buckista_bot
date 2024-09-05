from pydantic import BaseModel


class BaseReferral(BaseModel):

    Succ: bool = False
    ErrMsg: str = ""
    refer_code_status: str = ""


class ResponseMessages:

    not_exist: str = "refer code not exist"
    valid_code: str = "valid refer code"
    already_redeemed: str = "refer code already redeemed"