# apis_v1/urls.py
# Brought to you by We Vote. Be good.
# -*- coding: UTF-8 -*-
"""
This is called from config/urls.py like this:
    url(r'^apis/v1/', include('apis_v1.urls', namespace="apis_v1")),
"""

from django.conf.urls import url
from . import views
from . import views_docs

urlpatterns = [
    # Actual API Calls
    url(r'^ballotItemOptionsRetrieve/', views.ballot_item_options_retrieve_view, name='ballotItemOptionsRetrieveView'),
    url(r'^candidateRetrieve/', views.candidate_retrieve_view, name='candidateRetrieveView'),
    url(r'^candidatesRetrieve/', views.candidates_retrieve_view, name='candidatesRetrieveView'),
    url(r'^deviceIdGenerate/$', views.device_id_generate_view, name='deviceIdGenerateView'),
    url(r'^electionsRetrieve/', views.ElectionsRetrieveView.as_view(), name='electionsRetrieveView'),
    url(r'^measureRetrieve/', views.measure_retrieve_view, name='measureRetrieveView'),
    url(r'^officeRetrieve/', views.office_retrieve_view, name='officeRetrieveView'),
    url(r'^organizationCount/', views.organization_count_view, name='organizationCountView'),
    url(r'^organizationFollow/', views.organization_follow_api_view, name='organizationFollowView'),
    url(r'^organizationFollowIgnore/', views.organization_follow_ignore_api_view, name='organizationFollowIgnoreView'),
    url(r'^organizationRetrieve/', views.organization_retrieve_view, name='organizationRetrieveView'),
    url(r'^organizationSave/', views.organization_save_view, name='organizationSaveView'),
    url(r'^organizationSearch/', views.organization_search_view, name='organizationSearchView'),
    url(r'^organizationStopFollowing/',
        views.organization_stop_following_api_view, name='organizationStopFollowingView'),
    url(r'^positionLikeCount/', views.position_like_count_view, name='positionLikeCountView'),
    url(r'^positionListForBallotItem/', views.position_list_for_ballot_item_view, name='positionListForBallotItemView'),
    url(r'^positionOpposeCountForBallotItem/',
        views.position_oppose_count_for_ballot_item_view, name='positionOpposeCountForBallotItemView'),
    url(r'^positionRetrieve/', views.position_retrieve_view, name='positionRetrieveView'),
    url(r'^positionSave/', views.position_save_view, name='positionSaveView'),
    url(r'^positionSupportCountForBallotItem/',
        views.position_support_count_for_ballot_item_view, name='positionSupportCountForBallotItemView'),
    url(r'^quickInfoRetrieve/', views.quick_info_retrieve_view, name='quickInfoRetrieveView'),
    url(r'^voterAddressRetrieve/', views.voter_address_retrieve_view, name='voterAddressRetrieveView'),
    url(r'^voterAddressSave/', views.voter_address_save_view, name='voterAddressSaveView'),
    url(r'^voterBallotItemsRetrieve/', views.voter_ballot_items_retrieve_view, name='voterBallotItemsRetrieveView'),
    url(r'^voterBallotItemsRetrieveFromGoogleCivic/',
        views.voter_ballot_items_retrieve_from_google_civic_view, name='voterBallotItemsRetrieveFromGoogleCivicView'),
    url(r'^voterCount/', views.voter_count_view, name='voterCountView'),
    url(r'^voterCreate/', views.voter_create_view, name='voterCreateView'),
    url(r'^voterGuidePossibilityRetrieve/',
        views.voter_guide_possibility_retrieve_view, name='voterGuidePossibilityRetrieveView'),
    url(r'^voterGuidePossibilitySave/', views.voter_guide_possibility_save_view, name='voterGuidePossibilitySaveView'),
    url(r'^voterGuidesToFollowRetrieve/',
        views.voter_guides_to_follow_retrieve_view, name='voterGuidesToFollowRetrieveView'),
    url(r'^voterOpposingSave/', views.voter_opposing_save_view, name='voterOpposingSaveView'),
    url(r'^voterPositionCommentSave/', views.voter_position_comment_save_view, name='voterPositionCommentSaveView'),
    url(r'^voterPositionRetrieve/', views.voter_position_retrieve_view, name='voterPositionRetrieveView'),
    url(r'^voterPositionLikeOffSave/', views.voter_position_like_off_save_view, name='voterPositionLikeOffSaveView'),
    url(r'^voterPositionLikeOnSave/', views.voter_position_like_on_save_view, name='voterPositionLikeOnSaveView'),
    url(r'^voterPositionLikeStatusRetrieve/',
        views.voter_position_like_status_retrieve_view, name='voterPositionLikeStatusRetrieveView'),
    url(r'^voterRetrieve/', views.VoterRetrieveView.as_view(), name='voterRetrieveView'),
    url(r'^voterSupportingSave/', views.voter_supporting_save_view, name='voterSupportingSaveView'),
    url(r'^voterStarOffSave/', views.voter_star_off_save_view, name='voterStarOffSaveView'),
    url(r'^voterStarOnSave/', views.voter_star_on_save_view, name='voterStarOnSaveView'),
    url(r'^voterStarStatusRetrieve/', views.voter_star_status_retrieve_view, name='voterStarStatusRetrieveView'),
    url(r'^voterStopOpposingSave/', views.voter_stop_opposing_save_view, name='voterStopOpposingSaveView'),
    url(r'^voterStopSupportingSave/', views.voter_stop_supporting_save_view, name='voterStopSupportingSaveView'),

    ##########################
    # API Documentation Views
    url(r'^docs/$', views_docs.apis_index_doc_view, name='apisIndex'),
    url(r'^docs/ballotItemOptionsRetrieve/$',
        views_docs.ballot_item_options_retrieve_doc_view, name='ballotItemOptionsRetrieveDocs'),
    url(r'^docs/candidateRetrieve/$', views_docs.candidate_retrieve_doc_view, name='candidateRetrieveDocs'),
    url(r'^docs/candidatesRetrieve/$', views_docs.candidates_retrieve_doc_view, name='candidatesRetrieveDocs'),
    url(r'^docs/deviceIdGenerate/$', views_docs.device_id_generate_doc_view, name='deviceIdGenerateDocs'),
    url(r'^docs/electionsRetrieve/$', views_docs.elections_retrieve_doc_view, name='electionsRetrieveDocs'),
    url(r'^docs/measureRetrieve/$', views_docs.measure_retrieve_doc_view, name='measureRetrieveDocs'),
    url(r'^docs/officeRetrieve/$', views_docs.office_retrieve_doc_view, name='officeRetrieveDocs'),
    url(r'^docs/organizationCount/$', views_docs.organization_count_doc_view, name='organizationCountDocs'),
    url(r'^docs/organizationFollow/', views_docs.organization_follow_doc_view, name='organizationFollowDocs'),
    url(r'^docs/organizationFollowIgnore/',
        views_docs.organization_follow_ignore_doc_view, name='organizationFollowIgnoreDocs'),
    url(r'^docs/organizationRetrieve/$', views_docs.organization_retrieve_doc_view, name='organizationRetrieveDocs'),
    url(r'^docs/organizationSave/$', views_docs.organization_save_doc_view, name='organizationSaveDocs'),
    url(r'^docs/organizationSearch/$', views_docs.organization_search_doc_view, name='organizationSearchDocs'),
    url(r'^docs/organizationStopFollowing/',
        views_docs.organization_stop_following_doc_view, name='organizationStopFollowingDocs'),
    url(r'^docs/positionListForBallotItem/',
        views_docs.position_list_for_ballot_item_doc_view, name='positionListForBallotItemDocs'),
    url(r'^docs/positionOpposeCountForBallotItem/',
        views_docs.position_oppose_count_for_ballot_item_doc_view, name='positionOpposeCountForBallotItemDocs'),
    url(r'^docs/positionLikeCount/$', views_docs.position_like_count_doc_view, name='positionLikeCountDocs'),
    url(r'^docs/positionRetrieve/$', views_docs.position_retrieve_doc_view, name='positionRetrieveDocs'),
    url(r'^docs/positionSave/$', views_docs.position_save_doc_view, name='positionSaveDocs'),
    url(r'^docs/positionSupportCountForBallotItem/',
        views_docs.position_support_count_for_ballot_item_doc_view, name='positionSupportCountForBallotItemDocs'),
    url(r'^docs/quickInfoRetrieve/$', views_docs.quick_info_retrieve_doc_view, name='quickInfoRetrieveDocs'),
    url(r'^docs/voterAddressRetrieve/$', views_docs.voter_address_retrieve_doc_view, name='voterAddressRetrieveDocs'),
    url(r'^docs/voterAddressSave/$', views_docs.voter_address_save_doc_view, name='voterAddressSaveDocs'),
    url(r'^docs/voterBallotItemsRetrieve/$',
        views_docs.voter_ballot_items_retrieve_doc_view, name='voterBallotItemsRetrieveDocs'),
    url(r'^docs/voterBallotItemsRetrieveFromGoogleCivic/$',
        views_docs.voter_ballot_items_retrieve_from_google_civic_doc_view,
        name='voterBallotItemsRetrieveFromGoogleCivicDocs'),
    url(r'^docs/voterCount/$', views_docs.voter_count_doc_view, name='voterCountDocs'),
    url(r'^docs/voterCreate/$', views_docs.voter_create_doc_view, name='voterCreateDocs'),
    url(r'^docs/voterGuidePossibilityRetrieve/$',
        views_docs.voter_guide_possibility_retrieve_doc_view, name='voterGuidePossibilityRetrieveDocs'),
    url(r'^docs/voterGuidePossibilitySave/$',
        views_docs.voter_guide_possibility_save_doc_view, name='voterGuidePossibilitySaveDocs'),
    url(r'^docs/voterGuidesToFollowRetrieve/$',
        views_docs.voter_guides_to_follow_retrieve_doc_view, name='voterGuidesToFollowRetrieveDocs'),
    url(r'^docs/voterOpposingSave/$', views_docs.voter_opposing_save_doc_view, name='voterOpposingSaveDocs'),
    url(r'^docs/voterPositionRetrieve/$',
        views_docs.voter_position_retrieve_doc_view, name='voterPositionRetrieveDocs'),
    url(r'^docs/voterPositionCommentSave/$',
        views_docs.voter_position_comment_save_doc_view, name='voterPositionCommentSaveDocs'),
    url(r'^docs/voterPositionLikeOffSave/$',
        views_docs.voter_position_like_off_save_doc_view, name='voterPositionLikeOffSaveDocs'),
    url(r'^docs/voterPositionLikeOnSave/$',
        views_docs.voter_position_like_on_save_doc_view, name='voterPositionLikeOnSaveDocs'),
    url(r'^docs/voterPositionLikeStatusRetrieve/$',
        views_docs.voter_position_like_status_retrieve_doc_view, name='voterPositionLikeStatusRetrieveDocs'),
    url(r'^docs/voterRetrieve/$', views_docs.voter_retrieve_doc_view, name='voterRetrieveDocs'),
    url(r'^docs/voterStarOffSave/$', views_docs.voter_star_off_save_doc_view, name='voterStarOffSaveDocs'),
    url(r'^docs/voterStarOnSave/$', views_docs.voter_star_on_save_doc_view, name='voterStarOnSaveDocs'),
    url(r'^docs/voterStarStatusRetrieve/$',
        views_docs.voter_star_status_retrieve_doc_view, name='voterStarStatusRetrieveDocs'),
    url(r'^docs/voterStopOpposingSave/$',
        views_docs.voter_stop_opposing_save_doc_view, name='voterStopOpposingSaveDocs'),
    url(r'^docs/voterStopSupportingSave/$',
        views_docs.voter_stop_supporting_save_doc_view, name='voterStopSupportingSaveDocs'),
    url(r'^docs/voterSupportingSave/$', views_docs.voter_supporting_save_doc_view, name='voterSupportingSaveDocs'),
]
