from fastapi import APIRouter, HTTPException, Depends, status

from models.indexer import IndexerResponse, ReposResponse
from models.indexer import CreateNewRepo, RepoCredentials, NewRepoCredentials

from services.indexer import create_new_repo, list_repositories
from services.indexer import create_new_credentials, get_all_credentials

from dependencies import get_db

from sqlalchemy.orm import Session


router = APIRouter()


@router.post(
    "/repos",
    name="indexer:add-repo",
)
async def add_repo(new_repo: CreateNewRepo, db: Session = Depends(get_db)):
    """
    Add a new repository to be indexed.
    """
    if not new_repo.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid repository URL")

    create_new_repo(new_repo.url, new_repo.name, new_repo.credentials_name, db)

    return IndexerResponse(status=status.HTTP_200_OK, message="Repository added successfully")


@router.get(
    "/repos",
    name="indexer:list-repos",
)
async def list_repos(db: Session = Depends(get_db)):
    """
    List all indexed repositories.
    """
    repos = list_repositories(db)

    return ReposResponse(repos=repos)


@router.post(
    "/credentials",
    name="indexer:add-credentials",
)
async def add_credentials(credentials: NewRepoCredentials, db: Session = Depends(get_db)):
    """
    Add new credentials for accessing private repositories.
    """

    if not credentials.name:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Name is required")
    if not credentials.username:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="username is required")
    if not (credentials.password or credentials.token):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="Password or token is required")

    create_new_credentials(
        credentials.name, credentials.username, credentials.password, credentials.token, db)

    return IndexerResponse(status=status.HTTP_200_OK, message="Credentials added successfully")


@router.get(
    "/credentials",
    name="indexer:get-credentials",
)
async def get_credentials(db: Session = Depends(get_db)) -> list[RepoCredentials]:
    """
    List all stored credentials.
    """
    return get_all_credentials(db)


# @router.get(
#     "/index",
#     name="indexer:get-repo-info",
# )
# async def get_repo_info(name: str, db: Session = Depends(get_db)) -> IndexerResponse | None:
#     """
#     Get indexing information for a specific repository.
#     """
#     try:
#         get_credentials_by_name(name, db)
#     except HTTPException:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                             detail="get_credentials_by_name failed unexpectedly")
