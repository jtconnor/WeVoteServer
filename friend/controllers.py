# friend/controllers.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-

from .models import FriendInvitationVoterLink, FriendManager, CURRENT_FRIENDS, DELETE_INVITATION_EMAIL_SENT_BY_ME, \
    FRIEND_INVITATIONS_SENT_BY_ME, FRIEND_INVITATIONS_SENT_TO_ME, FRIENDS_IN_COMMON, UNFRIEND_CURRENT_FRIEND
from email_outbound.models import EmailAddress, EmailManager, FRIEND_INVITATION_TEMPLATE, VERIFY_EMAIL_ADDRESS_TEMPLATE
from validate_email import validate_email
from voter.models import Voter, VoterManager
import wevote_functions.admin
from wevote_functions.functions import is_voter_device_id_valid, positive_value_exists

logger = wevote_functions.admin.get_logger(__name__)


def friend_invitation_by_email_send_for_api(voter_device_id, email_addresses_raw, invitation_message,
                                            sender_email_address):
    success = False
    status = ""
    error_message_to_show_voter = ""

    results = is_voter_device_id_valid(voter_device_id)
    if not results['success']:
        error_results = {
            'status':                               results['status'],
            'success':                              False,
            'voter_device_id':                      voter_device_id,
            'sender_voter_email_address_missing':   True,
            'error_message_to_show_voter':          error_message_to_show_voter
        }
        return error_results

    voter_manager = VoterManager()
    voter_results = voter_manager.retrieve_voter_from_voter_device_id(voter_device_id)
    sender_voter_id = voter_results['voter_id']
    if not positive_value_exists(sender_voter_id):
        error_results = {
            'status':                               "VOTER_NOT_FOUND_FROM_VOTER_DEVICE_ID",
            'success':                              False,
            'voter_device_id':                      voter_device_id,
            'sender_voter_email_address_missing':   True,
            'error_message_to_show_voter':          error_message_to_show_voter
        }
        return error_results

    sender_voter = voter_results['voter']
    email_manager = EmailManager()
    messages_to_send = []

    send_now = False
    valid_new_sender_email_address = False
    if sender_voter.has_email_with_verified_ownership():
        send_now = True
    else:
        # If here, check to see if a sender_email_address was passed in
        valid_new_sender_email_address = False
        if not positive_value_exists(sender_email_address) or not validate_email(sender_email_address):
            error_results = {
                'status':                               "VOTER_DOES_NOT_HAVE_VALID_EMAIL",
                'success':                              False,
                'voter_device_id':                      voter_device_id,
                'sender_voter_email_address_missing':   True,
                'error_message_to_show_voter':          error_message_to_show_voter
            }
            return error_results
        else:
            valid_new_sender_email_address = True

    sender_email_address_object = EmailAddress()
    if valid_new_sender_email_address:
        # Does this email exist in the EmailAddress database?
        email_address_object_found = False
        results = email_manager.retrieve_email_address_object(sender_email_address)
        if results['email_address_object_found']:
            email_address_object_found = True
            sender_email_address_object = results['email_address_object']
            # Is this email address in use by another voter?
            in_use_by_another_voter = \
                sender_email_address_object.voter_we_vote_id.lower() == sender_voter.we_vote_id.lower()
            if in_use_by_another_voter:
                valid_new_sender_email_address = False
                error_message_to_show_voter = "This email is already in use by another voter."
        else:
            # Create email address object
            if sender_voter.signed_in_personal():
                email_results = email_manager.create_email_address_for_voter(sender_email_address, sender_voter)
            else:
                email_results = email_manager.create_email_address(sender_email_address)

            if email_results['email_address_object_saved']:
                # We recognize the email
                email_address_object_found = True
                sender_email_address_object = email_results['email_address_object']

        # double-check that we have email_address_object
        if not email_address_object_found:
            success = False
            status = "FRIEND_INVITATION_BY_EMAIL_SEND-EMAIL_ADDRESS_OBJECT_MISSING"
            error_results = {
                'success':                              success,
                'status':                               status,
                'voter_device_id':                      voter_device_id,
                'sender_voter_email_address_missing':   True,
                'error_message_to_show_voter':          error_message_to_show_voter
            }
            return error_results

    if valid_new_sender_email_address:
        # Send verification email, and store the rest of the data without processing until sender_email is verified
        recipient_voter_email = sender_email_address_object.normalized_email_address
        recipient_email_we_vote_id = sender_email_address_object.we_vote_id

        send_now = False
        kind_of_email_template = VERIFY_EMAIL_ADDRESS_TEMPLATE
        recipient_voter_we_vote_id = sender_voter.we_vote_id
        verification_message = ""
        outbound_results = email_manager.create_email_outbound_description(
            sender_voter.we_vote_id, recipient_voter_we_vote_id,
            recipient_email_we_vote_id, recipient_voter_email,
            verification_message, kind_of_email_template)
        status += outbound_results['status'] + " "
        if outbound_results['email_outbound_description_saved']:
            email_outbound_description = outbound_results['email_outbound_description']
            schedule_results = email_manager.schedule_email(email_outbound_description)
            if schedule_results['email_scheduled_saved']:
                messages_to_send.append(schedule_results['email_scheduled_id'])
            status += schedule_results['status'] + " "

    if sender_voter.has_valid_email() or valid_new_sender_email_address:
        # We can continue. Note that we are not checking for "voter.has_email_with_verified_ownership()"
        pass
    else:
        error_results = {
            'status':                               "VOTER_DOES_NOT_HAVE_VALID_EMAIL",
            'success':                              False,
            'voter_device_id':                      voter_device_id,
            'sender_voter_email_address_missing':   True,
            'error_message_to_show_voter':          error_message_to_show_voter
        }
        return error_results

    # Break apart all of the emails in email_addresses_raw input from the voter
    results = email_manager.parse_raw_emails_into_list(email_addresses_raw)
    if results['at_least_one_email_found']:
        raw_email_list_to_invite = results['email_list']
    else:
        error_message_to_show_voter = "Please enter the email address of at least one friend."
        error_results = {
            'status':                               "LIST_OF_EMAILS_NOT_RECEIVED " + results['status'],
            'success':                              False,
            'voter_device_id':                      voter_device_id,
            'sender_voter_email_address_missing':   False,
            'error_message_to_show_voter':          error_message_to_show_voter
        }
        return error_results

    # Check to see if we recognize any of these emails
    for one_normalized_raw_email in raw_email_list_to_invite:
        # Starting with a raw email address, find (or create) the EmailAddress entry
        # and the owner (Voter) if exists
        retrieve_results = retrieve_voter_and_email_address(one_normalized_raw_email)
        if not retrieve_results['success']:
            error_message_to_show_voter = "There was an error retrieving one of your friend's email addresses. " \
                                          "Please try again."
            results = {
                'success':                              False,
                'status':                               retrieve_results['status'],
                'voter_device_id':                      voter_device_id,
                'sender_voter_email_address_missing':   False,
                'error_message_to_show_voter':          error_message_to_show_voter
            }
            return results
        status += retrieve_results['status'] + " "

        email_address_object = retrieve_results['email_address_object']

        # Store the friend invitation linked to another voter, or to an email that isn't linked to a voter
        if retrieve_results['voter_found']:
            # Store the friend invitation in FriendInvitationVoterLink table
            voter_friend = retrieve_results['voter']
            friend_invitation_results = store_internal_friend_invitation_with_two_voters(
                sender_voter, invitation_message, voter_friend)
            status += friend_invitation_results['status'] + " "
            success = friend_invitation_results['success']
            sender_voter_we_vote_id = sender_voter.we_vote_id
            recipient_voter_we_vote_id = voter_friend.we_vote_id
            recipient_email_we_vote_id = email_address_object.we_vote_id
            recipient_voter_email = email_address_object.normalized_email_address
        else:
            # Store the friend invitation in FriendInvitationEmailLink table
            friend_invitation_results = store_internal_friend_invitation_with_unknown_email(
                sender_voter, invitation_message, email_address_object)
            status += friend_invitation_results['status'] + " "
            success = friend_invitation_results['success']
            sender_voter_we_vote_id = sender_voter.we_vote_id
            recipient_voter_we_vote_id = ""
            recipient_email_we_vote_id = email_address_object.we_vote_id
            recipient_voter_email = email_address_object.normalized_email_address

        # TODO DALE - What kind of policy do we want re: sending a second email to a person?
        # Create the outbound email description, then schedule it
        if friend_invitation_results['friend_invitation_saved'] and send_now:
            kind_of_email_template = FRIEND_INVITATION_TEMPLATE
            outbound_results = email_manager.create_email_outbound_description(
                sender_voter_we_vote_id, recipient_voter_we_vote_id,
                recipient_email_we_vote_id, recipient_voter_email,
                invitation_message, kind_of_email_template)
            status += outbound_results['status'] + " "
            if outbound_results['email_outbound_description_saved']:
                email_outbound_description = outbound_results['email_outbound_description']
                schedule_results = email_manager.schedule_email(email_outbound_description)
                if schedule_results['email_scheduled_saved']:
                    messages_to_send.append(schedule_results['email_scheduled_id'])
                status += schedule_results['status'] + " "

    # When we are done scheduling all email, send it with a single connection to the smtp server
    # if send_now:
    #     send_results = email_manager.send_scheduled_email_list(messages_to_send)

    results = {
        'success':                              success,
        'status':                               status,
        'voter_device_id':                      voter_device_id,
        'sender_voter_email_address_missing':   False,
        'error_message_to_show_voter':          error_message_to_show_voter
    }
    return results


