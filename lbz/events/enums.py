class CognitoEventType:
    """More information at:

    https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-custom-sms-sender.html
    """

    EMAIL_FORGOT_PASSWORD = "CustomEmailSender_ForgotPassword"
    EMAIL_RESEND_CODE = "CustomEmailSender_ResendCode"
    EMAIL_SIGNUP = "CustomEmailSender_SignUp"
    EMAIL_VERIFY_USER_ATTRIBUTE = "CustomEmailSender_VerifyUserAttribute"
    EMAIL_UPDATE_USER_ATTRIBUTE = "CustomEmailSender_UpdateUserAttribute"
    EMAIL_ADMIN_CREATEUSER = "CustomEmailSender_AdminCreateUser"
    EMAIL_ACCOUNT_TAKE_OVER_NOTIFICATION = "CustomEmailSender_AccountTakeOverNotification"

    SMS_UPDATE_USER_ATTRIBUTE = "CustomSMSSender_UpdateUserAttribute"
    SMS_VERIFY_USER_ATTRIBUTE = "CustomSMSSender_VerifyUserAttribute"
    SMS_AUTHENTICATION = "CustomSMSSender_Authentication"
    SMS_SIGNUP = "CustomSMSSender_SignUp"
    SMS_RESEND_CODE = "CustomSMSSender_ResendCode"
    SMS_FORGOT_PASSWORD = "CustomSMSSender_ForgotPassword"
    SMS_ADMIN_CREATEUSER = "CustomSMSSender_AdminCreateUser"
