class CognitoEventType:
    # https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-custom-email-sender.html
    EMAIL_ACCOUNT_TAKE_OVER_NOTIFICATION = "CustomEmailSender_AccountTakeOverNotification"
    EMAIL_ADMIN_CREATE_USER = "CustomEmailSender_AdminCreateUser"
    EMAIL_FORGOT_PASSWORD = "CustomEmailSender_ForgotPassword"  # nosec B105
    EMAIL_RESEND_CODE = "CustomEmailSender_ResendCode"
    EMAIL_SIGNUP = "CustomEmailSender_SignUp"
    EMAIL_UPDATE_USER_ATTRIBUTE = "CustomEmailSender_UpdateUserAttribute"
    EMAIL_VERIFY_USER_ATTRIBUTE = "CustomEmailSender_VerifyUserAttribute"

    # https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-custom-sms-sender.html
    SMS_ADMIN_CREATE_USER = "CustomSMSSender_AdminCreateUser"
    SMS_AUTHENTICATION = "CustomSMSSender_Authentication"
    SMS_FORGOT_PASSWORD = "CustomSMSSender_ForgotPassword"  # nosec B105
    SMS_RESEND_CODE = "CustomSMSSender_ResendCode"
    SMS_SIGNUP = "CustomSMSSender_SignUp"
    SMS_UPDATE_USER_ATTRIBUTE = "CustomSMSSender_UpdateUserAttribute"
    SMS_VERIFY_USER_ATTRIBUTE = "CustomSMSSender_VerifyUserAttribute"
