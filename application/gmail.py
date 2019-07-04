import base64

from googleapiclient import errors

import authentication


def get_body_from_message():
    service = authentication.build_gmail_api()
    messages = list_messages_matching_query(
        service, "me", "from:1184@nl.mcd.com newer_than:180d")
    msg_str_formatted = ""
    subject = ""

    for m in messages:
        msg = get_message(service, 'me', m['id'])

        msg_str = str(base64.b64decode(msg['payload']['body']['data']))
        msg_str_formatted = msg_str.replace('\\r', '').replace('\\n', '\n')
        headers = msg['payload']['headers']
        subject = str([i['value']
                       for i in headers if i['name'] == 'Subject'][0])
        print(subject)
    return msg_str_formatted, subject


def list_messages_matching_query(service, user_id, query=''):
    """List all Messages of the user's mailbox matching the query.

    Args:
      service: Authorized Gmail API service instance.
      user_id: User's email address. The special value "me"
      can be used to indicate the authenticated user.
      query: String used to filter messages returned.
      Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

    Returns:
      List of Messages that match the criteria of the query. Note that the
      returned list contains Message IDs, you must use get with the
      appropriate ID to get the details of a Message.
    """
    try:
        response = service.users().messages().list(userId=user_id,
                                                   q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])

            print(response['messages'])
        return messages
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def get_message(service, user_id, msg_id):
    """Get a Message with given ID.

      Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: The ID of the Message required.

      Returns:
        A Message.
      """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()

        # print('Message snippet: %s' % message['snippet'])

        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