def friend_invite_response_for_api(voter_device_id, kind_of_invite_response, other_voter_we_vote_id,
                                   recipient_voter_email=''):
    """
    friendInviteResponse
    :param voter_device_id:
    :param kind_of_invite_response:
    :param other_voter_we_vote_id:
    :param recipient_voter_email:
    :return:
    """
    success = False
    status = "IN_DEVELOPMENT"

    results = is_voter_device_id_valid(voter_device_id)
    if not results['success']:
        error_results = {
            'status':                               results['status'],
            'success':                              False,
            'voter_device_id':                      voter_device_id,
        }
        return error_results

    voter_manager = VoterManager()
    voter_results = voter_manager.retrieve_voter_from_voter_device_id(voter_device_id)
    voter_id = voter_results['voter_id']
    if not positive_value_exists(voter_id):
        error_results = {
            'status':                               "VOTER_NOT_FOUND_FROM_VOTER_DEVICE_ID",
            'success':                              False,
            'voter_device_id':                      voter_device_id,
        }
        return error_results
    voter = voter_results['voter']

    if kind_of_invite_response != DELETE_INVITATION_EMAIL_SENT_BY_ME:
        other_voter_results = voter_manager.retrieve_voter_by_we_vote_id(other_voter_we_vote_id)
        other_voter_id = other_voter_results['voter_id']
        if not positive_value_exists(other_voter_id):
            error_results = {
                'status':                               "VOTER_NOT_FOUND_FROM_OTHER_VOTER_WE_VOTE_ID",
                'success':                              False,
                'voter_device_id':                      voter_device_id,
            }
            return error_results
        other_voter = other_voter_results['voter']

    friend_manager = FriendManager()
    if kind_of_invite_response == UNFRIEND_CURRENT_FRIEND:
        results = friend_manager.unfriend_current_friend(voter.we_vote_id, other_voter.we_vote_id)
    elif kind_of_invite_response == DELETE_INVITATION_EMAIL_SENT_BY_ME:
        results = friend_manager.process_friend_invitation_email_response(voter, recipient_voter_email,
                                                                          kind_of_invite_response)
    else:
        results = friend_manager.process_friend_invitation_voter_response(other_voter, voter, kind_of_invite_response)
    success = results['success']
    status = results['status']

    results = {
        'success':              success,
        'status':               status,
        'voter_device_id':      voter_device_id,
    }
    return results


