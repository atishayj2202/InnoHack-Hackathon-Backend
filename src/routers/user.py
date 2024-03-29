from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status
from starlette.responses import Response

from src.auth.user_auth import VerifiedUser, verify_user
from src.client.cockroach import CockroachDBClient
from src.client.computer_vision import ComputerVisionCli
from src.client.firebase import FirebaseClient
from src.client.openai_client import OpenAIClient
from src.schemas.post import PostCreateRequest, PostLongResponse, PostResponse
from src.schemas.user import (
    RatingRequest,
    UserCreateRequest,
    UserResponse,
    UserUpdateRequest,
)
from src.services.user import UserService
from src.utils.client import getCockroachClient, getFirebaseClient
from src.utils.enums import PostCategory

USER_PREFIX = "/user"
user_router = APIRouter(prefix=USER_PREFIX)
ENDPOINT_CREATE_USER = "/create-user/"  # done
ENDPOINT_CHECK_USER = "/check-user/"  # done
ENDPOINT_GET_USER = "/get-user/"  # done
ENDPOINT_FIND_USER_BY_ID = "/{user_id}/fetch-user-by-id/"  # done
ENDPOINT_ADD_FEEDBACK = "/add-feedback/"  # done
ENDPOINT_UPDATE_USER = "/update-user/"  # done
ENDPOINT_NEW_POST = "/new-post/"  # done
ENDPOINT_LIST_POST = "/list-posts/"  # done
ENDPOINT_GET_LEADERBOARD = "/{category}/get-leaderboard/"  # done
ENDPOINT_NEW_POSTS = "/add-post-by-json/"


@user_router.post(ENDPOINT_CREATE_USER)
async def post_create_user(
    request: UserCreateRequest,
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    firebase_client: FirebaseClient = Depends(getFirebaseClient),
):
    UserService.create_user(request, cockroach_client, firebase_client)
    return Response(status_code=status.HTTP_200_OK)


@user_router.get(
    ENDPOINT_CHECK_USER,
    dependencies=[Depends(verify_user)],
)
async def get_check_user():
    return Response(status_code=status.HTTP_200_OK)


@user_router.get(ENDPOINT_GET_USER, response_model=UserResponse)
async def get_user(
    verified_user: VerifiedUser = Depends(verify_user),
):
    return UserService.fetch_user(verified_user.requesting_user)


@user_router.post(ENDPOINT_ADD_FEEDBACK)
async def post_add_feedback(
    request: RatingRequest,
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    verified_user: VerifiedUser = Depends(verify_user),
):
    UserService.add_feedback(
        user=verified_user.requesting_user,
        request=request,
        cockroach_client=cockroach_client,
    )
    return Response(status_code=status.HTTP_200_OK)


@user_router.get(
    ENDPOINT_FIND_USER_BY_ID,
    response_model=UserResponse,
    dependencies=[Depends(verify_user)],
)
async def get_user_by_id(
    user_id: UUID,
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
):
    return UserService.fetch_user_by_id(user_id, cockroach_client)


@user_router.post(ENDPOINT_UPDATE_USER)
async def post_update_user(
    request: UserUpdateRequest,
    verified_user: VerifiedUser = Depends(verify_user),
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
):
    UserService.update_user(
        user=verified_user.requesting_user,
        request=request,
        cockroach_client=cockroach_client,
    )
    return Response(status_code=status.HTTP_200_OK)


@user_router.post(ENDPOINT_NEW_POST)
async def post_new_post(
    request: PostCreateRequest,
    verified_user: VerifiedUser = Depends(verify_user),
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    ai_client: OpenAIClient = Depends(OpenAIClient),
    image_parser_client: ComputerVisionCli = Depends(ComputerVisionCli),
):
    UserService.create_post(
        user=verified_user.requesting_user,
        request=request,
        cockroach_client=cockroach_client,
        ai_client=ai_client,
        image_parser_client=image_parser_client,
    )
    return Response(status_code=status.HTTP_200_OK)


@user_router.post(ENDPOINT_NEW_POSTS)
async def post_new_post(
    request: list[PostCreateRequest],
    verified_user: VerifiedUser = Depends(verify_user),
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
    ai_client: OpenAIClient = Depends(OpenAIClient),
    image_parser_client: ComputerVisionCli = Depends(ComputerVisionCli),
):
    for i in request:
        try:
            UserService.create_post(
                user=verified_user.requesting_user,
                request=i,
                cockroach_client=cockroach_client,
                ai_client=ai_client,
                image_parser_client=image_parser_client,
            )
        except:
            pass
    return Response(status_code=status.HTTP_200_OK)


@user_router.get(ENDPOINT_LIST_POST, response_model=list[PostLongResponse])
async def get_list_post(
    verified_user: VerifiedUser = Depends(verify_user),
    cockroach_client: CockroachDBClient = Depends(getCockroachClient),
):
    return UserService.fetch_posts(
        user=verified_user.requesting_user, cockroach_client=cockroach_client
    )


@user_router.get(ENDPOINT_GET_LEADERBOARD, response_model=list[PostResponse])
async def get_leaderboard(
    category: str, cockroach_client: CockroachDBClient = Depends(getCockroachClient)
):
    return UserService.fetch_leaderboard(
        cockroach_client=cockroach_client, category=PostCategory[category]
    )