def friend_list_for_api(voter_device_id,
                        kind_of_list_we_are_looking_for=CURRENT_FRIENDS,
                        state_code=''):
    success = False
    friend_list_found = False
    friend_list = []

    results = is_voter_device_id_valid(voter_device_id)
    if not results['success']:
        error_results = {
            'status':               results['status'],
            'success':              False,
            'voter_device_id':      voter_device_id,
            'state_code':           state_code,
            'kind_of_list':         kind_of_list_we_are_looking_for,
            'friend_list_found':    False,
            'friend_list':          friend_list,
        }
        return error_results

    voter_manager = VoterManager()
    voter_results = voter_manager.retrieve_voter_from_voter_device_id(voter_device_id)
    voter_id = voter_results['voter_id']
    if not positive_value_exists(voter_id):
        error_results = {
            'status':               "VOTER_NOT_FOUND_FROM_VOTER_DEVICE_ID",
            'success':              False,
            'voter_device_id':      voter_device_id,
            'state_code':           state_code,
            'kind_of_list':         kind_of_list_we_are_looking_for,
            'friend_list_found':    False,
            'friend_list':          friend_list,
        }
        return error_results
    voter = voter_results['voter']

    # if kind_of_list in (
    # CURRENT_FRIENDS, FRIEND_INVITATIONS_SENT_TO_ME, FRIEND_INVITATIONS_SENT_BY_ME, FRIENDS_IN_COMMON,
    # IGNORED_FRIEND_INVITATIONS, SUGGESTED_FRIENDS):
    friend_manager = FriendManager()
    if kind_of_list_we_are_looking_for == CURRENT_FRIENDS:
        retrieve_current_friends_results = friend_manager.retrieve_current_friends(voter.we_vote_id)
        success = retrieve_current_friends_results['success']
        status = retrieve_current_friends_results['status']
        if retrieve_current_friends_results['friend_list_found']:
            current_friend_list = retrieve_current_friends_results['friend_list']
            for friend_voter in current_friend_list:
                one_friend = {
                    "voter_we_vote_id":                 friend_voter.we_vote_id,
                    "voter_display_name":               friend_voter.get_full_name(),
                    "voter_photo_url":                  friend_voter.voter_photo_url(),
                    "voter_twitter_handle":             friend_voter.twitter_screen_name,
                    "voter_twitter_description":        "",  # To be implemented
                    "voter_twitter_followers_count":    0,  # To be implemented
                    "voter_state_code":                 "",  # To be implemented
                    "invitation_status":                "",  # Not used with CurrentFriends
                }
                friend_list.append(one_friend)
    elif kind_of_list_we_are_looking_for == FRIEND_INVITATIONS_SENT_TO_ME:
        retrieve_invitations_sent_to_me_results = friend_manager.retrieve_friend_invitations_sent_to_me(
            voter.we_vote_id)
        success = retrieve_invitations_sent_to_me_results['success']
        status = retrieve_invitations_sent_to_me_results['status']
        if retrieve_invitations_sent_to_me_results['friend_list_found']:
            raw_friend_list = retrieve_invitations_sent_to_me_results['friend_list']
            for one_friend_invitation in raw_friend_list:
                # Augment the line with voter information
                friend_voter_results = voter_manager.retrieve_voter_by_we_vote_id(
                    one_friend_invitation.sender_voter_we_vote_id)  # This is the voter who sent the invitation to me
                if friend_voter_results['voter_found']:
                    friend_voter = friend_voter_results['voter']
                    one_friend = {
                        "voter_we_vote_id":                 friend_voter.we_vote_id,
                        "voter_display_name":               friend_voter.get_full_name(),
                        "voter_photo_url":                  friend_voter.voter_photo_url(),
                        "voter_twitter_handle":             friend_voter.twitter_screen_name,
                        "voter_twitter_description":        "",  # To be implemented
                        "voter_twitter_followers_count":    0,  # To be implemented
                        "voter_state_code":                 "",  # To be implemented
                        "invitation_status":                "",  # Not used for invitations sent to me
                    }
                    friend_list.append(one_friend)
    elif kind_of_list_we_are_looking_for == FRIEND_INVITATIONS_SENT_BY_ME:
        retrieve_invitations_sent_by_me_results = friend_manager.retrieve_friend_invitations_sent_by_me(
            voter.we_vote_id)
        success = retrieve_invitations_sent_by_me_results['success']
        status = retrieve_invitations_sent_by_me_results['status']
        if retrieve_invitations_sent_by_me_results['friend_list_found']:
            raw_friend_list = retrieve_invitations_sent_by_me_results['friend_list']
            for one_friend_invitation in raw_friend_list:
                # Two kinds of invitations come in the raw_friend_list, 1) an invitation connected to voter
                # 2) an invitation to a previously unrecognized email address
                if hasattr(one_friend_invitation, 'recipient_voter_we_vote_id'):
                    recipient_voter_we_vote_id = one_friend_invitation.recipient_voter_we_vote_id
                else:
                    recipient_voter_we_vote_id = ""

                if positive_value_exists(recipient_voter_we_vote_id):
                    friend_voter_results = voter_manager.retrieve_voter_by_we_vote_id(
                        recipient_voter_we_vote_id)  # The is the voter who received invitation
                    if friend_voter_results['voter_found']:
                        friend_voter = friend_voter_results['voter']
                        one_friend = {
                            "voter_we_vote_id":                 friend_voter.we_vote_id,
                            "voter_display_name":               friend_voter.get_full_name(),
                            "voter_photo_url":                  friend_voter.voter_photo_url(),
                            "voter_twitter_handle":             friend_voter.twitter_screen_name,
                            "voter_twitter_description":        "",  # To be implemented
                            "voter_twitter_followers_count":    0,  # To be implemented
                            "voter_state_code":                 "",  # To be implemented
                            "voter_email_address":              "",
                            "invitation_status":                one_friend_invitation.invitation_status,
                        }
                        friend_list.append(one_friend)
                else:
                    if hasattr(one_friend_invitation, 'recipient_voter_email'):
                        if positive_value_exists(one_friend_invitation.recipient_voter_email):
                            one_friend = {
                                "voter_we_vote_id":                 "",
                                "voter_display_name":               "",
                                "voter_photo_url":                  "",
                                "voter_twitter_handle":             "",
                                "voter_twitter_description":        "",  # To be implemented
                                "voter_twitter_followers_count":    0,  # To be implemented
                                "voter_state_code":                 "",  # To be implemented
                                "voter_email_address":              one_friend_invitation.recipient_voter_email,
                                "invitation_status":                one_friend_invitation.invitation_status,
                            }
                            friend_list.append(one_friend)
    else:
        status = kind_of_list_we_are_looking_for + " KIND_OF_LIST_NOT_IMPLEMENTED_YET"

    results = {
        'success':              success,
        'status':               status,
        'voter_device_id':      voter_device_id,
        'state_code':           state_code,
        'kind_of_list':         kind_of_list_we_are_looking_for,
        'friend_list_found':    friend_list_found,
        'friend_list':          friend_list,
    }
    return results


def retrieve_voter_and_email_address(one_normalized_raw_email):
    """
    Starting with an incoming email address, find the EmailAddress and Voter that owns it (if it exists)
    Includes code to "heal" the data if needed.
    :param one_normalized_raw_email:
    :return:
    """
    voter_friend_found = False
    voter_friend = Voter()
    success = False
    status = ""

    voter_manager = VoterManager()
    email_manager = EmailManager()
    email_address_object = EmailAddress()
    email_address_object_found = False

    email_results = email_manager.retrieve_email_address_object(one_normalized_raw_email)

    if email_results['email_address_object_found']:
        # We have an EmailAddress entry for this raw email
        email_address_object_found = True
        email_address_object = email_results['email_address_object']
    else:
        # We need to create an EmailAddress entry for this raw email
        voter_by_email_results = voter_manager.retrieve_voter_by_email(one_normalized_raw_email)
        if voter_by_email_results['voter_found']:
            # Create EmailAddress entry for existing voter
            voter_friend_found = True
            voter_friend = voter_by_email_results['voter']
            email_results = email_manager.create_email_address_for_voter(one_normalized_raw_email, voter_friend)
        else:
            # Create EmailAddress entry without voter
            voter_friend_found = False
            email_results = email_manager.create_email_address(one_normalized_raw_email)

        if email_results['email_address_object_saved']:
            # We recognize the email
            email_address_object_found = True
            email_address_object = email_results['email_address_object']

    # double-check that we have email_address_object
    if not email_address_object_found:
        success = False
        status = "RETRIEVE_VOTER_AND_EMAIL-EMAIL_ADDRESS_OBJECT_MISSING"
        results = {
            'success':              success,
            'status':               status,
            'voter_found':          voter_friend_found,
            'voter':                voter_friend,
            'email_address_object': email_address_object,
        }
        return results
    else:
        success = True

    if not voter_friend_found:
        if positive_value_exists(email_address_object.voter_we_vote_id):
            voter_friend_results = voter_manager.retrieve_voter_by_we_vote_id(email_address_object.voter_we_vote_id)
            if not voter_friend_results['success']:
                # Error making the call -- do not remove voter_we_vote_id from email_address_object
                pass
            else:
                if voter_friend_results['voter_found']:
                    voter_friend_found = True
                    voter_friend = voter_friend_results['voter']
                else:
                    email_address_object.voter_we_vote_id = ''
                    voter_friend_found = False
                    voter_friend = Voter()

    # Does another, different voter use this email address?
    # voter_by_email_results = voter_manager.retrieve_voter_by_email(one_normalized_raw_email)
    # If so, we need to ...

    results = {
        'success':              success,
        'status':               status,
        'voter_found':          voter_friend_found,
        'voter':                voter_friend,
        'email_address_object': email_address_object,
    }
    return results


def store_internal_friend_invitation_with_two_voters(voter, invitation_message,
                                                     voter_friend):
    sender_voter_we_vote_id = voter.we_vote_id
    recipient_voter_we_vote_id = voter_friend.we_vote_id

    # Check to make sure the sender_voter is not trying to invite self
    if sender_voter_we_vote_id == recipient_voter_we_vote_id:
        success = False
        status = "CANNOT_INVITE_SELF"
        friend_invitation = FriendInvitationVoterLink()
        results = {
            'success':                  success,
            'status':                   status,
            'friend_invitation_saved':  False,
            'friend_invitation':        friend_invitation,
        }
        return results

    friend_manager = FriendManager()
    sender_email_address_verified = voter.has_email_with_verified_ownership()
    create_results = friend_manager.create_or_update_friend_invitation_voter_link(
        sender_voter_we_vote_id, recipient_voter_we_vote_id, invitation_message, sender_email_address_verified)
    results = {
        'success':                  create_results['status'],
        'status':                   create_results['status'],
        'friend_invitation_saved':  create_results['friend_invitation_saved'],
        'friend_invitation':        create_results['friend_invitation'],
    }

    return results


def store_internal_friend_invitation_with_unknown_email(voter, invitation_message,
                                                        email_address_object):
    sender_voter_we_vote_id = voter.we_vote_id
    recipient_email_we_vote_id = email_address_object.we_vote_id
    recipient_voter_email = email_address_object.normalized_email_address

    friend_manager = FriendManager()
    sender_email_address_verified = voter.has_email_with_verified_ownership()
    create_results = friend_manager.create_or_update_friend_invitation_email_link(
        sender_voter_we_vote_id, recipient_email_we_vote_id,
        recipient_voter_email, invitation_message, sender_email_address_verified)
    results = {
        'success':                  create_results['success'],
        'status':                   create_results['status'],
        'friend_invitation_saved':  create_results['friend_invitation_saved'],
        'friend_invitation':        create_results['friend_invitation'],
    }

    return results
